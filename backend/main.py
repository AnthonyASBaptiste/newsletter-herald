import logging
import tempfile
import os
from typing import Dict
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from helpers.key_utils import verify_api_key
from helpers.text_utils import extract_text_from_file

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
    
    Args:
        app: The FastAPI application instance
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


@app.get("/")
async def root() -> Dict[str, str]:
    """
    A simple endpoint to confirm the API is running.
    
    Returns:
        Dict[str, str]: A welcome message
    """
    logger.debug("Root endpoint accessed")
    return {"message": f"Welcome to your {settings.app_name}"}


@app.post("/upload-document")
async def upload_summary(
    file: UploadFile = File(...),
    _: None = Depends(verify_api_key)
) -> JSONResponse:
    """
    Handles the uploading and summarization of document files through an HTTP POST endpoint.
    The function accepts a PDF or DOCX file, extracts its textual content, and generates
    a summary using a language model.

    Args:
        file: An instance of UploadFile containing the uploaded document. Accepted
            file types are "application/pdf" and
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document".
        _: Dependency to verify the API key
        
    Returns:
        JSONResponse: A response containing the generated summary of the document.
        
    Raises:
        HTTPException: If the file type is unsupported or if an error occurs during processing
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
            # Use a secure temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file_path = temp_file.name
                temp_file.write(contents)
            
            try:
                text = extract_text_from_file(temp_file_path, file_type="pdf")
            finally:
                # Ensure the temporary file is removed
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    logger.debug(f"Temporary file removed: {temp_file_path}")
        else:
            # Reset file position for docx processing
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
        
        # First, store newsletter information
        logger.debug("Storing newsletter information in database")
        newsletter_id = await database.execute(
            newsletters.insert().values(
                filename=file.filename,
                uploader="api_user",  # You might want to get this from auth
                delivered=False
            )
        )

        # Then store summary in database
        logger.debug("Storing summary in database")
        summary_id = await database.execute(
            summaries.insert().values(
                newsletter_id=newsletter_id,
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
    except Exception as e:
        logger.error(f"LLM error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    return JSONResponse(content={"summary": summary})