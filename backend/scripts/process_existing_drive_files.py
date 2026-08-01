import asyncio
import logging
import io
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_settings
from db.setup import database
from db.models import newsletters, summaries, model_usage
from helpers.storage import list_files_in_folder, download_from_drive, upload_to_drive
from helpers.text_utils import extract_text_from_file, generate_pdf_thumbnail, sanitize_filename, compress_pdf
from llm.providers import choose_llm_and_summarize

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

async def process_files():
    if not settings.google_drive_folder_id:
        logger.error("GOOGLE_DRIVE_FOLDER_ID not set.")
        return

    await database.connect()

    try:
        drive_files = list_files_in_folder(settings.google_drive_folder_id)
        logger.info(f"Found {len(drive_files)} files in folder.")

        # Filter files of correct mime type and extract their IDs
        filtered_files = [
            df for df in drive_files
            if df.get('mimeType') in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        ]
        file_ids = [df['id'] for df in filtered_files]

        if file_ids:
            from sqlalchemy import select
            query = select(newsletters.c.drive_file_id).where(newsletters.c.drive_file_id.in_(file_ids))
            existing_rows = await database.fetch_all(query)
            existing_drive_ids = {row['drive_file_id'] for row in existing_rows}
        else:
            existing_drive_ids = set()

        for df in filtered_files:
            file_id = df['id']
            filename = df['name']

            # Check if already in DB (by drive ID)
            if file_id in existing_drive_ids:
                logger.info(f"Skipping already processed file: {filename}")
                continue

            logger.info(f"Processing: {filename}")

            # Download
            content = download_from_drive(file_id)
            if not content: continue

            # Standardize Filename
            new_filename = sanitize_filename(filename)
            
            # For this script, we'll only re-upload if the filename actually changed
            # This helps avoid 'storageQuotaExceeded' errors for Service Accounts
            drive_file_id = file_id
            web_view_link = None
            
            if new_filename != filename:
                # Compress if PDF
                final_content = content
                if mime_type == "application/pdf":
                    final_content = compress_pdf(content)

                logger.info(f"Re-uploading as standardized/compressed: {new_filename}")
                drive_file_id, web_view_link = upload_to_drive(final_content, new_filename, mime_type)
                
                # If upload failed due to quota, fall back to original file_id
                if not drive_file_id:
                    logger.warning(f"Re-upload failed (likely quota). Falling back to original drive_id for {filename}")
                    drive_file_id = file_id
                    new_filename = filename # Keep original name in DB if re-upload failed
            else:
                logger.info(f"Filename already matches standard. Skipping re-upload for {filename}")
                final_content = content

            # Extract & Summarize
            file_type = "pdf" if mime_type == "application/pdf" else "docx"
            text = extract_text_from_file(io.BytesIO(final_content), file_type=file_type)
            summary_data = choose_llm_and_summarize(text)

            # Thumbnail
            thumbnail_drive_id = None
            if file_type == "pdf":
                thumb_bytes = generate_pdf_thumbnail(io.BytesIO(final_content))
                thumbnail_drive_id, _ = upload_to_drive(thumb_bytes, f"thumb_{new_filename}.png", "image/png")

            # Save to DB
            async with database.transaction():
                newsletter_id = await database.execute(
                    newsletters.insert().values(
                        filename=new_filename,
                        drive_file_id=drive_file_id,
                        drive_web_view_link=web_view_link,
                        thumbnail_drive_id=thumbnail_drive_id,
                        uploader="batch_script",
                        delivered=False
                    )
                )
                summary_id = await database.execute(
                    summaries.insert().values(
                        newsletter_id=newsletter_id,
                        summary=summary_data["summary"],
                    )
                )
                await database.execute(
                    model_usage.insert().values(
                        summary_id=summary_id,
                        model=summary_data["model"],
                        tokens=summary_data["tokens"],
                        cost_usd_estimate=summary_data["cost_usd_estimate"],
                    )
                )

            logger.info(f"Done: {new_filename}")

    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(process_files())
