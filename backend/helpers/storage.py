import json
import logging
import io
import boto3
from botocore.config import Config
from typing import Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Scopes required for Google Drive API (Fallback only)
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_r2_client():
    """
    Initializes and returns a boto3 client for Cloudflare R2 (S3-compatible).
    """
    if not all([settings.r2_endpoint_url, settings.r2_access_key_id, settings.r2_secret_access_key]):
        logger.warning("Cloudflare R2 settings not fully configured.")
        return None

    try:
        return boto3.client(
            service_name='s3',
            endpoint_url=settings.r2_endpoint_url,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            config=Config(signature_version='s3v4'),
            region_name='auto'  # R2 expects 'auto'
        )
    except Exception as e:
        logger.error(f"Failed to initialize R2 client: {e}")
        return None

def get_drive_service():
    """
    Initializes and returns a Google Drive service object (Fallback).
    """
    if not settings.google_service_account_json:
        return None

    try:
        service_account_info = json.loads(settings.google_service_account_json)
        creds = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=SCOPES
        )
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        logger.error(f"Failed to initialize Google Drive service: {e}")
        return None

def upload_to_drive_fallback(file_content: bytes, filename: str, mime_type: str) -> tuple[Optional[str], Optional[str]]:
    """
    Google Drive fallback for upload_to_drive.
    """
    service = get_drive_service()
    if not service: return None, None
    try:
        file_metadata = {'name': filename}
        if settings.google_drive_folder_id:
            file_metadata['parents'] = [settings.google_drive_folder_id]
        media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype=mime_type, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink', supportsAllDrives=True).execute()
        file_id = file.get('id')
        web_link = file.get('webViewLink')
        service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'reader'}, supportsAllDrives=True).execute()
        return file_id, web_link
    except Exception as e:
        logger.error(f"Google Drive fallback failed: {e}")
        return None, None

def make_file_public(file_id: str):
    """
    Sets file permissions to 'anyone with the link can view' (Google Drive) 
    or logs a reminder for R2.
    """
    # 1. If it's a Google Drive ID (likely longer or specific format)
    service = get_drive_service()
    if service:
        try:
            service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'},
                fields='id',
                supportsAllDrives=True
            ).execute()
            logger.info(f"Drive file {file_id} set to public view.")
            return
        except Exception:
            pass # Might be an R2 key instead
    
    # 2. For R2, public access is managed via Bucket Settings/Public Domain.
    logger.debug(f"Public access for {file_id} (R2) is managed at the bucket level.")

def upload_to_drive(file_content: bytes, filename: str, mime_type: str) -> tuple[Optional[str], Optional[str]]:
    """
    Uploads a file to Cloudflare R2 (Primary) or Google Drive (Fallback).
    Returns (file_id_or_key, web_view_link).
    """
    # 1. Try Cloudflare R2 (Primary)
    r2 = get_r2_client()
    if r2 and settings.r2_bucket_name:
        try:
            r2.put_object(
                Bucket=settings.r2_bucket_name,
                Key=filename,
                Body=file_content,
                ContentType=mime_type
            )
            
            # Construct public URL if domain is provided, else return key as ID
            public_url = None
            if settings.r2_public_domain:
                public_url = f"https://{settings.r2_public_domain}/{filename}"
            
            logger.info(f"File {filename} uploaded to Cloudflare R2.")
            return filename, public_url
        except Exception as e:
            logger.error(f"Error uploading to R2: {e}")

    # 2. Fallback to Google Drive
    logger.info("R2 failed or not configured. Falling back to Google Drive.")
    return upload_to_drive_fallback(file_content, filename, mime_type)

def download_from_drive(file_id: str) -> Optional[bytes]:
    """
    Downloads a file's content from Cloudflare R2 or Google Drive.
    """
    # 1. Try R2 (file_id here is the object Key)
    r2 = get_r2_client()
    if r2 and settings.r2_bucket_name:
        try:
            response = r2.get_object(Bucket=settings.r2_bucket_name, Key=file_id)
            return response['Body'].read()
        except Exception:
            # If not in R2, it might be an old Google Drive ID
            pass

    # 2. Try Google Drive (Legacy support)
    service = get_drive_service()
    if service:
        try:
            from googleapiclient.http import MediaIoBaseDownload
            request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            return fh.getvalue()
        except Exception as e:
            logger.error(f"Download failed for {file_id}: {e}")
    
    return None

def list_files_in_folder(folder_id: str):
    """
    Lists files in a specific Google Drive folder (Legacy/Fallback).
    """
    service = get_drive_service()
    if not service: return []
    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields="files(id, name, mimeType)",
            pageSize=100,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        return results.get('files', [])
    except Exception as e:
        logger.error(f"Error listing Drive files: {e}")
        return []
