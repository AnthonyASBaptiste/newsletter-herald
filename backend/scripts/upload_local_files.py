import asyncio
import logging
import io
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from config import get_settings
from db.setup import database
from db.models import newsletters, summaries, model_usage
from helpers.storage import upload_to_drive, make_file_public
from helpers.text_utils import extract_text_from_file, generate_pdf_thumbnail, sanitize_filename, compress_pdf
from llm.providers import choose_llm_and_summarize

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

async def process_local_files():
    # Folder containing newsletters (relative to the script)
    input_folder = Path(backend_dir).parent / "newsletters_to_upload"
    
    if not input_folder.exists():
        logger.error(f"Folder not found: {input_folder}")
        return

    await database.connect()

    try:
        # Get all PDF and DOCX files
        files = list(input_folder.glob("*.pdf")) + list(input_folder.glob("*.docx"))
        logger.info(f"Found {len(files)} files to process.")

        for file_path in files:
            filename = file_path.name
            mime_type = "application/pdf" if file_path.suffix.lower() == ".pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

            # Check if already in DB
            query = newsletters.select().where(newsletters.c.filename == sanitize_filename(filename))
            existing = await database.fetch_one(query)
            if existing:
                logger.info(f"Skipping already processed file: {filename}")
                continue

            logger.info(f"Processing: {filename}")

            try:
                # Read file content
                with open(file_path, "rb") as f:
                    content = f.read()

                # Standardize Filename
                new_filename = sanitize_filename(filename)
                
                # Compress if PDF
                final_content = content
                if mime_type == "application/pdf":
                    try:
                        final_content = compress_pdf(content)
                    except Exception as e:
                        logger.warning(f"Compression failed for {filename}, using original: {e}")

                # Upload to Cloudflare R2 (Primary) or Google Drive (Fallback)
                logger.info(f"Uploading {new_filename}...")
                drive_file_id, web_view_link = upload_to_drive(final_content, new_filename, mime_type)
                
                if not drive_file_id:
                    logger.error(f"Upload failed for {filename}, skipping.")
                    continue

                # Extract & Summarize
                file_type = "pdf" if mime_type == "application/pdf" else "docx"
                text = extract_text_from_file(io.BytesIO(final_content), file_type=file_type)
                
                logger.info(f"Generating summary for {new_filename}...")
                summary_data = choose_llm_and_summarize(text)

                # Thumbnail
                thumbnail_drive_id = None
                if file_type == "pdf":
                    try:
                        thumb_bytes = generate_pdf_thumbnail(io.BytesIO(final_content))
                        thumbnail_drive_id, _ = upload_to_drive(thumb_bytes, f"thumb_{new_filename}.png", "image/png")
                    except Exception as thumb_err:
                        logger.error(f"Failed to generate thumbnail for {new_filename}: {thumb_err}")

                # Save to DB
                try:
                    logger.info(f"Saving {new_filename} to DB...")
                    async with database.transaction():
                        # Construct tags string
                        tags_list = []
                        if summary_data.get("liturgical_season"):
                            tags_list.append(summary_data["liturgical_season"].lower().replace(" ", "-"))
                        if summary_data.get("calendar_year"):
                            tags_list.append(str(summary_data["calendar_year"]))
                        if summary_data.get("liturgical_year"):
                            tags_list.append(summary_data["liturgical_year"])
                        
                        tags_str = ", ".join(tags_list) if tags_list else None

                        newsletter_id = await database.execute(
                            newsletters.insert().values(
                                filename=new_filename,
                                drive_file_id=drive_file_id,
                                drive_web_view_link=web_view_link,
                                thumbnail_drive_id=thumbnail_drive_id,
                                uploader="local_batch_upload",
                                schedule_date=summary_data.get("schedule_date"),
                                tags=tags_str,
                                delivered=False
                            )
                        )
                        logger.info(f"Inserted newsletter ID: {newsletter_id}")
                        
                        summary_id = await database.execute(
                            summaries.insert().values(
                                newsletter_id=newsletter_id,
                                title=summary_data["title"],
                                summary=summary_data["summary"],
                            )
                        )
                        logger.info(f"Inserted summary ID: {summary_id}")

                        await database.execute(
                            model_usage.insert().values(
                                summary_id=summary_id,
                                model=summary_data["model"],
                                tokens=summary_data["tokens"],
                                cost_usd_estimate=summary_data["cost_usd_estimate"],
                            )
                        )
                    logger.info(f"Successfully processed and SAVED to DB: {new_filename}")
                except Exception as db_err:
                    logger.error(f"DATABASE INSERT FAILED for {new_filename}: {db_err}")
                    raise # Re-raise to be caught by outer try-except

            except Exception as e:
                logger.error(f"Failed to process {filename}: {e}", exc_info=True)

    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(process_local_files())
