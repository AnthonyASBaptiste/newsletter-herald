import logging
import tempfile
import os
import io
from typing import Dict, Any, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from helpers.key_utils import verify_api_key
from helpers.text_utils import extract_text_from_file, generate_pdf_thumbnail, sanitize_filename, compress_pdf
from helpers.storage import upload_to_drive
from helpers.validation import validate_newsletter_date
from sqlalchemy import and_

from llm.providers import choose_llm_and_summarize

from db.setup import database
from db.models import summaries, model_usage, newsletters

from config import get_settings

# Get settings from centralized configuration
settings = get_settings()

# Create a logger for this module
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI application.
    """
    # Startup
    logger.info("Starting up application")
    await database.connect()
    logger.info("Database connected")
    yield
    # Shutdown
    logger.info("Shutting down application")
    await database.disconnect()
    logger.info("Database disconnected")

app = FastAPI(
    title=settings.app_name,
    description="The API Gateway acts as a single entry point that manages client requests and delegates them to the "
                "appropriate backend services.",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> Dict[str, str]:
    """
    A simple endpoint to confirm the API is running.
    """
    logger.debug("Root endpoint accessed")
    return {"message": f"Welcome to your {settings.app_name}"}


@app.post("/upload-document")
async def upload_summary(
    file: UploadFile = File(...),
    _: None = Depends(verify_api_key)
) -> JSONResponse:
    """
    Handles the uploading and summarization of document files.
    """
    logger.info(f"Processing uploaded file: {file.filename} ({file.content_type})")
    
    # Validate file type
    accepted_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    if file.content_type not in accepted_types:
        logger.warning(f"Unsupported file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Read file contents
    contents = await file.read()
    
    # Extract text from file
    try:
        if file.content_type == "application/pdf":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file_path = temp_file.name
                temp_file.write(contents)
            
            try:
                text = extract_text_from_file(temp_file_path, file_type="pdf")
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        else:
            file.file.seek(0)
            text = extract_text_from_file(file.file, file_type="docx")
            
        logger.debug(f"Text extracted successfully from {file.filename}")
    except Exception as e:
        logger.error(f"Error extracting text from file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting text: {str(e)}")

    # Generate summary
    try:
        logger.info("Generating summary using LLM")
        summary = choose_llm_and_summarize(text)
        
        # Sanitize and standardize filename
        standard_filename = sanitize_filename(file.filename)
        logger.info(f"Standardized filename: {standard_filename}")

        # Compress file if it's a PDF
        final_contents = contents
        if file.content_type == "application/pdf":
            logger.info("Compressing PDF...")
            final_contents = compress_pdf(contents)

        # Upload to Google Drive
        logger.info("Uploading file to Google Drive")
        drive_file_id, web_view_link = upload_to_drive(final_contents, standard_filename, file.content_type)

        # Generate and upload thumbnail if it's a PDF
        thumbnail_drive_id = None
        if file.content_type == "application/pdf":
            try:
                logger.info("Generating PDF thumbnail")
                thumbnail_data = generate_pdf_thumbnail(io.BytesIO(final_contents))
                thumbnail_filename = f"thumb_{standard_filename}.png"
                thumbnail_drive_id, _ = upload_to_drive(thumbnail_data, thumbnail_filename, "image/png")
            except Exception as thumb_err:
                logger.error(f"Failed to generate thumbnail: {thumb_err}")

        # Construct tags string
        tags_list = []
        if summary.get("liturgical_season"):
            tags_list.append(summary["liturgical_season"].lower().replace(" ", "-"))
        if summary.get("calendar_year"):
            tags_list.append(str(summary["calendar_year"]))
        if summary.get("liturgical_year"):
            tags_list.append(summary["liturgical_year"])
        
        tags_str = ", ".join(tags_list) if tags_list else None

        # Validate newsletter date
        is_valid, target_sunday, error_msg = validate_newsletter_date(summary.get("schedule_date"))
        status = "draft" if is_valid else "failed_validation"
        logger.info(f"Date validation: is_valid={is_valid}, target_sunday={target_sunday}, status={status}")

        # Supersede older files for the same Sunday issue
        logger.info(f"Marking existing drafts/scheduled newsletters for Sunday {target_sunday} as superseded")
        update_query = newsletters.update().where(
            and_(
                newsletters.c.target_sunday == target_sunday,
                newsletters.c.status.in_(["draft", "scheduled", "failed_validation"])
            )
        ).values(status="superseded")
        await database.execute(update_query)

        # First, store newsletter information
        logger.debug("Storing newsletter information in database")
        newsletter_id = await database.execute(
            newsletters.insert().values(
                filename=standard_filename,
                drive_file_id=drive_file_id,
                drive_web_view_link=web_view_link,
                thumbnail_drive_id=thumbnail_drive_id,
                uploader="api_user",
                schedule_date=summary.get("schedule_date"),
                tags=tags_str,
                delivered=False,
                status=status,
                target_sunday=target_sunday
            )
        )

        # Then store summary in database
        logger.debug("Storing summary in database")
        summary_id = await database.execute(
            summaries.insert().values(
                newsletter_id=newsletter_id,
                title=summary["title"],
                summary=summary["summary"],
            )
        )

        # Store model usage in database
        await database.execute(
            model_usage.insert().values(
                summary_id=summary_id,
                model=summary["model"],
                tokens=summary["tokens"],
                cost_usd_estimate=summary["cost_usd_estimate"],
            )
        )
        
        logger.info(f"Summary generated and stored successfully (Newsletter ID: {newsletter_id}, Summary ID: {summary_id})")
        
        # Add drive info to response
        summary["newsletter_id"] = newsletter_id
        summary["thumbnail_drive_id"] = thumbnail_drive_id
        summary["drive_file_id"] = drive_file_id
        summary["drive_web_view_link"] = web_view_link
        summary["status"] = status
        summary["target_sunday"] = target_sunday.isoformat()
    except Exception as e:
        logger.error(f"LLM error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    return JSONResponse(content={
        "summary": summary,
        "validation": {
            "is_valid": is_valid,
            "target_sunday": target_sunday.isoformat(),
            "error_message": error_msg
        }
    })


@app.patch("/newsletters/{newsletter_id}")
async def update_newsletter(
    newsletter_id: int,
    data: Dict[str, Any],
    _: None = Depends(verify_api_key)
) -> JSONResponse:
    """
    Updates the metadata of a newsletter (e.g., schedule_date, tags).
    """
    logger.info(f"Updating newsletter {newsletter_id} with data: {data}")
    try:
        # Filter allowed fields
        allowed_fields = ["schedule_date", "tags", "delivered"]
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields to update")

        query = newsletters.update().where(newsletters.c.id == newsletter_id).values(**update_data)
        await database.execute(query)
        
        return JSONResponse(content={"message": "Newsletter updated successfully"})
    except Exception as e:
        logger.error(f"Error updating newsletter: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating newsletter: {e}")


@app.get("/newsletters")
async def get_newsletters() -> JSONResponse:
    """
    Fetches all newsletters and their associated summaries from the database.
    """
    logger.info("Fetching all newsletters from the database")
    try:
        query = """
            SELECT 
                n.id, n.filename, n.drive_web_view_link, n.thumbnail_drive_id, n.uploaded_at,
                s.title, s.summary
            FROM newsletters n
            LEFT JOIN summaries s ON n.id = s.newsletter_id
            ORDER BY n.uploaded_at DESC
        """
        rows = await database.fetch_all(query)
        
        result = []
        for row in rows:
            result.append({
                "id": row["id"],
                "filename": row["filename"],
                "drive_link": row["drive_web_view_link"],
                "thumbnail_id": row["thumbnail_drive_id"],
                "uploaded_at": row["uploaded_at"].isoformat() if row["uploaded_at"] else None,
                "title": row["title"],
                "summary": row["summary"]
            })
            
        return JSONResponse(content={"newsletters": result})
    except Exception as e:
        logger.error(f"Error fetching newsletters: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching newsletters: {e}")
