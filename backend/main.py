import logging
import tempfile
import os
import io
import json
import asyncio
import html
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request, Query
from fastapi.responses import JSONResponse, HTMLResponse, Response, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
from contextlib import asynccontextmanager

from helpers.key_utils import verify_api_key
from helpers.text_utils import (
    extract_text_from_file,
    generate_pdf_thumbnail,
    sanitize_filename,
    compress_pdf,
)
from helpers.storage import upload_to_drive, download_from_drive
from helpers.validation import validate_newsletter_date
from helpers.agent_bridge import notify_agent
from sqlalchemy import and_, select

from llm.providers import choose_llm_and_summarize

from db.setup import database
from db.models import summaries, model_usage, newsletters, subscribers, upload_logs

from config import get_settings

# Get settings from centralized configuration
settings = get_settings()

# Create a logger for this module
logger = logging.getLogger(__name__)


def sync_extract_text(contents: bytes, content_type: str) -> str:
    """
    Synchronously extracts text from the document bytes.
    This function should be run in a threadpool to prevent blocking the async event loop.
    """
    if content_type == "application/pdf":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(contents)

        try:
            return extract_text_from_file(temp_file_path, file_type="pdf")
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    else:
        return extract_text_from_file(io.BytesIO(contents), file_type="docx")


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
    lifespan=lifespan,
)

# Configure CORS with strict security controls:
# 1. Explicit production and local development origins
# 2. Dynamic regex matching for Vercel preview deployments (*.vercel.app)
cors_origins_list = [
    "https://newsletter-herald.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if settings.cors_origins:
    if isinstance(settings.cors_origins, list):
        cors_origins_list.extend(settings.cors_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list,
    allow_origin_regex=r"https://[a-zA-Z0-9-]+\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> Dict[str, str]:
    """
    A simple endpoint to confirm the API is running.
    """
    logger.debug("Root endpoint accessed")
    return {"message": f"Welcome to your {settings.app_name}"}


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint that verifies database connectivity.
    """
    try:
        # Run a simple query to verify database is connected
        await database.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "app_name": settings.app_name,
        }
    except Exception as e:
        logger.error(f"Health check failed - Database unreachable: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed")


@app.post("/upload-document")
async def upload_summary(
    request: Request, file: UploadFile = File(...), _: None = Depends(verify_api_key)
) -> JSONResponse:
    """
    Handles the uploading and summarization of document files.
    """
    uploader = request.headers.get("x-user-email", "api_user")
    filename = file.filename

    # Validate file type
    accepted_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]
    if file.content_type not in accepted_types:
        logger.warning(f"Unsupported file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="Unsupported file type")

    try:
        # Read file contents
        contents = await file.read()

        # Extract text from file
        try:
            if file.content_type == "application/pdf":
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".pdf"
                ) as temp_file:
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
            raise HTTPException(
                status_code=500, detail=f"Error extracting text: {str(e)}"
            )

        # Generate summary
        try:
            logger.info("Generating summary using LLM")
            summary = await run_in_threadpool(choose_llm_and_summarize, text)

            # Sanitize and standardize filename
            standard_filename = sanitize_filename(file.filename)
            logger.info(f"Standardized filename: {standard_filename}")

            # Compress file if it's a PDF
            final_contents = contents
            if file.content_type == "application/pdf":
                logger.info("Compressing PDF...")
                final_contents = compress_pdf(contents)

            # Upload to Google Drive / R2
            logger.info("Uploading file to Google Drive")
            drive_file_id, web_view_link = upload_to_drive(
                final_contents, standard_filename, file.content_type
            )

            # Generate and upload thumbnail if it's a PDF
            thumbnail_drive_id = None
            if file.content_type == "application/pdf":
                try:
                    logger.info("Generating PDF thumbnail")
                    thumbnail_data = generate_pdf_thumbnail(io.BytesIO(final_contents))
                    thumbnail_filename = f"thumb_{standard_filename}.png"
                    thumbnail_drive_id, _ = upload_to_drive(
                        thumbnail_data, thumbnail_filename, "image/png"
                    )
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
            is_valid, target_sunday, error_msg = validate_newsletter_date(
                summary.get("schedule_date")
            )
            if isinstance(target_sunday, str):
                try:
                    target_sunday = datetime.strptime(target_sunday, "%Y-%m-%d").date()
                except Exception:
                    pass
            status = "draft" if is_valid else "failed_validation"
            logger.info(
                f"Date validation: is_valid={is_valid}, target_sunday={target_sunday}, status={status}"
            )

            # Supersede older files for the same Sunday issue
            logger.info(
                f"Marking existing drafts/scheduled newsletters for Sunday {target_sunday} as superseded"
            )
            update_query = (
                newsletters.update()
                .where(
                    and_(
                        newsletters.c.target_sunday == target_sunday,
                        newsletters.c.status.in_(
                            ["draft", "scheduled", "failed_validation"]
                        ),
                    )
                )
                .values(status="superseded")
            )
            await database.execute(update_query)

            schedule_date_str = summary.get("schedule_date")
            schedule_date_val = None
            if isinstance(schedule_date_str, str):
                try:
                    schedule_date_val = datetime.strptime(
                        schedule_date_str, "%Y-%m-%d"
                    ).date()
                except Exception:
                    schedule_date_val = None

            # First, store newsletter information
            logger.debug("Storing newsletter information in database")
            newsletter_id = await database.execute(
                newsletters.insert().values(
                    filename=standard_filename,
                    drive_file_id=drive_file_id,
                    drive_web_view_link=web_view_link,
                    thumbnail_drive_id=thumbnail_drive_id,
                    uploader=uploader,
                    schedule_date=schedule_date_val,
                    tags=tags_str,
                    delivered=False,
                    status=status,
                    target_sunday=target_sunday,
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

            logger.info(
                f"Summary generated and stored successfully (Newsletter ID: {newsletter_id}, Summary ID: {summary_id})"
            )

            # Add drive info to response
            summary["newsletter_id"] = newsletter_id
            summary["thumbnail_drive_id"] = thumbnail_drive_id
            summary["drive_file_id"] = drive_file_id
            summary["drive_web_view_link"] = web_view_link
            summary["status"] = status
            summary["target_sunday"] = target_sunday.isoformat()

            # Handle Eval/Demo Mode (Immediate Preview Dispatch)
            demo_mode_header = request.headers.get("x-demo-mode", "false").lower() == "true"
            demo_mode_param = request.query_params.get("demo_mode", "false").lower() == "true"
            is_demo_mode = demo_mode_header or demo_mode_param

            demo_sent = False
            demo_recipient = None

            if is_demo_mode:
                logger.info("Demo/Eval Mode active: Dispatching immediate preview email...")
                if "@" in uploader:
                    demo_recipient = uploader
                elif settings.gmail_user:
                    demo_recipient = settings.gmail_user
                elif settings.from_email:
                    demo_recipient = settings.from_email
                else:
                    demo_recipient = "admin@newsletterherald.com"

                demo_subject = f"[DEMO/PREVIEW] {summary['title']}"
                summary_formatted = summary['summary'].replace('\n', '<br>')
                demo_html = f"""
                <html>
                <body style='font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #333;'>
                    <div style='max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;'>
                        <div style='background-color: #fff3cd; color: #856404; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px; font-weight: bold; text-align: center; font-size: 14px;'>
                            🧪 DEMO / PREVIEW MODE — Immediate Submission Simulation
                        </div>
                        <h2 style='color: #0071e3;'>{summary['title']}</h2>
                        <div style='font-size: 16px;'>
                            {summary_formatted}
                        </div>
                        <hr style='border: 0; border-top: 1px solid #eee; margin: 30px 0;'>
                        <p style='font-size: 12px; color: #86868b;'>This is an immediate demo simulation of the scheduled Sunday email dispatch. Target Sunday: {target_sunday}</p>
                    </div>
                </body>
                </html>
                """

                try:
                    from helpers.email import send_newsletter_email
                    demo_sent = send_newsletter_email(
                        to_email=demo_recipient,
                        subject=demo_subject,
                        html_content=demo_html
                    )
                    logger.info(f"Demo preview email sent to {demo_recipient}: status={demo_sent}")

                    await database.execute(
                        delivery_logs.insert().values(
                            newsletter_id=newsletter_id,
                            recipient=demo_recipient,
                            status="demo_sent" if demo_sent else "demo_failed",
                            error_message=None if demo_sent else "Demo SMTP delivery failure",
                        )
                    )
                except Exception as demo_err:
                    logger.error(f"Failed to send demo preview email: {demo_err}")

            summary["demo_mode"] = is_demo_mode
            summary["demo_sent"] = demo_sent
            summary["demo_recipient"] = demo_recipient

            # Notify local agent of the review request or validation failure
            if is_valid:
                await notify_agent(
                    "review_request",
                    {
                        "newsletter_id": newsletter_id,
                        "title": summary["title"],
                        "summary": summary["summary"],
                        "target_sunday": target_sunday,
                        "status": status,
                    },
                )
            else:
                await notify_agent(
                    "validation_alert",
                    {
                        "newsletter_id": newsletter_id,
                        "filename": standard_filename,
                        "target_sunday": target_sunday,
                        "status": status,
                        "error_message": error_msg,
                    },
                )
        except Exception as e:
            logger.error(f"LLM error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

        # Log success
        await database.execute(
            upload_logs.insert().values(
                filename=filename, uploader=uploader, status="success"
            )
        )

        return JSONResponse(
            content={
                "summary": summary,
                "validation": {
                    "is_valid": is_valid,
                    "target_sunday": target_sunday.isoformat(),
                    "error_message": error_msg,
                },
                "detail": "Newsletter uploaded and summary generated successfully.",
            }
        )

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Upload process failed: {error_msg}")

        # Log failure in database
        try:
            await database.execute(
                upload_logs.insert().values(
                    filename=filename,
                    uploader=uploader,
                    status="failed",
                    error_message=error_msg,
                )
            )
        except Exception as db_err:
            logger.error(f"Failed to write upload failure log to DB: {db_err}")

        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=error_msg)


@app.patch("/newsletters/{newsletter_id}")
async def update_newsletter(
    newsletter_id: int, data: Dict[str, Any], _: None = Depends(verify_api_key)
) -> JSONResponse:
    """
    Updates the metadata of a newsletter (e.g., schedule_date, target_sunday, tags, title, summary).
    """
    logger.info(f"Updating newsletter {newsletter_id} with data: {data}")
    try:
        # Filter allowed fields for newsletters table
        allowed_fields = ["schedule_date", "target_sunday", "tags", "delivered", "status", "scheduled_at"]
        update_data = {k: v for k, v in data.items() if k in allowed_fields}

        # Parse dates if they are passed as strings
        if "schedule_date" in update_data and isinstance(
            update_data["schedule_date"], str
        ):
            try:
                update_data["schedule_date"] = datetime.strptime(
                    update_data["schedule_date"].split("T")[0], "%Y-%m-%d"
                ).date()
            except ValueError:
                pass
        if "target_sunday" in update_data and isinstance(
            update_data["target_sunday"], str
        ):
            try:
                update_data["target_sunday"] = datetime.strptime(
                    update_data["target_sunday"].split("T")[0], "%Y-%m-%d"
                ).date()
            except ValueError:
                pass
        if "scheduled_at" in update_data and isinstance(update_data["scheduled_at"], str):
            val = update_data["scheduled_at"]
            if val.endswith('Z'):
                val = val[:-1] + '+00:00'
            try:
                update_data["scheduled_at"] = datetime.fromisoformat(val)
            except ValueError:
                # Fallback to alternate formats
                parsed = False
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                    try:
                        update_data["scheduled_at"] = datetime.strptime(val, fmt)
                        parsed = True
                        break
                    except ValueError:
                        pass
                if not parsed:
                    # If we cannot parse it, remove it or set it to None to avoid database error
                    update_data.pop("scheduled_at", None)

        if update_data:
            query = (
                newsletters.update()
                .where(newsletters.c.id == newsletter_id)
                .values(**update_data)
            )
            await database.execute(query)

        # Filter and update summary fields
        summary_fields = ["title", "summary"]
        summary_data = {k: v for k, v in data.items() if k in summary_fields}
        if summary_data:
            query = (
                summaries.update()
                .where(summaries.c.newsletter_id == newsletter_id)
                .values(**summary_data)
            )
            await database.execute(query)

        return JSONResponse(content={"message": "Newsletter updated successfully"})
    except Exception as e:
        logger.error(f"Error updating newsletter: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating newsletter: {e}")


THUMBNAIL_BYTES_CACHE: Dict[str, bytes] = {}


@app.get("/newsletters/{newsletter_id}/thumbnail")
async def get_newsletter_thumbnail(newsletter_id: int):
    """
    Serves the newsletter thumbnail directly by downloading it from R2 or Google Drive,
    cached in memory and with HTTP Cache-Control headers for browser caching.
    """
    try:
        # Fetch the thumbnail key/id from the database
        query = select(newsletters.c.thumbnail_drive_id).where(
            newsletters.c.id == newsletter_id
        )
        row = await database.fetch_one(query)
        if not row or not row["thumbnail_drive_id"]:
            raise HTTPException(status_code=404, detail="Thumbnail not found")

        thumbnail_id = row["thumbnail_drive_id"]

        # Check in-memory cache first
        if thumbnail_id in THUMBNAIL_BYTES_CACHE:
            content = THUMBNAIL_BYTES_CACHE[thumbnail_id]
        else:
            # Download file bytes and store in memory cache
            content = download_from_drive(thumbnail_id)
            if not content:
                raise HTTPException(
                    status_code=404, detail="Failed to retrieve thumbnail data"
                )
            THUMBNAIL_BYTES_CACHE[thumbnail_id] = content

        headers = {
            "Cache-Control": "public, max-age=2592000, immutable",
        }
        return Response(content=content, media_type="image/png", headers=headers)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching thumbnail: {e}")
        raise HTTPException(status_code=500, detail="Error fetching thumbnail")


@app.get("/newsletters/{newsletter_id}/download")
async def download_newsletter_file(newsletter_id: int):
    """
    Downloads the original newsletter PDF file by proxying it from R2 or Google Drive.
    """
    try:
        # Fetch the file name and drive_file_id from the database
        query = select(newsletters.c.filename, newsletters.c.drive_file_id).where(
            newsletters.c.id == newsletter_id
        )
        row = await database.fetch_one(query)
        if not row or not row["drive_file_id"]:
            raise HTTPException(status_code=404, detail="Newsletter file not found")

        file_id = row["drive_file_id"]
        filename = row["filename"] or f"newsletter_{newsletter_id}.pdf"

        # Download file bytes
        content = download_from_drive(file_id)
        if not content:
            raise HTTPException(status_code=404, detail="Failed to retrieve file data")

        # On-the-fly rename from SALLTO-Newsletter to Trinity-Newsletter for downloads
        download_filename = filename
        if "-SALLTO-Newsletter" in filename:
            download_filename = filename.replace(
                "-SALLTO-Newsletter", "-Trinity-Newsletter"
            )

        headers = {"Content-Disposition": f'attachment; filename="{download_filename}"'}
        return Response(content=content, media_type="application/pdf", headers=headers)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading newsletter: {e}")
        raise HTTPException(status_code=500, detail="Error downloading newsletter")


@app.get("/newsletters")
async def get_newsletters(
    limit: Optional[int] = Query(None, ge=1),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    _: None = Depends(verify_api_key)
) -> JSONResponse:
    """
    Fetches newsletters and their associated summaries from the database,
    supporting pagination (limit & offset) and status filtering.
    """
    logger.info(f"Fetching newsletters (limit={limit}, offset={offset}, status={status})")
    try:
        where_clause = ""
        params = {}
        if status:
            where_clause = "WHERE n.status = :status"
            params["status"] = status

        count_query = f"SELECT COUNT(*) FROM newsletters n {where_clause}"
        total_count = await database.fetch_val(query=count_query, values=params) or 0

        pagination_clause = ""
        if limit is not None:
            pagination_clause = "LIMIT :limit OFFSET :offset"
            params["limit"] = limit
            params["offset"] = offset

        query = f"""
            SELECT 
                n.id, n.filename, n.drive_web_view_link, n.thumbnail_drive_id, n.uploaded_at,
                n.status, n.target_sunday, n.tags, n.scheduled_at,
                s.title, s.summary
            FROM newsletters n
            LEFT JOIN summaries s ON n.id = s.newsletter_id
            {where_clause}
            ORDER BY n.target_sunday DESC, n.uploaded_at DESC
            {pagination_clause}
        """
        rows = await database.fetch_all(query=query, values=params)

        result = []
        for row in rows:
            result.append({
                "id": row["id"],
                "filename": row["filename"],
                "drive_link": row["drive_web_view_link"],
                "thumbnail_id": row["thumbnail_drive_id"],
                "uploaded_at": row["uploaded_at"].isoformat() if row["uploaded_at"] else None,
                "status": row["status"],
                "target_sunday": row["target_sunday"].isoformat() if row["target_sunday"] else None,
                "tags": row["tags"],
                "scheduled_at": row["scheduled_at"].isoformat() if row["scheduled_at"] else None,
                "title": row["title"],
                "summary": row["summary"]
            })

        has_more = (offset + len(result)) < total_count if limit is not None else False

        return JSONResponse(content={
            "newsletters": result,
            "total": total_count,
            "has_more": has_more
        })
    except Exception as e:
        logger.error(f"Error fetching newsletters: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching newsletters: {e}")


@app.get("/newsletters/{newsletter_id}/approve")
async def approve_newsletter_summary(newsletter_id: int, request: Request):
    """
    Approve a newsletter and schedule it for delivery.
    """
    logger.info(f"Approving newsletter {newsletter_id}")
    try:
        # Update status to 'scheduled' and ensure schedule_date is set (defaults to Sunday 8:00 AM)
        query = (
            newsletters.update()
            .where(newsletters.c.id == newsletter_id)
            .values(status="scheduled", delivered=False)
        )
        await database.execute(query)

        # Fetch details to display
        fetch_query = select(newsletters.c.filename, newsletters.c.target_sunday).where(
            newsletters.c.id == newsletter_id
        )
        row = await database.fetch_one(fetch_query)

        filename = row["filename"] if row else "Unknown File"
        target_sunday = row["target_sunday"] if row else "Unknown Date"

        # Check if caller wants JSON
        accept_header = request.headers.get("accept", "")
        if (
            "application/json" in accept_header
            or request.query_params.get("format") == "json"
        ):
            return JSONResponse(
                content={
                    "message": "Approved successfully",
                    "newsletter_id": newsletter_id,
                    "filename": filename,
                    "target_sunday": str(target_sunday),
                }
            )

        # Determine redirect URL from settings (CORS origins)
        redirect_url = (
            settings.cors_origins[0]
            if settings.cors_origins
            else "http://localhost:3000"
        )

        safe_filename = html.escape(filename)
        safe_target_sunday = html.escape(str(target_sunday))
        safe_redirect_url = html.escape(redirect_url, quote=True)

        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Summary Approved</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f5f5f7; color: #1d1d1f; }}
                .card {{ background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center; max-width: 450px; }}
                h1 {{ color: #0071e3; font-size: 24px; margin-bottom: 16px; }}
                p {{ font-size: 16px; line-height: 1.5; color: #86868b; margin-bottom: 24px; }}
                .btn {{ background-color: #0071e3; color: white; border: none; padding: 12px 24px; border-radius: 980px; font-size: 14px; font-weight: 600; text-decoration: none; cursor: pointer; display: inline-block; }}
                .btn:hover {{ background-color: #0077ed; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>✓ Approved & Scheduled</h1>
                <p>The newsletter <strong>{safe_filename}</strong> has been approved.<br>It is scheduled for delivery on <strong>Sunday {safe_target_sunday} at 8:00 AM</strong>.</p>
                <a href="{safe_redirect_url}" class="btn">Go to Dashboard</a>
            </div>
        </body>
        </html>
        """)
    except Exception as e:
        logger.error(f"Error approving newsletter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/upload-logs")
async def get_upload_logs(_: None = Depends(verify_api_key)) -> JSONResponse:
    """
    Retrieves all manual/batch upload attempts and their outcomes.
    """
    logger.info("Fetching upload logs")
    try:
        query = select(upload_logs).order_by(upload_logs.c.created_at.desc())
        results = await database.fetch_all(query)
        logs_list = []
        for r in results:
            logs_list.append(
                {
                    "id": r["id"],
                    "filename": r["filename"],
                    "uploader": r["uploader"],
                    "status": r["status"],
                    "error_message": r["error_message"],
                    "created_at": (
                        r["created_at"].isoformat() if r["created_at"] else None
                    ),
                }
            )
        return JSONResponse(content={"upload_logs": logs_list})
    except Exception as e:
        logger.error(f"Error fetching upload logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/newsletters/{newsletter_id}/regenerate")
async def regenerate_newsletter_summary(newsletter_id: int, request: Request):
    """
    Regenerate a newsletter's AI summary from its stored file.
    """
    logger.info(f"Regenerating summary for newsletter {newsletter_id}")
    try:
        # 1. Fetch newsletter details
        query = select(newsletters).where(newsletters.c.id == newsletter_id)
        newsletter = await database.fetch_one(query)
        if not newsletter:
            raise HTTPException(status_code=404, detail="Newsletter not found")

        # 2. Download original file
        file_id = newsletter["drive_file_id"]
        filename = newsletter["filename"]
        content = download_from_drive(file_id)
        if not content:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve newsletter file from storage",
            )

        # 3. Extract text
        file_type = "pdf" if filename.lower().endswith(".pdf") else "docx"
        text = extract_text_from_file(io.BytesIO(content), file_type=file_type)

        # 4. Summarize again
        summary_data = await run_in_threadpool(choose_llm_and_summarize, text)

        # 5. Update summaries database
        update_query = (
            summaries.update()
            .where(summaries.c.newsletter_id == newsletter_id)
            .values(title=summary_data["title"], summary=summary_data["summary"])
        )
        await database.execute(update_query)

        # 6. Notify agent of the regenerated review request
        await notify_agent(
            "review_request",
            {
                "newsletter_id": newsletter_id,
                "title": summary_data["title"],
                "summary": summary_data["summary"],
                "target_sunday": newsletter["target_sunday"],
                "status": newsletter["status"],
            },
        )

        # Check if caller wants JSON
        accept_header = request.headers.get("accept", "")
        if (
            "application/json" in accept_header
            or request.query_params.get("format") == "json"
        ):
            return JSONResponse(
                content={
                    "message": "Summary regenerated successfully",
                    "newsletter_id": newsletter_id,
                    "title": summary_data["title"],
                    "summary": summary_data["summary"],
                }
            )

        # Determine redirect URL from settings (CORS origins)
        redirect_url = (
            settings.cors_origins[0]
            if settings.cors_origins
            else "http://localhost:3000"
        )

        safe_filename = html.escape(filename)
        safe_redirect_url = html.escape(redirect_url, quote=True)

        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Summary Regenerated</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f5f5f7; color: #1d1d1f; }}
                .card {{ background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center; max-width: 450px; }}
                h1 {{ color: #0071e3; font-size: 24px; margin-bottom: 16px; }}
                p {{ font-size: 16px; line-height: 1.5; color: #86868b; margin-bottom: 24px; }}
                .btn {{ background-color: #0071e3; color: white; border: none; padding: 12px 24px; border-radius: 980px; font-size: 14px; font-weight: 600; text-decoration: none; cursor: pointer; display: inline-block; }}
                .btn:hover {{ background-color: #0077ed; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>🔄 Regenerated Successfully</h1>
                <p>A new AI summary has been generated for <strong>{safe_filename}</strong>.<br>The review notification has been sent to your WhatsApp/Signal channels.</p>
                <a href="{safe_redirect_url}" class="btn">Go to Dashboard</a>
            </div>
        </body>
        </html>
        """)
    except Exception as e:
        logger.error(f"Error regenerating newsletter summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class SubscriberRequest(BaseModel):
    email: str
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None


class BatchSubscribersRequest(BaseModel):
    emails: list[str]


class UpdateSubscriberRequest(BaseModel):
    is_active: bool


@app.get("/subscribers")
async def get_all_subscribers():
    """
    Retrieves all subscribers and list statistics.
    """
    try:
        query = select(subscribers).order_by(subscribers.c.created_at.desc())
        rows = await database.fetch_all(query)

        result = []
        active_count = 0
        inactive_count = 0

        for r in rows:
            is_act = r["is_active"]
            if is_act:
                active_count += 1
            else:
                inactive_count += 1

            result.append(
                {
                    "id": r["id"],
                    "email": r["email"],
                    "first_name": r["first_name"],
                    "last_name": r["last_name"],
                    "phone": r["phone"],
                    "is_active": is_act,
                    "created_at": (
                        r["created_at"].isoformat() if r["created_at"] else None
                    ),
                }
            )

        return JSONResponse(
            content={
                "subscribers": result,
                "stats": {
                    "total": len(result),
                    "active": active_count,
                    "inactive": inactive_count,
                },
            }
        )
    except Exception as e:
        logger.error(f"Error fetching subscribers: {e}")
        raise HTTPException(status_code=500, detail="Error fetching subscribers")


@app.post("/subscribers")
async def subscribe_user(data: SubscriberRequest):
    """
    Subscribes a parishioner to the mailing list.
    """
    email = data.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email address")

    try:
        # Check if already exists
        query = select(subscribers).where(subscribers.c.email == email)
        existing = await database.fetch_one(query)

        if existing:
            if existing["is_active"]:
                return JSONResponse(
                    content={"message": "You are already subscribed!"}, status_code=200
                )
            else:
                # Reactivate subscription
                update_query = (
                    subscribers.update()
                    .where(subscribers.c.email == email)
                    .values(
                        is_active=True,
                        first_name=data.first_name or existing["first_name"],
                        last_name=data.last_name or existing["last_name"],
                        phone=data.phone or existing["phone"],
                    )
                )
                await database.execute(update_query)
                return JSONResponse(
                    content={"message": "Subscription reactivated successfully!"},
                    status_code=200,
                )

        # Create new subscriber
        insert_query = subscribers.insert().values(
            email=email,
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            is_active=True,
        )
        await database.execute(insert_query)
        return JSONResponse(
            content={"message": "Successfully subscribed to the parish newsletter!"},
            status_code=201,
        )
    except Exception as e:
        logger.error(f"Error subscribing email: {e}")
        raise HTTPException(status_code=500, detail="Error subscribing email")


@app.post("/subscribers/batch")
async def batch_subscribe_users(data: BatchSubscribersRequest):
    """
    Imports a list of subscriber emails in batch (e.g. from Gmail export or CSV).
    """
    if not data.emails:
        raise HTTPException(status_code=400, detail="No email addresses provided")

    added_count = 0
    skipped_count = 0
    reactivated_count = 0

    # 1. Clean and filter incoming emails
    cleaned_emails = []
    seen_in_batch = set()
    for raw_email in data.emails:
        email = raw_email.strip().lower()
        if not email or "@" not in email:
            skipped_count += 1
            continue
        if email in seen_in_batch:
            skipped_count += 1
            continue
        seen_in_batch.add(email)
        cleaned_emails.append(email)

    if not cleaned_emails:
        return JSONResponse(
            content={
                "message": f"Import completed: {added_count} added, {reactivated_count} reactivated, {skipped_count} skipped/duplicates.",
                "added": added_count,
                "reactivated": reactivated_count,
                "skipped": skipped_count,
            },
            status_code=200,
        )

    try:
        # 2. Fetch existing subscribers in a single query
        query = select(subscribers).where(subscribers.c.email.in_(cleaned_emails))
        existing_rows = await database.fetch_all(query)

        # Build lookup of existing subscribers: email -> is_active
        existing_map = {row["email"]: row["is_active"] for row in existing_rows}

        emails_to_insert = []
        emails_to_reactivate = []

        for email in cleaned_emails:
            if email in existing_map:
                is_active = existing_map[email]
                if not is_active:
                    emails_to_reactivate.append(email)
                else:
                    skipped_count += 1
            else:
                emails_to_insert.append(email)

        # 3. Perform bulk operations
        if emails_to_reactivate:
            update_query = "UPDATE subscribers SET is_active = true WHERE email = :email"
            update_values = [{"email": email} for email in emails_to_reactivate]
            await database.execute_many(update_query, update_values)
            reactivated_count = len(emails_to_reactivate)

        if emails_to_insert:
            insert_query = "INSERT INTO subscribers (email, is_active) VALUES (:email, true)"
            insert_values = [{"email": email} for email in emails_to_insert]
            await database.execute_many(insert_query, insert_values)
            added_count = len(emails_to_insert)

    except Exception as e:
        logger.error(f"Error importing batch emails: {e}")
        raise HTTPException(status_code=500, detail="Error during batch subscriber import")

    return JSONResponse(
        content={
            "message": f"Import completed: {added_count} added, {reactivated_count} reactivated, {skipped_count} skipped/duplicates.",
            "added": added_count,
            "reactivated": reactivated_count,
            "skipped": skipped_count,
        },
        status_code=200,
    )


@app.patch("/subscribers/{subscriber_id}")
async def update_subscriber(subscriber_id: int, data: UpdateSubscriberRequest):
    """
    Updates a subscriber's active status.
    """
    try:
        query = select(subscribers).where(subscribers.c.id == subscriber_id)
        existing = await database.fetch_one(query)
        if not existing:
            raise HTTPException(status_code=404, detail="Subscriber not found")

        update_query = (
            subscribers.update()
            .where(subscribers.c.id == subscriber_id)
            .values(is_active=data.is_active)
        )
        await database.execute(update_query)
        return JSONResponse(
            content={"message": "Subscriber status updated successfully"}
        )
    except Exception as e:
        logger.error(f"Error updating subscriber {subscriber_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating subscriber")


@app.delete("/subscribers/{subscriber_id}")
async def delete_subscriber(subscriber_id: int):
    """
    Deletes a subscriber from the mailing list.
    """
    try:
        query = select(subscribers).where(subscribers.c.id == subscriber_id)
        existing = await database.fetch_one(query)
        if not existing:
            raise HTTPException(status_code=404, detail="Subscriber not found")

        delete_query = subscribers.delete().where(subscribers.c.id == subscriber_id)
        await database.execute(delete_query)
        return JSONResponse(content={"message": "Subscriber removed successfully"})
    except Exception as e:
        logger.error(f"Error deleting subscriber {subscriber_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting subscriber")


@app.post("/subscribers/unsubscribe")
async def unsubscribe_user(data: SubscriberRequest):
    """
    Unsubscribes a user from the mailing list.
    """
    email = data.email.strip().lower()
    try:
        query = select(subscribers).where(subscribers.c.email == email)
        existing = await database.fetch_one(query)

        if not existing or not existing["is_active"]:
            return JSONResponse(
                content={"message": "Email is not subscribed."}, status_code=200
            )

        update_query = (
            subscribers.update()
            .where(subscribers.c.email == email)
            .values(is_active=False)
        )
        await database.execute(update_query)
        return JSONResponse(
            content={"message": "You have been successfully unsubscribed."}
        )
    except Exception as e:
        logger.error(f"Error unsubscribing email: {e}")
        raise HTTPException(status_code=500, detail="Error unsubscribing email")


@app.get("/notifications/poll")
async def poll_agent_notifications(_: None = Depends(verify_api_key)) -> JSONResponse:
    """
    Polled by the local agent (Hortense) to fetch pending notifications.
    Deletes notifications from the database after returning them.
    """
    from db.models import agent_notifications

    try:
        # 1. Fetch all pending notifications
        query = select(agent_notifications).order_by(
            agent_notifications.c.created_at.asc()
        )
        rows = await database.fetch_all(query)

        result = []
        for row in sorted_rows:
            result.append(json.loads(row["payload"]))

        # 2. Delete the fetched notifications
        if rows:
            ids = [row["id"] for row in rows]
            delete_query = agent_notifications.delete().where(
                agent_notifications.c.id.in_(ids)
            )
            await database.execute(delete_query)

        return JSONResponse(content={"notifications": result})
    except Exception as e:
        logger.error(f"Error polling agent notifications: {e}")
        raise HTTPException(status_code=500, detail="Error fetching notifications")


@app.post("/deliver")
async def trigger_newsletter_delivery(
    _: None = Depends(verify_api_key),
) -> JSONResponse:
    """
    Triggers the delivery worker process manually (or via cloud cron).
    """
    from scripts.delivery_worker import check_and_deliver

    logger.info("Manual delivery trigger initiated via API")
    try:
        # Run delivery worker check_and_deliver logic asynchronously
        asyncio.create_task(check_and_deliver())
        return JSONResponse(content={"status": "Delivery run initiated in background"})
    except Exception as e:
        logger.error(f"Failed to initiate delivery: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/newsletters/{newsletter_id}/send-now")
async def send_newsletter_now(
    newsletter_id: int, _: None = Depends(verify_api_key)
) -> JSONResponse:
    """
    Immediately sends a specific newsletter to all active subscribers.
    """
    logger.info(f"Initiating immediate send for newsletter {newsletter_id}")
    try:
        query = (
            select(
                newsletters.c.id,
                summaries.c.title,
                summaries.c.summary,
            )
            .select_from(
                newsletters.join(summaries, newsletters.c.id == summaries.c.newsletter_id)
            )
            .where(newsletters.c.id == newsletter_id)
        )

        item = await database.fetch_one(query)
        if not item:
            raise HTTPException(status_code=404, detail="Newsletter not found")

        sub_query = select(subscribers.c.email).where(subscribers.c.is_active == True)
        active_subs = await database.fetch_all(sub_query)
        if not active_subs:
            raise HTTPException(status_code=400, detail="No active subscribers to send to")

        html_content = f"""
        <html>
        <body style='font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #333;'>
            <div style='max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;'>
                <h2 style='color: #0071e3;'>{item['title']}</h2>
                <div style='font-size: 16px;'>
                    {item['summary'].replace('\n', '<br>')}
                </div>
                <hr style='border: 0; border-top: 1px solid #eee; margin: 30px 0;'>
                <p style='font-size: 12px; color: #86868b;'>Sent by Newsletter Herald. To unsubscribe, please visit the parish website.</p>
            </div>
        </body>
        </html>
        """

        from helpers.email import send_newsletter_email

        semaphore = asyncio.Semaphore(10)

        async def deliver_to_subscriber(sub):
            async with semaphore:
                recipient = sub["email"]
                try:
                    success = await asyncio.to_thread(
                        send_newsletter_email,
                        to_email=recipient,
                        subject=item["title"],
                        html_content=html_content,
                    )
                except Exception as err:
                    logger.error(f"Error sending email to {recipient}: {err}")
                    success = False
                return recipient, success

        tasks = [deliver_to_subscriber(sub) for sub in active_subs]
        results = await asyncio.gather(*tasks)

        sent_count = 0
        failed_count = 0
        log_values = []

        for recipient, success in results:
            log_values.append(
                {
                    "newsletter_id": item["id"],
                    "recipient": recipient,
                    "status": "sent" if success else "failed",
                    "error_message": None if success else "SMTP delivery failure",
                }
            )
            if success:
                sent_count += 1
            else:
                failed_count += 1

        if log_values:
            await database.execute_many(
                query=delivery_logs.insert(), values=log_values
            )

        update_query = (
            newsletters.update()
            .where(newsletters.c.id == item["id"])
            .values(delivered=True, status="delivered")
        )
        await database.execute(update_query)

        return JSONResponse(
            content={
                "message": f"Newsletter delivered to {sent_count} subscribers successfully ({failed_count} failed).",
                "sent_count": sent_count,
                "failed_count": failed_count,
                "status": "delivered",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send_newsletter_now: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/newsletters/{newsletter_id}/archive")
async def archive_newsletter(
    newsletter_id: int, _: None = Depends(verify_api_key)
) -> JSONResponse:
    """
    Archives a newsletter so it is no longer pending or active.
    """
    logger.info(f"Archiving newsletter {newsletter_id}")
    try:
        query = (
            newsletters.update()
            .where(newsletters.c.id == newsletter_id)
            .values(status="archived")
        )
        await database.execute(query)
        return JSONResponse(
            content={"message": "Newsletter archived successfully", "status": "archived"}
        )
    except Exception as e:
        logger.error(f"Error archiving newsletter {newsletter_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
