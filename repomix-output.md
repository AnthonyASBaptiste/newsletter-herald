This file is a merged representation of a subset of the codebase, containing files not matching ignore patterns, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching these patterns are excluded: repomix-output.md
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
````
.agents/
  rules/
    graphify.md
  workflows/
    graphify.md
backend/
  db/
    __init__.py
    models.py
    setup.py
  helpers/
    __init__.py
    agent_bridge.py
    auth.py
    constants.py
    email.py
    key_utils.py
    storage.py
    text_utils.py
    validation.py
  llm/
    providers.py
  scripts/
    benchmark_delivery.py
    benchmark_drive_files.py
    benchmark_extraction.py
    benchmark_import.py
    benchmark_subscribers.py
    benchmark_upload.py
    check_db_count.py
    clear_db.py
    create_tables.py
    delivery_worker.py
    generate_google_token.py
    import_gmail_contacts.py
    poll_notifications.py
    process_existing_drive_files.py
    setup_cron.sh
    setup_scheduler.ps1
    test_agent_bridge.py
    test_delivery_flow.py
    test_email.py
    test_pii_filtering.py
    test_validation.py
    upload_local_files.py
  tests/
    test_config.py
    test_email_masking.py
    test_extraction.py
    test_import.py
    test_key_utils.py
    test_newsletters_auth.py
    test_sanitize.py
    test_subscribers.py
    test_xss.py
  .env.example
  .gitignore
  .python-version
  benchmark_llm.py
  config.py
  main.py
  pyproject.toml
  README.md
  requirements.txt
docs/
  HERMES_BRIEF.md
frontend/
  app/
    components/
      AuthButtons.tsx
    docs/
      DocsTabs.tsx
      page.tsx
    errors/
      page.tsx
    preview/
      page.tsx
    signup/
      page.tsx
    subscribers/
      page.tsx
    apple-icon.png
    favicon.ico
    globals.css
    HomeContent.tsx
    icon.png
    layout.tsx
    page.tsx
    theme.ts
  docs/
    ADMIN_GUIDE.md
    CHANGELOG.md
  public/
    apple-touch-icon.png
    favicon-96x96.png
    favicon.ico
    file.svg
    globe.svg
    icon-32x32.png
    icon.svg
    next.svg
    site.webmanifest
    vercel.svg
    web-app-manifest-192x192.png
    web-app-manifest-512x512.png
    window.svg
  .env.example
  .gitignore
  eslint.config.mjs
  next.config.ts
  package.json
  postcss.config.mjs
  proxy.ts
  README.md
  tsconfig.json
studio-newsletter-herald/
  schemaTypes/
    delivery.ts
    editorialWorkflow.ts
    index.ts
    newsletterEdition.ts
    theme.ts
  static/
    .gitkeep
  .gitignore
  eslint.config.mjs
  package.json
  README.md
  sanity.cli.ts
  sanity.config.ts
  tsconfig.json
test_newsletters/
  test.pdf
.gitignore
.python-version
CHANGELOG.md
Dockerfile
LICENSE
main.py
package.json
README.md
start_dev.py
````

# Files

## File: backend/db/__init__.py
````python

````

## File: backend/db/setup.py
````python
from sqlalchemy import MetaData
from databases import Database
from config import get_settings

settings = get_settings()

database = Database(settings.database_url)
metadata = MetaData()
````

## File: backend/helpers/__init__.py
````python

````

## File: backend/helpers/agent_bridge.py
````python
import json
import logging
import datetime
from typing import Dict, Any
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

async def notify_agent(event_type: str, data: Dict[str, Any]):
    """
    Asynchronously inserts a new notification event into the database.
    Your local agent Hortense can fetch this via a REST API endpoint.
    """
    event_id = data.get("newsletter_id") or data.get("id") or int(datetime.datetime.now().timestamp())
    
    # Base URLs for callbacks
    # In production, use the production domain if available, fallback to settings
    base_url = f"https://{settings.r2_public_domain}" if settings.r2_public_domain else f"http://localhost:{settings.api_port}"
    
    event = {
        "event_id": event_id,
        "type": event_type,
        "timestamp": datetime.datetime.now().isoformat(),
        "title": data.get("title", "No Title"),
        "summary": data.get("summary", ""),
        "target_sunday": str(data.get("target_sunday", "")),
        "status": data.get("status", ""),
        "error_message": data.get("error_message", ""),
        "actions": {
            "approve_url": f"{base_url}/newsletters/{event_id}/approve",
            "regenerate_url": f"{base_url}/newsletters/{event_id}/regenerate"
        }
    }
    
    # Format a human-readable message for Signal/WhatsApp
    if event_type == "review_request":
        event["formatted_message"] = (
            f"🔔 *New Newsletter Summary for Review*\n\n"
            f"*Target Sunday:* {event['target_sunday']}\n"
            f"*Title:* {event['title']}\n\n"
            f"{event['summary']}\n\n"
            f"👉 *Approve & Schedule (Sun 8:00 AM):* {event['actions']['approve_url']}\n"
            f"🔄 *Regenerate Summary:* {event['actions']['regenerate_url']}"
        )
    elif event_type == "validation_alert":
        event["formatted_message"] = (
            f"⚠️ *Newsletter Validation Failed*\n\n"
            f"*File:* {data.get('filename')}\n"
            f"*Issue:* {event['error_message']}\n"
            f"*Target Sunday:* {event['target_sunday']}\n\n"
            f"Click here to override or review details on the dashboard."
        )
    elif event_type == "delivery_report":
        event["formatted_message"] = (
            f"✅ *Newsletter Delivery Report*\n\n"
            f"*Newsletter:* {event['title']}\n"
            f"*Status:* Dispatched\n"
            f"*Sent:* {data.get('sent_count', 0)}\n"
            f"*Failed/Bounced:* {data.get('failed_count', 0)}"
        )
    elif event_type == "bounce_alert":
        event["formatted_message"] = (
            f"🚨 *Email Bounce Detected*\n\n"
            f"*Recipient:* {data.get('recipient')}\n"
            f"*Reason:* {data.get('error_message')}"
        )
    else:
        event["formatted_message"] = f"Notification Alert: {event_type} - {event['title']}"

    try:
        from db.setup import database
        from db.models import agent_notifications
        
        # Insert event into the database table
        query = agent_notifications.insert().values(
            event_type=event_type,
            payload=json.dumps(event)
        )
        await database.execute(query)
        
        logger.info(f"Agent notification written to DB: {event_type} (ID: {event_id})")
        return True
    except Exception as e:
        logger.error(f"Failed to write agent notification to DB: {e}")
        return False
````

## File: backend/helpers/constants.py
````python
import logging
from config import get_settings

# Get settings from centralized configuration
settings = get_settings()

# Create a logger for this module
logger = logging.getLogger(__name__)

# Constants from settings
ANTHROPIC_API_KEY = settings.anthropic_api_key
MAX_ALLOWED_TOKENS = settings.max_allowed_tokens
DATABASE_URL = settings.database_url

logger.debug("Constants loaded from settings")
````

## File: backend/helpers/validation.py
````python
import datetime
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

def get_target_sunday(from_datetime: datetime.datetime = None) -> datetime.date:
    """
    Calculates the target Sunday date for the newsletter.
    - If today is Friday, Saturday, or Sunday (before 8 AM), returns the current Sunday.
    - If today is Sunday after 8 AM, or Mon-Thu, returns the next Sunday.
    """
    if from_datetime is None:
        from_datetime = datetime.datetime.now()
        
    from_date = from_datetime.date()
    weekday = from_date.weekday() # Monday is 0, Sunday is 6
    
    target = from_date + datetime.timedelta(days=(6 - weekday))
    
    # If today is Sunday and it is past 8:00 AM, target the next Sunday
    if weekday == 6 and from_datetime.hour >= 8:
        target += datetime.timedelta(days=7)
        
    return target

def validate_newsletter_date(extracted_date_str: str) -> Tuple[bool, datetime.date, str]:
    """
    Validates whether the AI-extracted date matches the expected target Sunday.
    
    Returns:
        Tuple[bool, datetime.date, str]: (is_valid, target_sunday, error_message)
    """
    target_sunday = get_target_sunday()
    
    if not extracted_date_str:
        return False, target_sunday, "No schedule date could be extracted by AI from the document."
        
    try:
        # Expected format YYYY-MM-DD
        extracted_date = datetime.datetime.strptime(extracted_date_str, "%Y-%m-%d").date()
    except ValueError:
        return False, target_sunday, f"Extracted date '{extracted_date_str}' is not in YYYY-MM-DD format."
        
    if extracted_date != target_sunday:
        return False, target_sunday, f"Extracted date '{extracted_date}' does not match the expected target Sunday '{target_sunday}'."
        
    return True, target_sunday, ""
````

## File: backend/scripts/check_db_count.py
````python
import asyncio
import sys
import os

# Add backend directory to path
current_script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_script_dir)
sys.path.append(backend_dir)

from db.setup import database

async def check_db():
    print(f"Connecting to: {database.url}")
    await database.connect()
    try:
        count = await database.fetch_val("SELECT count(*) FROM newsletters")
        print(f"Newsletters in DB: {count}")
    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(check_db())
````

## File: backend/scripts/clear_db.py
````python
import asyncio
import os
import sys

# Add backend directory to path
current_script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_script_dir)
sys.path.append(backend_dir)

from db.setup import database
from db.models import newsletters, summaries, model_usage

async def clear_db():
    print(f"Connecting to: {database.url}")
    await database.connect()
    try:
        # Delete in order of dependencies
        await database.execute(model_usage.delete())
        await database.execute(summaries.delete())
        await database.execute(newsletters.delete())
        print("Database cleared successfully.")
    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(clear_db())
````

## File: backend/scripts/create_tables.py
````python
import logging
import sys
import os
from sqlalchemy import create_engine

# Add backend directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.models import metadata
from config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Get settings from centralized configuration
settings = get_settings()

# Create database engine
engine = create_engine(settings.database_url)

# Drop all tables
logger.info("Dropping all tables...")
metadata.drop_all(engine)

# Create tables
logger.info("Creating database tables...")
metadata.create_all(engine)

# Log created tables
logger.info(f"Created tables: {', '.join(metadata.tables.keys())}")
logger.info("✅ Tables created successfully")
````

## File: backend/scripts/generate_google_token.py
````python
"""
Script to generate a Google Drive Refresh Token for personal account use.
Requirements: google-auth-oauthlib

Instructions:
1. Go to https://console.cloud.google.com/
2. Enable "Google Drive API".
3. Configure "OAuth consent screen":
   - User Type: External
   - App Name: Newsletter Herald
   - Scopes: Add 'https://www.googleapis.com/auth/drive'
   - Test Users: Add your own email address.
4. Go to "Credentials":
   - Create Credentials -> OAuth client ID
   - Application Type: Desktop App
   - Name: Herald CLI
5. Copy the Client ID and Client Secret into this script or environment.
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes required for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    client_id = input("Enter your Google Client ID: ").strip()
    client_secret = input("Enter your Google Client Secret: ").strip()

    if not client_id or not client_secret:
        print("Error: Client ID and Client Secret are required.")
        return

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    
    # This will open a browser window for authentication
    creds = flow.run_local_server(port=0)

    print("\n" + "="*50)
    print("SUCCESS! Add these to your backend/.env file:")
    print("="*50)
    print(f"GOOGLE_CLIENT_ID={client_id}")
    print(f"GOOGLE_CLIENT_SECRET={client_secret}")
    print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
    print("="*50)

if __name__ == "__main__":
    main()
````

## File: backend/scripts/poll_notifications.py
````python
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def poll_notifications():
    # Load backend URL and API key from environment variables
    # Defaults to localhost for development
    backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
    api_key = os.getenv("API_KEY")
    
    if not api_key:
        sys.stderr.write("Error: API_KEY environment variable is not set.\n")
        sys.exit(1)
        
    url = f"{backend_url.rstrip('/')}/notifications/poll"
    headers = {
        "X-API-Key": api_key,
        "Authorization": f"Bearer {api_key}" # Provide both formats for compatibility
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 401:
            sys.stderr.write("Error: Unauthorized. Check your API_KEY configuration.\n")
            sys.exit(1)
            
        response.raise_for_status()
        data = response.json()
        
        notifications = data.get("notifications", [])
        if not notifications:
            return
            
        for event in notifications:
            msg = event.get("formatted_message", "")
            if msg:
                sys.stdout.buffer.write((msg + "\n---\n").encode("utf-8"))
                
    except Exception as e:
        sys.stderr.write(f"Error polling notifications from {url}: {e}\n")

if __name__ == "__main__":
    poll_notifications()
````

## File: backend/scripts/setup_cron.sh
````bash
#!/bin/bash
# setup_cron.sh
# Run this script on your Debian 13 server to register the Sunday 8:00 AM delivery cron.

# Get the absolute path of the backend directory
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$BACKEND_DIR/venv/bin/python"
SCRIPT_PATH="$BACKEND_DIR/scripts/delivery_worker.py"
CRON_JOB="0 8 * * 7 cd $BACKEND_DIR && $PYTHON_BIN $SCRIPT_PATH >> $BACKEND_DIR/cron_delivery.log 2>&1"

echo "Configuring Linux Crontab for Weekly Delivery..."

# Check if Python exists in venv
if [ ! -f "$PYTHON_BIN" ]; then
    # Fallback to system python3 if venv doesn't exist yet
    PYTHON_BIN="python3"
    echo "Warning: Virtual environment python not found, falling back to system '$PYTHON_BIN'"
fi

# Check if the delivery script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Delivery worker script not found at $SCRIPT_PATH"
    exit 1
fi

# Add job to crontab if it doesn't already exist
(crontab -l 2>/dev/null | grep -F "$SCRIPT_PATH" >/dev/null)
if [ $? -eq 0 ]; then
    echo "Task is already registered in crontab."
else
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "Successfully registered Sunday 8:00 AM delivery task in crontab!"
    echo "Job details: $CRON_JOB"
fi
````

## File: backend/scripts/setup_scheduler.ps1
````powershell
# setup_scheduler.ps1
# Run this script as Administrator to register the Weekly Delivery Task

$ProjectDir = "C:\Users\CBCGaming\Documents\Projects\newsletter-herald"
$PythonExe = "$ProjectDir\backend\venv\Scripts\python.exe"
$ScriptPath = "$ProjectDir\backend\scripts\delivery_worker.py"
$WorkDir = "$ProjectDir\backend"

Write-Host "Registering Newsletter Herald Weekly Sunday Delivery Task..." -ForegroundColor Cyan

# 1. Verify paths exist
if (-not (Test-Path $PythonExe)) {
    Write-Error "Error: Python executable not found at $PythonExe. Please make sure the venv is built."
    Exit 1
}

if (-not (Test-Path $ScriptPath)) {
    Write-Error "Error: Delivery worker script not found at $ScriptPath."
    Exit 1
}

# 2. Define Scheduled Task parameters
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument $ScriptPath -WorkingDirectory $WorkDir
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 8:00AM
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 3. Register Scheduled Task
try {
    Register-ScheduledTask -TaskName "NewsletterHeraldDelivery" -Action $Action -Trigger $Trigger -Settings $Settings -Description "Runs the weekly Sunday 8:00 AM delivery worker for SALLTO Herald bulletins." -Force
    Write-Host "Successfully registered Weekly Task 'NewsletterHeraldDelivery'!" -ForegroundColor Green
    Write-Host "Task will run every Sunday at 8:00 AM." -ForegroundColor Green
} catch {
    Write-Error "Failed to register task. Make sure you are running PowerShell as Administrator: $_"
}
````

## File: backend/scripts/test_email.py
````python
import sys
import os
import asyncio

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.email import send_newsletter_email
from config import get_settings

def main():
    settings = get_settings()
    
    print("Starting email test script...")
    
    if settings.gmail_user and settings.gmail_app_password:
        print(f"Gmail SMTP Configured (User: {settings.gmail_user})")
        recipient = settings.gmail_user
    elif settings.from_email:
        print(f"SendGrid Configured (From: {settings.from_email})")
        recipient = settings.from_email
    else:
        print("Error: No email configurations found in settings/.env!")
        return
        
    print(f"Sending test email to: {recipient}...")
    
    subject = "Newsletter Herald SMTP Test Connection"
    html_content = """
    <h2>SMTP Test Connection Successful</h2>
    <p>This is a test email sent from the <strong>Newsletter Herald Backend</strong>.</p>
    <p>If you received this email, your SMTP configurations are working perfectly!</p>
    <hr>
    <p><small>Sent by Newsletter Herald Automated Test</small></p>
    """
    
    success = send_newsletter_email(recipient, subject, html_content)
    
    if success:
        print("Email sent successfully!")
    else:
        print("Failed to send email. Please check your credentials and logs.")

if __name__ == "__main__":
    main()
````

## File: backend/scripts/test_validation.py
````python
import sys
import os
import datetime

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.validation import get_target_sunday, validate_newsletter_date

def test_sunday_calculation():
    print("Testing target Sunday calculations...")
    
    # Test cases: (Input Date & Time, Expected Sunday Date)
    test_cases = [
        # Monday
        (datetime.datetime(2026, 5, 18, 12, 0, 0), datetime.date(2026, 5, 24)),
        # Thursday
        (datetime.datetime(2026, 5, 21, 15, 30, 0), datetime.date(2026, 5, 24)),
        # Friday
        (datetime.datetime(2026, 5, 22, 9, 0, 0), datetime.date(2026, 5, 24)),
        # Saturday
        (datetime.datetime(2026, 5, 23, 18, 0, 0), datetime.date(2026, 5, 24)),
        # Sunday morning (before 8 AM)
        (datetime.datetime(2026, 5, 24, 7, 59, 59), datetime.date(2026, 5, 24)),
        # Sunday morning (after 8 AM)
        (datetime.datetime(2026, 5, 24, 8, 0, 0), datetime.date(2026, 5, 31)),
        # Sunday afternoon
        (datetime.datetime(2026, 5, 24, 14, 0, 0), datetime.date(2026, 5, 31)),
    ]
    
    all_passed = True
    for input_dt, expected_date in test_cases:
        actual_date = get_target_sunday(input_dt)
        passed = (actual_date == expected_date)
        status = "PASSED" if passed else "FAILED"
        print(f"Input: {input_dt} | Expected: {expected_date} | Actual: {actual_date} | {status}")
        if not passed:
            all_passed = False
            
    return all_passed

def test_date_validation():
    print("\nTesting extracted date validation...")
    target_sunday = get_target_sunday()
    print(f"Current Target Sunday: {target_sunday}")
    
    # Valid date matching current target
    is_valid, date, err = validate_newsletter_date(target_sunday.isoformat())
    print(f"Valid case: is_valid={is_valid}, date={date}, err='{err}' (Expected: True)")
    assert is_valid == True, "Failed valid case"
    
    # Invalid date (e.g. past Sunday)
    past_sunday = target_sunday - datetime.timedelta(days=7)
    is_valid, date, err = validate_newsletter_date(past_sunday.isoformat())
    print(f"Invalid case: is_valid={is_valid}, date={date}, err='{err}' (Expected: False)")
    assert is_valid == False, "Failed invalid date case"
    
    # Format error
    is_valid, date, err = validate_newsletter_date("invalid-date-format")
    print(f"Format error case: is_valid={is_valid}, date={date}, err='{err}' (Expected: False)")
    assert is_valid == False, "Failed format error case"
    
    # Empty date
    is_valid, date, err = validate_newsletter_date("")
    print(f"Empty case: is_valid={is_valid}, date={date}, err='{err}' (Expected: False)")
    assert is_valid == False, "Failed empty date case"
    
    print("All validation tests passed successfully!")

def main():
    calc_passed = test_sunday_calculation()
    if calc_passed:
        print("Target Sunday calculation test passed successfully!")
    else:
        print("Target Sunday calculation test FAILED!")
        sys.exit(1)
        
    test_date_validation()

if __name__ == "__main__":
    main()
````

## File: backend/.env.example
````
# Newsletter Herald API - Environment Variables
# Copy this file to .env and fill in your actual values

# API Authentication
# Your internal API key for authenticating requests between frontend and backend
API_KEY=your_api_key_here

# LLM Provider API Keys
# Anthropic API key (required for Claude model / remote strategy)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# Groq API key (used for Llama models / free tier)
GROQ_API_KEY=your_groq_api_key_here
# OpenAI API key (optional)
OPENAI_API_KEY=your_openai_api_key_here

# LLM Configuration
# LLM Strategy: auto (default), local (force Ollama), remote (force Claude)
LLM_STRATEGY=local
# Local Ollama URL (default: http://localhost:11434)
# Local Ollama model (default: llama3.1:8b for speed, or llama3.3 for high quality)
OLLAMA_MODEL=llama3.1:8b

# Database Configuration
# Connection string for your Neon PostgreSQL database
# Format: postgresql://username:password@host:port/database?sslmode=require
DATABASE_URL=your_neon_postgresql_url_here

# Google Drive Configuration
# The ID of the folder where newsletters will be stored
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
# The entire JSON content of your Service Account key file (as a single line or string)
GOOGLE_SERVICE_ACCOUNT_JSON=your_service_account_json_here

# SendGrid Configuration
SENDGRID_API_KEY=your_sendgrid_api_key_here
FROM_EMAIL=your_verified_sender_email_here

# Stack Auth Configuration
STACK_PROJECT_ID=your_stack_project_id_here
STACK_PUBLISHABLE_CLIENT_KEY=your_stack_publishable_client_key_here
STACK_SECRET_SERVER_KEY=your_stack_secret_server_key_here

# Application Configuration
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000
````

## File: backend/.gitignore
````
/.idea/
/codealike.json
.env
.venv
````

## File: backend/README.md
````markdown
# Newsletter Herald Backend API

FastAPI-based service designed to automate document processing, text extraction, and AI-powered summarization of church newsletters.

## Tech Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLAlchemy (async) with Neon.tech (PostgreSQL)
- **LLM Integrations**:
  - **Ollama**: Local processing (Llama 3.3 70B recommended)
  - **Groq**: High-speed cloud API (Llama 3.3 70B)
  - **Anthropic**: Claude 3 Opus for complex documents
- **Storage**:
  - **Cloudflare R2**: Primary storage for newsletter PDFs and thumbnails
  - **Google Drive**: Fallback storage and backup
- **Auth**: Stack Auth for user management and secure API access

## Project Structure
- `main.py`: FastAPI entry point
- `config.py`: Configuration and environment variable management
- `db/`: Database models and connection setup
- `llm/`: LLM provider logic and summarization orchestration
- `helpers/`: Utilities for text extraction (OCR), storage, and auth
- `scripts/`: Batch processing and maintenance scripts

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: Using a virtual environment (`python -m venv venv`) is recommended.*

2. **Configuration**:
   Copy `.env.example` to `.env` and configure your API keys, database URLs, and cloud storage credentials.

3. **Initialize Database**:
   ```bash
   python scripts/create_tables.py
   ```

4. **Run the API**:
   ```bash
   uvicorn main:app --reload
   ```

## Key Scripts

### Batch Upload
Process all PDF/DOCX files in `newsletters_to_upload/`:
```bash
python scripts/upload_local_files.py
```

### Drive Synchronization
Process existing files in the configured Google Drive folder:
```bash
python scripts/process_existing_drive_files.py
```

## LLM Configuration

The backend supports multiple strategies configured in `.env` via `LLM_STRATEGY`:
- **`local`**: Uses the local Ollama instance at `OLLAMA_BASE_URL`.
- **`groq`**: Forces usage of Groq's high-performance inference.
- **`remote`**: Forces usage of Anthropic's Claude.
- **`auto`**: Uses local models for standard documents and remote models for large ones.

## API Documentation
Interactive docs are available at `http://localhost:8000/docs`.
````

## File: backend/requirements.txt
````
# This file was autogenerated by uv via the following command:
#    uv pip compile pyproject.toml -o requirements.txt
annotated-types==0.7.0
    # via pydantic
anyio==4.9.0
    # via starlette
asyncpg==0.31.0
    # via newsletter-herald-backend (pyproject.toml)
boto3==1.43.14
    # via newsletter-herald-backend (pyproject.toml)
botocore==1.43.14
    # via
    #   boto3
    #   s3transfer
certifi==2025.7.14
    # via requests
cffi==2.0.0
    # via cryptography
charset-normalizer==3.4.2
    # via requests
click==8.2.1
    # via uvicorn
colorama==0.4.6
    # via click
cryptography==48.0.0
    # via
    #   google-auth
    #   sendgrid
databases==0.9.0
    # via newsletter-herald-backend (pyproject.toml)
fastapi==0.116.1
    # via newsletter-herald-backend (pyproject.toml)
google-api-core==2.30.3
    # via google-api-python-client
google-api-python-client==2.196.0
    # via newsletter-herald-backend (pyproject.toml)
google-auth==2.53.0
    # via
    #   newsletter-herald-backend (pyproject.toml)
    #   google-api-core
    #   google-api-python-client
    #   google-auth-httplib2
    #   google-auth-oauthlib
google-auth-httplib2==0.4.0
    # via google-api-python-client
google-auth-oauthlib==1.4.0
    # via newsletter-herald-backend (pyproject.toml)
googleapis-common-protos==1.75.0
    # via google-api-core
greenlet==3.5.1
    # via sqlalchemy
h11==0.16.0
    # via uvicorn
httplib2==0.31.2
    # via
    #   google-api-python-client
    #   google-auth-httplib2
idna==3.10
    # via
    #   anyio
    #   requests
jmespath==1.1.0
    # via
    #   boto3
    #   botocore
lxml==6.0.0
    # via python-docx
markupsafe==3.0.3
    # via werkzeug
oauthlib==3.3.1
    # via requests-oauthlib
proto-plus==1.28.0
    # via google-api-core
protobuf==7.35.0
    # via
    #   google-api-core
    #   googleapis-common-protos
    #   proto-plus
psycopg2-binary==2.9.12
    # via newsletter-herald-backend (pyproject.toml)
pyasn1==0.6.3
    # via pyasn1-modules
pyasn1-modules==0.4.2
    # via google-auth
pycparser==3.0
    # via cffi
pydantic==2.11.7
    # via
    #   fastapi
    #   pydantic-settings
pydantic-core==2.33.2
    # via pydantic
pydantic-settings==2.10.1
    # via newsletter-herald-backend (pyproject.toml)
pymupdf==1.26.3
    # via newsletter-herald-backend (pyproject.toml)
pyparsing==3.3.2
    # via httplib2
python-dateutil==2.9.0.post0
    # via botocore
python-docx==1.2.0
    # via newsletter-herald-backend (pyproject.toml)
python-dotenv==1.1.1
    # via
    #   newsletter-herald-backend (pyproject.toml)
    #   pydantic-settings
python-http-client==3.3.7
    # via sendgrid
python-multipart==0.0.20
    # via newsletter-herald-backend (pyproject.toml)
regex==2024.11.6
    # via tiktoken
requests==2.32.4
    # via
    #   newsletter-herald-backend (pyproject.toml)
    #   google-api-core
    #   requests-oauthlib
    #   tiktoken
requests-oauthlib==2.0.0
    # via google-auth-oauthlib
s3transfer==0.17.0
    # via boto3
sendgrid==6.12.5
    # via newsletter-herald-backend (pyproject.toml)
six==1.17.0
    # via python-dateutil
sniffio==1.3.1
    # via anyio
sqlalchemy==2.0.49
    # via
    #   newsletter-herald-backend (pyproject.toml)
    #   databases
starlette==0.47.1
    # via fastapi
tiktoken==0.9.0
    # via newsletter-herald-backend (pyproject.toml)
typing-extensions==4.14.1
    # via
    #   anyio
    #   fastapi
    #   pydantic
    #   pydantic-core
    #   python-docx
    #   sqlalchemy
    #   starlette
    #   typing-inspection
typing-inspection==0.4.1
    # via
    #   pydantic
    #   pydantic-settings
uritemplate==4.2.0
    # via google-api-python-client
urllib3==2.5.0
    # via
    #   botocore
    #   requests
uvicorn==0.35.0
    # via newsletter-herald-backend (pyproject.toml)
werkzeug==3.1.8
    # via sendgrid
````

## File: frontend/app/globals.css
````css
@import "tailwindcss";

:root {
  --background: #ffffff;
  --foreground: #171717;
}

@theme inline {
  --font-sans: var(--font-geist-sans);
  --font-mono: var(--font-geist-mono);
}

body {
  background: var(--background);
  color: var(--foreground);
  font-family: var(--font-sans);
}
````

## File: frontend/app/theme.ts
````typescript
'use client';
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#000000',
    },
    secondary: {
      main: '#666666',
    },
    background: {
      default: '#f8f9fa',
    },
  },
  typography: {
    fontFamily: 'var(--font-geist-sans), sans-serif',
    h1: {
      fontWeight: 800,
    },
    h4: {
      fontWeight: 700,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        },
      },
    },
  },
});

export default theme;
````

## File: frontend/public/file.svg
````xml
<svg fill="none" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg"><path d="M14.5 13.5V5.41a1 1 0 0 0-.3-.7L9.8.29A1 1 0 0 0 9.08 0H1.5v13.5A2.5 2.5 0 0 0 4 16h8a2.5 2.5 0 0 0 2.5-2.5m-1.5 0v-7H8v-5H3v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1M9.5 5V2.12L12.38 5zM5.13 5h-.62v1.25h2.12V5zm-.62 3h7.12v1.25H4.5zm.62 3h-.62v1.25h7.12V11z" clip-rule="evenodd" fill="#666" fill-rule="evenodd"/></svg>
````

## File: frontend/public/globe.svg
````xml
<svg fill="none" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><g clip-path="url(#a)"><path fill-rule="evenodd" clip-rule="evenodd" d="M10.27 14.1a6.5 6.5 0 0 0 3.67-3.45q-1.24.21-2.7.34-.31 1.83-.97 3.1M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16m.48-1.52a7 7 0 0 1-.96 0H7.5a4 4 0 0 1-.84-1.32q-.38-.89-.63-2.08a40 40 0 0 0 3.92 0q-.25 1.2-.63 2.08a4 4 0 0 1-.84 1.31zm2.94-4.76q1.66-.15 2.95-.43a7 7 0 0 0 0-2.58q-1.3-.27-2.95-.43a18 18 0 0 1 0 3.44m-1.27-3.54a17 17 0 0 1 0 3.64 39 39 0 0 1-4.3 0 17 17 0 0 1 0-3.64 39 39 0 0 1 4.3 0m1.1-1.17q1.45.13 2.69.34a6.5 6.5 0 0 0-3.67-3.44q.65 1.26.98 3.1M8.48 1.5l.01.02q.41.37.84 1.31.38.89.63 2.08a40 40 0 0 0-3.92 0q.25-1.2.63-2.08a4 4 0 0 1 .85-1.32 7 7 0 0 1 .96 0m-2.75.4a6.5 6.5 0 0 0-3.67 3.44 29 29 0 0 1 2.7-.34q.31-1.83.97-3.1M4.58 6.28q-1.66.16-2.95.43a7 7 0 0 0 0 2.58q1.3.27 2.95.43a18 18 0 0 1 0-3.44m.17 4.71q-1.45-.12-2.69-.34a6.5 6.5 0 0 0 3.67 3.44q-.65-1.27-.98-3.1" fill="#666"/></g><defs><clipPath id="a"><path fill="#fff" d="M0 0h16v16H0z"/></clipPath></defs></svg>
````

## File: frontend/public/next.svg
````xml
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 394 80"><path fill="#000" d="M262 0h68.5v12.7h-27.2v66.6h-13.6V12.7H262V0ZM149 0v12.7H94v20.4h44.3v12.6H94v21h55v12.6H80.5V0h68.7zm34.3 0h-17.8l63.8 79.4h17.9l-32-39.7 32-39.6h-17.9l-23 28.6-23-28.6zm18.3 56.7-9-11-27.1 33.7h17.8l18.3-22.7z"/><path fill="#000" d="M81 79.3 17 0H0v79.3h13.6V17l50.2 62.3H81Zm252.6-.4c-1 0-1.8-.4-2.5-1s-1.1-1.6-1.1-2.6.3-1.8 1-2.5 1.6-1 2.6-1 1.8.3 2.5 1a3.4 3.4 0 0 1 .6 4.3 3.7 3.7 0 0 1-3 1.8zm23.2-33.5h6v23.3c0 2.1-.4 4-1.3 5.5a9.1 9.1 0 0 1-3.8 3.5c-1.6.8-3.5 1.3-5.7 1.3-2 0-3.7-.4-5.3-1s-2.8-1.8-3.7-3.2c-.9-1.3-1.4-3-1.4-5h6c.1.8.3 1.6.7 2.2s1 1.2 1.6 1.5c.7.4 1.5.5 2.4.5 1 0 1.8-.2 2.4-.6a4 4 0 0 0 1.6-1.8c.3-.8.5-1.8.5-3V45.5zm30.9 9.1a4.4 4.4 0 0 0-2-3.3 7.5 7.5 0 0 0-4.3-1.1c-1.3 0-2.4.2-3.3.5-.9.4-1.6 1-2 1.6a3.5 3.5 0 0 0-.3 4c.3.5.7.9 1.3 1.2l1.8 1 2 .5 3.2.8c1.3.3 2.5.7 3.7 1.2a13 13 0 0 1 3.2 1.8 8.1 8.1 0 0 1 3 6.5c0 2-.5 3.7-1.5 5.1a10 10 0 0 1-4.4 3.5c-1.8.8-4.1 1.2-6.8 1.2-2.6 0-4.9-.4-6.8-1.2-2-.8-3.4-2-4.5-3.5a10 10 0 0 1-1.7-5.6h6a5 5 0 0 0 3.5 4.6c1 .4 2.2.6 3.4.6 1.3 0 2.5-.2 3.5-.6 1-.4 1.8-1 2.4-1.7a4 4 0 0 0 .8-2.4c0-.9-.2-1.6-.7-2.2a11 11 0 0 0-2.1-1.4l-3.2-1-3.8-1c-2.8-.7-5-1.7-6.6-3.2a7.2 7.2 0 0 1-2.4-5.7 8 8 0 0 1 1.7-5 10 10 0 0 1 4.3-3.5c2-.8 4-1.2 6.4-1.2 2.3 0 4.4.4 6.2 1.2 1.8.8 3.2 2 4.3 3.4 1 1.4 1.5 3 1.5 5h-5.8z"/></svg>
````

## File: frontend/public/vercel.svg
````xml
<svg fill="none" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1155 1000"><path d="m577.3 0 577.4 1000H0z" fill="#fff"/></svg>
````

## File: frontend/public/window.svg
````xml
<svg fill="none" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path fill-rule="evenodd" clip-rule="evenodd" d="M1.5 2.5h13v10a1 1 0 0 1-1 1h-11a1 1 0 0 1-1-1zM0 1h16v11.5a2.5 2.5 0 0 1-2.5 2.5h-11A2.5 2.5 0 0 1 0 12.5zm3.75 4.5a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5M7 4.75a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0m1.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5" fill="#666"/></svg>
````

## File: frontend/eslint.config.mjs
````javascript
import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
]);

export default eslintConfig;
````

## File: frontend/next.config.ts
````typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
};

export default nextConfig;
````

## File: frontend/postcss.config.mjs
````javascript
const config = {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};

export default config;
````

## File: frontend/README.md
````markdown
# Newsletter Herald Frontend

A modern dashboard for managing church newsletters and viewing AI-generated summaries.

## Tech Stack
- **Framework**: Next.js 15+ (App Router)
- **Styling**: Material UI (MUI) and Tailwind CSS
- **Authentication**: Stack Auth
- **State Management**: React Hooks and Context API

## Getting Started

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Run Development Server**:
   ```bash
   npm run dev
   ```
   Open `http://localhost:3000` to view the application.

## Project Structure
- `app/`: Next.js 15 pages and layouts
- `app/components/`: Reusable MUI components
- `app/theme.ts`: Global MUI theme configuration
- `stack/`: Stack Auth client and server configuration

## Configuration
Ensure your `frontend/.env.local` contains the following Stack Auth credentials:
- `NEXT_PUBLIC_STACK_PROJECT_ID`
- `NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY`
- `STACK_SECRET_SERVER_KEY`

## Deployment
The frontend is designed to be deployed on Vercel or any other Next.js-compatible platform.

## Learn More
To learn more about Next.js, check out the [Next.js Documentation](https://nextjs.org/docs).
````

## File: frontend/tsconfig.json
````json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "react-jsx",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.tsx",
    ".next/types/**/*.ts",
    ".next/dev/types/**/*.ts",
    "**/*.mts"
  ],
  "exclude": ["node_modules"]
}
````

## File: studio-newsletter-herald/schemaTypes/delivery.ts
````typescript
import {defineType, defineField} from 'sanity'

export const delivery = defineType({
  name: 'delivery',
  title: 'Delivery',
  type: 'document',
  fields: [
    defineField({
      name: 'newsletter',
      title: 'Newsletter Edition',
      description: 'The newsletter edition to be dispatched',
      type: 'reference',
      to: [{type: 'newsletterEdition'}],
      validation: (Rule) => Rule.required().error('Newsletter edition reference is required'),
    }),
    defineField({
      name: 'scheduledFor',
      title: 'Scheduled For',
      description: 'Date and time when the delivery queue should execute sending',
      type: 'datetime',
      validation: (Rule) => Rule.required().error('Scheduled delivery datetime is required'),
    }),
    defineField({
      name: 'status',
      title: 'Status',
      description: 'Dispatch delivery state',
      type: 'string',
      options: {
        list: [
          {title: 'Pending', value: 'pending'},
          {title: 'Scheduled', value: 'scheduled'},
          {title: 'Sending', value: 'sending'},
          {title: 'Sent', value: 'sent'},
          {title: 'Failed', value: 'failed'},
          {title: 'Cancelled', value: 'cancelled'},
        ],
      },
      initialValue: 'pending',
      validation: (Rule) =>
        Rule.required()
          .error('Status is required')
          .custom((val) => {
            const allowed = ['pending', 'scheduled', 'sending', 'sent', 'failed', 'cancelled']
            return (
              (val && allowed.includes(val as string)) ||
              `Status must be one of: ${allowed.join(', ')}`
            )
          }),
    }),
    defineField({
      name: 'sentAt',
      title: 'Sent At',
      description: 'Timestamp when delivery batch completed transmission',
      type: 'datetime',
    }),
    defineField({
      name: 'deliveryStats',
      title: 'Delivery Statistics',
      description: 'Aggregated metrics for email transmission',
      type: 'object',
      fields: [
        defineField({
          name: 'recipientCount',
          title: 'Recipient Count',
          description: 'Total subscribers targeted for delivery',
          type: 'number',
          validation: (Rule) => Rule.min(0).precision(0),
        }),
        defineField({
          name: 'deliveredCount',
          title: 'Delivered Count',
          description: 'Successfully confirmed deliveries',
          type: 'number',
          validation: (Rule) => Rule.min(0).precision(0),
        }),
        defineField({
          name: 'failedCount',
          title: 'Failed Count',
          description: 'Failed or bounced deliveries',
          type: 'number',
          validation: (Rule) => Rule.min(0).precision(0),
        }),
        defineField({
          name: 'lastUpdatedAt',
          title: 'Last Updated At',
          description: 'Timestamp when statistics were last synced from Herald delivery engine',
          type: 'datetime',
          initialValue: () => new Date().toISOString(),
        }),
      ],
    }),
  ],
  preview: {
    select: {
      newsletterTitle: 'newsletter.title',
      status: 'status',
      scheduledFor: 'scheduledFor',
    },
    prepare({newsletterTitle, status, scheduledFor}) {
      const dateStr = scheduledFor ? new Date(scheduledFor).toLocaleString() : 'Unscheduled'
      return {
        title: newsletterTitle ? `Delivery: ${newsletterTitle}` : 'Delivery Record',
        subtitle: `Status: ${status || 'pending'} • Scheduled: ${dateStr}`,
      }
    },
  },
})
````

## File: studio-newsletter-herald/schemaTypes/editorialWorkflow.ts
````typescript
import {defineType, defineField, defineArrayMember} from 'sanity'

export const editorialWorkflow = defineType({
  name: 'editorialWorkflow',
  title: 'Editorial Workflow',
  type: 'document',
  fields: [
    defineField({
      name: 'newsletter',
      title: 'Newsletter Edition',
      description: 'The newsletter edition governed by this workflow',
      type: 'reference',
      to: [{type: 'newsletterEdition'}],
      validation: (Rule) => Rule.required().error('Newsletter edition reference is required'),
    }),
    defineField({
      name: 'currentStage',
      title: 'Current Stage',
      description: 'Current stage in the editorial governance pipeline',
      type: 'string',
      options: {
        list: [
          {title: 'Received', value: 'received'},
          {title: 'Processing', value: 'processing'},
          {title: 'Draft', value: 'draft'},
          {title: 'Awaiting Review', value: 'awaiting_review'},
          {title: 'Approved', value: 'approved'},
          {title: 'Scheduled', value: 'scheduled'},
          {title: 'Sent', value: 'sent'},
        ],
      },
      initialValue: 'received',
      validation: (Rule) =>
        Rule.required()
          .error('Current stage is required')
          .custom((val) => {
            const allowed = [
              'received',
              'processing',
              'draft',
              'awaiting_review',
              'approved',
              'scheduled',
              'sent',
            ]
            return (
              (val && allowed.includes(val as string)) ||
              `Current stage must be one of: ${allowed.join(', ')}`
            )
          }),
    }),
    defineField({
      name: 'assignedAgent',
      title: 'Assigned Agent',
      description: 'Identifier of the AI editorial agent handling automated tasks',
      type: 'string',
    }),
    defineField({
      name: 'reviewer',
      title: 'Human Reviewer',
      description: 'Name or email of the human editor reviewing the edition',
      type: 'string',
    }),
    defineField({
      name: 'decision',
      title: 'Review Decision',
      description: 'Human editorial gate decision',
      type: 'string',
      options: {
        list: [
          {title: 'Pending', value: 'pending'},
          {title: 'Approved', value: 'approved'},
          {title: 'Rejected', value: 'rejected'},
        ],
      },
      initialValue: 'pending',
      validation: (Rule) =>
        Rule.custom((val) => {
          if (!val) return true
          const allowed = ['pending', 'approved', 'rejected']
          return allowed.includes(val as string) || `Decision must be one of: ${allowed.join(', ')}`
        }),
    }),
    defineField({
      name: 'decisionAt',
      title: 'Decision Timestamp',
      description: 'Timestamp when the human review decision was executed',
      type: 'datetime',
    }),
    defineField({
      name: 'scheduledFor',
      title: 'Scheduled For',
      description: 'Target delivery datetime set upon approval',
      type: 'datetime',
    }),
    defineField({
      name: 'history',
      title: 'Workflow History',
      description: 'Immutable chronological audit trail of editorial stages and actions',
      type: 'array',
      of: [
        defineArrayMember({
          type: 'object',
          name: 'workflowHistoryEntry',
          title: 'Workflow History Entry',
          fields: [
            defineField({
              name: 'stage',
              title: 'Stage',
              type: 'string',
              validation: (Rule) => Rule.required().error('History stage is required'),
            }),
            defineField({
              name: 'actor',
              title: 'Actor',
              description: 'Agent or user responsible for this state transition',
              type: 'string',
              validation: (Rule) => Rule.required().error('History actor is required'),
            }),
            defineField({
              name: 'note',
              title: 'Note',
              description: 'Optional commentary or reason for state transition',
              type: 'text',
              rows: 2,
            }),
            defineField({
              name: 'timestamp',
              title: 'Timestamp',
              type: 'datetime',
              initialValue: () => new Date().toISOString(),
              validation: (Rule) => Rule.required().error('History timestamp is required'),
            }),
          ],
          preview: {
            select: {
              stage: 'stage',
              actor: 'actor',
              timestamp: 'timestamp',
            },
            prepare({stage, actor, timestamp}) {
              const formattedDate = timestamp ? new Date(timestamp).toLocaleString() : ''
              return {
                title: `${stage || 'Unknown stage'} • ${actor || 'Unknown actor'}`,
                subtitle: formattedDate,
              }
            },
          },
        }),
      ],
    }),
  ],
  preview: {
    select: {
      newsletterTitle: 'newsletter.title',
      stage: 'currentStage',
      decision: 'decision',
    },
    prepare({newsletterTitle, stage, decision}) {
      return {
        title: newsletterTitle ? `Workflow: ${newsletterTitle}` : 'Editorial Workflow',
        subtitle: `Stage: ${stage || 'N/A'} • Decision: ${decision || 'pending'}`,
      }
    },
  },
})
````

## File: studio-newsletter-herald/schemaTypes/newsletterEdition.ts
````typescript
import {defineType, defineField, defineArrayMember} from 'sanity'

export const newsletterEdition = defineType({
  name: 'newsletterEdition',
  title: 'Newsletter Edition',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: 'Title',
      description: 'Headline or liturgical title for this newsletter edition',
      type: 'string',
      validation: (Rule) => Rule.required().error('Title is required'),
    }),
    defineField({
      name: 'sourceDocumentUrl',
      title: 'Source Document URL',
      description: 'Direct link to the original PDF or cloud storage document',
      type: 'url',
      validation: (Rule) =>
        Rule.uri({
          scheme: ['http', 'https'],
        }),
    }),
    defineField({
      name: 'sourceFilename',
      title: 'Source Filename',
      description: 'Original filename of the uploaded bulletin or newsletter PDF',
      type: 'string',
    }),
    defineField({
      name: 'publicationDate',
      title: 'Publication Date',
      description: 'Date the newsletter was originally published or issued',
      type: 'date',
      validation: (Rule) => Rule.required().error('Publication date is required'),
    }),
    defineField({
      name: 'targetSunday',
      title: 'Target Sunday',
      description: 'The upcoming Sunday liturgical date this newsletter addresses',
      type: 'date',
      validation: (Rule) => Rule.required().error('Target Sunday is required'),
    }),
    defineField({
      name: 'liturgicalOccasion',
      title: 'Liturgical Occasion',
      description: 'Specific liturgical feast or celebration (e.g. 26th Sunday in Ordinary Time)',
      type: 'string',
    }),
    defineField({
      name: 'liturgicalSeason',
      title: 'Liturgical Season',
      description: 'Church season (e.g. Ordinary Time, Advent, Christmas, Lent, Easter)',
      type: 'string',
    }),
    defineField({
      name: 'liturgicalYear',
      title: 'Liturgical Year',
      description: 'Liturgical reading cycle (e.g. Year A, Year B, Year C)',
      type: 'string',
    }),
    defineField({
      name: 'primaryTheme',
      title: 'Primary Theme',
      description: 'Core editorial theme identified by the editorial agent or editor',
      type: 'string',
      validation: (Rule) => Rule.required().error('Primary theme is required'),
    }),
    defineField({
      name: 'supportingThemes',
      title: 'Supporting Themes',
      description: 'Curated secondary themes linked from the Theme taxonomy',
      type: 'array',
      of: [
        defineArrayMember({
          type: 'reference',
          to: [{type: 'theme'}],
        }),
      ],
    }),
    defineField({
      name: 'summary',
      title: 'Summary',
      description: 'Structured two-paragraph editorial digest synthesized for parishioners',
      type: 'text',
      rows: 6,
      validation: (Rule) => Rule.required().error('Summary is required'),
    }),
    defineField({
      name: 'status',
      title: 'Status',
      description: 'Current editorial publication lifecycle status',
      type: 'string',
      options: {
        list: [
          {title: 'Draft', value: 'draft'},
          {title: 'Awaiting Review', value: 'awaiting_review'},
          {title: 'Approved', value: 'approved'},
          {title: 'Scheduled', value: 'scheduled'},
          {title: 'Sent', value: 'sent'},
          {title: 'Rejected', value: 'rejected'},
          {title: 'Failed', value: 'failed'},
        ],
      },
      initialValue: 'draft',
      validation: (Rule) =>
        Rule.required()
          .error('Status is required')
          .custom((val) => {
            const allowed = [
              'draft',
              'awaiting_review',
              'approved',
              'scheduled',
              'sent',
              'rejected',
              'failed',
            ]
            return (
              (val && allowed.includes(val as string)) ||
              `Status must be one of: ${allowed.join(', ')}`
            )
          }),
    }),
    defineField({
      name: 'workflow',
      title: 'Editorial Workflow',
      description: 'Associated workflow record tracking stages and human approval history',
      type: 'reference',
      to: [{type: 'editorialWorkflow'}],
    }),
    defineField({
      name: 'delivery',
      title: 'Delivery Schedule',
      description: 'Associated email dispatch schedule and transmission statistics',
      type: 'reference',
      to: [{type: 'delivery'}],
    }),
    defineField({
      name: 'aiGenerated',
      title: 'AI Generated',
      description: 'Indicates whether the initial draft and themes were prepared by an AI agent',
      type: 'boolean',
      initialValue: true,
      validation: (Rule) => Rule.required().error('AI Generated flag is required'),
    }),
    defineField({
      name: 'aiModel',
      title: 'AI Model',
      description: 'Model identifier used by the editorial agent (e.g. mistral-large, claude-3-5-sonnet)',
      type: 'string',
    }),
    defineField({
      name: 'createdAt',
      title: 'Created At',
      description: 'Timestamp when this edition was initially created',
      type: 'datetime',
      initialValue: () => new Date().toISOString(),
      validation: (Rule) => Rule.required().error('Creation timestamp is required'),
    }),
    defineField({
      name: 'updatedAt',
      title: 'Updated At',
      description: 'Timestamp when this edition was last modified',
      type: 'datetime',
      initialValue: () => new Date().toISOString(),
      validation: (Rule) => Rule.required().error('Update timestamp is required'),
    }),
  ],
  preview: {
    select: {
      title: 'title',
      targetSunday: 'targetSunday',
      status: 'status',
      liturgicalOccasion: 'liturgicalOccasion',
    },
    prepare({title, targetSunday, status, liturgicalOccasion}) {
      const statusLabel = status ? `[${status.replace(/_/g, ' ').toUpperCase()}]` : ''
      const subtitle = [
        liturgicalOccasion,
        targetSunday ? `Sunday: ${targetSunday}` : '',
        statusLabel,
      ]
        .filter(Boolean)
        .join(' • ')
      return {
        title: title || 'Untitled Newsletter Edition',
        subtitle,
      }
    },
  },
})
````

## File: studio-newsletter-herald/schemaTypes/theme.ts
````typescript
import {defineType, defineField} from 'sanity'

export const theme = defineType({
  name: 'theme',
  title: 'Theme',
  type: 'document',
  fields: [
    defineField({
      name: 'name',
      title: 'Name',
      description: 'Name of the parish or liturgical theme',
      type: 'string',
      validation: (Rule) => Rule.required().error('Theme name is required'),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      description: 'Brief description of the theme and its parish context',
      type: 'text',
      rows: 3,
    }),
    defineField({
      name: 'category',
      title: 'Category',
      description: 'Liturgical or parish ministry category',
      type: 'string',
      options: {
        list: [
          {title: 'Spiritual', value: 'spiritual'},
          {title: 'Community', value: 'community'},
          {title: 'Service', value: 'service'},
          {title: 'Stewardship', value: 'stewardship'},
          {title: 'Vocation', value: 'vocation'},
          {title: 'Social', value: 'social'},
          {title: 'Liturgy', value: 'liturgy'},
          {title: 'Parish', value: 'parish'},
        ],
      },
      validation: (Rule) =>
        Rule.custom((val) => {
          if (!val) return true
          const allowed = [
            'spiritual',
            'community',
            'service',
            'stewardship',
            'vocation',
            'social',
            'liturgy',
            'parish',
          ]
          return allowed.includes(val as string) || `Category must be one of: ${allowed.join(', ')}`
        }),
    }),
  ],
  preview: {
    select: {
      title: 'name',
      category: 'category',
    },
    prepare({title, category}) {
      return {
        title: title || 'Untitled Theme',
        subtitle: category ? `Category: ${category}` : undefined,
      }
    },
  },
})
````

## File: LICENSE
````
Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
````

## File: start_dev.py
````python
import subprocess
import os
import sys
import time

def start_services():
    # Get the root directory
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to backend and frontend
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")
    
    print("🚀 Starting Newsletter Herald Services...")

    # Start Backend (FastAPI) using the virtual environment if it exists
    print("📂 Starting Backend on http://localhost:8000")
    
    python_exe = "python"
    venv_exists = False
    if os.name == 'nt':
        venv_python = os.path.join(backend_dir, "venv", "Scripts", "python.exe")
        if os.path.exists(venv_python):
            python_exe = venv_python
            venv_exists = True
    else:
        venv_python = os.path.join(backend_dir, "venv", "bin", "python")
        if os.path.exists(venv_python):
            python_exe = venv_python
            venv_exists = True

    # Check if uvicorn is installed in the selected python environment
    try:
        subprocess.check_call([python_exe, "-m", "uvicorn", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Uvicorn not found in backend environment. Installing dependencies...")
        subprocess.check_call([python_exe, "-m", "pip", "install", "-r", os.path.join(backend_dir, "requirements.txt")])

    backend_process = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "main:app", "--reload"],
        cwd=backend_dir,
        shell=True if os.name == 'nt' else False
    )

    # Give backend a moment to start
    time.sleep(2)

    # Start Frontend (Next.js)
    print("📂 Starting Frontend on http://localhost:3000")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        shell=True if os.name == 'nt' else False
    )

    try:
        # Keep the script running while services are active
        while True:
            time.sleep(1)
            if backend_process.poll() is not None:
                print("❌ Backend process stopped.")
                break
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped.")
                break
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Services stopped.")
        sys.exit(0)

if __name__ == "__main__":
    start_services()
````

## File: .agents/rules/graphify.md
````markdown
---
trigger: always_on
description: Consult the graphify knowledge graph at graphify-out/ for codebase and architecture questions.
---

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- For codebase or architecture questions, when `graphify-out/graph.json` exists, first run `graphify query "<question>"` (CLI) or `query_graph` (MCP). Use `graphify path "<A>" "<B>"` / `shortest_path` for relationships and `graphify explain "<concept>"` / `get_node` for focused concepts. These return a scoped subgraph, usually much smaller than `GRAPH_REPORT.md` or raw grep output.
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)
````

## File: .agents/workflows/graphify.md
````markdown
---
name: graphify
description: Turn any folder of files into a navigable knowledge graph
---

# Workflow: graphify

Follow the graphify skill to run the full pipeline.

If no path argument is given, use `.` (current directory).
````

## File: backend/helpers/auth.py
````python
import requests
import logging
from typing import Dict, Any
from config import get_settings

# Get settings from centralized configuration
settings = get_settings()

# Create a logger for this module
logger = logging.getLogger(__name__)


def stack_auth_request(method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
    """
    Make an authenticated request to the Stack Auth API.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        **kwargs: Additional arguments to pass to requests.request
        
    Returns:
        Dict[str, Any]: JSON response from the API
        
    Raises:
        Exception: If the API request fails
    """
    logger.debug(f"Making Stack Auth API request: {method} {endpoint}")
    
    res = requests.request(
        method,
        f'https://api.stack-auth.com/{endpoint}',
        headers={
            'x-stack-access-type': 'server',
            'x-stack-project-id': settings.stack_project_id,
            'x-stack-publishable-client-key': settings.stack_publishable_client_key,
            'x-stack-secret-server-key': settings.stack_secret_server_key,
            **kwargs.pop('headers', {}),
        },
        **kwargs,
    )
    
    if res.status_code >= 400:
        error_msg = f"Stack Auth API request failed with {res.status_code}: {res.text}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    logger.debug("Stack Auth API request successful")
    return res.json()
````

## File: backend/helpers/email.py
````python
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

def mask_email(email: str) -> str:
    """
    Masks an email address to prevent PII exposure in logs.
    Example: user@example.com -> u**r@example.com
             ab@example.com -> a*@example.com
             a@example.com -> *@example.com
    """
    if not email or "@" not in email:
        return email
    try:
        local, domain = email.split("@", 1)
        if len(local) > 2:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
        elif len(local) == 2:
            masked_local = local[0] + "*"
        else:
            masked_local = "*"
        return f"{masked_local}@{domain}"
    except Exception:
        return "masked_email"

def send_newsletter_email(to_email: str, subject: str, html_content: str):
    """
    Sends an email using Gmail SMTP (Primary) or SendGrid (Fallback).
    """
    masked_to = mask_email(to_email)

    # 1. Try Gmail SMTP first if configured
    if settings.gmail_user and settings.gmail_app_password:
        try:
            logger.info(f"Attempting to send email via Gmail SMTP to {masked_to}")
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.gmail_user
            msg["To"] = to_email
            
            # Attach html content
            part = MIMEText(html_content, "html")
            msg.attach(part)
            
            # Connect to Gmail SMTP server
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(settings.gmail_user, settings.gmail_app_password)
                server.sendmail(settings.gmail_user, to_email, msg.as_string())
                
            logger.info(f"Email sent successfully via Gmail SMTP to {masked_to}")
            return True
        except Exception as smtp_err:
            logger.error(f"Gmail SMTP failed: {smtp_err}. Falling back if possible.")

    # 2. Fallback to SendGrid
    if settings.sendgrid_api_key and settings.from_email:
        try:
            logger.info(f"Attempting to send email via SendGrid to {masked_to}")
            message = Mail(
                from_email=Email(settings.from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            sg = SendGridAPIClient(settings.sendgrid_api_key)
            response = sg.send(message)
            logger.info(f"Email sent successfully via SendGrid to {masked_to}. Status code: {response.status_code}")
            return True
        except Exception as sg_err:
            logger.error(f"SendGrid failed: {sg_err}")
            return False

    logger.error("No valid email configuration (Gmail or SendGrid) available.")
    return False
````

## File: backend/helpers/key_utils.py
````python
import logging
import secrets
from fastapi import Request, HTTPException
from config import get_settings

# Get settings from centralized configuration
settings = get_settings()

# Create a logger for this module
logger = logging.getLogger(__name__)

def verify_api_key(request: Request):
    """
    Verify that the request contains a valid API key in the Authorization or X-API-Key header.
    
    Args:
        request: The FastAPI request object
        
    Raises:
        HTTPException: If the API key is missing or invalid
    """
    auth_header = request.headers.get("Authorization")
    x_api_key = request.headers.get("X-API-Key")
    
    verified = False
    
    if auth_header and secrets.compare_digest(auth_header, f"Bearer {settings.api_key}"):
        verified = True
    elif x_api_key and secrets.compare_digest(x_api_key, settings.api_key):
        verified = True
        
    if not verified:
        logger.warning("Unauthorized API request attempt")
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    logger.debug("API key verified successfully")
````

## File: backend/helpers/storage.py
````python
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
````

## File: backend/scripts/benchmark_delivery.py
````python
import asyncio
import time
from unittest.mock import MagicMock, AsyncMock

# Simulate the original delivery loop logic
async def run_original_logic(subscribers, send_email_fn, db_execute_fn):
    sent_count = 0
    failed_count = 0

    for sub in subscribers:
        recipient = sub['email']
        success = send_email_fn(
            to_email=recipient,
            subject="Test Newsletter",
            html_content="<p>Test</p>"
        )

        status = "sent" if success else "failed"
        err_msg = None if success else "SMTP delivery failure"

        await db_execute_fn(recipient, status, err_msg)

        if success:
            sent_count += 1
        else:
            failed_count += 1

    return sent_count, failed_count

# Simulate the optimized logic (using asyncio.gather, to_thread, Semaphore and execute_many)
async def run_optimized_logic(subscribers, send_email_fn, db_execute_many_fn, semaphore_limit=10):
    semaphore = asyncio.Semaphore(semaphore_limit)

    async def deliver_to_subscriber(sub):
        async with semaphore:
            recipient = sub['email']
            # Run the synchronous send_email in a thread pool
            success = await asyncio.to_thread(
                send_email_fn,
                to_email=recipient,
                subject="Test Newsletter",
                html_content="<p>Test</p>"
            )
            return recipient, success

    # Trigger deliveries concurrently
    tasks = [deliver_to_subscriber(sub) for sub in subscribers]
    results = await asyncio.gather(*tasks)

    # Collect values for bulk insert
    log_values = []
    sent_count = 0
    failed_count = 0

    for recipient, success in results:
        status = "sent" if success else "failed"
        err_msg = None if success else "SMTP delivery failure"
        log_values.append({
            "recipient": recipient,
            "status": status,
            "error_message": err_msg
        })
        if success:
            sent_count += 1
        else:
            failed_count += 1

    # Bulk insert
    if log_values:
        await db_execute_many_fn(log_values)

    return sent_count, failed_count

# Mock email send with 0.05 seconds of artificial latency
def mock_send_email(to_email, subject, html_content):
    time.sleep(0.05)
    return True

# Mock DB operations
async def mock_db_execute(recipient, status, error_message):
    await asyncio.sleep(0.005) # Simulate database query latency

async def mock_db_execute_many(values):
    await asyncio.sleep(0.01) # Bulk insert takes a tiny bit of time once

async def main():
    print("=== STARTING BENCHMARK ===")
    num_subscribers = 50
    subscribers = [{"email": f"user{i}@example.com"} for i in range(num_subscribers)]

    print(f"Scenario: Delivering newsletter to {num_subscribers} subscribers.")
    print("Each email delivery has a simulated SMTP latency of 50ms.")
    print("Each DB insert has a simulated DB query latency of 5ms.\n")

    # 1. Benchmark Original Logic
    print("Running Original Logic (sequential, blocking SMTP, N+1 DB inserts)...")
    start_time = time.perf_counter()
    sent, failed = await run_original_logic(subscribers, mock_send_email, mock_db_execute)
    original_duration = time.perf_counter() - start_time
    print(f"Original Logic Complete: Sent={sent}, Failed={failed}")
    print(f"Original Logic Time: {original_duration:.4f} seconds\n")

    # 2. Benchmark Optimized Logic
    print("Running Optimized Logic (concurrent threads, batch DB insert)...")
    start_time = time.perf_counter()
    sent, failed = await run_optimized_logic(subscribers, mock_send_email, mock_db_execute_many, semaphore_limit=10)
    optimized_duration = time.perf_counter() - start_time
    print(f"Optimized Logic Complete: Sent={sent}, Failed={failed}")
    print(f"Optimized Logic Time: {optimized_duration:.4f} seconds\n")

    # 3. Calculate Speedup
    speedup = original_duration / optimized_duration
    improvement = ((original_duration - optimized_duration) / original_duration) * 100
    print("=== BENCHMARK RESULTS ===")
    print(f"Original Duration:  {original_duration:.4f}s")
    print(f"Optimized Duration: {optimized_duration:.4f}s")
    print(f"Speedup Factor:     {speedup:.2f}x faster")
    print(f"Time Reduction:     {improvement:.2f}%")
    print("=========================")

if __name__ == "__main__":
    asyncio.run(main())
````

## File: backend/scripts/benchmark_drive_files.py
````python
import asyncio
import sys
import os
import time
from sqlalchemy import select

# Add backend directory to path
current_script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_script_dir)
sys.path.append(backend_dir)

from db.setup import database
from db.models import newsletters

async def run_benchmark():
    print("Connecting to DB...")
    await database.connect()

    try:
        # Generate 150 mock drive files
        print("Generating mock drive files...")
        drive_files = []
        for i in range(150):
            drive_files.append({
                "id": f"benchmark_file_{i}",
                "name": f"newsletter_bulletin_{i}.pdf",
                "mimeType": "application/pdf"
            })

        # Add 10 non-pdf files to test filtering
        for i in range(10):
            drive_files.append({
                "id": f"benchmark_ignored_{i}",
                "name": f"image_{i}.png",
                "mimeType": "image/png"
            })

        # Clean up any existing benchmark files in DB just in case
        await database.execute(newsletters.delete().where(newsletters.c.uploader == "benchmark_temp"))

        # Insert 75 of them into DB to simulate "already processed" files
        print("Inserting mock newsletters to database to simulate existing files...")
        for i in range(75):
            await database.execute(
                newsletters.insert().values(
                    filename=f"newsletter_bulletin_{i}.pdf",
                    drive_file_id=f"benchmark_file_{i}",
                    drive_web_view_link="http://drive.google.com/mock",
                    thumbnail_drive_id="mock_thumb",
                    uploader="benchmark_temp",
                    delivered=False
                )
            )

        # 1. Baseline Benchmark (N+1 Queries)
        print("\n--- Running Baseline Check (N+1 queries) ---")
        start_time = time.perf_counter()

        skipped_base = 0
        processed_base = 0
        for df in drive_files:
            file_id = df['id']
            filename = df['name']
            mime_type = df['mimeType']

            if mime_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                continue

            query = newsletters.select().where(newsletters.c.drive_file_id == file_id)
            existing = await database.fetch_one(query)
            if existing:
                skipped_base += 1
            else:
                processed_base += 1

        end_time = time.perf_counter()
        baseline_duration = end_time - start_time
        print(f"Baseline: Processed {processed_base}, Skipped {skipped_base} in {baseline_duration:.4f} seconds")

        # 2. Optimized Benchmark (Bulk Query + Set Check)
        print("\n--- Running Optimized Check (Bulk query + Set) ---")
        start_time = time.perf_counter()

        skipped_opt = 0
        processed_opt = 0

        # We only care about matching mime types
        filtered_files = [
            df for df in drive_files
            if df.get('mimeType') in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        ]

        file_ids = [df['id'] for df in filtered_files]
        if file_ids:
            # Query all matching IDs at once
            query = select(newsletters.c.drive_file_id).where(newsletters.c.drive_file_id.in_(file_ids))
            rows = await database.fetch_all(query)
            existing_drive_ids = {row['drive_file_id'] for row in rows}
        else:
            existing_drive_ids = set()

        for df in filtered_files:
            file_id = df['id']
            if file_id in existing_drive_ids:
                skipped_opt += 1
            else:
                processed_opt += 1

        end_time = time.perf_counter()
        optimized_duration = end_time - start_time
        print(f"Optimized: Processed {processed_opt}, Skipped {skipped_opt} in {optimized_duration:.4f} seconds")

        speedup = baseline_duration / optimized_duration if optimized_duration > 0 else float('inf')
        print(f"\n--- Results Summary ---")
        print(f"Baseline Time: {baseline_duration:.4f}s (performed {len(filtered_files)} DB queries)")
        print(f"Optimized Time: {optimized_duration:.4f}s (performed 1 DB query)")
        print(f"Speedup: {speedup:.2f}x faster!")

        # Verify correctness
        assert skipped_base == skipped_opt, "Skipped count mismatch!"
        assert processed_base == processed_opt, "Processed count mismatch!"
        print("Success: Correctness verified (both strategies yielded identical results)!")

    finally:
        # Clean up benchmark files from DB
        print("\nCleaning up mock data from DB...")
        await database.execute(newsletters.delete().where(newsletters.c.uploader == "benchmark_temp"))
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(run_benchmark())
````

## File: backend/scripts/benchmark_extraction.py
````python
import asyncio
import time
import os
import sys
from starlette.concurrency import run_in_threadpool

# Add backend directory to path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import sync_extract_text, extract_text_from_file

PDF_PATH = "../test_newsletters/test.pdf"

async def simulate_other_event_loop_activity():
    """
    Simulates lightweight event-loop activity (like handling pings, database queries, or CORS preflights)
    by running a periodic async ping every 10ms. We measure the maximum latency of these pings.
    If the event loop is blocked, the ping latency will spike to the duration of the block!
    If the event loop is free, the ping latency will remain extremely low (< 15ms).
    """
    ping_latencies = []
    stop_event = asyncio.Event()

    async def ping_loop():
        while not stop_event.is_set():
            t0 = time.perf_counter()
            await asyncio.sleep(0.01)
            latency = (time.perf_counter() - t0 - 0.01) * 1000 # in ms
            ping_latencies.append(latency)

    ping_task = asyncio.create_task(ping_loop())
    return stop_event, ping_task, ping_latencies

async def run_sync_extraction_blocked(pdf_bytes: bytes, num_runs: int = 5):
    """
    Simulates the blocking scenario where synchronous file writing and OCR
    parsing run directly on the async event loop thread.
    Since they block the loop, even when we gather them, they will execute sequentially
    because the event loop thread is completely held hostage by each CPU/IO task.
    """
    def block_loop(b):
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(b)
        try:
            return extract_text_from_file(temp_file_path, file_type="pdf")
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    async def worker():
        return block_loop(pdf_bytes)

    stop_event, ping_task, latencies = await simulate_other_event_loop_activity()

    start_time = time.perf_counter()
    tasks = [worker() for _ in range(num_runs)]
    results = await asyncio.gather(*tasks)
    end_time = time.perf_counter()

    stop_event.set()
    await ping_task

    return end_time - start_time, len(results), max(latencies or [0]), sum(latencies or [0])/len(latencies or [1])

async def run_async_extraction_threadpool(pdf_bytes: bytes, num_runs: int = 5):
    """
    Runs the extraction in the threadpool. Since these run on separate worker threads,
    they can run concurrently, and do not block the event loop thread!
    """
    async def worker():
        return await run_in_threadpool(sync_extract_text, pdf_bytes, "application/pdf")

    stop_event, ping_task, latencies = await simulate_other_event_loop_activity()

    start_time = time.perf_counter()
    tasks = [worker() for _ in range(num_runs)]
    results = await asyncio.gather(*tasks)
    end_time = time.perf_counter()

    stop_event.set()
    await ping_task

    return end_time - start_time, len(results), max(latencies or [0]), sum(latencies or [0])/len(latencies or [1])

async def main():
    if not os.path.exists(PDF_PATH):
        print(f"Error: PDF file not found at {PDF_PATH}")
        sys.exit(1)

    print(f"Reading PDF from {PDF_PATH}...")
    with open(PDF_PATH, "rb") as f:
        pdf_bytes = f.read()

    print(f"Loaded {len(pdf_bytes) / 1024 / 1024:.2f} MB PDF file.\n")
    print("======================================================================")
    print("⚡ Running Benchmarks: Concurrent Document Parsing (5 concurrent tasks)")
    print("======================================================================\n")

    # Warmup
    print("Warming up...")
    await run_async_extraction_threadpool(pdf_bytes, num_runs=1)
    print("Warmup done.\n")

    # 1. Blocked Event Loop (Old Sync approach)
    print("1. Running old synchronous extraction (event loop blocked)...")
    sync_duration, sync_count, sync_max_lat, sync_avg_lat = await run_sync_extraction_blocked(pdf_bytes, num_runs=5)
    print(f"   Done. Took {sync_duration:.4f} seconds for {sync_count} runs.")
    print(f"   Max event loop delay: {sync_max_lat:.2f} ms | Avg delay: {sync_avg_lat:.2f} ms\n")

    # 2. Async Threadpool (New Optimized approach)
    print("2. Running optimized async threadpool extraction (event loop free)...")
    async_duration, async_count, async_max_lat, async_avg_lat = await run_async_extraction_threadpool(pdf_bytes, num_runs=5)
    print(f"   Done. Took {async_duration:.4f} seconds for {async_count} runs.")
    print(f"   Max event loop delay: {async_max_lat:.2f} ms | Avg delay: {async_avg_lat:.2f} ms\n")

    # Calculate Speedup and Responsiveness boost
    latency_reduction = (sync_max_lat - async_max_lat)
    latency_reduction_percent = (sync_max_lat / async_max_lat) if async_max_lat > 0 else 0

    print("======================================================================")
    print("📊 BENCHMARK RESULTS SUMMARY")
    print("======================================================================")
    print(f"{'Metric':<38} | {'Synchronous (Blocked)':<22} | {'Threadpool (Optimized)':<22}")
    print("-" * 88)
    print(f"{'Total execution time (5 runs)':<38} | {sync_duration:19.4f}s | {async_duration:19.4f}s")
    print(f"{'Average extraction time / doc':<38} | {sync_duration / 5:19.4f}s | {async_duration / 5:19.4f}s")
    print(f"{'Worst-case event loop latency':<38} | {sync_max_lat:17.2f} ms | {async_max_lat:17.2f} ms")
    print(f"{'Average event loop latency':<38} | {sync_avg_lat:17.2f} ms | {async_avg_lat:17.2f} ms")
    print("-" * 88)
    print(f"{'Worst-case Event Loop Speedup':<38} | {'0.0% (Baseline)':<22} | {latency_reduction_percent:20.1f}x faster")
    print("======================================================================")
    print(f"💡 Explanation: Running CPU-bound OCR and I/O inside threadpool")
    print(f"   prevents event-loop starvation, allowing concurrent API requests (e.g.,")
    print(f"   health checks, dashboard pings) to respond {latency_reduction_percent:.1f}x faster")
    print(f"   under load, with maximum response lag reduced by {latency_reduction:.1f} ms!")
    print("======================================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
````

## File: backend/scripts/benchmark_import.py
````python
import csv
import time
import asyncio
import os
import sys

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from db.setup import database
from db.models import subscribers
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import func

# Generate a mock contacts.csv for benchmarking
def create_mock_csv(file_path, num_rows=100):
    with open(file_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["First Name", "Last Name", "E-mail 1 - Value", "Phone 1 - Value"])
        for i in range(num_rows):
            writer.writerow([
                f"First{i}",
                f"Last{i}",
                f"bench_user_{i}@example.com",
                f"+12345678{i:02d}"
            ])

async def cleanup_bench_users():
    try:
        query = subscribers.delete().where(subscribers.c.email.like("bench_user_%"))
        await database.execute(query)
        print("Cleaned up benchmark subscribers from DB")
    except Exception as e:
        print(f"Cleanup error: {e}")

async def run_legacy_method(csv_path):
    print("\n--- Running current slow import method (legacy) ---")
    try:
        with open(csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            count = 0
            start_time = time.time()
            for row in reader:
                email = row.get("E-mail 1 - Value", "").strip().lower()
                if not email or "@" not in email:
                    continue

                first_name = row.get("First Name", "").strip() or None
                last_name = row.get("Last Name", "").strip() or None
                phone = row.get("Phone 1 - Value", "").strip() or None

                # Check if subscriber already exists
                query = select(subscribers).where(subscribers.c.email == email)
                existing = await database.fetch_one(query)

                if existing:
                    # Update details if changed
                    update_query = subscribers.update().where(subscribers.c.email == email).values(
                        first_name=first_name or existing["first_name"],
                        last_name=last_name or existing["last_name"],
                        phone=phone or existing["phone"],
                        is_active=True
                    )
                    await database.execute(update_query)
                else:
                    # Insert new subscriber
                    insert_query = subscribers.insert().values(
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        phone=phone,
                        is_active=True
                    )
                    await database.execute(insert_query)
                count += 1
            duration = time.time() - start_time
            print(f"Legacy import took: {duration:.4f} seconds for {count} rows")
            return duration
    except Exception as e:
        print(f"Legacy import error: {e}")
        return 0

async def run_optimized_method(csv_path):
    print("\n--- Running optimized bulk import method ---")
    try:
        with open(csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            values_to_insert = []
            seen_emails = set()
            start_time = time.time()

            for row in reader:
                email = row.get("E-mail 1 - Value", "").strip().lower()
                if not email or "@" not in email:
                    continue

                if email in seen_emails:
                    continue
                seen_emails.add(email)

                first_name = row.get("First Name", "").strip() or None
                last_name = row.get("Last Name", "").strip() or None
                phone = row.get("Phone 1 - Value", "").strip() or None

                values_to_insert.append({
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone": phone,
                    "is_active": True
                })

            if not values_to_insert:
                print("No valid contacts found in CSV.")
                return 0

            stmt = pg_insert(subscribers)
            stmt = stmt.on_conflict_do_update(
                index_elements=['email'],
                set_={
                    'first_name': func.coalesce(stmt.excluded.first_name, subscribers.c.first_name),
                    'last_name': func.coalesce(stmt.excluded.last_name, subscribers.c.last_name),
                    'phone': func.coalesce(stmt.excluded.phone, subscribers.c.phone),
                    'is_active': True
                }
            )

            await database.execute_many(stmt, values_to_insert)
            duration = time.time() - start_time
            print(f"Optimized import took: {duration:.4f} seconds for {len(values_to_insert)} rows")
            return duration
    except Exception as e:
        print(f"Optimized import error: {e}")
        return 0

async def main():
    csv_path = "bench_contacts.csv"
    create_mock_csv(csv_path, num_rows=100)

    await database.connect()
    try:
        # Measure legacy
        await cleanup_bench_users()
        leg_ins = await run_legacy_method(csv_path)
        leg_upd = await run_legacy_method(csv_path)

        # Measure optimized
        await cleanup_bench_users()
        opt_ins = await run_optimized_method(csv_path)
        opt_upd = await run_optimized_method(csv_path)

        # Final cleanup
        await cleanup_bench_users()

        print("\n================ BENCHMARK RESULTS ================")
        print(f"{'Operation':<15} | {'Legacy Time (s)':<15} | {'Optimized Time (s)':<18} | {'Speedup':<10}")
        print("-" * 68)
        print(f"{'100 Inserts':<15} | {leg_ins:<15.4f} | {opt_ins:<18.4f} | {leg_ins/opt_ins:<10.2f}x")
        print(f"{'100 Updates':<15} | {leg_upd:<15.4f} | {opt_upd:<18.4f} | {leg_upd/opt_upd:<10.2f}x")
        print("===================================================")

    finally:
        await database.disconnect()
        if os.path.exists(csv_path):
            os.remove(csv_path)

if __name__ == "__main__":
    asyncio.run(main())
````

## File: backend/scripts/benchmark_subscribers.py
````python
import asyncio
import time
import sys
import os

# Add backend directory to path
current_script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_script_dir)
sys.path.append(backend_dir)

from db.setup import database
from db.models import subscribers
from main import batch_subscribe_users, BatchSubscribersRequest
from sqlalchemy import select, delete

async def setup_subscribers(num_active: int, num_inactive: int):
    # Clean up benchmark test emails first
    print("Cleaning up previous benchmark data...")
    query = delete(subscribers).where(subscribers.c.email.like("%@benchmark-test.com"))
    await database.execute(query)

    print(f"Seeding {num_active} active and {num_inactive} inactive subscribers...")

    # Seed active ones
    for i in range(num_active):
        email = f"active_{i}@benchmark-test.com"
        query = subscribers.insert().values(email=email, is_active=True)
        await database.execute(query)

    # Seed inactive ones
    for i in range(num_inactive):
        email = f"inactive_{i}@benchmark-test.com"
        query = subscribers.insert().values(email=email, is_active=False)
        await database.execute(query)

async def run_benchmark():
    print(f"Connecting to database...")
    await database.connect()

    try:
        # We will seed 50 active and 50 inactive subscribers
        num_active = 50
        num_inactive = 50
        await setup_subscribers(num_active, num_inactive)

        # Prepare a large batch of 200 emails:
        # - 50 existing active emails
        # - 50 existing inactive emails (to reactivate)
        # - 100 brand new emails
        emails_batch = []
        for i in range(num_active):
            emails_batch.append(f"active_{i}@benchmark-test.com")
        for i in range(num_inactive):
            emails_batch.append(f"inactive_{i}@benchmark-test.com")
        for i in range(100):
            emails_batch.append(f"new_{i}@benchmark-test.com")

        print(f"Preparing batch subscription for {len(emails_batch)} emails...")
        request_data = BatchSubscribersRequest(emails=emails_batch)

        # Run and measure time
        start_time = time.perf_counter()
        response = await batch_subscribe_users(request_data)
        end_time = time.perf_counter()

        duration = end_time - start_time
        print("\n==================================================")
        print("📊 BENCHMARK RESULT")
        print("==================================================")
        print(f"Execution time: {duration:.4f} seconds")
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.body.decode()}")
        print("==================================================\n")

    finally:
        # Clean up benchmark test emails
        print("Cleaning up benchmark data...")
        query = delete(subscribers).where(subscribers.c.email.like("%@benchmark-test.com"))
        await database.execute(query)
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(run_benchmark())
````

## File: backend/scripts/benchmark_upload.py
````python
import asyncio
import time
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from db.setup import database
from db.models import newsletters
from helpers.text_utils import sanitize_filename


async def run_benchmark():
    await database.connect()

    # Let's get some existing filenames from DB to query
    query = newsletters.select().limit(50)
    rows = await database.fetch_all(query)
    filenames = [row["filename"] for row in rows]

    # If DB is empty, let's generate some dummy filenames to simulate
    if not filenames:
        filenames = [f"2024-12-{i:02d}-Trinity-Newsletter.pdf" for i in range(1, 21)]

    print(f"Benchmarking with {len(filenames)} filenames.")

    # ------------------ N+1 Implementation ------------------
    print("\n--- Running N+1 Query Baseline ---")
    start_time = time.perf_counter()

    n_plus_one_results = []
    for filename in filenames:
        # Check if already in DB (N+1 query)
        q = newsletters.select().where(newsletters.c.filename == filename)
        existing = await database.fetch_one(q)
        if existing:
            n_plus_one_results.append(existing["filename"])

    n_plus_one_duration = time.perf_counter() - start_time
    print(f"N+1 baseline duration: {n_plus_one_duration:.4f} seconds")
    print(f"Found {len(n_plus_one_results)} matching records.")

    # ------------------ Optimized Implementation ------------------
    print("\n--- Running Bulk Query Optimized ---")
    start_time = time.perf_counter()

    # Bulk query
    q = newsletters.select().where(newsletters.c.filename.in_(filenames))
    existing_rows = await database.fetch_all(q)
    existing_filenames = {row["filename"] for row in existing_rows}

    optimized_results = []
    for filename in filenames:
        if filename in existing_filenames:
            optimized_results.append(filename)

    optimized_duration = time.perf_counter() - start_time
    print(f"Optimized bulk query duration: {optimized_duration:.4f} seconds")
    print(f"Found {len(optimized_results)} matching records.")

    # Verification
    assert set(n_plus_one_results) == set(optimized_results), "Results do not match!"
    print("\n✅ Verification PASSED: Both implementations returned identical results.")

    # Calculate improvement
    speedup = n_plus_one_duration / optimized_duration
    reduction = (1 - (optimized_duration / n_plus_one_duration)) * 100
    print(f"🚀 Speedup: {speedup:.2f}x faster")
    print(f"⚡ Time reduction: {reduction:.2f}%")

    await database.disconnect()


if __name__ == "__main__":
    asyncio.run(run_benchmark())
````

## File: backend/scripts/test_agent_bridge.py
````python
import sys
import os
import asyncio
import json
import datetime
from sqlalchemy import select

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.agent_bridge import notify_agent
from db.setup import database
from db.models import agent_notifications

async def main():
    print("Testing local agent bridge (Database Queue)...")
    await database.connect()
    
    try:
        # 1. Clean previous test notifications if any
        print("Cleaning up old test notifications...")
        await database.execute(
            agent_notifications.delete().where(
                agent_notifications.c.event_type.in_(["validation_alert", "review_request"])
            )
        )
            
        # 2. Add validation alert event
        print("Inserting validation alert...")
        await notify_agent("validation_alert", {
            "newsletter_id": 999,
            "filename": "invalid_newsletter.docx",
            "target_sunday": datetime.date(2026, 5, 24),
            "status": "failed_validation",
            "error_message": "Date mismatch: Expected 2026-05-24 but found 2026-05-17"
        })
        
        # 3. Add review request event
        print("Inserting review request...")
        await notify_agent("review_request", {
            "newsletter_id": 1000,
            "title": "4th Sunday of Easter Bulletin",
            "summary": "This is a warm test summary of parish events. Join us for Sunday Mass and our parish fundraising bake sale this weekend.",
            "target_sunday": datetime.date(2026, 5, 24),
            "status": "draft"
        })
        
        # 4. Verify database contents
        print("Verifying agent notifications in DB...")
        query = select(agent_notifications).where(
            agent_notifications.c.event_type.in_(["validation_alert", "review_request"])
        ).order_by(agent_notifications.c.created_at.asc())
        
        rows = await database.fetch_all(query)
        print(f"Loaded {len(rows)} notifications from database.")
        assert len(rows) == 2, f"Expected 2 events, got {len(rows)}"
        
        event1 = json.loads(rows[0]["payload"])
        event2 = json.loads(rows[1]["payload"])
        
        assert event1["type"] == "validation_alert", "First event type incorrect"
        assert event2["type"] == "review_request", "Second event type incorrect"
        assert "actions" in event2, "Review request event is missing actions URL"
        assert "approve_url" in event2["actions"], "Review request is missing approve_url"
        
        print("First event type: " + event1["type"])
        print("Second event type: " + event2["type"])
        print("Approve URL: " + event2["actions"]["approve_url"])
        
        # 5. Clean up
        print("Cleaning up test notifications...")
        await database.execute(
            agent_notifications.delete().where(
                agent_notifications.c.event_type.in_(["validation_alert", "review_request"])
            )
        )
        
        print("All local agent bridge database tests completed successfully!")
        
    except Exception as err:
        print(f"Error validating database agent bridge: {err}")
        sys.exit(1)
    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
````

## File: backend/scripts/test_pii_filtering.py
````python
import sys
import json
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from llm.providers import choose_llm_and_summarize, SANITIZATION_INSTRUCTION

TEST_TEXT = """
Holy Trinity Parish Newsletter - March 15, 2026

Dear Parishioners,
Please join us for our Bake Sale this Saturday, hosted by Mary Smith at her home on 123 Church Street. 
You can contact her at mary.smith@email.com or 555-0123 for details.

PRAYER REQUESTS:
Please pray for John Doe who is currently in the hospital recovering from heart surgery. 
Also, keep Jane Brown in your prayers as she deals with her ongoing battle with cancer.

ANNOUNCEMENTS:
The Youth Group and Father O'Reilly will lead the Stations of the Cross this Friday at 7 PM.
"""

def test_pii_filtering():
    print("=== PII/PHI Filtering Test ===")
    print("\n[Sanitization Instruction being used]:")
    print("-" * 40)
    print(SANITIZATION_INSTRUCTION)
    print("-" * 40)

    print("\n[Input Text containing PII/PHI]:")
    print(TEST_TEXT)

    print("\n[Running LLM Summarization...]")
    try:
        result = choose_llm_and_summarize(TEST_TEXT)
        print("\n[Resulting Summary]:")
        print(json.dumps(result, indent=2))
        
        # Simple check for obvious PII in the summary
        summary = result.get("summary", "").lower()
        title = result.get("title", "").lower()
        pii_found = []
        
        if "mary smith" in summary or "mary smith" in title: pii_found.append("Name (Mary Smith)")
        if "123 church street" in summary: pii_found.append("Address (123 Church Street)")
        if "555-0123" in summary: pii_found.append("Phone Number")
        if "mary.smith@email.com" in summary: pii_found.append("Email")
        if "john doe" in summary or "john doe" in title: pii_found.append("Name (John Doe)")
        if "heart surgery" in summary: pii_found.append("PHI (Heart Surgery)")
        if "jane brown" in summary: pii_found.append("Name (Jane Brown)")
        if "cancer" in summary: pii_found.append("PHI (Cancer)")

        if pii_found:
            print(f"\n[WARNING] Potential PII/PHI detected in output: {', '.join(pii_found)}")
        else:
            print("\n[SUCCESS] No obvious PII/PHI detected in the summary.")
            
    except Exception as e:
        print(f"\n[ERROR] Failed to run summarization: {e}")
        print("\nNote: Ensure Ollama is running if using strategy='local', or check your API keys.")

if __name__ == "__main__":
    test_pii_filtering()
````

## File: backend/tests/test_email_masking.py
````python
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from helpers.email import mask_email

def test_mask_email():
    test_cases = [
        # (input_email, expected_output)
        ("user@example.com", "u**r@example.com"),
        ("ab@example.com", "a*@example.com"),
        ("a@example.com", "*@example.com"),
        ("john.doe@gmail.com", "j******e@gmail.com"),
        ("admin@church.org", "a***n@church.org"),
        ("", ""),
        (None, None),
        ("invalid_email", "invalid_email"),
    ]

    print("=== Testing email masking logic ===")
    print(f"{'Input Email':<30} | {'Masked Email':<30} | {'Status':<10}")
    print("-" * 76)

    failed = False
    for input_email, expected in test_cases:
        try:
            result = mask_email(input_email)
            status = "PASS" if result == expected else "FAIL"
            print(f"{str(input_email):<30} | {str(result):<30} | {status:<10}")
            if result != expected:
                print(f"  [ERROR] Expected: '{expected}', got: '{result}'")
                failed = True
        except Exception as e:
            print(f"{str(input_email):<30} | ERROR: {str(e):<23} | FAIL")
            failed = True

    if failed:
        print("\n[FAIL] Some test cases did not pass.")
        assert False, "Some email masking test cases failed"
    else:
        print("\n[SUCCESS] All test cases passed successfully!")

if __name__ == "__main__":
    try:
        test_mask_email()
        sys.exit(0)
    except AssertionError:
        sys.exit(1)
````

## File: backend/tests/test_extraction.py
````python
import asyncio
import os
import sys
import pytest
from starlette.concurrency import run_in_threadpool

# Add backend directory to path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import sync_extract_text

PDF_PATH = "../test_newsletters/test.pdf"

@pytest.fixture
def anyio_backend():
    return 'asyncio'

def test_sync_extract_text_pdf():
    assert os.path.exists(PDF_PATH), f"PDF not found at {PDF_PATH}"
    with open(PDF_PATH, "rb") as f:
        pdf_bytes = f.read()

    # Run sync_extract_text directly (synchronously)
    text = sync_extract_text(pdf_bytes, "application/pdf")

    # Assertions
    assert isinstance(text, str)
    assert len(text) > 0
    # Let us print the first 100 characters to verify
    print(f"Extracted PDF text length: {len(text)}")
    print(f"Sample: {text[:100]}...")

@pytest.mark.anyio
async def test_async_extract_text_pdf_threadpool(anyio_backend):
    assert os.path.exists(PDF_PATH), f"PDF not found at {PDF_PATH}"
    with open(PDF_PATH, "rb") as f:
        pdf_bytes = f.read()

    # Run via threadpool
    text = await run_in_threadpool(sync_extract_text, pdf_bytes, "application/pdf")

    # Assertions
    assert isinstance(text, str)
    assert len(text) > 0
    print("Async threadpool test passed!")

if __name__ == "__main__":
    print("Running synchronous extraction test...")
    test_sync_extract_text_pdf()
    print("Running asynchronous threadpool extraction test...")
    asyncio.run(test_async_extract_text_pdf_threadpool('asyncio'))
    print("All functional tests passed successfully!")
````

## File: backend/tests/test_import.py
````python
import csv
import os
import sys

import pytest

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from db.models import subscribers
from db.setup import database
from scripts.import_gmail_contacts import import_contacts


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
async def cleanup_test_contacts():
    # Setup - make sure we connect to database
    if not database.is_connected:
        await database.connect()
    # Delete before test
    await database.execute(
        subscribers.delete().where(subscribers.c.email.like("test_import_%"))
    )
    yield
    # Cleanup after test
    await database.execute(
        subscribers.delete().where(subscribers.c.email.like("test_import_%"))
    )
    if database.is_connected:
        await database.disconnect()


@pytest.mark.anyio
async def test_bulk_import_and_upsert(anyio_backend, tmp_path):
    # 1. Create temporary CSV with some contacts
    csv_file = tmp_path / "contacts.csv"
    with open(csv_file, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["First Name", "Last Name", "E-mail 1 - Value", "Phone 1 - Value"]
        )
        writer.writerow(["John", "Doe", "test_import_john@example.com", "12345"])
        writer.writerow(["Jane", "Smith", "test_import_jane@example.com", "67890"])
        writer.writerow(["SkipInvalid", "", "invalid_email", ""])  # Should be ignored

    # 2. Run import (this will re-use the connected database state)
    await import_contacts(str(csv_file))

    # 3. Verify they were inserted
    query = (
        select(subscribers)
        .where(subscribers.c.email.like("test_import_%"))
        .order_by(subscribers.c.email)
    )
    results = await database.fetch_all(query)
    assert len(results) == 2

    contacts_map = {r["email"]: dict(r) for r in results}
    assert "test_import_john@example.com" in contacts_map
    assert "test_import_jane@example.com" in contacts_map

    assert contacts_map["test_import_john@example.com"]["first_name"] == "John"
    assert contacts_map["test_import_john@example.com"]["last_name"] == "Doe"
    assert contacts_map["test_import_john@example.com"]["phone"] == "12345"
    assert contacts_map["test_import_john@example.com"]["is_active"] is True

    # 4. Now perform an upsert update using a new CSV where we update John's phone number, Keep Jane's first_name/last_name using empty values (fallback testing)
    with open(csv_file, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["First Name", "Last Name", "E-mail 1 - Value", "Phone 1 - Value"]
        )
        # John updates last name and phone
        writer.writerow(["", "Doe-Updated", "test_import_john@example.com", "99999"])
        # Jane updates nothing (all other columns empty)
        writer.writerow(["", "", "test_import_jane@example.com", ""])

    # Run import_contacts again
    await import_contacts(str(csv_file))

    # 5. Verify the updates
    results_updated = await database.fetch_all(query)
    assert len(results_updated) == 2

    updated_map = {r["email"]: dict(r) for r in results_updated}

    # John's first_name should still be "John" (coalesced), last_name updated to "Doe-Updated", phone updated to "99999"
    assert updated_map["test_import_john@example.com"]["first_name"] == "John"
    assert updated_map["test_import_john@example.com"]["last_name"] == "Doe-Updated"
    assert updated_map["test_import_john@example.com"]["phone"] == "99999"

    # Jane's details should all remain exactly as they were (coalesced)
    assert updated_map["test_import_jane@example.com"]["first_name"] == "Jane"
    assert updated_map["test_import_jane@example.com"]["last_name"] == "Smith"
    assert updated_map["test_import_jane@example.com"]["phone"] == "67890"
````

## File: backend/tests/test_key_utils.py
````python
import pytest
from unittest.mock import Mock
from fastapi import Request, HTTPException
from helpers.key_utils import verify_api_key, settings

def create_mock_request(headers: dict):
    request = Mock(spec=Request)
    request.headers = headers
    return request

def test_verify_api_key_bearer_success():
    api_key = settings.api_key
    headers = {"Authorization": f"Bearer {api_key}"}
    request = create_mock_request(headers)

    # Should run without raising an exception
    verify_api_key(request)

def test_verify_api_key_x_api_key_success():
    api_key = settings.api_key
    headers = {"X-API-Key": api_key}
    request = create_mock_request(headers)

    # Should run without raising an exception
    verify_api_key(request)

def test_verify_api_key_missing_headers():
    headers = {}
    request = create_mock_request(headers)

    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Unauthorized"

def test_verify_api_key_invalid_bearer():
    headers = {"Authorization": "Bearer invalid_key"}
    request = create_mock_request(headers)

    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(request)
    assert exc_info.value.status_code == 401

def test_verify_api_key_invalid_x_api_key():
    headers = {"X-API-Key": "invalid_key"}
    request = create_mock_request(headers)

    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(request)
    assert exc_info.value.status_code == 401
````

## File: backend/tests/test_newsletters_auth.py
````python
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from main import app
from config import get_settings

client = TestClient(app)
settings = get_settings()

@patch("main.database.fetch_all", new_callable=AsyncMock)
def test_get_newsletters_unauthenticated(mock_fetch_all):
    response = client.get("/newsletters")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
    mock_fetch_all.assert_not_called()


@patch("main.database.fetch_all", new_callable=AsyncMock)
def test_get_newsletters_invalid_api_key(mock_fetch_all):
    response = client.get("/newsletters", headers={"X-API-Key": "invalid_key"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
    mock_fetch_all.assert_not_called()


@patch("main.database.fetch_all", new_callable=AsyncMock)
def test_get_newsletters_valid_x_api_key(mock_fetch_all):
    mock_fetch_all.return_value = []
    headers = {"X-API-Key": settings.api_key}
    response = client.get("/newsletters", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"newsletters": []}
    mock_fetch_all.assert_called_once()


@patch("main.database.fetch_all", new_callable=AsyncMock)
def test_get_newsletters_valid_bearer_token(mock_fetch_all):
    mock_fetch_all.return_value = []
    headers = {"Authorization": f"Bearer {settings.api_key}"}
    response = client.get("/newsletters", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"newsletters": []}
    mock_fetch_all.assert_called_once()
````

## File: backend/tests/test_sanitize.py
````python
from helpers.text_utils import sanitize_filename
import logging

# Set up logging to see warnings
logging.basicConfig(level=logging.INFO)

test_files = [
    "2nd Sunday of Advent - 8Dec2024_20241207_064550_0000.pdf",
    "_HTP Newsletter Sunday 15 Feb 2026 (1).pdf",
    "05.10.25.pdf",
    "1 Sept 2019 Newsletter.pdf",
    "29Sept2024-compressed.pdf",
    "NEWSLETTER Sunday 15th March 2025_20250315_162554_0000.pdf",
    "Holy Trinity Newsletter_01.12.24-3.pdf",
    "Holy Trinity Newsletter 6th April 2025.pdf",
    "FEAST of EPIPHANY - Sunday 5th January 2025.pdf",
    "Feb 1 2026 Newsletter.pdf",
    "NoDateFile.pdf"
]

print(f"{'Original Filename':<60} | {'Sanitized Filename':<40}")
print("-" * 105)
for f in test_files:
    sanitized = sanitize_filename(f)
    print(f"{f:<60} | {sanitized:<40}")
````

## File: backend/tests/test_subscribers.py
````python
import pytest
from main import BatchSubscribersRequest, batch_subscribe_users
from db.setup import database
from db.models import subscribers
from sqlalchemy import delete

@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"

@pytest.mark.anyio
async def test_batch_subscribe_endpoint(anyio_backend):
    # Connect database if not connected
    if not database.is_connected:
        await database.connect()

    try:
        # Clean up any prior test emails
        await database.execute(
            delete(subscribers).where(subscribers.c.email.like("%@subscriber-test.com"))
        )

        # 1. Insert a subscriber as inactive first so we can test reactivation
        await database.execute(
            subscribers.insert().values(email="inactive@subscriber-test.com", is_active=False)
        )
        # 2. Insert a subscriber as active so we can test skip/duplicate
        await database.execute(
            subscribers.insert().values(email="active@subscriber-test.com", is_active=True)
        )

        # Prepare test batch
        emails = [
            "  New@subscriber-test.com  ",    # Should be cleaned to "new@subscriber-test.com"
            "active@subscriber-test.com",      # Should be skipped
            "inactive@subscriber-test.com",    # Should be reactivated
            "invalid_email",                   # Should be skipped (no @)
            "new@subscriber-test.com",         # Duplicate in batch, should be skipped
        ]

        request_data = BatchSubscribersRequest(emails=emails)
        response = await batch_subscribe_users(request_data)

        # Verify response structure and correctness
        assert response.status_code == 200
        import json
        res_data = json.loads(response.body.decode())

        # 1 new added: new@subscriber-test.com
        # 1 reactivated: inactive@subscriber-test.com
        # 3 skipped: active@subscriber-test.com (duplicate), invalid_email (invalid), second new@subscriber-test.com (internal duplicate)
        assert res_data["added"] == 1
        assert res_data["reactivated"] == 1
        assert res_data["skipped"] == 3

    finally:
        # Clean up test emails
        await database.execute(
            delete(subscribers).where(subscribers.c.email.like("%@subscriber-test.com"))
        )
        await database.disconnect()
````

## File: backend/tests/test_xss.py
````python
import pytest
import html
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from main import app

client = TestClient(app)

@pytest.mark.asyncio
@patch("main.database.execute", new_callable=AsyncMock)
@patch("main.database.fetch_one", new_callable=AsyncMock)
async def test_approve_newsletter_summary_xss(mock_fetch_one, mock_execute):
    # Setup malicious XSS inputs
    malicious_filename = "<script>alert(\"XSS Filename\")</script>.pdf"
    malicious_target_sunday = "<img src=x onerror=alert(\"XSS Sunday\")>"

    # Mock database responses
    mock_fetch_one.return_value = {
        "filename": malicious_filename,
        "target_sunday": malicious_target_sunday
    }

    # Send request to approve endpoint
    # Note: We must not send 'accept: application/json' to get the HTMLResponse
    response = client.get("/newsletters/1/approve", headers={"accept": "text/html"})

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    html_content = response.text

    # Verify malicious inputs are escaped and NOT present in their raw form
    assert malicious_filename not in html_content
    assert malicious_target_sunday not in html_content

    # Verify the escaped entities are present instead
    assert html.escape(malicious_filename) in html_content
    assert html.escape(malicious_target_sunday) in html_content


@pytest.mark.asyncio
@patch("main.notify_agent", new_callable=AsyncMock)
@patch("main.choose_llm_and_summarize")
@patch("main.extract_text_from_file")
@patch("main.download_from_drive")
@patch("main.database.execute", new_callable=AsyncMock)
@patch("main.database.fetch_one", new_callable=AsyncMock)
async def test_regenerate_newsletter_summary_xss(
    mock_fetch_one, mock_execute, mock_download, mock_extract, mock_summarize, mock_notify
):
    # Setup malicious XSS inputs
    malicious_filename = "<script>alert(\"XSS Filename\")</script>.pdf"

    # Mock database / storage responses
    mock_fetch_one.return_value = {
        "drive_file_id": "mock_drive_id",
        "filename": malicious_filename,
        "target_sunday": "2026-02-15",
        "status": "draft"
    }
    mock_download.return_value = b"mock PDF content"
    mock_extract.return_value = "extracted newsletter text"
    mock_summarize.return_value = {
        "title": "Newsletter Title",
        "summary": "Newsletter Summary",
        "liturgical_season": "Ordinary Time",
        "calendar_year": "2026",
        "liturgical_year": "C"
    }

    # Send request to regenerate endpoint with html accept header
    response = client.get("/newsletters/1/regenerate", headers={"accept": "text/html"})

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    html_content = response.text

    # Verify malicious inputs are escaped and NOT present in their raw form
    assert malicious_filename not in html_content

    # Verify the escaped entities are present instead
    assert html.escape(malicious_filename) in html_content
````

## File: backend/benchmark_llm.py
````python
import asyncio
import time
import os
import sys
from starlette.concurrency import run_in_threadpool

# Add backend directory to path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# A simulated mock of choose_llm_and_summarize that blocks the thread for 1 second.
# This represents a slow API request or a retry-delay sleep (e.g., time.sleep(retry_delay))
def mock_choose_llm_and_summarize(text: str) -> dict:
    time.sleep(1.0)  # Simulates blocking I/O or sleep
    return {
        "title": "Simulated Newsletter Title",
        "summary": "This is a simulated summary.",
        "model": "mock-model",
        "tokens": 100,
        "cost_usd_estimate": 0.0
    }

async def simulate_other_event_loop_activity():
    """
    Simulates lightweight event-loop activity (like handling pings or health checks)
    by running a periodic async ping every 10ms. We measure the maximum latency of these pings.
    If the event loop is blocked, the ping latency will spike to the duration of the block!
    If the event loop is free, the ping latency will remain extremely low (< 15ms).
    """
    ping_latencies = []
    stop_event = asyncio.Event()

    async def ping_loop():
        while not stop_event.is_set():
            t0 = time.perf_counter()
            await asyncio.sleep(0.01)
            latency = (time.perf_counter() - t0 - 0.01) * 1000  # in ms
            ping_latencies.append(latency)

    ping_task = asyncio.create_task(ping_loop())
    return stop_event, ping_task, ping_latencies

async def run_sync_mock(text: str):
    """
    Simulates the blocking scenario where choose_llm_and_summarize
    runs directly on the async event loop thread.
    """
    stop_event, ping_task, latencies = await simulate_other_event_loop_activity()

    # Give the ping loop a moment to start
    await asyncio.sleep(0.02)

    start_time = time.perf_counter()
    # Synchronous call directly blocking the event loop thread
    result = mock_choose_llm_and_summarize(text)
    end_time = time.perf_counter()

    # Crucial: let the event loop run once so the blocked ping can resume and record its delay!
    await asyncio.sleep(0.02)

    stop_event.set()
    try:
        await ping_task
    except Exception:
        pass

    return end_time - start_time, result, max(latencies or [0]), sum(latencies or [0])/len(latencies or [1])

async def run_async_threadpool_mock(text: str):
    """
    Runs the choose_llm_and_summarize mock in a threadpool.
    """
    stop_event, ping_task, latencies = await simulate_other_event_loop_activity()

    # Give the ping loop a moment to start
    await asyncio.sleep(0.02)

    start_time = time.perf_counter()
    # Offloaded to threadpool, allowing the event loop to continue pings
    result = await run_in_threadpool(mock_choose_llm_and_summarize, text)
    end_time = time.perf_counter()

    # Let the event loop run once
    await asyncio.sleep(0.02)

    stop_event.set()
    try:
        await ping_task
    except Exception:
        pass

    return end_time - start_time, result, max(latencies or [0]), sum(latencies or [0])/len(latencies or [1])

async def main():
    text = "Some church newsletter text..."
    print("======================================================================")
    print("⚡ Running LLM Summarization Event Loop Block Benchmarks")
    print("======================================================================\n")

    # 1. Blocked Event Loop (Old Sync approach)
    print("1. Running old synchronous choose_llm_and_summarize (event loop blocked)...")
    sync_duration, _, sync_max_lat, sync_avg_lat = await run_sync_mock(text)
    print(f"   Done. Took {sync_duration:.4f} seconds.")
    print(f"   Max event loop delay: {sync_max_lat:.2f} ms | Avg delay: {sync_avg_lat:.2f} ms\n")

    # 2. Async Threadpool (New Optimized approach)
    print("2. Running optimized async threadpool choose_llm_and_summarize (event loop free)...")
    async_duration, _, async_max_lat, async_avg_lat = await run_async_threadpool_mock(text)
    print(f"   Done. Took {async_duration:.4f} seconds.")
    print(f"   Max event loop delay: {async_max_lat:.2f} ms | Avg delay: {async_avg_lat:.2f} ms\n")

    # Calculate Speedup and Responsiveness boost
    latency_reduction = (sync_max_lat - async_max_lat)
    latency_reduction_percent = (sync_max_lat / async_max_lat) if async_max_lat > 0 else 0

    print("======================================================================")
    print("📊 BENCHMARK RESULTS SUMMARY")
    print("======================================================================")
    print(f"{'Metric':<38} | {'Synchronous (Blocked)':<22} | {'Threadpool (Optimized)':<22}")
    print("-" * 88)
    print(f"{'Total execution time':<38} | {sync_duration:19.4f}s | {async_duration:19.4f}s")
    print(f"{'Worst-case event loop latency':<38} | {sync_max_lat:17.2f} ms | {async_max_lat:17.2f} ms")
    print(f"{'Average event loop latency':<38} | {sync_avg_lat:17.2f} ms | {async_avg_lat:17.2f} ms")
    print("-" * 88)
    print(f"{'Worst-case Event Loop Speedup':<38} | {'0.0% (Baseline)':<22} | {latency_reduction_percent:20.1f}x faster")
    print("======================================================================")
    print(f"💡 Explanation: Running blocking choose_llm_and_summarize inside a threadpool")
    print(f"   prevents event-loop starvation, allowing concurrent API requests (e.g.,")
    print(f"   health checks, dashboard pings) to respond {latency_reduction_percent:.1f}x faster")
    print(f"   under load, with maximum response lag reduced by {latency_reduction:.1f} ms!")
    print("======================================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
````

## File: frontend/app/docs/DocsTabs.tsx
````typescript
"use client";

import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import ArticleIcon from '@mui/icons-material/Article';
import HistoryIcon from '@mui/icons-material/History';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import Button from '@mui/material/Button';
import Link from 'next/link';

interface DocsTabsProps {
  adminGuide: string;
  changelog: string;
}

export default function DocsTabs({ adminGuide, changelog }: DocsTabsProps) {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f7', py: 6 }}>
      <Container maxWidth="md">
        
        {/* Back button and Title */}
        <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Link href="/" style={{ textDecoration: 'none' }}>
              <Button 
                variant="outlined" 
                startIcon={<ArrowBackIcon />}
                sx={{ borderRadius: '980px', textTransform: 'none', px: 2, borderColor: '#e0e0e0', color: '#1d1d1f', '&:hover': { borderColor: '#86868b', bgcolor: 'rgba(0,0,0,0.02)' } }}
              >
                Back
              </Button>
            </Link>
            <Typography variant="h4" fontWeight={800} sx={{ letterSpacing: '-0.02em', color: '#1d1d1f' }}>
              Documentation Center
            </Typography>
          </Box>
          
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange} 
            sx={{
              '& .MuiTabs-indicator': { bgcolor: '#0071e3' },
              '& .MuiTab-root': { textTransform: 'none', fontWeight: 600, fontSize: '0.95rem' },
              '& .Mui-selected': { color: '#0071e3 !important' }
            }}
          >
            <Tab icon={<ArticleIcon sx={{ fontSize: 18 }} />} iconPosition="start" label="Admin Manual" />
            <Tab icon={<HistoryIcon sx={{ fontSize: 18 }} />} iconPosition="start" label="Changelog" />
          </Tabs>
        </Box>

        {/* Document Render Paper */}
        <Paper sx={{ p: { xs: 3, md: 6 }, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.02)', border: '1px solid #e0e0e0', bgcolor: 'white' }}>
          {activeTab === 0 ? (
            <MarkdownRenderer content={adminGuide} />
          ) : (
            <MarkdownRenderer content={changelog} />
          )}
        </Paper>

      </Container>
    </Box>
  );
}

interface MarkdownRendererProps {
  content: string;
}

function MarkdownRenderer({ content }: MarkdownRendererProps) {
  const lines = content.split('\n');
  const renderedElements: React.ReactNode[] = [];
  let currentList: React.ReactNode[] = [];
  let listType: 'ol' | 'ul' | null = null;
  let inCodeBlock = false;
  let codeLines: string[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Handle code blocks
    if (line.trim().startsWith('```')) {
      if (inCodeBlock) {
        renderedElements.push(
          <Box
            key={`code-${i}`}
            component="pre"
            sx={{
              p: 2.5,
              bgcolor: '#f5f5f7',
              borderRadius: 3,
              overflowX: 'auto',
              fontFamily: 'SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace',
              fontSize: '0.85rem',
              border: '1px solid #e3e3e8',
              my: 3.5,
              color: '#1d1d1f',
              lineHeight: 1.5
            }}
          >
            {codeLines.join('\n')}
          </Box>
        );
        codeLines = [];
        inCodeBlock = false;
      } else {
        inCodeBlock = true;
      }
      continue;
    }

    if (inCodeBlock) {
      codeLines.push(line);
      continue;
    }

    // Process lists (flushing them if the line is not a list item)
    const isUnordered = line.trim().startsWith('- ') || line.trim().startsWith('* ');
    const isOrdered = /^\d+\.\s/.test(line.trim());

    if (isUnordered || isOrdered) {
      const type = isUnordered ? 'ul' : 'ol';
      const cleanLine = isUnordered 
        ? line.trim().substring(2) 
        : line.trim().replace(/^\d+\.\s/, '');

      if (listType && listType !== type) {
        renderedElements.push(
          listType === 'ul' 
            ? <Box component="ul" key={`list-ul-${i}`} sx={{ pl: 3.5, my: 2, color: '#333333' }}>{currentList}</Box>
            : <Box component="ol" key={`list-ol-${i}`} sx={{ pl: 3.5, my: 2, color: '#333333' }}>{currentList}</Box>
        );
        currentList = [];
      }

      listType = type;
      currentList.push(
        <Box component="li" key={`item-${i}`} sx={{ mb: 1, lineHeight: 1.6, fontSize: '1.05rem' }}>
          {parseInlineMarkdown(cleanLine)}
        </Box>
      );
      continue;
    } else if (listType) {
      renderedElements.push(
        listType === 'ul' 
          ? <Box component="ul" key={`list-ul-${i}`} sx={{ pl: 3.5, my: 2, color: '#333333' }}>{currentList}</Box>
          : <Box component="ol" key={`list-ol-${i}`} sx={{ pl: 3.5, my: 2, color: '#333333' }}>{currentList}</Box>
      );
      currentList = [];
      listType = null;
    }

    // Handle horizontal rules
    if (line.trim() === '---') {
      renderedElements.push(<Divider key={`div-${i}`} sx={{ my: 4, borderColor: '#e0e0e0' }} />);
      continue;
    }

    // Handle headers
    if (line.startsWith('# ')) {
      renderedElements.push(
        <Typography variant="h4" key={`h1-${i}`} sx={{ fontWeight: 800, mt: 4, mb: 2.5, letterSpacing: '-0.03em', color: '#1d1d1f' }}>
          {parseInlineMarkdown(line.substring(2))}
        </Typography>
      );
    } else if (line.startsWith('## ')) {
      renderedElements.push(
        <Typography variant="h5" key={`h2-${i}`} sx={{ fontWeight: 700, mt: 4, mb: 2, letterSpacing: '-0.02em', color: '#1d1d1f' }}>
          {parseInlineMarkdown(line.substring(3))}
        </Typography>
      );
    } else if (line.startsWith('### ')) {
      renderedElements.push(
        <Typography variant="h6" key={`h3-${i}`} sx={{ fontWeight: 650, mt: 3, mb: 1.5, color: '#1d1d1f', letterSpacing: '-0.01em' }}>
          {parseInlineMarkdown(line.substring(4))}
        </Typography>
      );
    } else if (line.trim() === '') {
      renderedElements.push(<Box key={`space-${i}`} sx={{ height: 12 }} />);
    } else {
      renderedElements.push(
        <Typography variant="body1" key={`p-${i}`} sx={{ mb: 2, lineHeight: 1.65, fontSize: '1.05rem', color: '#333333' }}>
          {parseInlineMarkdown(line)}
        </Typography>
      );
    }
  }

  if (listType) {
    renderedElements.push(
      listType === 'ul' 
        ? <Box component="ul" key={`list-ul-final`} sx={{ pl: 3.5, my: 2, color: '#333333' }}>{currentList}</Box>
        : <Box component="ol" key={`list-ol-final`} sx={{ pl: 3.5, my: 2, color: '#333333' }}>{currentList}</Box>
    );
  }

  return <Box>{renderedElements}</Box>;
}

function parseInlineMarkdown(text: string): React.ReactNode[] {
  const parts: React.ReactNode[] = [];
  const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
  let match;
  let lastIndex = 0;
  
  const linkMatches: { text: string; url: string; start: number; end: number }[] = [];
  while ((match = linkRegex.exec(text)) !== null) {
    linkMatches.push({
      text: match[1],
      url: match[2],
      start: match.index,
      end: linkRegex.lastIndex
    });
  }
  
  const parseBold = (str: string, keyPrefix: string): React.ReactNode[] => {
    const boldParts: React.ReactNode[] = [];
    const boldRegex = /\*\*([^*]+)\*\*/g;
    let boldMatch;
    let boldLastIndex = 0;
    let subIdx = 0;
    
    while ((boldMatch = boldRegex.exec(str)) !== null) {
      if (boldMatch.index > boldLastIndex) {
        boldParts.push(str.substring(boldLastIndex, boldMatch.index));
      }
      boldParts.push(<strong key={`${keyPrefix}-bold-${subIdx++}`} style={{ fontWeight: 700, color: '#1d1d1f' }}>{boldMatch[1]}</strong>);
      boldLastIndex = boldRegex.lastIndex;
    }
    if (boldLastIndex < str.length) {
      boldParts.push(str.substring(boldLastIndex));
    }
    return boldParts;
  };
  
  if (linkMatches.length === 0) {
    return parseBold(text, 'text');
  }
  
  linkMatches.forEach((link, idx) => {
    if (link.start > lastIndex) {
      parts.push(...parseBold(text.substring(lastIndex, link.start), `link-pre-${idx}`));
    }
    parts.push(
      <a href={link.url} key={`link-${idx}`} style={{ color: '#0071e3', textDecoration: 'none', fontWeight: 500 }} target={link.url.startsWith('http') ? '_blank' : undefined} rel={link.url.startsWith('http') ? 'noopener noreferrer' : undefined}>
        {link.text}
      </a>
    );
    lastIndex = link.end;
  });
  
  if (lastIndex < text.length) {
    parts.push(...parseBold(text.substring(lastIndex), 'link-post'));
  }
  
  return parts;
}
````

## File: frontend/docs/CHANGELOG.md
````markdown
# SALLTO Herald — Changelog

All notable changes to the SALLTO Herald platform are documented in this file.

---

## [0.2.0] — 2026-07-25
### Added
- **Clerk Authentication Migration**: Swapped the entire authentication engine from Stack Auth to Clerk to align with core SaaS stack frameworks.
- **Premium Rounded Favicons**: Generated circular squircle web, Apple Touch, PWA manifest, and tab favicon files from custom user graphics.
- **Ignored Build Steps**: Added Vercel build-minute optimization scripts targeting only production branches.
- **Dynamic Documents Center**: Integrated frontend docs directory to render user manuals and version changelogs natively.

### Changed
- **Unified State Console**: Extracted component rendering state into modular components for strict Next.js static rendering compliance.
- **Root Git Ignore**: Optimized workspace tracking to isolate root-level dependency node folders and developer credential profiles.

---

## [0.1.1] — 2026-07-20
### Added
- **Concurrently Root Runner**: Configured cross-directory runner scripts to boot frontend and backend environments simultaneously with a single command.
- **Google CSV Subscriber Import**: Implemented parsing utilities that automatically extract contacts from Google Contacts export structures and sync them to PostgreSQL.

### Fixed
- **Name Parsing Logic**: Corrected layout mapping issues during contact ingestion when importing users with missing phone details or compound last names.

---

## [0.1.0] — 2026-06-12
### Added
- **FastAPI Core Processor**: Configured document extraction routes using PyMuPDF and Llama 3.1 70B summaries.
- **Liturgical Auditing Log**: Implemented state-machine validators for liturgical season calendar tracking and database ingestion error reporting.
- **Human-in-the-Loop Dialog**: Developed override controls allowing admins to edit failed metadata, bypass delivery queues, and execute direct archiving.
````

## File: frontend/public/icon.svg
````xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <defs>
    <!-- Premium Gold Gradient -->
    <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFE082" />
      <stop offset="30%" stop-color="#FFD54F" />
      <stop offset="70%" stop-color="#FFB300" />
      <stop offset="100%" stop-color="#FF8F00" />
    </linearGradient>
    <!-- Background Gradient -->
    <linearGradient id="bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1E1E24" />
      <stop offset="100%" stop-color="#0E0E11" />
    </linearGradient>
  </defs>
  
  <!-- Rounded Square Background -->
  <rect width="512" height="512" rx="128" fill="url(#bg)" />
  
  <!-- Gold Heraldic Trumpet -->
  <g transform="translate(256, 256) rotate(-45) translate(-256, -256)">
    <!-- Mouthpiece -->
    <rect x="70" y="240" width="12" height="32" rx="4" fill="url(#gold)" />
    <!-- Leadpipe -->
    <rect x="82" y="248" width="220" height="16" fill="url(#gold)" />
    <!-- Bell Flare -->
    <path d="M 302 248 
             L 410 210 
             A 12 60 0 0 1 410 302 
             L 302 264 
             Z" fill="url(#gold)" />
    <!-- Bell Rim / Lip -->
    <ellipse cx="410" cy="256" rx="8" ry="46" fill="url(#gold)" />
    <!-- Connecting brace/detail -->
    <rect x="180" y="236" width="6" height="40" rx="2" fill="url(#gold)" opacity="0.8" />
  </g>
</svg>
````

## File: frontend/public/site.webmanifest
````
{
  "name": "Herald - Church Newsletter Summaries",
  "short_name": "Herald",
  "icons": [
    {
      "src": "/favicon-96x96.png",
      "sizes": "96x96",
      "type": "image/png"
    },
    {
      "src": "/apple-touch-icon.png",
      "sizes": "180x180",
      "type": "image/png"
    }
  ],
  "theme_color": "#0071e3",
  "background_color": "#121214",
  "display": "standalone"
}
````

## File: frontend/package.json
````json
{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev --webpack",
    "build": "next build --webpack",
    "start": "next start --webpack",
    "lint": "eslint"
  },
  "dependencies": {
    "@clerk/nextjs": "^7.6.1",
    "@emotion/cache": "^11.14.0",
    "@emotion/react": "^11.14.0",
    "@emotion/styled": "^11.14.1",
    "@mui/icons-material": "^7.3.9",
    "@mui/material": "^7.3.9",
    "@mui/material-nextjs": "^7.3.9",
    "next": "16.1.6",
    "react": "19.2.3",
    "react-dom": "19.2.3"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "eslint": "^9",
    "eslint-config-next": "16.1.6",
    "tailwindcss": "^4",
    "typescript": "^5"
  }
}
````

## File: frontend/proxy.ts
````typescript
import { clerkMiddleware } from "@clerk/nextjs/server";

export default clerkMiddleware();

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.[\\w]+$|_next/image|favicon.ico|site.webmanifest).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
};
````

## File: studio-newsletter-herald/schemaTypes/index.ts
````typescript
import {newsletterEdition} from './newsletterEdition'
import {theme} from './theme'
import {editorialWorkflow} from './editorialWorkflow'
import {delivery} from './delivery'

export const schemaTypes = [
  newsletterEdition,
  theme,
  editorialWorkflow,
  delivery,
]
````

## File: studio-newsletter-herald/static/.gitkeep
````
Files placed here will be served by the Sanity server under the `/static`-prefix
````

## File: studio-newsletter-herald/.gitignore
````
# See https://help.github.com/articles/ignoring-files/ for more about ignoring files.

# Dependencies
/node_modules
/.pnp
.pnp.js

# Compiled Sanity Studio
/dist

# Temporary Sanity runtime, generated by the CLI on every dev server start
/.sanity

# Logs
/logs
*.log

# Coverage directory used by testing tools
/coverage

# Misc
.DS_Store
*.pem

# Typescript
*.tsbuildinfo

# Dotenv and similar local-only files
*.local
````

## File: studio-newsletter-herald/eslint.config.mjs
````javascript
import studio from '@sanity/eslint-config-studio'

export default [...studio]
````

## File: studio-newsletter-herald/package.json
````json
{
  "name": "newsletter-herald",
  "private": true,
  "version": "1.0.0",
  "main": "package.json",
  "license": "UNLICENSED",
  "scripts": {
    "build": "sanity build",
    "deploy": "sanity deploy",
    "deploy-graphql": "sanity graphql deploy",
    "dev": "sanity dev",
    "start": "sanity start"
  },
  "keywords": [
    "sanity"
  ],
  "dependencies": {
    "@sanity/vision": "^6.16.0",
    "react": "^19.2.4",
    "react-dom": "^19.2.4",
    "sanity": "^6.16.0",
    "styled-components": "^6.1.18"
  },
  "devDependencies": {
    "@sanity/eslint-config-studio": "^7",
    "@types/react": "^19.2.14",
    "eslint": "^10.8.1",
    "prettier": "^3.5",
    "typescript": "^5.8"
  },
  "prettier": {
    "bracketSpacing": false,
    "printWidth": 100,
    "semi": false,
    "singleQuote": true
  }
}
````

## File: studio-newsletter-herald/README.md
````markdown
# Sanity Clean Content Studio

Congratulations, you have now installed the Sanity Content Studio, an open-source real-time content editing environment connected to the Sanity backend.

Now you can do the following things:

- [Read “getting started” in the docs](https://www.sanity.io/docs/introduction/getting-started?utm_source=readme)
- [Join the Sanity community](https://www.sanity.io/community/join?utm_source=readme)
- [Extend and build plugins](https://www.sanity.io/docs/content-studio/extending?utm_source=readme)
````

## File: studio-newsletter-herald/sanity.cli.ts
````typescript
import {defineCliConfig} from 'sanity/cli'

export default defineCliConfig({
  api: {
    projectId: 'qbl0snjp',
    dataset: 'production'
  },
  deployment: {
    /**
     * Enable auto-updates for studios.
     * Learn more at https://www.sanity.io/docs/studio/latest-version-of-sanity#k47faf43faf56
     */
    autoUpdates: true,
  },
})
````

## File: studio-newsletter-herald/sanity.config.ts
````typescript
import {defineConfig} from 'sanity'
import {structureTool} from 'sanity/structure'
import {visionTool} from '@sanity/vision'
import {schemaTypes} from './schemaTypes'

export default defineConfig({
  name: 'default',
  title: 'Newsletter Herald',

  projectId: 'qbl0snjp',
  dataset: 'production',

  plugins: [structureTool(), visionTool()],

  schema: {
    types: schemaTypes,
  },
})
````

## File: studio-newsletter-herald/tsconfig.json
````json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "module": "Preserve",
    "moduleDetection": "force",
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true
  },
  "include": ["**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
````

## File: Dockerfile
````dockerfile
# Multi-stage lightweight Dockerfile for Newsletter Herald on GCP Cloud Run
FROM python:3.11-slim as builder

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production image
FROM python:3.11-slim

WORKDIR /app

# Copy installed python packages from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /usr/lib /usr/lib

# Ensure local bin is in PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Copy application source code
COPY backend/ /app/backend/
COPY main.py /app/main.py

EXPOSE 8080

# Run Uvicorn listening on $PORT (injected dynamically by GCP Cloud Run)
CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT
````

## File: main.py
````python
import sys
import os

# Add backend directory to sys.path so imports resolve seamlessly
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from backend.main import app

__all__ = ["app"]
````

## File: README.md
````markdown
# Newsletter Herald

An automated pipeline for summarizing Roman Catholic church newsletters into warm, concise email messages for parishioners.

## Project Overview

Newsletter Herald is a full-stack application that automates the extraction, summarization, and management of church newsletters. It features a robust FastAPI backend for document processing and an interactive Next.js frontend for visualization and management.

### Key Features
- **Intelligent Summarization**: Integrated with dual LLM providers:
  - **Local**: Ollama (Llama 3.1 8B for local history seeding to prevent rate limits).
  - **Remote**: Groq Cloud (Llama 3.1 70B for fast runtime summaries).
- **Hybrid Storage & Sync**: Uses Cloudflare R2 for file storage and Google Drive for backups.
- **Subscriber Directory Sync**: Synchronizes Gmail CSV contacts into PostgreSQL with advanced name/phone mapping.
- **Human-in-the-Loop Override**: Features interactive metadata validation failure overrides and selective email dispatch queue bypassing ("Archive Only").
- **Secure Admin Controls**: Access locked down with Clerk Auth and whitelist restrictions.

## Repository Structure

- **`backend/`**: FastAPI service handling OCR, LLM orchestration, database management, and cloud storage.
- **`frontend/`**: Next.js application for users to view summaries and manage newsletters.
- **`newsletters_to_upload/`**: Local staging directory for batch newsletter processing. only needed for a one time upload of all newsletters.

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.ai/) (for local LLM processing)
- PostgreSQL (Neon.tech recommended)

### Quick Start

Run both services with a single command from the root:
```bash
npm start
```
*Note: This uses `concurrently` to run the FastAPI backend and Next.js frontend simultaneously.*

### Manual Setup

1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env  # Fill in your API keys
   uvicorn main:app --reload
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Batch Processing**:
   Place newsletters in `newsletters_to_upload/` and run:
   ```bash
   python backend/scripts/upload_local_files.py
   ```

## LLM Strategy

The project supports a flexible LLM strategy configured via `.env`:
- `local`: Forces usage of local Ollama (Llama 3.1).
- `groq`: Forces high-speed Groq API.
- `auto`: Automatically routes queries based on document availability.

## License
[MIT](LICENSE)
````

## File: backend/db/models.py
````python
from sqlalchemy import (
    Table, Column, Integer, String, Boolean, Date, DateTime,
    Float, Text, ForeignKey
)
from sqlalchemy.sql import func
from db.setup import metadata

newsletters = Table(
    "newsletters",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("filename", String),
    Column("drive_file_id", String, nullable=True),
    Column("drive_web_view_link", String, nullable=True),
    Column("thumbnail_drive_id", String, nullable=True),
    Column("uploader", String),
    Column("uploaded_at", DateTime(timezone=True), server_default=func.now()),
    Column("schedule_date", Date, nullable=True),
    Column("tags", Text, nullable=True),
    Column("delivered", Boolean, default=False),
    Column("status", String, default="draft"),
    Column("target_sunday", Date, nullable=True),
    Column("scheduled_at", DateTime(timezone=True), nullable=True),
)

summaries = Table(
    "summaries",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("newsletter_id", Integer, ForeignKey("newsletters.id"), unique=True),
    Column("title", String, nullable=True),
    Column("summary", Text),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

model_usage = Table(
    "model_usage",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("summary_id", Integer, ForeignKey("summaries.id")),
    Column("model", String),
    Column("tokens", Integer),
    Column("cost_usd_estimate", Float),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

subscribers = Table(
    "subscribers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, unique=True, index=True, nullable=False),
    Column("first_name", String, nullable=True),
    Column("last_name", String, nullable=True),
    Column("phone", String, nullable=True),
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

delivery_logs = Table(
    "delivery_logs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("newsletter_id", Integer, ForeignKey("newsletters.id")),
    Column("recipient", String, nullable=False),
    Column("status", String, nullable=False),
    Column("error_message", Text, nullable=True),
    Column("timestamp", DateTime(timezone=True), server_default=func.now()),
)

agent_notifications = Table(
    "agent_notifications",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("event_type", String, nullable=False),
    Column("payload", Text, nullable=False), # JSON payload
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

upload_logs = Table(
    "upload_logs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("filename", String, nullable=False),
    Column("uploader", String, nullable=False),
    Column("status", String, nullable=False), # "success", "failed"
    Column("error_message", Text, nullable=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)
````

## File: backend/helpers/text_utils.py
````python
import fitz
import docx
import tiktoken
import logging
import os
import io
import re
import datetime
from typing import Union, BinaryIO, Optional, IO

# Create a logger for this module
logger = logging.getLogger(__name__)

# Common month names mapping for date extraction
MONTHS_MAP = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

# Pre-compiled regular expression patterns for date extraction from filenames (ordered by specificity)
FILENAME_DATE_PATTERNS = [
    # DD Month YYYY (e.g., 15 Feb 2026, 8Dec2024, 15th March 2025)
    re.compile(r'(\d{1,2})(?:st|nd|rd|th)?\s*([A-Za-z]{3,})\s*(\d{4})', re.IGNORECASE),
    # Month DD YYYY (e.g., Feb 1 2026)
    re.compile(r'([A-Za-z]{3,})\s*(\d{1,2})(?:st|nd|rd|th)?\s*(\d{4})', re.IGNORECASE),
    # DD.MM.YY or DD.MM.YYYY
    re.compile(r'(\d{1,2})[._/](\d{1,2})[._/](\d{2,4})', re.IGNORECASE),
]


def sanitize_filename(filename: str) -> str:
    """
    Standardizes and sanitizes a filename by extracting a date from it.
    Format: YYYY-MM-DD-SALLTO-Newsletter.pdf
    """
    _, ext = os.path.splitext(filename)
    
    found_date = None
    
    for i, pattern in enumerate(FILENAME_DATE_PATTERNS):
        match = pattern.search(filename)
        if match:
            try:
                if i == 0: # DD Month YYYY
                    day = int(match.group(1))
                    month_str = match.group(2)[:3].lower()
                    year = int(match.group(3))
                    if month_str in MONTHS_MAP:
                        found_date = datetime.date(year, MONTHS_MAP[month_str], day)
                elif i == 1: # Month DD YYYY
                    month_str = match.group(1)[:3].lower()
                    day = int(match.group(2))
                    year = int(match.group(3))
                    if month_str in MONTHS_MAP:
                        found_date = datetime.date(year, MONTHS_MAP[month_str], day)
                elif i == 2: # DD.MM.YY
                    day = int(match.group(1))
                    month = int(match.group(2))
                    year = int(match.group(3))
                    if year < 100:
                        year += 2000
                    found_date = datetime.date(year, month, day)
                
                if found_date:
                    break
            except Exception as e:
                logger.debug(f"Failed to parse date with pattern {pattern.pattern}: {e}")
                continue

    if not found_date:
        # Fallback to today if no date found in filename
        found_date = datetime.date.today()
        logger.warning(f"No date found in filename '{filename}', falling back to {found_date}")
    
    date_str = found_date.strftime('%Y-%m-%d')
    return f"{date_str}-Trinity-Newsletter{ext.lower()}"

def compress_pdf(pdf_bytes: bytes) -> bytes:
    """
    Compresses a PDF to save space while keeping it looking good.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        out_stream = io.BytesIO()
        # garbage=4: remove unused objects, compact xref, etc.
        # deflate=True: compress streams
        doc.save(out_stream, garbage=4, deflate=True, clean=True)
        compressed = out_stream.getvalue()
        doc.close()
        
        orig_size = len(pdf_bytes)
        comp_size = len(compressed)
        reduction = (1 - comp_size / orig_size) * 100 if orig_size > 0 else 0
        logger.info(f"PDF compressed: {orig_size/1024:.1f}KB -> {comp_size/1024:.1f}KB ({reduction:.1f}% reduction)")
        
        return compressed
    except Exception as e:
        logger.error(f"Error compressing PDF: {e}")
        return pdf_bytes

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Estimate token count for a given string and model.
    """
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))


def extract_text_from_file(file: Union[str, BinaryIO, IO], file_type: Optional[str] = None) -> str:
    """
    Extract text from a file. Supports PDF and DOCX formats.
    """
    if file_type is None:
        if isinstance(file, str):
            _, ext = os.path.splitext(file)
            file_type = ext.lower().lstrip('.')
        else:
            raise ValueError("file_type must be specified when file is not a path string")
    
    if file_type == 'pdf':
        return extract_text_from_pdf(file)
    elif file_type == 'docx':
        return extract_text_from_docx(file)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def extract_text_from_pdf(file: Union[str, BinaryIO, IO]) -> str:
    """
    Extract text from a PDF file.
    """
    try:
        text = ""
        if isinstance(file, (str, bytes)):
            doc = fitz.open(file)
        else:
            # Handle BytesIO or file stream
            doc = fitz.open(stream=file.read(), filetype="pdf")
            
        with doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        error_msg = f"Error extracting text from PDF: {str(e)}"
        logger.error(error_msg)
        raise IOError(error_msg)


def extract_text_from_docx(file: Union[str, BinaryIO, IO]) -> str:
    """
    Extract text from a DOCX file.
    """
    try:
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        error_msg = f"Error extracting text from DOCX: {str(e)}"
        logger.error(error_msg)
        raise IOError(error_msg)

def generate_pdf_thumbnail(file: Union[str, BinaryIO, IO]) -> bytes:
    """
    Generates a PNG image of the first page of a PDF.
    """
    try:
        if isinstance(file, (str, bytes)):
            doc = fitz.open(file)
        else:
            file.seek(0)
            doc = fitz.open(stream=file.read(), filetype="pdf")
            
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_data = pix.tobytes("png")
        doc.close()
        return img_data
    except Exception as e:
        logger.error(f"Error generating PDF thumbnail: {e}")
        raise
````

## File: backend/scripts/delivery_worker.py
````python
import asyncio
import logging
import datetime
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, and_, or_
from db.setup import database
from db.models import newsletters, summaries, subscribers, delivery_logs
from helpers.email import send_newsletter_email
from helpers.agent_bridge import notify_agent
from config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("delivery_worker")
settings = get_settings()

async def check_and_deliver():
    """
    Checks the database for newsletters scheduled for today or custom date/time,
    and sends them to all active subscribers.
    """
    try:
        await database.connect()
        logger.info("Connected to database for delivery check")

        now = datetime.datetime.now(datetime.timezone.utc)
        today = datetime.date.today()
        logger.info(f"Checking for newsletters scheduled at/before: {now} (or target Sunday <= {today})")

        # Fetch newsletters that are scheduled and not yet delivered
        query = select(
            newsletters.c.id,
            summaries.c.title,
            summaries.c.summary
        ).select_from(
            newsletters.join(summaries, newsletters.c.id == summaries.c.newsletter_id)
        ).where(
            and_(
                newsletters.c.status == "scheduled",
                newsletters.c.delivered == False,
                or_(
                    and_(newsletters.c.scheduled_at != None, newsletters.c.scheduled_at <= now),
                    and_(newsletters.c.scheduled_at == None, newsletters.c.target_sunday <= today)
                )
            )
        )

        pending = await database.fetch_all(query)
        logger.info(f"Found {len(pending)} newsletters pending delivery")

        if not pending:
            logger.info("No newsletters scheduled for delivery today.")
            return

        # Fetch active subscribers
        sub_query = select(subscribers.c.email).where(subscribers.c.is_active == True)
        active_subs = await database.fetch_all(sub_query)
        logger.info(f"Retrieved {len(active_subs)} active subscribers")

        if not active_subs:
            logger.warning("No active subscribers found in database. Aborting delivery.")
            return

        for item in pending:
            logger.info(f"Delivering newsletter {item['id']}: {item['title']}")
            
            sent_count = 0
            failed_count = 0
            
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
            
            # Create a Semaphore to limit the number of concurrent email deliveries (e.g. max 10 concurrent requests)
            # This is critical to avoid SMTP socket rate limits, Google/SendGrid connection drops, or thread starvation.
            semaphore = asyncio.Semaphore(10)

            async def deliver_to_subscriber(sub):
                async with semaphore:
                    recipient = sub['email']
                    try:
                        # send_newsletter_email is synchronous, so we offload it to a worker thread
                        success = await asyncio.to_thread(
                            send_newsletter_email,
                            to_email=recipient,
                            subject=item['title'],
                            html_content=html_content
                        )
                    except Exception as email_err:
                        logger.error(f"Error executing email send to {recipient} in thread: {email_err}")
                        success = False
                    return recipient, success

            # Initiate all subscriber delivery tasks concurrently
            tasks = [deliver_to_subscriber(sub) for sub in active_subs]
            results = await asyncio.gather(*tasks)

            # Collect results and prepare bulk insert for logs
            log_values = []
            for recipient, success in results:
                status = "sent" if success else "failed"
                err_msg = None if success else "SMTP delivery failure"
                
                log_values.append({
                    "newsletter_id": item['id'],
                    "recipient": recipient,
                    "status": status,
                    "error_message": err_msg
                })
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1

            # Bulk insert delivery logs using databases.execute_many to avoid N+1 DB round-trips
            if log_values:
                await database.execute_many(
                    query=delivery_logs.insert(),
                    values=log_values
                )

            # Mark newsletter as delivered
            update_query = newsletters.update().where(newsletters.c.id == item['id']).values(
                delivered=True,
                status="delivered"
            )
            await database.execute(update_query)
            logger.info(f"Newsletter {item['id']} delivery run complete. Sent: {sent_count}, Failed: {failed_count}")
            
            # Send notification report to local agent queue
            await notify_agent("delivery_report", {
                "id": item['id'],
                "title": item['title'],
                "sent_count": sent_count,
                "failed_count": failed_count
            })

    except Exception as e:
        logger.error(f"Error in delivery worker: {e}", exc_info=True)
    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(check_and_deliver())
````

## File: backend/scripts/import_gmail_contacts.py
````python
import asyncio
import csv
import os
import sys

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as pg_insert

from db.models import subscribers
from db.setup import database


async def import_contacts(csv_path: str = r"C:\Users\CBCGaming\Downloads\contacts.csv"):
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    print(f"Reading contacts from: {csv_path}")
    was_connected = database.is_connected
    if not was_connected:
        await database.connect()
    try:
        with open(csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            values_to_insert = []
            seen_emails = set()

            for row in reader:
                email = row.get("E-mail 1 - Value", "").strip().lower()
                if not email or "@" not in email:
                    continue

                # Prevent duplicate entries within the same CSV file
                if email in seen_emails:
                    continue
                seen_emails.add(email)

                first_name = row.get("First Name", "").strip() or None
                last_name = row.get("Last Name", "").strip() or None
                phone = row.get("Phone 1 - Value", "").strip() or None

                values_to_insert.append(
                    {
                        "email": email,
                        "first_name": first_name,
                        "last_name": last_name,
                        "phone": phone,
                        "is_active": True,
                    }
                )

            if not values_to_insert:
                print("No valid contacts found in CSV.")
                return

            print(
                f"Loaded {len(values_to_insert)} unique contacts. Bulk importing to database..."
            )

            # Use PostgreSQL bulk upsert (INSERT ... ON CONFLICT DO UPDATE)
            # COALESCE ensures we preserve existing data if the CSV row has a null/empty value for a column.
            stmt = pg_insert(subscribers)
            stmt = stmt.on_conflict_do_update(
                index_elements=["email"],
                set_={
                    "first_name": func.coalesce(
                        stmt.excluded.first_name, subscribers.c.first_name
                    ),
                    "last_name": func.coalesce(
                        stmt.excluded.last_name, subscribers.c.last_name
                    ),
                    "phone": func.coalesce(stmt.excluded.phone, subscribers.c.phone),
                    "is_active": True,
                },
            )

            await database.execute_many(stmt, values_to_insert)
            print(f"Successfully processed {len(values_to_insert)} subscribers!")
    except Exception as e:
        print(f"Error importing contacts: {e}")
    finally:
        if not was_connected:
            await database.disconnect()


if __name__ == "__main__":
    asyncio.run(import_contacts())
````

## File: backend/scripts/process_existing_drive_files.py
````python
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
````

## File: backend/scripts/test_delivery_flow.py
````python
import sys
import os
import asyncio
import datetime
import json

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from db.setup import database
from db.models import (
    newsletters,
    summaries,
    subscribers,
    delivery_logs,
    agent_notifications,
)
from scripts.delivery_worker import check_and_deliver


async def run_integration_test():
    print("Connecting to DB for integration test...")
    await database.connect()

    try:
        # 1. Add a test subscriber
        print("Inserting test subscriber...")
        test_email = "test_parishioner@example.com"

        # Clean up existing if any
        await database.execute(
            subscribers.delete().where(subscribers.c.email == test_email)
        )

        await database.execute(
            subscribers.insert().values(email=test_email, is_active=True)
        )

        # 2. Add a mock newsletter scheduled for today with status='scheduled'
        print("Inserting mock newsletter scheduled for today...")
        today = datetime.date.today()

        # Clean up existing test ones by resolving foreign key first
        find_query = select(newsletters.c.id).where(
            newsletters.c.filename == "test_weekly_bulletin.pdf"
        )
        existing_rows = await database.fetch_all(find_query)
        if existing_rows:
            nl_ids = [row["id"] for row in existing_rows]
            await database.execute(
                delivery_logs.delete().where(delivery_logs.c.newsletter_id.in_(nl_ids))
            )
            await database.execute(
                summaries.delete().where(summaries.c.newsletter_id.in_(nl_ids))
            )
            await database.execute(
                newsletters.delete().where(newsletters.c.id.in_(nl_ids))
            )

        # Clean up mock database notifications
        await database.execute(
            agent_notifications.delete().where(
                agent_notifications.c.event_type == "delivery_report"
            )
        )

        newsletter_id = await database.execute(
            newsletters.insert().values(
                filename="test_weekly_bulletin.pdf",
                drive_file_id="mock_file_id_12345",
                drive_web_view_link="http://drive.google.com/mock",
                thumbnail_drive_id="mock_thumb_id_12345",
                uploader="test_script",
                schedule_date=today,
                tags="test,ordinary-time",
                delivered=False,
                status="scheduled",
                target_sunday=today,
            )
        )

        # Add summary
        await database.execute(
            summaries.insert().values(
                newsletter_id=newsletter_id,
                title="Mock 5th Sunday bulletin summary",
                summary="Paragraph 1 of the mock summary.\nParagraph 2 of the mock summary.",
            )
        )

        print("Setup complete. Disconnecting temporarily so delivery worker can run...")
        await database.disconnect()

        # 3. Run delivery worker
        print("Running delivery worker...")
        await check_and_deliver()

        # 4. Reconnect to verify side-effects
        print("Reconnecting to verify database state...")
        await database.connect()

        # Verify newsletter was updated
        query = newsletters.select().where(newsletters.c.id == newsletter_id)
        nl = await database.fetch_one(query)
        print(f"Newsletter Status after delivery: {nl['status']} (Expected: delivered)")
        print(f"Newsletter Delivered flag: {nl['delivered']} (Expected: True)")
        assert nl["status"] == "delivered", "Status was not updated to delivered"
        assert nl["delivered"] == True, "Delivered flag was not set to True"

        # Verify delivery logs
        log_query = delivery_logs.select().where(
            delivery_logs.c.newsletter_id == newsletter_id
        )
        logs = await database.fetch_all(log_query)
        print(f"Delivery logs recorded: {len(logs)}")
        assert len(logs) >= 1, f"Expected at least 1 delivery log, got {len(logs)}"

        # Check if our test recipient has a delivery log recorded
        test_recipient_log = next((l for l in logs if l['recipient'] == test_email), None)
        assert test_recipient_log is not None, f"Expected delivery log for test email '{test_email}', but none was found."
        print(f"Recipient: {test_recipient_log['recipient']} | Status: {test_recipient_log['status']}")
        
        # Verify agent bridge database notification
        print("Verifying database agent_notifications queue...")
        note_query = select(agent_notifications).where(
            agent_notifications.c.event_type == "delivery_report"
        )
        notes = await database.fetch_all(note_query)
        print(f"Database notifications recorded: {len(notes)}")
        assert len(notes) >= 1, f"Expected at least 1 database notification, got {len(notes)}"

        # Check that one of the notifications contains our newsletter ID in payload
        target_note = None
        for n in notes:
            payload = json.loads(n['payload'])
            if payload.get('event_id') == newsletter_id:
                target_note = n
                break

        assert target_note is not None, "Could not find agent notification for our test newsletter ID"
        payload = json.loads(target_note['payload'])
        print(f"Event type: {payload['type']} (Expected: delivery_report)")
        assert (
            payload["type"] == "delivery_report"
        ), "Event type was not delivery_report"

        # Clean up
        print("Cleaning up test data...")
        await database.execute(delivery_logs.delete().where(delivery_logs.c.newsletter_id == newsletter_id))
        await database.execute(summaries.delete().where(summaries.c.newsletter_id == newsletter_id))
        await database.execute(newsletters.delete().where(newsletters.c.id == newsletter_id))
        await database.execute(subscribers.delete().where(subscribers.c.email == test_email))
        await database.execute(agent_notifications.delete().where(agent_notifications.c.id == target_note['id']))
            
        print("All delivery worker integration tests passed successfully!")

    except Exception as err:
        print(f"Test failed with error: {err}")
        sys.exit(1)
    finally:
        if database.is_connected:
            await database.disconnect()


if __name__ == "__main__":
    asyncio.run(run_integration_test())
````

## File: backend/tests/test_config.py
````python
import unittest
import os
from unittest import mock
from config import Settings

class TestConfigCORS(unittest.TestCase):
    def test_cors_origins_default(self):
        """Test that cors_origins defaults to an empty list."""
        env_vars = {
            "API_KEY": "test_key",
            "ANTHROPIC_API_KEY": "test_anthropic",
            "STACK_PROJECT_ID": "test_stack",
            "STACK_PUBLISHABLE_CLIENT_KEY": "test_pub",
            "STACK_SECRET_SERVER_KEY": "test_secret",
            "DATABASE_URL": "postgresql://localhost/db",
        }
        with mock.patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            self.assertEqual(settings.cors_origins, [
                "https://newsletter-herald.vercel.app",
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ])

    def test_cors_origins_comma_separated(self):
        """Test that cors_origins parses a comma-separated string."""
        env_vars = {
            "API_KEY": "test_key",
            "ANTHROPIC_API_KEY": "test_anthropic",
            "STACK_PROJECT_ID": "test_stack",
            "STACK_PUBLISHABLE_CLIENT_KEY": "test_pub",
            "STACK_SECRET_SERVER_KEY": "test_secret",
            "DATABASE_URL": "postgresql://localhost/db",
            "CORS_ORIGINS": "http://localhost:3000, https://newsletter-herald.vercel.app , http://127.0.0.1:3000",
        }
        with mock.patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            self.assertEqual(settings.cors_origins, [
                "http://localhost:3000",
                "https://newsletter-herald.vercel.app",
                "http://127.0.0.1:3000"
            ])

    def test_cors_origins_json_list(self):
        """Test that cors_origins parses a JSON encoded list."""
        env_vars = {
            "API_KEY": "test_key",
            "ANTHROPIC_API_KEY": "test_anthropic",
            "STACK_PROJECT_ID": "test_stack",
            "STACK_PUBLISHABLE_CLIENT_KEY": "test_pub",
            "STACK_SECRET_SERVER_KEY": "test_secret",
            "DATABASE_URL": "postgresql://localhost/db",
            "CORS_ORIGINS": '["http://localhost:3000", "https://newsletter-herald.vercel.app"]',
        }
        with mock.patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            self.assertEqual(settings.cors_origins, [
                "http://localhost:3000",
                "https://newsletter-herald.vercel.app"
            ])

    def test_cors_origins_empty_string(self):
        """Test that cors_origins handles an empty string environment variable."""
        env_vars = {
            "API_KEY": "test_key",
            "ANTHROPIC_API_KEY": "test_anthropic",
            "STACK_PROJECT_ID": "test_stack",
            "STACK_PUBLISHABLE_CLIENT_KEY": "test_pub",
            "STACK_SECRET_SERVER_KEY": "test_secret",
            "DATABASE_URL": "postgresql://localhost/db",
            "CORS_ORIGINS": "   ",
        }
        with mock.patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            self.assertEqual(settings.cors_origins, [])

if __name__ == "__main__":
    unittest.main()
````

## File: backend/.python-version
````
3.12.13
````

## File: backend/pyproject.toml
````toml
[project]
name = "newsletter-herald-backend"
version = "0.1.0"
description = "The API Gateway acts as a single entry point that manages client requests and delegates them to the appropriate backend services."
authors = [
    {name = "Anthony A.S Baptiste",email = "anthony.baptiste@outlook.com"}
]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">3.11"
dependencies = [
    "fastapi (>=0.116.1,<0.117.0)",
    "requests (>=2.32.4,<3.0.0)",
    "pydantic-settings (>=2.10.1,<3.0.0)",
    "python-dotenv (>=1.1.1,<2.0.0)",
    "uvicorn (>=0.35.0,<0.36.0)",
    "python-multipart (>=0.0.20,<0.0.21)",
    "python-docx (>=1.2.0,<2.0.0)",
    "pymupdf (>=1.26.3,<2.0.0)",
    "tiktoken (>=0.9.0,<0.10.0)",
    "sendgrid (>=6.11.0,<7.0.0)",
    "boto3 (>=1.34.0)",
    "google-api-python-client (>=2.120.0)",
    "google-auth (>=2.28.0)",
    "google-auth-oauthlib (>=1.2.0)",
    "databases (>=0.9.0)",
    "asyncpg (>=0.30.0)",
    "SQLAlchemy (>=2.0.0)",
    "psycopg2-binary (>=2.9.0)"
]

[tool.poetry]
package-mode = false

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"

[dependency-groups]
dev = [
    "pytest (>=9.1.1,<10.0.0)"
]
````

## File: frontend/app/preview/page.tsx
````typescript
'use client';

import React from 'react';
import { HomeContent } from '../HomeContent';
import { Box, Button, Container, Typography } from '@mui/material';
import Link from 'next/link';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

export default function PreviewPage() {
  return (
    <Box sx={{ position: 'relative' }}>
      {/* Admin Preview Banner */}
      <Box sx={{ bgcolor: '#fff3cd', borderBottom: '1px solid #ffeeba', py: 1.5 }}>
        <Container maxWidth="lg" sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
          <Typography variant="body2" sx={{ color: '#856404', fontWeight: 600 }}>
            👀 Preview Mode: You are viewing the landing page exactly as an unauthenticated guest.
          </Typography>
          <Link href="/" style={{ textDecoration: 'none' }}>
            <Button
              variant="outlined"
              color="warning"
              size="small"
              startIcon={<ArrowBackIcon />}
              sx={{ borderRadius: '100px', textTransform: 'none', px: 3 }}
            >
              Return to Console
            </Button>
          </Link>
        </Container>
      </Box>

      {/* Main Home Page forced to Public */}
      <HomeContent forcePublic={true} />
    </Box>
  );
}
````

## File: frontend/app/signup/page.tsx
````typescript
'use client';

import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  TextField,
  Alert,
  CircularProgress,
  Stack,
  Card,
  CardContent
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import MarkEmailReadIcon from '@mui/icons-material/MarkEmailRead';
import Link from 'next/link';

export default function PublicSignupPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    setLoading(true);
    setSuccess(null);
    setError(null);

    try {
      const res = await fetch(`${backendUrl}/subscribers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim() }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to sign up');

      setSuccess(data.message || 'Successfully subscribed!');
      setEmail('');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to complete signup';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ 
      minHeight: '80vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      bgcolor: '#f5f5f7',
      py: 6,
      px: 2
    }}>
      <Container maxWidth="sm">
        <Link href="/" style={{ textDecoration: 'none' }}>
          <Button startIcon={<ArrowBackIcon />} variant="outlined" sx={{ borderRadius: '100px', mb: 3, textTransform: 'none' }}>
            Back to Home
          </Button>
        </Link>


        <Card sx={{ borderRadius: 4, boxShadow: '0 8px 30px rgba(0,0,0,0.05)', border: '1px solid #e0e0e0', overflow: 'hidden' }}>
          <Box sx={{ bgcolor: '#0071e3', py: 4, textAlign: 'center', color: 'white' }}>
            <MarkEmailReadIcon sx={{ fontSize: 50, mb: 1 }} />
            <Typography variant="h5" fontWeight={700}>
              Join Our Parish Mailing List
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              Receive weekly bulletins and announcements straight to your inbox.
            </Typography>
          </Box>

          <CardContent sx={{ p: 4 }}>
            {success ? (
              <Box sx={{ textAlign: 'center', py: 2 }}>
                <Alert severity="success" sx={{ mb: 3, borderRadius: 2 }}>
                  {success}
                </Alert>
                <Typography variant="body1" sx={{ color: '#515154', mb: 3 }}>
                  Thank you for subscribing! You will receive our next newsletter issue on Sunday morning.
                </Typography>
                <Link href="/" style={{ textDecoration: 'none' }}>
                  <Button variant="contained" sx={{ borderRadius: '100px', px: 4, bgcolor: '#0071e3' }}>
                    Go to Home
                  </Button>
                </Link>
              </Box>
            ) : (
              <Box component="form" onSubmit={handleSignup}>
                {error && (
                  <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }} onClose={() => setError(null)}>
                    {error}
                  </Alert>
                )}

                <Stack spacing={3}>
                  <Typography variant="body2" color="text.secondary">
                    Please enter your email address below to subscribe to the weekly parish newsletter.
                  </Typography>

                  <TextField
                    label="Email Address"
                    type="email"
                    fullWidth
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                  />

                  <Button
                    type="submit"
                    variant="contained"
                    fullWidth
                    disabled={loading}
                    size="large"
                    sx={{ 
                      borderRadius: '980px', 
                      py: 1.5, 
                      bgcolor: '#0071e3', 
                      textTransform: 'none', 
                      fontWeight: 600,
                      boxShadow: 'none',
                      '&:hover': { bgcolor: '#0077ed', boxShadow: 'none' }
                    }}
                  >
                    {loading ? <CircularProgress size={24} color="inherit" /> : 'Subscribe to Newsletter'}
                  </Button>
                </Stack>
              </Box>
            )}
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
}
````

## File: frontend/docs/ADMIN_GUIDE.md
````markdown
# Newsletter Herald — Admin User Manual
Welcome to Newsletter Herald! This guide explains how to manage the parish bulletin summarization, archives, and email subscription lists.

---

## 📌 Executive Summary

Newsletter Herald is an automated liturgical newsletter pipeline. It parses weekly parish bulletins, extracts theological and calendar metadata, generates warm summaries using Groq Cloud AI, and distributes the email newsletter directly to your active parish subscriber database.

---

## 📤 1. Manual Bulletin Ingestion
To upload a new bulletin (when the automated pipeline is bypassed or for manual entries):
1. Navigate to the **Console Dashboard**.
2. Click **Upload Bulletin** (or drag a file into the upload zone).
3. Select a weekly parish bulletin (`.pdf` or `.docx` format).
4. The system will automatically:
   - Compress the document for fast web loading.
   - Run AI summarization to extract the **Target Sunday**, **Liturgical Season**, **Calendar Year**, and **Liturgical Summary**.
5. Once processed, it will appear in the main feed or redirect to the audit logs if a validation error occurs.

---

## ⚠️ 2. Ingestion Auditing & Metadata Overrides
To prevent AI hallucination or incorrect dates, the pipeline performs strict **Validation Checks** (e.g., verifying if the extracted Target Sunday is correct).

If a file fails validation, it enters the **System Errors & Audit Log**:
1. Click **System Errors** from the navigation bar.
2. Under **Ingestion Errors**, locate the failed document.
3. Click **Edit & Resolve** to open the metadata correction dialog.
4. Correct any fields (e.g. adjust the target Sunday date).
5. Choose one of two action buttons:
   *   **Save & Schedule Email**: Saves the corrections and queues the newsletter for weekly email delivery to all subscribers.
   *   **Archive Only (No Email)**: Publishes the newsletter directly to the public feed archives. It will mark the bulletin as "delivered" without queueing any emails (perfect for adding missing historic editions).

---

## 👥 3. Subscriber Directory Management
To view or update your parish mailing list, navigate to the **Subscribers** view:

### Add Single Subscriber:
1. Click **Add Subscriber**.
2. Enter the **Email**, **First Name**, **Last Name**, and **Phone Number**.
3. Click **Save** to insert the record.

### Sync from Google Contacts (CSV Batch Import):
1. Export your contact list from Gmail/Google Contacts as a **Google CSV** file.
2. In SALLTO Herald, click **Sync from Google Contacts** in the Subscribers panel.
3. Upload the exported `contacts.csv` file.
4. The import script will automatically parse and map the complex Gmail columns, extracting names, email addresses, and phone numbers to keep your database synchronized.

---

## 🔒 4. Access Control & Troubleshooting
*   **Whitelisted Administrators**: Only users logged in via Clerk with the emails `anthony.as.baptiste@gmail.com` or `sallto.newsletter@gmail.com` are granted access to the console and subscriber directories.
*   **Access Denied Screen**: If you sign in with an unauthorized personal account, you will see a restricted access card. Click **Sign Out** to switch accounts or **View Public Feed** to browse the public bulletin archive.
````

## File: frontend/.env.example
````
# Backend API URL (CRITICAL for production deployment on Vercel)
# Set this in Vercel Environment Variables to your live backend endpoint (e.g. https://api.yourdomain.com)
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000

# API Authentication Key
NEXT_PUBLIC_INTERNAL_API_KEY=

# Clerk Auth Keys
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=

# Google Drive Connectivity & Database (if used server-side in Next.js)
DATABASE_URL=
GOOGLE_DRIVE_FOLDER_ID=
GOOGLE_SERVICE_ACCOUNT_JSON=
````

## File: frontend/.gitignore
````
# See https://help.github.com/articles/ignoring-files/ for more about ignoring files.

# dependencies
/node_modules
/.pnp
.pnp.*
.yarn/*
!.yarn/patches
!.yarn/plugins
!.yarn/releases
!.yarn/versions

# testing
/coverage

# next.js
/.next/
/out/

# production
/build

# misc
.DS_Store
*.pem

# debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# env files (can opt-in for committing if needed)
.env.local

# vercel
.vercel

# typescript
*.tsbuildinfo
next-env.d.ts

# clerk configuration (can include secrets)
/.clerk/
````

## File: .python-version
````
3.12.13
````

## File: backend/llm/providers.py
````python
import requests
import logging
from typing import Dict, Any, Optional

from config import get_settings
from helpers.text_utils import count_tokens

# Get settings from centralized configuration
settings = get_settings()

# Create a logger for this module
logger = logging.getLogger(__name__)

# Core Prompt Instruction for Sanitization
# This is shared across all providers to ensure consistent PII/PHI filtering.
SANITIZATION_INSTRUCTION = (
    "CRITICAL: YOUR SUMMARY MUST NOT INCLUDE ANY PERSONALLY IDENTIFIABLE INFORMATION (PII) OR PROTECTED HEALTH INFORMATION (PHI). "
    "Do NOT include names of parishioners, specific home addresses, personal phone numbers, or personal email addresses. "
    "Do NOT include details about medical conditions, hospitalizations, or specific health requests for individuals. "
    "If you mention upcoming events, refer to them by the event name or group, not by the names of the individuals hosting them (unless they are official church staff like the Priest). "
    "The goal is a public-facing summary that protects the privacy of all individuals mentioned in the original newsletter."
)

GROQ_SYSTEM_INSTRUCTION = (
    "You are a helpful assistant that summarizes Roman Catholic church newsletters. Return your response as a JSON object with the following keys:\n"
    "1. 'title': A warm, descriptive subject line.\n"
    "2. 'summary': A warm, 2-paragraph email message.\n"
    "3. 'schedule_date': Newsletter date in YYYY-MM-DD format.\n"
    "4. 'liturgical_season': Liturgical season (e.g., 'Ordinary Time', 'Lent', 'Advent', 'Christmas', 'Easter').\n"
    "5. 'calendar_year': Calendar year (e.g., '2025').\n"
    "6. 'liturgical_year': Liturgical year (e.g., 'Year A', 'Year B', 'Year C')."
    f"\n\n{SANITIZATION_INSTRUCTION}"
)


def summarize_with_model(prompt: str, timeout: int = 300) -> Dict[str, str]:
    """
    Summarizes a given text input using a local Ollama model.
    Returns: Dict containing 'title' and 'summary'.
    """
    logger.debug("Sending request to model API")

    system_instruction = (
        "You are a helpful assistant that summarizes Roman Catholic church newsletters into warm, concise 2-paragraph email messages for parishioners. "
        "Return your response in JSON format with the following keys:\n"
        "1. 'title': A concise subject line (e.g., '4th Sunday of Lent – Living as Children of the Light')\n"
        "2. 'summary': The 2-paragraph email body.\n"
        "3. 'schedule_date': The date the newsletter is for, in YYYY-MM-DD format.\n"
        "4. 'liturgical_season': The liturgical season (e.g., 'Ordinary Time', 'Lent', 'Advent', 'Christmas', 'Easter').\n"
        "5. 'calendar_year': The calendar year (e.g., '2025').\n"
        "6. 'liturgical_year': The liturgical year (e.g., 'Year A', 'Year B', 'Year C')."
        f"\n{SANITIZATION_INSTRUCTION}"
    )
    full_prompt = f"{system_instruction}\n\nUser Request: {prompt}"

    try:
        response = requests.post(
            f"{settings.ollama_base_url}/api/generate",
            timeout=timeout,
            json={
                "model": settings.ollama_model,
                "prompt": full_prompt,
                "stream": False,
                "format": "json"
            }
        )

        if response.status_code != 200:
            error_msg = f"Model error: {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

        data = response.json()
        import json
        resp_data = json.loads(data["response"])
        return {
            "title": resp_data.get("title", "Church Newsletter"),
            "summary": resp_data.get("summary", ""),
            "schedule_date": resp_data.get("schedule_date"),
            "liturgical_season": resp_data.get("liturgical_season"),
            "calendar_year": resp_data.get("calendar_year"),
            "liturgical_year": resp_data.get("liturgical_year")
        }

    except Exception as e:
        error_msg = f"Request to model API failed: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


def summarize_with_claude(prompt: str, timeout: int = 300) -> Dict[str, str]:
    """
    Summarizes using Claude. Returns: Dict containing 'title' and 'summary'.
    """
    if not settings.anthropic_api_key:
        error_msg = "ANTHROPIC_API_KEY environment variable is not set"
        logger.error(error_msg)
        raise ValueError(error_msg)

    headers = {
        "x-api-key": settings.anthropic_api_key,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }

    payload = {
        "model": "claude-opus-4-20250514",
        "max_tokens": settings.max_allowed_tokens,
        "temperature": 0.7,
        "system": (
            "Summarize the newsletter. Return ONLY a JSON object with the following keys:\n"
            "1. 'title': A warm subject line.\n"
            "2. 'summary': 2-paragraph email body.\n"
            "3. 'schedule_date': Newsletter date in YYYY-MM-DD format.\n"
            "4. 'liturgical_season': Liturgical season (e.g., 'Ordinary Time', 'Lent', 'Advent', 'Christmas', 'Easter').\n"
            "5. 'calendar_year': Calendar year (e.g., '2025').\n"
            "6. 'liturgical_year': Liturgical year (e.g., 'Year A', 'Year B', 'Year C')."
            f"\n\n{SANITIZATION_INSTRUCTION}"
        ),
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()

        data = response.json()
        import json
        resp_data = json.loads(data["content"][0]["text"])
        return {
            "title": resp_data.get("title", "Church Newsletter"),
            "summary": resp_data.get("summary", ""),
            "schedule_date": resp_data.get("schedule_date"),
            "liturgical_season": resp_data.get("liturgical_season"),
            "calendar_year": resp_data.get("calendar_year"),
            "liturgical_year": resp_data.get("liturgical_year")
        }

    except Exception as e:
        error_msg = f"Claude API failed: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


def summarize_with_groq(prompt: str, timeout: int = 60) -> Dict[str, str]:
    """
    Summarizes using Groq. Returns: Dict containing 'title' and 'summary'.
    """
    if not settings.groq_api_key:
        error_msg = "GROQ_API_KEY environment variable is not set"
        logger.error(error_msg)
        raise ValueError(error_msg)

    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": settings.groq_model,
        "messages": [
            {
                "role": "system", 
                "content": GROQ_SYSTEM_INSTRUCTION
            },
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.7,
        "max_tokens": 1024
    }

    import time
    max_retries = 5
    retry_delay = 70
    last_exception = None

    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=timeout
            )
            if response.status_code == 429:
                logger.warning(f"Groq API returned 429 (Too Many Requests). Retrying in {retry_delay}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(retry_delay)
                # Keep delay high to clear the 60-second window
                continue

            response.raise_for_status()

            data = response.json()
            import json
            resp_data = json.loads(data["choices"][0]["message"]["content"])
            return {
                "title": resp_data.get("title", "Church Newsletter"),
                "summary": resp_data.get("summary", ""),
                "schedule_date": resp_data.get("schedule_date"),
                "liturgical_season": resp_data.get("liturgical_season"),
                "calendar_year": resp_data.get("calendar_year"),
                "liturgical_year": resp_data.get("liturgical_year")
            }
        except Exception as e:
            last_exception = e
            logger.warning(f"Groq API call attempt {attempt+1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)

    error_msg = f"Groq API failed after {max_retries} attempts: {last_exception}"
    logger.error(error_msg)
    raise Exception(error_msg)



def choose_llm_and_summarize(text: str) -> Dict[str, Any]:
    """
    Summarizes a given text into a title and a 2-paragraph email message.
    Respects the configured LLM strategy.
    """
    # Truncate text if it's extremely long to avoid 413 Payload Too Large and stay within context limits
    max_chars = 18000
    if len(text) > max_chars:
        logger.info(f"Truncating text from {len(text)} to {max_chars} characters to fit context limits.")
        text = text[:max_chars] + "\n...[TRUNCATED FOR LENGTH]..."

    prompt = f"Summarize this church newsletter: {text}"
    token_estimate = count_tokens(prompt)

    logger.info(f"Estimated tokens: {token_estimate}")

    if token_estimate > settings.max_allowed_tokens:
        error_msg = f"Document too long ({token_estimate} tokens). Limit is {settings.max_allowed_tokens}."
        logger.error(error_msg)
        raise ValueError(error_msg)

    strategy = settings.llm_strategy.lower()

    # Explicit strategy overrides
    if strategy == "groq" and settings.groq_api_key:
        model = f"{settings.groq_model} (Groq)"
        logger.info(f"Forcing Groq ({settings.groq_model})")
        res = summarize_with_groq(prompt)
        cost_estimate = 0
    elif strategy == "local":
        model = f"{settings.ollama_model} (Ollama)"
        logger.info(f"Forcing Local Model ({settings.ollama_model})")
        res = summarize_with_model(prompt)
        cost_estimate = 0
    elif strategy == "remote":
        model = "claude (Anthropic)"
        logger.info("Forcing Remote Model (Claude)")
        res = summarize_with_claude(prompt)
        cost_estimate = (token_estimate / 1000) * 0.015
    else:
        # Auto strategy or default fallback
        if token_estimate > 5000:
            model = "claude (Anthropic)"
            logger.info(f"Token count {token_estimate} > 5000, using Claude")
            res = summarize_with_claude(prompt)
            cost_estimate = (token_estimate / 1000) * 0.015
        elif settings.groq_api_key and strategy == "auto":
            model = f"{settings.groq_model} (Groq)"
            logger.info(f"Auto strategy: using Groq ({settings.groq_model})")
            res = summarize_with_groq(prompt)
            cost_estimate = 0
        else:
            model = f"{settings.ollama_model} (Ollama)"
            logger.info(f"Auto strategy: using Local Model ({settings.ollama_model})")
            res = summarize_with_model(prompt)
            cost_estimate = 0

    # Defensive sanitization for local LLM nested dictionary structures
    title_val = res.get("title", "Church Newsletter")
    if isinstance(title_val, dict):
        title_val = title_val.get("title") or title_val.get("text") or str(title_val)
    elif not isinstance(title_val, str):
        title_val = str(title_val)

    summary_val = res.get("summary", "")
    if isinstance(summary_val, dict):
        summary_val = summary_val.get("summary") or summary_val.get("text") or str(summary_val)
    elif not isinstance(summary_val, str):
        summary_val = str(summary_val)

    return {
        "title": title_val,
        "summary": summary_val,
        "schedule_date": res.get("schedule_date"),
        "liturgical_season": res.get("liturgical_season"),
        "calendar_year": res.get("calendar_year"),
        "liturgical_year": res.get("liturgical_year"),
        "model": model,
        "tokens": token_estimate,
        "cost_usd_estimate": round(cost_estimate, 4)
    }
````

## File: docs/HERMES_BRIEF.md
````markdown
# 🤖 Hermes Agent Integration Brief: Automated Newsletter Ingestion & Alerts

## 📌 Executive Summary
This document specifies the integration protocol for **Hermes Agent** to automate weekend bulletin ingestion from parish staff (Irma Carter), transmit documents to the Newsletter Herald backend, and route review requests or validation alerts directly to the admin via WhatsApp, Signal, or Email.

---

## ⚙️ Configuration & Environment

| Property | Value | Notes |
|---|---|---|
| **Backend API URL** | `http://localhost:8000` *(or deployed backend URL)* | Endpoint target |
| **Dashboard URL** | `https://newsletter-herald.vercel.app` | Production frontend |
| **API Header** | `X-API-Key: YOUR_INTERNAL_API_KEY` | Authentication key |
| **Target Email Sender** | Irma Carter (`irma.carter@church.org` or parish staff) | Sender filter |

---

## 🔄 Automated Ingestion Flow

```
[Irma Carter Email] ──► [Hermes Routine] ──► [POST /upload-document]
                                                     │
                                        ┌────────────┴────────────┐
                                        ▼                         ▼
                                 is_valid: true           is_valid: false
                                        │                         │
                                        ▼                         ▼
                                [Review Request]         [Validation Alert]
```

### Step-by-Step Execution Sequence

1. **Email Monitoring Routine (Saturday & Sunday 08:00–12:00)**:
   Hermes checks the incoming inbox for unread messages containing `.pdf` or `.docx` attachments.
2. **Document Extraction & API POST**:
   Hermes saves the attachment and sends a `multipart/form-data` request:
   ```bash
   POST /upload-document
   Header: X-API-Key: <API_KEY>
   Header: x-user-email: irma.carter@church.org
   Body: file=<attachment_bytes>
   ```
3. **Response Inspection**:
   Hermes inspects the returned JSON payload:
   ```json
   {
     "summary": {
       "title": "20th Sunday in Ordinary Time",
       "status": "draft"
     },
     "validation": {
       "is_valid": true,
       "target_sunday": "2026-08-23",
       "error_message": null
     }
   }
   ```
4. **Intelligent Notification Routing**:
   - **If `is_valid == true`**: Hermes forwards the formatted summary to the admin with approval links:
     > 🔔 **New Newsletter Summary for Review**  
     > **Target Sunday:** 2026-08-23  
     > **Title:** 20th Sunday in Ordinary Time  
     > *[Summary text...]*  
     > 👉 **Approve & Schedule:** `https://.../newsletters/324/approve`
   - **If `is_valid == false`**: Hermes sends an urgent validation alert:
     > ⚠️ **Newsletter Validation Failed**  
     > **File:** `Trinity_Newsletter_16.08.26.pdf`  
     > **Issue:** Extracted date '2026-08-16' does not match target Sunday '2026-08-23'.  
     > 🔗 Review on Dashboard: `https://newsletter-herald.vercel.app/`

---

## 🐍 Hermes Skill Script Template (`~/.hermes/skills/newsletter_ingest.py`)

```python
import requests
import json

API_URL = "http://localhost:8000/upload-document"
API_KEY = "YOUR_INTERNAL_API_KEY"

def process_and_upload_bulletin(file_path: str, uploader_email: str):
    headers = {
        "X-API-Key": API_KEY,
        "x-user-email": uploader_email
    }
    
    with open(file_path, "rb") as f:
        files = {"file": (file_path.split("/")[-1], f, "application/pdf")}
        response = requests.post(API_URL, headers=headers, files=files)
        
    data = response.json()
    validation = data.get("validation", {})
    summary = data.get("summary", {})
    
    if not validation.get("is_valid", True):
        # Validation Failed - Send Urgent Alert
        alert_msg = (
            f"⚠️ *Newsletter Validation Failed*\n\n"
            f"*File:* {file_path.split('/')[-1]}\n"
            f"*Issue:* {validation.get('error_message')}\n"
            f"*Target Sunday:* {validation.get('target_sunday')}\n\n"
            f"🔗 Review on Dashboard: https://newsletter-herald.vercel.app/"
        )
        return {"status": "alert_sent", "message": alert_msg}
    else:
        # Success - Send Review Request
        review_msg = (
            f"🔔 *New Newsletter Summary for Review*\n\n"
            f"*Target Sunday:* {validation.get('target_sunday')}\n"
            f"*Title:* {summary.get('title')}\n\n"
            f"{summary.get('summary')}\n\n"
            f"🔗 Approve on Dashboard: https://newsletter-herald.vercel.app/"
        )
        return {"status": "review_sent", "message": review_msg}
````

## File: frontend/app/components/AuthButtons.tsx
````typescript
'use client';

import { Box, Button } from "@mui/material";
import { useUser, UserButton, SignInButton } from "@clerk/nextjs";
import Link from "next/link";

export default function AuthButtons() {
  const { isLoaded, isSignedIn } = useUser();

  if (!isLoaded) {
    return <Box sx={{ width: 100 }} />;
  }

  return (
    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
      {isSignedIn ? (
        <>
          <Link href="/docs" style={{ textDecoration: 'none' }}>
            <Button sx={{ textTransform: 'none', fontWeight: 600, color: '#1d1d1f', fontSize: '0.95rem' }}>
              Docs
            </Button>
          </Link>
          <UserButton />
        </>
      ) : (
        <>
          <SignInButton mode="modal" fallbackRedirectUrl="/">
            <Button variant="text" color="primary" sx={{ textTransform: 'none', fontWeight: 600 }}>
              Login
            </Button>
          </SignInButton>
          <Link href="/signup" style={{ textDecoration: 'none' }}>
            <Button 
              variant="contained" 
              color="primary" 
              sx={{ px: 3, borderRadius: '980px', textTransform: 'none', fontWeight: 600 }} 
            >
              Join Mailing List
            </Button>
          </Link>
        </>
      )}
    </Box>
  );
}
````

## File: frontend/app/docs/page.tsx
````typescript
import React from 'react';
import fs from 'fs';
import path from 'path';
import DocsTabs from './DocsTabs';
import { Metadata } from 'next';

import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';

export const metadata: Metadata = {
  title: "Documentation Center - Newsletter Herald",
  description: "User manuals, operational guidelines, and development changelogs for the Newsletter Herald platform.",
};

export default async function DocsPage() {
  const { userId } = await auth();
  if (!userId) {
    redirect('/');
  }

  const docsDir = path.join(process.cwd(), 'docs');
  const adminGuidePath = path.join(docsDir, 'ADMIN_GUIDE.md');
  const changelogPath = path.join(docsDir, 'CHANGELOG.md');

  let adminGuide = '';
  let changelog = '';

  try {
    adminGuide = fs.readFileSync(adminGuidePath, 'utf8');
  } catch (err) {
    console.error("Failed to read ADMIN_GUIDE.md:", err);
    adminGuide = "# Error\nFailed to load the Admin Manual. Please check that `docs/ADMIN_GUIDE.md` exists.";
  }

  try {
    changelog = fs.readFileSync(changelogPath, 'utf8');
  } catch (err) {
    console.error("Failed to read CHANGELOG.md:", err);
    changelog = "# Error\nFailed to load the Changelog. Please check that `docs/CHANGELOG.md` exists.";
  }

  return <DocsTabs adminGuide={adminGuide} changelog={changelog} />;
}
````

## File: frontend/app/page.tsx
````typescript
'use client';

import React from 'react';
import { Box, CircularProgress } from '@mui/material';
import { useSearchParams } from 'next/navigation';
import { HomeContent } from "./HomeContent";

function HomeWithSearchParams() {
  const searchParams = useSearchParams();
  const forcePublic = searchParams.get('forcePublic') === 'true';
  return <HomeContent forcePublic={forcePublic} />;
}

export default function Home() {
  return (
    <React.Suspense fallback={<Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>}>
      <HomeWithSearchParams />
    </React.Suspense>
  );
}
````

## File: backend/scripts/upload_local_files.py
````python
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
from db.models import newsletters, summaries, model_usage, upload_logs
from helpers.storage import upload_to_drive, make_file_public
from helpers.text_utils import (
    extract_text_from_file,
    generate_pdf_thumbnail,
    sanitize_filename,
    compress_pdf,
)
from helpers.validation import validate_newsletter_date
from llm.providers import choose_llm_and_summarize
from datetime import datetime

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

        # Batch query existing filenames in DB to avoid N+1 query
        existing_filenames = set()
        if files:
            sanitized_filenames = [sanitize_filename(f.name) for f in files]
            query = newsletters.select().where(
                newsletters.c.filename.in_(sanitized_filenames)
            )
            existing_rows = await database.fetch_all(query)
            existing_filenames = {row["filename"] for row in existing_rows}

        for file_path in files:
            filename = file_path.name
            mime_type = (
                "application/pdf"
                if file_path.suffix.lower() == ".pdf"
                else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

            # Check if already in DB (using pre-fetched set to avoid N+1 query)
            new_filename = sanitize_filename(filename)
            if new_filename in existing_filenames:
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
                        logger.warning(
                            f"Compression failed for {filename}, using original: {e}"
                        )

                # Upload to Cloudflare R2 (Primary) or Google Drive (Fallback)
                logger.info(f"Uploading {new_filename}...")
                drive_file_id, web_view_link = upload_to_drive(
                    final_content, new_filename, mime_type
                )

                if not drive_file_id:
                    logger.error(f"Upload failed for {filename}, skipping.")
                    continue

                # Extract & Summarize
                file_type = "pdf" if mime_type == "application/pdf" else "docx"
                text = extract_text_from_file(
                    io.BytesIO(final_content), file_type=file_type
                )

                logger.info(f"Generating summary for {new_filename}...")
                summary_data = choose_llm_and_summarize(text)

                # Thumbnail
                thumbnail_drive_id = None
                if file_type == "pdf":
                    try:
                        thumb_bytes = generate_pdf_thumbnail(io.BytesIO(final_content))
                        thumbnail_drive_id, _ = upload_to_drive(
                            thumb_bytes, f"thumb_{new_filename}.png", "image/png"
                        )
                    except Exception as thumb_err:
                        logger.error(
                            f"Failed to generate thumbnail for {new_filename}: {thumb_err}"
                        )

                # Save to DB
                try:
                    logger.info(f"Saving {new_filename} to DB...")

                    # Parse schedule_date and target_sunday for historical files
                    schedule_date_str = summary_data.get("schedule_date")
                    schedule_date_val = None
                    target_sunday = None
                    status = "failed_validation"

                    if isinstance(schedule_date_str, str):
                        try:
                            schedule_date_val = datetime.strptime(
                                schedule_date_str, "%Y-%m-%d"
                            ).date()
                            target_sunday = schedule_date_val
                            status = "delivered"  # Historical bulletins are already published
                        except Exception:
                            pass

                    async with database.transaction():
                        # Construct tags string
                        tags_list = []
                        if summary_data.get("liturgical_season"):
                            tags_list.append(
                                summary_data["liturgical_season"]
                                .lower()
                                .replace(" ", "-")
                            )
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
                                schedule_date=schedule_date_val,
                                tags=tags_str,
                                delivered=False,
                                status=status,
                                target_sunday=target_sunday,
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
                    logger.info(
                        f"Successfully processed and SAVED to DB: {new_filename}"
                    )
                    existing_filenames.add(new_filename)  # Track newly saved filename
                    await database.execute(
                        upload_logs.insert().values(
                            filename=new_filename,
                            uploader="local_batch_upload",
                            status="success",
                        )
                    )
                except Exception as db_err:
                    logger.error(f"DATABASE INSERT FAILED for {new_filename}: {db_err}")
                    raise  # Re-raise to be caught by outer try-except

            except Exception as e:
                logger.error(f"Failed to process {filename}: {e}", exc_info=True)
                try:
                    await database.execute(
                        upload_logs.insert().values(
                            filename=filename,
                            uploader="local_batch_upload",
                            status="failed",
                            error_message=str(e),
                        )
                    )
                except Exception as db_log_err:
                    logger.error(f"Failed to log upload failure to DB: {db_log_err}")

            # Avoid API rate limiting
            await asyncio.sleep(1.5)

    finally:
        await database.disconnect()


if __name__ == "__main__":
    asyncio.run(process_local_files())
````

## File: frontend/app/subscribers/page.tsx
````typescript
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Switch,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Stack,
  InputAdornment,
  Card,
  CardContent,
  Breadcrumbs
} from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import SearchIcon from '@mui/icons-material/Search';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import PauseCircleOutlineIcon from '@mui/icons-material/PauseCircleOutline';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import HomeIcon from '@mui/icons-material/Home';
import Link from 'next/link';
import { useUser, useClerk } from "@clerk/nextjs";

interface Subscriber {
  id: number;
  email: string;
  first_name: string | null;
  last_name: string | null;
  phone: string | null;
  is_active: boolean;
  created_at: string | null;
}

interface Stats {
  total: number;
  active: number;
  inactive: number;
}

export default function SubscribersPage() {
  return (
    <React.Suspense fallback={<Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>}>
      <SubscribersPageContent />
    </React.Suspense>
  );
}

function SubscribersPageContent() {
  const { isLoaded, isSignedIn, user } = useUser();
  const { signOut } = useClerk();
  const [subscribers, setSubscribers] = useState<Subscriber[]>([]);

  const userEmail = user?.primaryEmailAddress?.emailAddress;

  // Admin Email Whitelist check
  const ADMIN_WHITELIST = ['sallto.newsletter@gmail.com', 'anthony.as.baptiste@gmail.com'];
  const hasAdminAccess = userEmail ? ADMIN_WHITELIST.includes(userEmail) : false;

  const [stats, setStats] = useState<Stats>({ total: 0, active: 0, inactive: 0 });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState<string>('');

  // Single Add Form States
  const [newEmail, setNewEmail] = useState<string>('');
  const [newFirstName, setNewFirstName] = useState<string>('');
  const [newLastName, setNewLastName] = useState<string>('');
  const [newPhone, setNewPhone] = useState<string>('');
  const [addLoading, setAddLoading] = useState<boolean>(false);
  const [addSuccess, setAddSuccess] = useState<string | null>(null);

  // Batch Import Modal State
  const [batchOpen, setBatchOpen] = useState<boolean>(false);
  const [batchRawInput, setBatchRawInput] = useState<string>('');
  const [batchLoading, setBatchLoading] = useState<boolean>(false);
  const [batchResult, setBatchResult] = useState<{ message: string; added: number; reactivated: number; skipped: number } | null>(null);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

  const fetchSubscribers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${backendUrl}/subscribers`);
      if (!res.ok) throw new Error('Failed to fetch subscriber list');
      const data = await res.json();
      setSubscribers(data.subscribers || []);
      setStats(data.stats || { total: 0, active: 0, inactive: 0 });
    } catch (err) {
      const error = err as Error;
      setError(error.message || 'Failed to load subscribers');
    } finally {
      setLoading(false);
    }
  }, [backendUrl]);

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      window.location.href = '/';
    }
  }, [isLoaded, isSignedIn]);

  useEffect(() => {
    if (user && hasAdminAccess) {
      fetchSubscribers();
    }
  }, [user, hasAdminAccess, fetchSubscribers]);

  if (!isLoaded || !isSignedIn) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>;
  }

  if (!hasAdminAccess) {
    return (
      <Box sx={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: '#f5f5f7', p: 3 }}>
        <Paper sx={{ p: 5, maxWidth: 500, width: '100%', textAlign: 'center', borderRadius: 4, boxShadow: '0 8px 30px rgba(0,0,0,0.05)' }}>
          <Box sx={{ width: 64, height: 64, bgcolor: '#fce8e6', color: '#d93025', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto', mb: 3 }}>
            <PeopleIcon sx={{ fontSize: 32 }} />
          </Box>
          <Typography variant="h5" sx={{ fontWeight: 700, mb: 1, letterSpacing: '-0.01em', color: '#1d1d1f' }}>
            Access Denied
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4, lineHeight: 1.6 }}>
            Your account (<strong>{userEmail}</strong>) is not authorized to access subscriber management.
          </Typography>
          <Stack spacing={2} direction="row" justifyContent="center">
            <Button 
              variant="outlined" 
              onClick={() => signOut()} 
              sx={{ borderRadius: '980px', textTransform: 'none', px: 3 }}
            >
              Sign Out
            </Button>
            <Link href="/" style={{ textDecoration: 'none' }}>
              <Button 
                variant="contained" 
                sx={{ borderRadius: '980px', textTransform: 'none', px: 3, bgcolor: '#0071e3', '&:hover': { bgcolor: '#0077ed' } }}
              >
                Go to Dashboard
              </Button>
            </Link>
          </Stack>
        </Paper>
      </Box>
    );
  }

  const handleSingleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEmail.trim()) return;

    setAddLoading(true);
    setAddSuccess(null);
    setError(null);

    try {
      const res = await fetch(`${backendUrl}/subscribers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: newEmail.trim(),
          first_name: newFirstName.trim() || null,
          last_name: newLastName.trim() || null,
          phone: newPhone.trim() || null,
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to add subscriber');

      setAddSuccess(data.message);
      setNewEmail('');
      setNewFirstName('');
      setNewLastName('');
      setNewPhone('');
      fetchSubscribers();
    } catch (err) {
      const error = err as Error;
      setError(error.message);
    } finally {
      setAddLoading(false);
    }
  };

  const handleBatchImport = async () => {
    if (!batchRawInput.trim()) return;

    setBatchLoading(true);
    setBatchResult(null);

    // Parse emails split by newline, comma, or semicolon
    const emailList = batchRawInput
      .split(/[\n,;]+/)
      .map(e => e.trim())
      .filter(e => e.length > 0);

    try {
      const res = await fetch(`${backendUrl}/subscribers/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ emails: emailList }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to import subscribers');

      setBatchResult(data);
      fetchSubscribers();
    } catch (err) {
      const error = err as Error;
      setError(error.message);
    } finally {
      setBatchLoading(false);
    }
  };

  const handleToggleActive = async (id: number, currentStatus: boolean) => {
    try {
      const res = await fetch(`${backendUrl}/subscribers/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !currentStatus }),
      });

      if (!res.ok) throw new Error('Failed to update status');

      // Optimistic state update
      setSubscribers(prev =>
        prev.map(sub => (sub.id === id ? { ...sub, is_active: !currentStatus } : sub))
      );
      setStats(prev => ({
        ...prev,
        active: currentStatus ? prev.active - 1 : prev.active + 1,
        inactive: currentStatus ? prev.inactive + 1 : prev.inactive - 1,
      }));
    } catch (err) {
      const error = err as Error;
      setError(error.message);
    }
  };

  const handleDeleteSubscriber = async (id: number, email: string) => {
    if (!confirm(`Are you sure you want to remove ${email} from your subscriber list?`)) return;

    try {
      const res = await fetch(`${backendUrl}/subscribers/${id}`, {
        method: 'DELETE',
      });

      if (!res.ok) throw new Error('Failed to delete subscriber');

      fetchSubscribers();
    } catch (err) {
      const error = err as Error;
      setError(error.message);
    }
  };

  const filteredSubscribers = subscribers.filter(s => {
    const searchLower = search.toLowerCase();
    const emailMatch = s.email.toLowerCase().includes(searchLower);
    const firstNameMatch = s.first_name ? s.first_name.toLowerCase().includes(searchLower) : false;
    const lastNameMatch = s.last_name ? s.last_name.toLowerCase().includes(searchLower) : false;
    return emailMatch || firstNameMatch || lastNameMatch;
  });

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f7', py: 5 }}>
      <Container maxWidth="lg">
        {/* Navigation Breadcrumbs */}
        <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 3 }}>
          <Link href="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', color: '#86868b' }}>
            <HomeIcon sx={{ mr: 0.5, fontSize: 16 }} />
            Dashboard
          </Link>
          <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center', fontWeight: 600 }}>
            <PeopleIcon sx={{ mr: 0.5, fontSize: 16, color: '#0071e3' }} />
            Subscriber Management
          </Typography>
        </Breadcrumbs>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4, flexWrap: 'wrap', gap: 2 }}>
          <Box>
            <Typography variant="h4" fontWeight={800} sx={{ letterSpacing: '-0.02em', color: '#1d1d1f' }}>
              Subscriber Management
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Manage your parish mailing list, track personal details, and view Google Contacts / website signups.
            </Typography>
          </Box>
          <Stack direction="row" spacing={2} alignItems="center">
            <Button
              variant="contained"
              startIcon={<UploadFileIcon />}
              onClick={() => { setBatchOpen(true); setBatchResult(null); setBatchRawInput(''); }}
              sx={{
                borderRadius: '980px',
                bgcolor: '#0071e3',
                py: 1.2,
                px: 3,
                textTransform: 'none',
                fontWeight: 600,
                boxShadow: 'none',
                '&:hover': { bgcolor: '#0077ed', boxShadow: 'none' }
              }}
            >
              Batch Import Emails
            </Button>
            <Link href="/" style={{ textDecoration: 'none' }}>
              <Button startIcon={<ArrowBackIcon />} variant="outlined" sx={{ borderRadius: '100px', py: 1.2, px: 3, textTransform: 'none' }}>
                Back to Dashboard
              </Button>
            </Link>
          </Stack>
        </Box>

        {/* Global Feedback Alerts */}
        {error && (
          <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        {addSuccess && (
          <Alert severity="success" sx={{ mb: 3, borderRadius: 2 }} onClose={() => setAddSuccess(null)}>
            {addSuccess}
          </Alert>
        )}

        {/* Stat Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid size={{ xs: 12, sm: 4 }}>
            <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: '#e8f2ff', color: '#0071e3' }}>
                  <PeopleIcon fontSize="large" />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Total Subscribers</Typography>
                  <Typography variant="h4" fontWeight={700}>{stats.total}</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, sm: 4 }}>
            <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: '#e6f4ea', color: '#137333' }}>
                  <CheckCircleOutlineIcon fontSize="large" />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Active Subscribers</Typography>
                  <Typography variant="h4" fontWeight={700} sx={{ color: '#137333' }}>{stats.active}</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, sm: 4 }}>
            <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: '#fce8e6', color: '#c5221f' }}>
                  <PauseCircleOutlineIcon fontSize="large" />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Unsubscribed / Paused</Typography>
                  <Typography variant="h4" fontWeight={700} sx={{ color: '#c5221f' }}>{stats.inactive}</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Quick Add Form */}
        <Paper sx={{ p: 3, mb: 4, borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
            Add Single Subscriber
          </Typography>
          <Box component="form" onSubmit={handleSingleAdd}>
            <Grid container spacing={2} alignItems="center">
              <Grid size={{ xs: 12, sm: 3 }}>
                <TextField
                  placeholder="First Name"
                  fullWidth
                  value={newFirstName}
                  onChange={(e) => setNewFirstName(e.target.value)}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                  size="small"
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 3 }}>
                <TextField
                  placeholder="Last Name"
                  fullWidth
                  value={newLastName}
                  onChange={(e) => setNewLastName(e.target.value)}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                  size="small"
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 3 }}>
                <TextField
                  placeholder="Email (required)"
                  type="email"
                  required
                  fullWidth
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                  size="small"
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 3 }} sx={{ display: 'flex', gap: 1.5 }}>
                <TextField
                  placeholder="Phone"
                  fullWidth
                  value={newPhone}
                  onChange={(e) => setNewPhone(e.target.value)}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                  size="small"
                />
                <Button
                  type="submit"
                  variant="contained"
                  disabled={addLoading}
                  sx={{ borderRadius: 2, bgcolor: '#0071e3', textTransform: 'none', px: 3, minWidth: '130px' }}
                >
                  {addLoading ? <CircularProgress size={20} color="inherit" /> : 'Add'}
                </Button>
              </Grid>
            </Grid>
          </Box>
        </Paper>

        {/* Subscriber List & Search */}
        <Paper sx={{ p: 3, borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
          <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Typography variant="h6" fontWeight={600}>
              Parish Subscriber List ({filteredSubscribers.length})
            </Typography>
            <TextField
              placeholder="Search subscribers by name or email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              size="small"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon color="action" />
                  </InputAdornment>
                ),
              }}
              sx={{ minWidth: 320, '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
            />
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
              <CircularProgress color="primary" />
            </Box>
          ) : filteredSubscribers.length === 0 ? (
            <Box sx={{ textAlignment: 'center', py: 6, textAlign: 'center' }}>
              <Typography color="text.secondary">
                {search ? 'No subscribers match your search filter.' : 'No subscribers in database yet. Add your first subscriber above or import your Gmail list.'}
              </Typography>
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: '#fafafa' }}>
                    <TableCell sx={{ fontWeight: 700 }}>Name</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Email Address</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Phone Number</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Date Added</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
                    <TableCell sx={{ fontWeight: 700 }} align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredSubscribers.map((sub) => (
                    <TableRow key={sub.id} hover>
                      <TableCell sx={{ fontWeight: 600 }}>
                        {sub.first_name || sub.last_name
                          ? `${sub.first_name || ''} ${sub.last_name || ''}`.trim()
                          : '—'}
                      </TableCell>
                      <TableCell sx={{ color: '#0071e3', fontWeight: 500 }}>{sub.email}</TableCell>
                      <TableCell sx={{ color: 'text.secondary' }}>{sub.phone || '—'}</TableCell>
                      <TableCell sx={{ color: 'text.secondary' }}>
                        {sub.created_at ? new Date(sub.created_at).toLocaleDateString() : 'N/A'}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={sub.is_active ? 'Active' : 'Unsubscribed'}
                          color={sub.is_active ? 'success' : 'default'}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Stack direction="row" spacing={1} justifyContent="flex-end" alignItems="center">
                          <Switch
                            checked={sub.is_active}
                            onChange={() => handleToggleActive(sub.id, sub.is_active)}
                            color="success"
                            size="small"
                          />
                          <IconButton
                            color="error"
                            size="small"
                            onClick={() => handleDeleteSubscriber(sub.id, sub.email)}
                            title="Remove Subscriber"
                          >
                            <DeleteOutlineIcon fontSize="small" />
                          </IconButton>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>

        {/* Batch Import Dialog */}
        <Dialog open={batchOpen} onClose={() => setBatchOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle sx={{ fontWeight: 700 }}>
            Import Subscribers from Gmail List or CSV
          </DialogTitle>
          <DialogContent>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Paste your raw email list below (separated by line breaks, commas, or semicolons). Duplicates will automatically be skipped.
            </Typography>

            {batchResult && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {batchResult.message}
              </Alert>
            )}

            <TextField
              multiline
              rows={8}
              fullWidth
              placeholder={`john.doe@example.com\nmary.smith@example.com, father.paul@parish.org`}
              value={batchRawInput}
              onChange={(e) => setBatchRawInput(e.target.value)}
              disabled={batchLoading}
              sx={{ fontFamily: 'monospace' }}
            />
          </DialogContent>
          <DialogActions sx={{ px: 3, pb: 2 }}>
            <Button onClick={() => setBatchOpen(false)} disabled={batchLoading}>
              Close
            </Button>
            <Button
              variant="contained"
              onClick={handleBatchImport}
              disabled={batchLoading || !batchRawInput.trim()}
              sx={{ bgcolor: '#0071e3', textTransform: 'none', px: 3 }}
            >
              {batchLoading ? <CircularProgress size={24} color="inherit" /> : 'Import Emails'}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
}
````

## File: .gitignore
````
GEMINI.md
newsletters_to_upload/* 
node_modules/
backend/venv/
.env
.env*.local

# Python cache / bytecode
**/__pycache__/
**/*.pyc
**/*.pyo
**/*.pyd
GRAPH.md

backend/.env.prod
frontend/.env.prod
graphify-out/
````

## File: backend/config.py
````python
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
import logging
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # API Keys
    api_key: str
    openai_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"
    
    # Database Configuration
    database_url: str

    # Google Drive Configuration
    google_service_account_json: Optional[str] = None
    google_drive_folder_id: Optional[str] = None
    
    # SendGrid Configuration
    sendgrid_api_key: Optional[str] = None
    from_email: Optional[str] = None
    
    # Gmail Configuration
    gmail_user: Optional[str] = None
    gmail_app_password: Optional[str] = None
    
    # Cloudflare R2 / S3 Configuration
    r2_endpoint_url: Optional[str] = None
    r2_access_key_id: Optional[str] = None
    r2_secret_access_key: Optional[str] = None
    r2_bucket_name: Optional[str] = None
    r2_public_domain: Optional[str] = None  # Optional: for public URLs

    # LLM Configuration
    max_allowed_tokens: int = 20_000
    llm_strategy: str = "auto"  # Choices: auto, local, remote, groq
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    groq_model: str = "llama-3.3-70b-versatile"
    groq_api_key: Optional[str] = None

    # Application Configuration
    app_name: str = "Newsletter Herald API Gateway"
    debug: bool = False

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # CORS Configuration
    cors_origins: list[str] | str = [
        "https://newsletter-herald.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: any) -> list[str]:
        if isinstance(v, str):
            if not v.strip():
                return []
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        if isinstance(v, list):
            return [origin.strip() for origin in v if isinstance(origin, str) and origin.strip()]
        return []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def configure_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings.
    
    Returns:
        Settings: Application settings loaded from environment variables.
        
    Raises:
        ValueError: If required environment variables are missing.
    """
    configure_logging()
    logger = logging.getLogger("config")
    
    try:
        settings = Settings()
        logger.info(f"Loaded settings for {settings.app_name}")
        return settings
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        raise ValueError(f"Configuration error: {e}. Please check your environment variables.")
````

## File: frontend/app/errors/page.tsx
````typescript
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Stack,
  Divider,
  Breadcrumbs,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  IconButton
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import HomeIcon from '@mui/icons-material/Home';
import EditIcon from '@mui/icons-material/Edit';
import HistoryIcon from '@mui/icons-material/History';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import { useUser, useClerk } from "@clerk/nextjs";
import Link from 'next/link';

interface ErrorNewsletter {
  id: number;
  filename: string;
  drive_link?: string;
  target_sunday?: string;
  title?: string;
  summary?: string;
  status: string;
}

interface UploadLog {
  id: number;
  filename?: string;
  uploader?: string;
  status: string;
  created_at: string;
  error_message?: string;
  drive_link?: string;
}

export default function SystemErrorsPage() {
  return (
    <React.Suspense fallback={<Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>}>
      <SystemErrorsPageContent />
    </React.Suspense>
  );
}

function SystemErrorsPageContent() {
  const { isLoaded, isSignedIn, user } = useUser();
  const { signOut } = useClerk();

  const userEmail = user?.primaryEmailAddress?.emailAddress;

  // Admin Email Whitelist check
  const ADMIN_WHITELIST = ['sallto.newsletter@gmail.com', 'anthony.as.baptiste@gmail.com'];
  const hasAdminAccess = userEmail ? ADMIN_WHITELIST.includes(userEmail) : false;

  const [activeTab, setActiveTab] = useState(0);
  const [errorLogs, setErrorLogs] = useState<ErrorNewsletter[]>([]);
  const [uploadLogs, setUploadLogs] = useState<UploadLog[]>([]);
  const [loadingNewsletters, setLoadingNewsletters] = useState(true);
  const [loadingLogs, setLoadingLogs] = useState(true);
  const [message, setMessage] = useState<string | null>(null);

  // Edit Modal States
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<ErrorNewsletter | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editSummary, setEditSummary] = useState('');
  const [editDate, setEditDate] = useState('');
  const [savingEdit, setSavingEdit] = useState(false);
  const [savingArchive, setSavingArchive] = useState(false);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

  const fetchErrorNewsletters = useCallback(async () => {
    setLoadingNewsletters(true);
    try {
      const response = await fetch(`${backendUrl}/newsletters`, {
        headers: {
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '85fb0ffd7ff26541e6361e5063bdfbde9299f1938a5ffae44d05ff3f9a4dd630',
        },
      });
      if (response.ok) {
        const data = await response.json();
        const failures = (data.newsletters || []).filter((n: ErrorNewsletter) => n.status === 'failed_validation');
        setErrorLogs(failures);
      }
    } catch (err) {
      console.error("Failed to fetch newsletters:", err);
    } finally {
      setLoadingNewsletters(false);
    }
  }, [backendUrl]);

  const fetchUploadLogs = useCallback(async () => {
    setLoadingLogs(true);
    try {
      const response = await fetch(`${backendUrl}/upload-logs`, {
        headers: {
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '85fb0ffd7ff26541e6361e5063bdfbde9299f1938a5ffae44d05ff3f9a4dd630',
        }
      });
      if (response.ok) {
        const data = await response.json();
        setUploadLogs(data.upload_logs || []);
      }
    } catch (err) {
      console.error("Failed to fetch upload logs:", err);
    } finally {
      setLoadingLogs(false);
    }
  }, [backendUrl]);

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      window.location.href = '/';
    }
  }, [isLoaded, isSignedIn]);

  useEffect(() => {
    if (user && hasAdminAccess) {
      fetchErrorNewsletters();
      fetchUploadLogs();
    }
  }, [user, hasAdminAccess, fetchErrorNewsletters, fetchUploadLogs]);

  if (!isLoaded || !isSignedIn) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>;
  }

  if (!hasAdminAccess) {
    return (
      <Box sx={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: '#f5f5f7', p: 3 }}>
        <Paper sx={{ p: 5, maxWidth: 500, width: '100%', textAlign: 'center', borderRadius: 4, boxShadow: '0 8px 30px rgba(0,0,0,0.05)' }}>
          <Box sx={{ width: 64, height: 64, bgcolor: '#fce8e6', color: '#d93025', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto', mb: 3 }}>
            <ErrorOutlineIcon sx={{ fontSize: 32 }} />
          </Box>
          <Typography variant="h5" sx={{ fontWeight: 700, mb: 1, letterSpacing: '-0.01em', color: '#1d1d1f' }}>
            Access Denied
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4, lineHeight: 1.6 }}>
            Your account (<strong>{userEmail}</strong>) is not authorized to access system error logs.
          </Typography>
          <Stack spacing={2} direction="row" justifyContent="center">
            <Button 
              variant="outlined" 
              onClick={() => signOut()} 
              sx={{ borderRadius: '980px', textTransform: 'none', px: 3 }}
            >
              Sign Out
            </Button>
            <Link href="/" style={{ textDecoration: 'none' }}>
              <Button 
                variant="contained" 
                sx={{ borderRadius: '980px', textTransform: 'none', px: 3, bgcolor: '#0071e3', '&:hover': { bgcolor: '#0077ed' } }}
              >
                Go to Dashboard
              </Button>
            </Link>
          </Stack>
        </Paper>
      </Box>
    );
  }

  const handleApprove = async (id: number) => {
    try {
      const res = await fetch(`${backendUrl}/newsletters/${id}/approve`);
      if (res.ok) {
        setMessage("Newsletter approved and scheduled successfully!");
        fetchErrorNewsletters();
      } else {
        alert("Failed to approve newsletter.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleReject = async (id: number) => {
    if (!confirm("Are you sure you want to archive this validation failure?")) return;
    try {
      const res = await fetch(`${backendUrl}/newsletters/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '85fb0ffd7ff26541e6361e5063bdfbde9299f1938a5ffae44d05ff3f9a4dd630',
        },
        body: JSON.stringify({ status: 'superseded' }),
      });
      if (res.ok) {
        setMessage("Newsletter archived successfully.");
        fetchErrorNewsletters();
      } else {
        alert("Failed to archive newsletter.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const openEditModal = (item: ErrorNewsletter) => {
    setEditingItem(item);
    setEditTitle(item.title || '');
    setEditSummary(item.summary || '');
    setEditDate(item.target_sunday ? item.target_sunday.split('T')[0] : '');
    setEditModalOpen(true);
  };

  const handleSaveAndApprove = async () => {
    if (!editingItem) return;
    setSavingEdit(true);
    try {
      // 1. Update the target Sunday, title, and summary
      const response = await fetch(`${backendUrl}/newsletters/${editingItem.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '85fb0ffd7ff26541e6361e5063bdfbde9299f1938a5ffae44d05ff3f9a4dd630',
        },
        body: JSON.stringify({
          title: editTitle,
          summary: editSummary,
          target_sunday: editDate || null,
          status: 'draft' // Revert to draft first to enable approval
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to update details");
      }

      // 2. Approve/schedule it
      const approveRes = await fetch(`${backendUrl}/newsletters/${editingItem.id}/approve`);
      if (approveRes.ok) {
        setMessage(`Successfully corrected details and approved "${editTitle}"!`);
        setEditModalOpen(false);
        fetchErrorNewsletters();
      } else {
        alert("Saved details, but failed to approve automatically.");
      }
    } catch (err) {
      const error = err as Error;
      alert(`Error updating newsletter: ${error.message}`);
    } finally {
      setSavingEdit(false);
    }
  };

  const handleSaveArchiveOnly = async () => {
    if (!editingItem) return;
    setSavingArchive(true);
    try {
      // Update details and set status directly to 'delivered' and delivered to true
      const response = await fetch(`${backendUrl}/newsletters/${editingItem.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '85fb0ffd7ff26541e6361e5063bdfbde9299f1938a5ffae44d05ff3f9a4dd630',
        },
        body: JSON.stringify({
          title: editTitle,
          summary: editSummary,
          target_sunday: editDate || null,
          status: 'delivered',
          delivered: true
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to archive details");
      }

      setMessage(`Successfully archived "${editTitle}" directly without scheduling!`);
      setEditModalOpen(false);
      fetchErrorNewsletters();
    } catch (err) {
      const error = err as Error;
      alert(`Error archiving newsletter: ${error.message}`);
    } finally {
      setSavingArchive(false);
    }
  };

  return (
    <Box sx={{ minHeight: '90vh', bgcolor: '#f5f5f7', py: 6 }}>
      <Container maxWidth="lg">
        {/* Navigation Breadcrumbs */}
        <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 3 }}>
          <Link href="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', color: '#86868b' }}>
            <HomeIcon sx={{ mr: 0.5, fontSize: 16 }} />
            Dashboard
          </Link>
          <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center', fontWeight: 600 }}>
            <WarningIcon sx={{ mr: 0.5, fontSize: 16, color: '#d93025' }} />
            System Errors & Ingest Logs
          </Typography>
        </Breadcrumbs>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4, flexWrap: 'wrap', gap: 2 }}>
          <Box>
            <Typography variant="h4" fontWeight={800} sx={{ letterSpacing: '-0.02em', color: '#1d1d1f' }}>
              System Ingestion & Errors
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Monitor batch and manual document uploads, and rectify target-date mismatch validation failures.
            </Typography>
          </Box>
          <Link href="/" style={{ textDecoration: 'none' }}>
            <Button startIcon={<ArrowBackIcon />} variant="outlined" sx={{ borderRadius: '100px', textTransform: 'none' }}>
              Back to Dashboard
            </Button>
          </Link>
        </Box>

        {message && (
          <Alert severity="success" sx={{ mb: 3, borderRadius: 2 }} onClose={() => setMessage(null)}>
            {message}
          </Alert>
        )}

        {/* Tab System */}
        <Paper sx={{ borderRadius: 3, mb: 4, overflow: 'hidden', boxShadow: '0 4px 12px rgba(0,0,0,0.02)' }}>
          <Tabs
            value={activeTab}
            onChange={(_, val) => setActiveTab(val)}
            indicatorColor="primary"
            textColor="primary"
            variant="fullWidth"
            sx={{ borderBottom: '1px solid #e0e0e0', bgcolor: 'white' }}
          >
            <Tab 
              icon={<WarningIcon sx={{ fontSize: 18 }} />} 
              iconPosition="start" 
              label={`Validation Failures (${errorLogs.length})`} 
              sx={{ textTransform: 'none', fontWeight: 700, minHeight: 60 }} 
            />
            <Tab 
              icon={<HistoryIcon sx={{ fontSize: 18 }} />} 
              iconPosition="start" 
              label={`Ingestion/Upload Logs (${uploadLogs.length})`} 
              sx={{ textTransform: 'none', fontWeight: 700, minHeight: 60 }} 
            />
          </Tabs>
        </Paper>

        {/* Tab Panel: Validation Failures */}
        {activeTab === 0 && (
          loadingNewsletters ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
              <CircularProgress />
            </Box>
          ) : errorLogs.length === 0 ? (
            <Paper sx={{ p: 6, textAlign: 'center', borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.02)' }}>
              <CheckCircleIcon sx={{ fontSize: 60, color: '#137333', mb: 2 }} />
              <Typography variant="h6" fontWeight={700}>
                No Validation Failures
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                All ingested bulletins matched the schedule target Sunday successfully.
              </Typography>
            </Paper>
          ) : (
            <Grid container spacing={3}>
              {errorLogs.map((item) => (
                <Grid size={{ xs: 12, md: 6 }} key={item.id}>
                  <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.03)', border: '1px solid #fce8e6', bgcolor: '#fdf7f7', height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <CardContent sx={{ p: 3, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <Typography variant="subtitle1" fontWeight={700} color="error" sx={{ wordBreak: 'break-all', mr: 2 }}>
                          {item.filename}
                        </Typography>
                        {item.drive_link && (
                          <IconButton size="small" href={item.drive_link} target="_blank" title="View File">
                            <OpenInNewIcon fontSize="small" />
                          </IconButton>
                        )}
                      </Box>
                      <Divider sx={{ my: 1.5, borderColor: '#fce8e6' }} />
                      
                      <Box sx={{ mb: 3, flexGrow: 1 }}>
                        <Typography variant="body2" sx={{ color: '#d93025', fontWeight: 700, mb: 1 }}>
                          ⚠️ Target Date Mismatch
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#5f6368', lineHeight: 1.6 }}>
                          The extracted target Sunday is <strong>{item.target_sunday ? new Date(item.target_sunday + 'T00:00:00Z').toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' }) : 'Unknown'}</strong>, which does not match the expected next Sunday. This usually happens when uploading older historical newsletters or if the file content dates are scanned/unreadable.
                        </Typography>
                      </Box>

                      <Stack direction="row" spacing={1.5} flexWrap="wrap" gap={1} sx={{ mt: 'auto' }}>
                        <Button
                          variant="contained"
                          color="primary"
                          size="small"
                          startIcon={<EditIcon />}
                          onClick={() => openEditModal(item)}
                          sx={{ textTransform: 'none', borderRadius: 2, boxShadow: 'none', '&:hover': { boxShadow: 'none' } }}
                        >
                          Edit & Approve
                        </Button>
                        <Button
                          variant="outlined"
                          color="success"
                          size="small"
                          startIcon={<CheckCircleIcon />}
                          onClick={() => handleApprove(item.id)}
                          sx={{ textTransform: 'none', borderRadius: 2 }}
                        >
                          Approve Anyway
                        </Button>
                        <Button
                          variant="outlined"
                          color="error"
                          size="small"
                          startIcon={<CancelIcon />}
                          onClick={() => handleReject(item.id)}
                          sx={{ textTransform: 'none', borderRadius: 2 }}
                        >
                          Archive
                        </Button>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )
        )}

        {/* Tab Panel: Ingestion/Upload Logs */}
        {activeTab === 1 && (
          loadingLogs ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
              <CircularProgress />
            </Box>
          ) : uploadLogs.length === 0 ? (
            <Paper sx={{ p: 6, textAlign: 'center', borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.02)' }}>
              <HistoryIcon sx={{ fontSize: 60, color: '#86868b', mb: 2 }} />
              <Typography variant="h6" fontWeight={700}>
                No Upload Logs Available
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Logs will populate as documents are uploaded manually or via batch processes.
              </Typography>
            </Paper>
          ) : (
            <TableContainer component={Paper} sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.02)', overflow: 'hidden' }}>
              <Table>
                <TableHead sx={{ bgcolor: '#f5f5f7' }}>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 700 }}>Filename</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Uploader</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Time</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Error Details</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {uploadLogs.map((log) => (
                    <TableRow key={log.id} hover>
                      <TableCell sx={{ fontWeight: 600, wordBreak: 'break-all', maxWidth: 300 }}>{log.filename}</TableCell>
                      <TableCell>
                        <Chip 
                          label={log.uploader} 
                          size="small" 
                          variant="outlined" 
                          color={log.uploader === 'local_batch_upload' ? 'secondary' : 'default'}
                        />
                      </TableCell>
                      <TableCell sx={{ whiteSpace: 'nowrap' }}>
                        {log.created_at ? new Date(log.created_at).toLocaleString() : ''}
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={log.status === 'success' ? <CheckCircleIcon /> : <ErrorOutlineIcon />}
                          label={log.status.toUpperCase()}
                          color={log.status === 'success' ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell sx={{ color: '#d93025', fontSize: '0.85rem', maxWidth: 400, wordBreak: 'break-word' }}>
                        {log.error_message || '—'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )
        )}
      </Container>

      {/* Edit Date & Details Dialog Modal */}
      <Dialog open={editModalOpen} onClose={() => setEditModalOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 700 }}>
          Edit & Approve Validation Failure
        </DialogTitle>
        <DialogContent dividers>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Manually correct the schedule target Sunday and details extracted by AI. Saving will override validation and publish the newsletter on the selected Sunday.
          </Typography>

          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField
              label="Target Sunday (Schedule Date)"
              type="date"
              fullWidth
              value={editDate}
              onChange={(e) => setEditDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              helperText="The specific Sunday liturgical date for this newsletter bulletin issue."
            />
            <TextField
              label="Liturgical Title"
              fullWidth
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              placeholder="e.g. 1st Sunday of Advent"
            />
            <TextField
              label="Weekly Summary Narrative"
              fullWidth
              multiline
              rows={5}
              value={editSummary}
              onChange={(e) => setEditSummary(e.target.value)}
              placeholder="Enter the 2-paragraph highlight summary for parishioners..."
            />
          </Stack>
        </DialogContent>
        <DialogActions sx={{ p: 3, justifyContent: 'space-between' }}>
          <Button onClick={() => setEditModalOpen(false)} color="inherit" sx={{ borderRadius: '100px', textTransform: 'none' }}>
            Cancel
          </Button>
          <Stack direction="row" spacing={2}>
            <Button
              onClick={handleSaveArchiveOnly}
              variant="outlined"
              color="primary"
              disabled={savingEdit || savingArchive || !editDate}
              sx={{ borderRadius: '100px', textTransform: 'none' }}
            >
              {savingArchive ? <CircularProgress size={20} color="inherit" /> : 'Archive Only (No Email)'}
            </Button>
            <Button
              onClick={handleSaveAndApprove}
              variant="contained"
              color="primary"
              disabled={savingEdit || savingArchive || !editDate}
              sx={{ borderRadius: '100px', textTransform: 'none', px: 4 }}
            >
              {savingEdit ? <CircularProgress size={20} color="inherit" /> : 'Save & Schedule Email'}
            </Button>
          </Stack>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
````

## File: CHANGELOG.md
````markdown
# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [0.1.5](https://github.com/AnthonyASBaptiste/newsletter-herald/compare/v0.1.4...v0.1.5) (2026-08-07)


### Features

* add infinite loading and thumbnail caching ([da1b6ac](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/da1b6acdc093caaa3abfe2d91389b818d17d1958))


### Bug Fixes

* implement Missing Authentication on Newsletter Retrieval Endpoint ([8f3425c](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/8f3425ca02c9e83c35cdffd56d3dae3e2d7ee883))

### [0.1.4](https://github.com/AnthonyASBaptiste/newsletter-herald/compare/v0.1.3...v0.1.4) (2026-07-30)


### Features

* Add Eval/Demo mode with immediate preview dispatch to allow testing app ([5206a2c](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/5206a2c668976fa05af476096139acfd079cd6a7))

### [0.1.3](https://github.com/AnthonyASBaptiste/newsletter-herald/compare/v0.1.2...v0.1.3) (2026-07-30)

### [0.1.2](https://github.com/AnthonyASBaptiste/newsletter-herald/compare/v0.1.1...v0.1.2) (2026-07-30)


### Features

* add advanced scheduling and email content editor for upcoming newsletters ([4100f6c](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/4100f6cc249cbd33f0c686a177d7833c39d792ca))
* implement Pydantic settings configuration and update .gitignore to exclude production environment files ([c32798a](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/c32798a154db925a52b0383cc4660744832c4d9c))
* implement pydantic-based configuration management with environment variable validation and add sample frontend environment variables ([bf76cc9](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/bf76cc92b4dc4670660b72b14db3f959cbe05093))

### 0.1.1 (2026-07-26)


### Features

* add Clerk middleware and implement authenticated admin dashboard in HomeContent ([33de813](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/33de8132c2cd8bba7f8a509674be8a22643aa67f))
* **dependencies:** add Tailwind CSS WASM dependencies to package-lock.json ([23df844](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/23df844c045e36f1a03887333800de6f45b849e9))
* **frontend:** initialize frontend project with Next.js, TypeScript, and Tailwind CSS ([eee4477](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/eee44772dfdc3a2f90a867c79411aab38af2e325))
* gate docs page behind Clerk auth, render navigation link conditionally ([e2f6c84](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/e2f6c84ec2494bc4b6da9e341fc17b5ed9109f00))
* implement backend newsletter processing pipeline and frontend summary dashboard ([d1f73ba](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/d1f73ba51f31048205a79d956ae7deaeb25f7942))
* Implement initial full-stack application for newsletter processing and summarization. ([b189668](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/b1896680b5321a7eb39fb680729d2d2002e588a6))
* implement newsletter management system with frontend preview mode and backend file processing utilities ([e242d72](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/e242d724e5ec1f82bcdf67eefa625c733f38162f))
* initialize frontend environment template and git ignore rules ([4ca8e6a](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/4ca8e6a054b2229775d499ec12be2912313cd427))
* move admin manual to frontend/docs, add changelog, and implement docs page ([eec50f6](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/eec50f68b28a666af891c431351f202e9c8a56e6))


### Bug Fixes

* add missing boto3 and google api dependencies to requirements.txt ([195347d](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/195347d2b8e5c807f515ac500a35a811bdbeda01))
* resolve frontend Grid compilation errors and stack frame projectId typos ([546e124](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/546e124e4bd31c0ec44d06e822091bb7f5d075f8))
* resolve redirect URL dynamically in approve and regenerate html ([4f26df2](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/4f26df23d80dc549f92868dd79a48189989d8ffa))
* resolve vercel build errors and linter warnings ([76af155](https://github.com/AnthonyASBaptiste/newsletter-herald/commit/76af1550f5289f2be3e42a637643ff82f2bdef3a))
````

## File: package.json
````json
{
  "name": "newsletter-herald",
  "version": "0.1.5",
  "description": "Roman Catholic church newsletter summarization and delivery system",
  "scripts": {
    "dev:backend": "cd backend && .\\venv\\Scripts\\python -m uvicorn main:app --reload",
    "dev:frontend": "cd frontend && npm run dev",
    "start": "npx concurrently \"npm run dev:backend\" \"npm run dev:frontend\"",
    "install:all": "npm install",
    "release": "standard-version",
    "release:patch": "standard-version --release-as patch",
    "release:minor": "standard-version --release-as minor",
    "release:major": "standard-version --release-as major",
    "release:revert": "git tag -d v$(node -p \"require('./package.json').version\") && git reset --hard HEAD~1"
  },
  "devDependencies": {
    "concurrently": "^8.2.2",
    "standard-version": "^9.5.0"
  }
}
````

## File: frontend/app/layout.tsx
````typescript
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AppRouterCacheProvider } from '@mui/material-nextjs/v16-appRouter';
import { ThemeProvider } from '@mui/material/styles';
import theme from './theme';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Link from 'next/link';
import { ClerkProvider } from "@clerk/nextjs";
import AuthButtons from "./components/AuthButtons";
import React from "react";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Newsletter Herald — AI-Powered Catholic Church Bulletin Summaries",
  description: "Newsletter Herald automatically parses Roman Catholic parish bulletins, extracts theological and calendar metadata, generates warm AI summaries, and schedules weekly email delivery to parishioners.",
  keywords: ["Newsletter Herald", "Catholic Church Newsletter", "Parish Bulletin Summarizer", "Liturgical AI", "Anthony Baptiste"],
  authors: [{ name: "Anthony Baptiste", url: "https://anthonybaptiste.dev" }],
  creator: "Anthony Baptiste",
  metadataBase: new URL("https://newsletter-herald.vercel.app"),
  openGraph: {
    title: "Newsletter Herald — AI-Powered Catholic Church Bulletin Summaries",
    description: "Automated bulletin processing, theological summary generation, and parishioner email scheduling.",
    url: "https://newsletter-herald.vercel.app",
    siteName: "Newsletter Herald",
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Newsletter Herald",
    description: "Automated parish bulletin summarization & weekly email dispatch.",
    creator: "@anthonybaptiste",
  },
  icons: {
    icon: [
      { url: '/favicon.ico' },
      { url: '/favicon-96x96.png', sizes: '96x96', type: 'image/png' },
      { url: '/icon.svg', type: 'image/svg+xml' },
    ],
    shortcut: '/favicon.ico',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
};


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="en">
        <head>
          <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{
              __html: JSON.stringify({
                "@context": "https://schema.org",
                "@type": "SoftwareApplication",
                "name": "Newsletter Herald",
                "applicationCategory": "BusinessApplication",
                "operatingSystem": "Web",
                "description": "Automated liturgical newsletter pipeline and Roman Catholic church bulletin summarization platform.",
                "author": {
                  "@type": "Person",
                  "name": "Anthony Baptiste",
                  "url": "https://anthonybaptiste.dev"
                },
                "creator": {
                  "@type": "Person",
                  "name": "Anthony Baptiste",
                  "url": "https://anthonybaptiste.dev"
                },
                "url": "https://newsletter-herald.vercel.app"
              })
            }}
          />
        </head>
        <body
          className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        >
          <AppRouterCacheProvider>
            <ThemeProvider theme={theme}>
              <CssBaseline />
              <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: 'background.default' }}>
                <AppBar position="sticky" elevation={0} sx={{ bgcolor: 'white', color: 'black', borderBottom: '1px solid #e0e0e0' }}>
                  <Container maxWidth="lg">
                    <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 0, sm: 2 } }}>
                      <Link href="/" style={{ textDecoration: 'none', color: 'inherit' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="h6" component="div" sx={{ fontWeight: 800, letterSpacing: '-0.02em' }}>
                            HERALD
                          </Typography>
                        </Box>
                      </Link>
                      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                        <React.Suspense fallback={<Box sx={{ width: 100 }} />}>
                          <AuthButtons />
                        </React.Suspense>
                      </Box>
                    </Toolbar>
                  </Container>
                </AppBar>
                <main style={{ flexGrow: 1 }}>
                  {children}
                </main>
                <Box component="footer" sx={{ py: 6, bgcolor: 'white', mt: 'auto', borderTop: '1px solid #e0e0e0' }}>
                  <Container maxWidth="lg">
                    <Typography variant="body2" color="text.secondary" align="center">
                      © {new Date().getFullYear()} Newsletter Herald. Built with ❤️ by{' '}
                      <a 
                        href="https://anthonybaptiste.dev" 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        style={{ color: '#0071e3', textDecoration: 'none', fontWeight: 600 }}
                      >
                        Anthony
                      </a>{' '}
                      for our community.
                    </Typography>
                  </Container>
                </Box>
              </Box>
            </ThemeProvider>
          </AppRouterCacheProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
````

## File: frontend/app/HomeContent.tsx
````typescript
'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Button, 
  Paper, 
  Grid, 
  CircularProgress,
  Fade,
  Alert,
  Stack,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Card,
  CardContent,
  TextField,
  Divider,
  Switch,
  FormControlLabel
} from '@mui/material';
import ArticleIcon from '@mui/icons-material/Article';
import CloseIcon from '@mui/icons-material/Close';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import RefreshIcon from '@mui/icons-material/Refresh';
import WarningIcon from '@mui/icons-material/Warning';
import DownloadIcon from '@mui/icons-material/Download';
import PeopleIcon from '@mui/icons-material/People';
import ScheduleIcon from '@mui/icons-material/Schedule';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import EditIcon from '@mui/icons-material/Edit';
import SendIcon from '@mui/icons-material/Send';
import ArchiveIcon from '@mui/icons-material/Archive';
import { useUser, useClerk } from "@clerk/nextjs";
import Link from "next/link";

interface Newsletter {
  id: number;
  filename?: string;
  drive_link?: string;
  target_sunday?: string;
  uploaded_at?: string;
  title?: string;
  summary?: string;
  status: string;
  tags?: string;
  thumbnail_id?: string;
  scheduled_at?: string;
}

interface SummaryResponse {
  newsletter_id?: number;
  schedule_date?: string;
  liturgical_season?: string;
  calendar_year?: number;
  title?: string;
  summary?: string;
}



export function HomeContent({ forcePublic = false }: { forcePublic?: boolean }) {
  const { isSignedIn, user: clerkUser } = useUser();
  const { signOut } = useClerk();
  
  const user = (forcePublic || !isSignedIn) ? null : clerkUser;
  const userEmail = clerkUser?.primaryEmailAddress?.emailAddress;

  // Admin Email Whitelist check
  const ADMIN_WHITELIST = ['sallto.newsletter@gmail.com', 'anthony.as.baptiste@gmail.com'];
  const hasAdminAccess = !user || (userEmail && ADMIN_WHITELIST.includes(userEmail));

  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [, setSummary] = useState<SummaryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [publicNewsletters, setPublicNewsletters] = useState<Newsletter[]>([]);
  const [fetchingNewsletters, setFetchingNewsletters] = useState(false);
  const [subscribersCount, setSubscribersCount] = useState(0);

  // New state for confirmation and editing
  const [, setScheduleDate] = useState("");
  const [, setTags] = useState("");
  
  // Modal state for viewing summaries
  const [selectedNewsletter, setSelectedNewsletter] = useState<Newsletter | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  // Upload Modal State
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [evalDemoMode, setEvalDemoMode] = useState(false);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);

  // Edit Schedule Modal State
  const [editScheduledOpen, setEditScheduledOpen] = useState(false);
  const [editScheduledTitle, setEditScheduledTitle] = useState("");
  const [editScheduledSummary, setEditScheduledSummary] = useState("");
  const [editScheduledDate, setEditScheduledDate] = useState("");
  const [editScheduledTime, setEditScheduledTime] = useState("");
  const [editScheduledSaving, setEditScheduledSaving] = useState(false);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

  // Infinite scroll & Pagination state
  const INITIAL_BATCH = 6;
  const SCROLL_BATCH = 3;

  const [visibleCount, setVisibleCount] = useState<number>(INITIAL_BATCH);
  const [loadingMore, setLoadingMore] = useState<boolean>(false);
  const [hasMoreBackend, setHasMoreBackend] = useState<boolean>(true);
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  const fetchNewsletters = useCallback(async () => {
    setFetchingNewsletters(true);
    try {
      const url = user 
        ? `${backendUrl}/newsletters`
        : `${backendUrl}/newsletters?limit=${INITIAL_BATCH}&offset=0`;

      const response = await fetch(url, {
        headers: {
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '',
        },
      });
      if (response.ok) {
        const data = await response.json();
        setPublicNewsletters(data.newsletters || []);
        if (!user) {
          setHasMoreBackend(data.has_more ?? false);
        }
      }
    } catch (err) {
      console.error("Failed to fetch newsletters:", err);
    } finally {
      setFetchingNewsletters(false);
    }
  }, [backendUrl, user]);

  const fetchMoreNewsletters = useCallback(async () => {
    if (loadingMore || !hasMoreBackend) return;
    setLoadingMore(true);
    try {
      const currentOffset = publicNewsletters.length;
      const response = await fetch(
        `${backendUrl}/newsletters?limit=${SCROLL_BATCH}&offset=${currentOffset}`,
        {
          headers: {
            'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '',
          },
        }
      );
      if (response.ok) {
        const data = await response.json();
        const newItems: Newsletter[] = data.newsletters || [];
        setHasMoreBackend(data.has_more ?? false);
        setPublicNewsletters((prev) => {
          const existingIds = new Set(prev.map((n) => n.id));
          const uniqueNew = newItems.filter((n) => !existingIds.has(n.id));
          return [...prev, ...uniqueNew];
        });
        setVisibleCount((prev) => prev + newItems.length);
      }
    } catch (err) {
      console.error("Failed to load more newsletters:", err);
    } finally {
      setLoadingMore(false);
    }
  }, [backendUrl, loadingMore, hasMoreBackend, publicNewsletters.length]);

  useEffect(() => {
    setVisibleCount(INITIAL_BATCH);
  }, [selectedTag]);

  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const first = entries[0];
        if (first.isIntersecting && !fetchingNewsletters && !loadingMore) {
          if (!user && hasMoreBackend) {
            fetchMoreNewsletters();
          } else {
            setVisibleCount((prev) => prev + SCROLL_BATCH);
          }
        }
      },
      { rootMargin: '200px', threshold: 0.1 }
    );

    observer.observe(sentinel);
    return () => observer.unobserve(sentinel);
  }, [fetchingNewsletters, loadingMore, hasMoreBackend, user, fetchMoreNewsletters]);

  const fetchSubscribersCount = useCallback(async () => {
    try {
      const res = await fetch(`${backendUrl}/subscribers`);
      if (res.ok) {
        const data = await res.json();
        setSubscribersCount(data.stats?.active || 0);
      }
    } catch (err) {
      console.error("Failed to fetch subscribers stats:", err);
    }
  }, [backendUrl]);

  useEffect(() => {
    fetchNewsletters();
    if (user) {
      fetchSubscribersCount();
    }
  }, [user, fetchNewsletters, fetchSubscribersCount]);

  if (user && !hasAdminAccess) {
    return (
      <Box sx={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: '#f5f5f7', p: 3 }}>
        <Paper sx={{ p: 5, maxWidth: 500, width: '100%', textAlign: 'center', borderRadius: 4, boxShadow: '0 8px 30px rgba(0,0,0,0.05)' }}>
          <Box sx={{ width: 64, height: 64, bgcolor: '#fce8e6', color: '#d93025', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto', mb: 3 }}>
            <WarningIcon sx={{ fontSize: 32 }} />
          </Box>
          <Typography variant="h5" sx={{ fontWeight: 700, mb: 1, letterSpacing: '-0.01em', color: '#1d1d1f' }}>
            Access Denied
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4, lineHeight: 1.6 }}>
            Your account (<strong>{userEmail}</strong>) is not authorized as an administrator for Newsletter Herald.
          </Typography>
          <Stack spacing={2} direction="row" justifyContent="center">
            <Button 
              variant="outlined" 
              onClick={() => signOut()} 
              sx={{ borderRadius: '980px', textTransform: 'none', px: 3 }}
            >
              Sign Out
            </Button>
            <Link href="/?forcePublic=true" style={{ textDecoration: 'none' }}>
              <Button 
                variant="contained" 
                sx={{ borderRadius: '980px', textTransform: 'none', px: 3, bgcolor: '#0071e3', '&:hover': { bgcolor: '#0077ed' } }}
              >
                View Public Feed
              </Button>
            </Link>
          </Stack>
        </Paper>
      </Box>
    );
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    setLoading(true);
    setError(null);
    setSummary(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${backendUrl}/upload-document`, {
        method: 'POST',
        body: formData,
        headers: {
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '', 
          'X-User-Email': userEmail || 'anonymous',
          'X-Demo-Mode': evalDemoMode ? 'true' : 'false',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload document');
      }

      const data = await response.json();
      setSummary(data.summary);
      
      // Initialize edit fields from AI response
      setScheduleDate(data.summary.schedule_date || '');
      
      // Construct initial tags from liturgical info
      const tagsList = [];
      if (data.summary.liturgical_season) tagsList.push(data.summary.liturgical_season.toLowerCase().replace(" ", "-"));
      if (data.summary.calendar_year) tagsList.push(String(data.summary.calendar_year));
      
      setTags(tagsList.join(', '));
      setUploadModalOpen(false); // Close modal on success
      setFile(null); // Clear selected file

      if (data.summary?.demo_mode) {
        alert(`🧪 [DEMO / PREVIEW MODE ACTIVE]\n\nNewsletter uploaded & immediate preview email sent!\nRecipient: ${data.summary.demo_recipient || userEmail || 'your email'}\nSubject: [DEMO/PREVIEW] ${data.summary.title}`);
      }
    } catch (err) {
      const error = err as Error;
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSchedule = async (id: number) => {
    if (!confirm("Are you sure you want to cancel the scheduled delivery? The newsletter will revert to draft status.")) return;
    try {
      const response = await fetch(`${backendUrl}/newsletters/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '',
        },
        body: JSON.stringify({ status: 'draft' }),
      });
      if (response.ok) {
        alert("Delivery canceled. Newsletter reverted to drafts.");
        fetchNewsletters();
      } else {
        alert("Failed to cancel schedule.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleApprove = async (id: number) => {
    try {
      const res = await fetch(`${backendUrl}/newsletters/${id}/approve`);
      if (res.ok) {
        alert("Newsletter approved and scheduled for Sunday morning!");
        fetchNewsletters();
      } else {
        alert("Failed to approve newsletter.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleRegenerate = async (id: number) => {
    try {
      const res = await fetch(`${backendUrl}/newsletters/${id}/regenerate`);
      if (res.ok) {
        alert("AI summary regenerated successfully!");
        fetchNewsletters();
      } else {
        alert("Failed to regenerate summary.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleReject = async (id: number) => {
    if (!confirm("Are you sure you want to reject and supersede this newsletter summary?")) return;
    try {
      const res = await fetch(`${backendUrl}/newsletters/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '',
        },
        body: JSON.stringify({ status: 'superseded' }),
      });
      if (res.ok) {
        fetchNewsletters();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSendNow = async (id: number) => {
    if (!confirm("Are you sure you want to send this newsletter immediately to all active subscribers?")) return;
    try {
      const res = await fetch(`${backendUrl}/newsletters/${id}/send-now`, {
        method: 'POST',
        headers: {
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '',
        },
      });
      if (res.ok) {
        const data = await res.json();
        alert(data.message || "Newsletter sent successfully!");
        fetchNewsletters();
      } else {
        const errData = await res.json().catch(() => ({}));
        alert(errData.detail || "Failed to send newsletter.");
      }
    } catch (err) {
      console.error(err);
      alert("Error triggering immediate send.");
    }
  };

  const handleArchive = async (id: number) => {
    if (!confirm("Are you sure you want to archive this newsletter? It will be removed from active processing.")) return;
    try {
      const res = await fetch(`${backendUrl}/newsletters/${id}/archive`, {
        method: 'POST',
        headers: {
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '',
        },
      });
      if (res.ok) {
        alert("Newsletter archived successfully!");
        fetchNewsletters();
      } else {
        alert("Failed to archive newsletter.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleOpenEditScheduled = (newsletter: Newsletter) => {
    setEditScheduledTitle(newsletter.title || "");
    setEditScheduledSummary(newsletter.summary || "");
    
    // Parse scheduled_at if set, otherwise default to target_sunday at 08:00
    if (newsletter.scheduled_at) {
      try {
        const dt = new Date(newsletter.scheduled_at);
        const year = dt.getFullYear();
        const month = String(dt.getMonth() + 1).padStart(2, '0');
        const date = String(dt.getDate()).padStart(2, '0');
        const hours = String(dt.getHours()).padStart(2, '0');
        const minutes = String(dt.getMinutes()).padStart(2, '0');
        
        setEditScheduledDate(`${year}-${month}-${date}`);
        setEditScheduledTime(`${hours}:${minutes}`);
      } catch (e) {
        console.error("Failed to parse scheduled_at date", e);
        setEditScheduledDate(newsletter.target_sunday || "");
        setEditScheduledTime("08:00");
      }
    } else if (newsletter.target_sunday) {
      setEditScheduledDate(newsletter.target_sunday);
      setEditScheduledTime("08:00");
    } else {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const date = String(today.getDate()).padStart(2, '0');
      setEditScheduledDate(`${year}-${month}-${date}`);
      setEditScheduledTime("08:00");
    }
    setEditScheduledOpen(true);
  };

  const handleSaveScheduledChanges = async (id: number) => {
    if (!editScheduledDate || !editScheduledTime) {
      alert("Please select both a date and a time for scheduling.");
      return;
    }
    setEditScheduledSaving(true);
    try {
      const scheduledAtStr = `${editScheduledDate}T${editScheduledTime}:00`;
      
      const response = await fetch(`${backendUrl}/newsletters/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_INTERNAL_API_KEY || '',
        },
        body: JSON.stringify({
          title: editScheduledTitle,
          summary: editScheduledSummary,
          scheduled_at: scheduledAtStr,
          target_sunday: editScheduledDate
        }),
      });
      if (response.ok) {
        alert("Newsletter schedule and content updated successfully!");
        setEditScheduledOpen(false);
        fetchNewsletters();
      } else {
        alert("Failed to save changes.");
      }
    } catch (err) {
      console.error(err);
      alert("Error saving changes.");
    } finally {
      setEditScheduledSaving(false);
    }
  };

  // Filter lists for dashboard
  const pendingApprovals = publicNewsletters.filter(n => n.status === 'draft');
  const errorLogs = publicNewsletters.filter(n => n.status === 'failed_validation');
  
  // Find latest scheduled newsletter
  const scheduledNewsletters = publicNewsletters.filter(n => n.status === 'scheduled');
  const latestScheduled = scheduledNewsletters.length > 0 ? scheduledNewsletters[0] : null;

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f7' }}>
      
      {/* 1. PUBLIC HERO SECTION (Only visible if NOT logged in) */}
      {!user && (
        <Box 
          sx={{ 
            pt: { xs: 8, md: 12 }, 
            pb: { xs: 8, md: 10 }, 
            bgcolor: 'white',
            borderBottom: '1px solid #e0e0e0',
            textAlign: 'center'
          }}
        >
          <Container maxWidth="md">
            <Fade in timeout={800}>
              <Box>
                <Typography 
                  variant="h1" 
                  sx={{ 
                    fontSize: { xs: '2.5rem', md: '4rem' }, 
                    mb: 2,
                    letterSpacing: '-0.04em',
                    fontWeight: 800
                  }}
                >
                  Stay Connected with <br /> 
                  <Box component="span" sx={{ color: '#0071e3' }}>Your Parish.</Box>
                </Typography>
                <Typography 
                  variant="h6" 
                  color="text.secondary" 
                  sx={{ mb: 6, fontWeight: 400, maxWidth: '600px', mx: 'auto' }}
                >
                  Read the latest church newsletters and stay up to date with 
                  community events, prayers, and announcements.
                </Typography>
              </Box>
            </Fade>

            <Box sx={{ maxWidth: '600px', mx: 'auto' }}>
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center">
                <Link href="/signup" style={{ textDecoration: 'none' }}>
                  <Button 
                    variant="contained" 
                    color="primary" 
                    size="large"
                    sx={{ 
                      borderRadius: '100px', 
                      px: 6, 
                      py: 2, 
                      fontSize: '1.1rem', 
                      width: { xs: '100%', sm: 'auto' },
                      textTransform: 'none',
                      boxShadow: 'none',
                      '&:hover': { boxShadow: 'none' }
                    }}
                  >
                    Join Mailing List
                  </Button>
                </Link>
                <Button 
                  variant="outlined" 
                  color="primary" 
                  size="large"
                  sx={{ borderRadius: '100px', px: 6, py: 2, fontSize: '1.1rem', width: { xs: '100%', sm: 'auto' }, textTransform: 'none' }}
                  onClick={() => document.getElementById('newsletters-feed')?.scrollIntoView({ behavior: 'smooth' })}
                >
                  Browse Newsletters
                </Button>
              </Stack>
            </Box>
          </Container>
        </Box>
      )}

      {/* 2. AUTHENTICATED CONSOLE HEADER (Only visible if logged in) */}
      {user && (
        <Box sx={{ pt: 5, pb: 2, bgcolor: 'white', borderBottom: '1px solid #e0e0e0' }}>
          <Container maxWidth="lg">
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
              <Box>
                <Typography variant="h4" fontWeight={800} sx={{ letterSpacing: '-0.02em', color: '#1d1d1f' }}>
                  Console Dashboard
                </Typography>
                <Typography variant="body1" sx={{ color: '#86868b' }}>
                  Welcome back, {userEmail}. Manage parish newsletters, approvals, and error states.
                </Typography>
              </Box>
              
              <Stack direction="row" spacing={2} alignItems="center">
                <Paper
                  variant="outlined"
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    px: 2,
                    py: 0.5,
                    borderRadius: '980px',
                    borderColor: evalDemoMode ? '#ffa726' : '#e0e0e0',
                    bgcolor: evalDemoMode ? '#fff8e1' : '#fcfcfc',
                    transition: 'all 0.2s ease',
                  }}
                >
                  <FormControlLabel
                    control={
                      <Switch
                        checked={evalDemoMode}
                        onChange={(e) => setEvalDemoMode(e.target.checked)}
                        size="small"
                        color="warning"
                      />
                    }
                    label={
                      <Typography variant="body2" fontWeight={700} color={evalDemoMode ? "warning.dark" : "text.secondary"}>
                        🧪 Eval / Demo Mode
                      </Typography>
                    }
                    sx={{ m: 0 }}
                  />
                </Paper>
                <Link href="/preview" style={{ textDecoration: 'none' }}>
                  <Button
                    variant="outlined"
                    startIcon={<OpenInNewIcon />}
                    sx={{
                      borderRadius: '980px',
                      py: 1.2,
                      px: 3,
                      fontWeight: 600,
                      textTransform: 'none',
                    }}
                  >
                    View Public Site
                  </Button>
                </Link>
                <Button
                  variant="contained"
                  startIcon={<CloudUploadIcon />}
                  onClick={() => setUploadModalOpen(true)}
                  sx={{
                    borderRadius: '980px',
                    bgcolor: '#0071e3',
                    py: 1.2,
                    px: 4,
                    fontWeight: 600,
                    textTransform: 'none',
                    boxShadow: 'none',
                    '&:hover': { bgcolor: '#0077ed', boxShadow: 'none' }
                  }}
                >
                  Upload Newsletter
                </Button>
              </Stack>
            </Box>

            {/* Stats Overview */}
            <Grid container spacing={3} sx={{ mt: 3, mb: 2 }}>
              <Grid size={{ xs: 12, sm: 4, md: 3 }}>
                <Link href="/subscribers" style={{ textDecoration: 'none' }}>
                  <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.02)', border: '1px solid #f0f0f0', cursor: 'pointer', '&:hover': { borderColor: 'primary.light' } }}>
                    <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2, py: '16px !important' }}>
                      <Box sx={{ p: 1.2, borderRadius: 2, bgcolor: '#e8f2ff', color: '#0071e3', display: 'flex' }}>
                        <PeopleIcon />
                      </Box>
                      <Box>
                        <Typography variant="caption" color="text.secondary" fontWeight={500}>Active Subscribers</Typography>
                        <Typography variant="h6" fontWeight={700}>{subscribersCount}</Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Link>
              </Grid>
              <Grid size={{ xs: 12, sm: 4, md: 3 }}>
                <Link href="#newsletters-feed" style={{ textDecoration: 'none' }}>
                  <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.02)', border: '1px solid #f0f0f0', cursor: 'pointer', '&:hover': { borderColor: 'primary.light' } }}>
                    <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2, py: '16px !important' }}>
                      <Box sx={{ p: 1.2, borderRadius: 2, bgcolor: '#e6f4ea', color: '#137333', display: 'flex' }}>
                        <ArticleIcon />
                      </Box>
                      <Box>
                        <Typography variant="caption" color="text.secondary" fontWeight={500}>Total Publications</Typography>
                        <Typography variant="h6" fontWeight={700}>{publicNewsletters.length}</Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Link>
              </Grid>
              <Grid size={{ xs: 12, sm: 4, md: 3 }}>
                <Link href="/errors" style={{ textDecoration: 'none' }}>
                  <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.02)', border: '1px solid #f0f0f0', cursor: 'pointer', '&:hover': { borderColor: 'error.light' } }}>
                    <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2, py: '16px !important' }}>
                      <Box sx={{ p: 1.2, borderRadius: 2, bgcolor: '#fff0e6', color: '#d93025', display: 'flex' }}>
                        <WarningIcon />
                      </Box>
                      <Box>
                        <Typography variant="caption" color="text.secondary" fontWeight={500}>Validation Failures</Typography>
                        <Typography variant="h6" fontWeight={700} sx={{ color: '#d93025' }}>{errorLogs.length}</Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Link>
              </Grid>
              <Grid size={{ xs: 12, sm: 4, md: 3 }}>
                <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.02)', border: '1px solid #f0f0f0' }}>
                  <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2, py: '16px !important' }}>
                    <Box sx={{ p: 1.2, borderRadius: 2, bgcolor: '#fbf0ff', color: '#a142f4', display: 'flex' }}>
                      <ScheduleIcon />
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary" fontWeight={500}>Pending Approvals</Typography>
                      <Typography variant="h6" fontWeight={700} sx={{ color: '#a142f4' }}>{pendingApprovals.length}</Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

          </Container>
        </Box>
      )}

      {/* 3. MAIN DASHBOARD CONTENT */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        
        {/* If Logged In: Show Admin Approval Table & Error logs */}
        {user && (
          <Box>
            
            {/* Row 1: Human-in-the-Middle Approvals */}
            {pendingApprovals.length > 0 && (
              <Paper sx={{ p: 3, mb: 4, borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
                <Typography variant="h6" fontWeight={700} sx={{ mb: 2, color: '#1d1d1f' }}>
                  🔔 Human-in-the-Middle Approvals ({pendingApprovals.length})
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ bgcolor: '#fafafa' }}>
                        <TableCell sx={{ fontWeight: 600 }}>File Name</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Target Sunday</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Upload Date</TableCell>
                        <TableCell sx={{ fontWeight: 600 }} align="right">Quick Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {pendingApprovals.map((item) => (
                        <TableRow key={item.id} hover>
                          <TableCell sx={{ fontWeight: 500 }}>{item.filename}</TableCell>
                          <TableCell>{item.target_sunday ? new Date(item.target_sunday).toLocaleDateString() : 'N/A'}</TableCell>
                          <TableCell color="text.secondary">
                            {item.uploaded_at ? new Date(item.uploaded_at).toLocaleDateString() : 'Recent'}
                          </TableCell>
                          <TableCell align="right">
                            <Stack direction="row" spacing={1} justifyContent="flex-end">
                              <Button 
                                variant="contained" 
                                color="success" 
                                size="small" 
                                startIcon={<CheckCircleIcon />} 
                                onClick={() => handleApprove(item.id)}
                                sx={{ textTransform: 'none', borderRadius: 2 }}
                              >
                                Approve
                              </Button>
                              <Button 
                                variant="outlined" 
                                color="primary" 
                                size="small" 
                                startIcon={<RefreshIcon />} 
                                onClick={() => handleRegenerate(item.id)}
                                sx={{ textTransform: 'none', borderRadius: 2 }}
                              >
                                Regenerate
                              </Button>
                              <Button 
                                variant="text" 
                                color="error" 
                                size="small" 
                                startIcon={<CancelIcon />} 
                                onClick={() => handleReject(item.id)}
                                sx={{ textTransform: 'none' }}
                              >
                                Reject
                              </Button>
                            </Stack>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Paper>
            )}



            {/* Row 3: Latest Scheduled Newsletter */}
            {latestScheduled && (
              <Paper sx={{ p: 4, mb: 4, borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
                <Typography variant="h6" fontWeight={700} sx={{ mb: 3, color: '#1d1d1f' }}>
                  📅 Upcoming Scheduled Newsletter {latestScheduled.scheduled_at ? '(Custom Schedule)' : '(Sunday Morning Delivery)'}
                </Typography>
                
                <Grid container spacing={4} alignItems="center">
                  {latestScheduled.thumbnail_id && (
                    <Grid size={{ xs: 12, md: 4 }}>
                      <Box sx={{ border: '1px solid #e0e0e0', borderRadius: 3, overflow: 'hidden', boxShadow: '0 6px 20px rgba(0,0,0,0.06)' }}>
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img 
                          src={`${backendUrl}/newsletters/${latestScheduled.id}/thumbnail`} 
                          alt="Thumbnail preview"
                          loading="lazy"
                          style={{ width: '100%', display: 'block' }}
                        />
                      </Box>
                    </Grid>
                  )}
                  <Grid size={{ xs: 12, md: latestScheduled.thumbnail_id ? 8 : 12 }}>
                    <Typography variant="caption" sx={{ color: '#0071e3', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1 }}>
                      {latestScheduled.scheduled_at ? (
                        <>
                          ⏱️ Scheduled For: {new Date(latestScheduled.scheduled_at).toLocaleString(undefined, {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: 'numeric',
                            minute: '2-digit'
                          })}
                        </>
                      ) : (
                        <>
                          📅 Scheduled Sunday: {latestScheduled.target_sunday ? new Date(latestScheduled.target_sunday + 'T00:00:00Z').toLocaleDateString(undefined, { 
                            weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC'
                          }) : ''} (Sunday morning)
                        </>
                      )}
                    </Typography>
                    <Typography variant="h5" fontWeight={700} sx={{ my: 1 }}>
                      {latestScheduled.title}
                    </Typography>
                    <Typography variant="body1" sx={{ color: '#515154', mb: 3, whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                      {latestScheduled.summary}
                    </Typography>
                    
                    <Stack direction="row" spacing={2} useFlexGap flexWrap="wrap">
                      <Button
                        variant="contained"
                        color="success"
                        startIcon={<SendIcon />}
                        onClick={() => handleSendNow(latestScheduled.id)}
                        sx={{ textTransform: 'none', borderRadius: 2, px: 3, fontWeight: 600 }}
                      >
                        Send Now
                      </Button>
                      <Button
                        variant="contained"
                        startIcon={<EditIcon />}
                        onClick={() => handleOpenEditScheduled(latestScheduled)}
                        sx={{ textTransform: 'none', borderRadius: 2, bgcolor: '#0071e3', px: 3 }}
                      >
                        Edit Schedule & Content
                      </Button>
                      <Button 
                        variant="outlined" 
                        startIcon={<DownloadIcon />} 
                        href={`${backendUrl}/newsletters/${latestScheduled.id}/download`}
                        target="_blank"
                        sx={{ textTransform: 'none', borderRadius: 2, px: 3 }}
                      >
                        Download original
                      </Button>
                      <Button
                        variant="outlined"
                        color="warning"
                        startIcon={<ArchiveIcon />}
                        onClick={() => handleArchive(latestScheduled.id)}
                        sx={{ textTransform: 'none', borderRadius: 2, px: 3 }}
                      >
                        Archive
                      </Button>
                      <Button
                        variant="outlined"
                        color="error"
                        onClick={() => handleCancelSchedule(latestScheduled.id)}
                        sx={{ textTransform: 'none', borderRadius: 2, px: 3 }}
                      >
                        Cancel Schedule
                      </Button>
                    </Stack>

                  </Grid>
                </Grid>
              </Paper>
            )}

          </Box>
        )}

        {/* Public Feed (For non-authenticated users, or lower section list of published issues) */}
        <Box sx={{ mt: user ? 6 : 0 }} id="newsletters-feed">
          <Typography variant="h4" sx={{ mb: 4, letterSpacing: '-0.02em', fontWeight: 700 }}>
            {user ? 'All Published Newsletters' : 'Latest Newsletters'}
          </Typography>

          {/* Tag Filter Chips Row */}
          {!fetchingNewsletters && publicNewsletters.length > 0 && (() => {
            const allTags = Array.from(
              new Set(
                publicNewsletters
                  .filter(n => !user || n.status === 'delivered')
                  .flatMap(n => n.tags ? n.tags.split(',').map((t: string) => t.trim().toLowerCase()) : [])
              )
            ).filter(Boolean);

            if (allTags.length === 0) return null;

            return (
              <Stack 
                direction="row" 
                spacing={1} 
                sx={{ 
                  mb: 4, 
                  overflowX: 'auto', 
                  pb: 1.5,
                  scrollbarWidth: 'none',
                  '&::-webkit-scrollbar': { display: 'none' } 
                }}
              >
                <Chip
                  label="All Issues"
                  onClick={() => setSelectedTag(null)}
                  color={selectedTag === null ? "primary" : "default"}
                  variant={selectedTag === null ? "filled" : "outlined"}
                  sx={{ fontWeight: 600, borderRadius: '980px', px: 1.5 }}
                />
                {allTags.map((tag) => (
                  <Chip
                    key={tag}
                    label={tag.replace(/-/g, ' ')}
                    onClick={() => setSelectedTag(tag)}
                    color={selectedTag === tag ? "primary" : "default"}
                    variant={selectedTag === tag ? "filled" : "outlined"}
                    sx={{ fontWeight: 600, textTransform: 'capitalize', borderRadius: '980px', px: 1.5 }}
                  />
                ))}
              </Stack>
            );
          })()}

          {fetchingNewsletters ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
              <CircularProgress />
            </Box>
          ) : publicNewsletters.length > 0 ? (() => {
            const allFiltered = publicNewsletters
              .filter(n => !user || n.status === 'delivered')
              .filter(n => {
                if (!selectedTag) return true;
                if (!n.tags) return false;
                const tagList = n.tags.split(',').map((t: string) => t.trim().toLowerCase());
                return tagList.includes(selectedTag);
              });

            const displayedNewsletters = allFiltered.slice(0, visibleCount);

            if (allFiltered.length === 0) {
              return (
                <Box sx={{ textAlign: 'center', py: 8, opacity: 0.6 }}>
                  <Typography variant="body1">No newsletters match the filter category &quot;{selectedTag}&quot;.</Typography>
                  <Button variant="text" onClick={() => setSelectedTag(null)} sx={{ mt: 1, textTransform: 'none' }}>
                    Clear Filter
                  </Button>
                </Box>
              );
            }

            return (
              <Box>
                <Grid container spacing={3}>
                  {displayedNewsletters.map((item) => (
                    <Grid size={{ xs: 12, sm: 6, md: 4 }} key={item.id}>
                      <Paper 
                        sx={{ 
                          height: '100%', 
                          display: 'flex', 
                          flexDirection: 'column', 
                          borderRadius: 3, 
                          boxShadow: '0 4px 12px rgba(0,0,0,0.03)',
                          overflow: 'hidden',
                          transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                          '&:hover': {
                            transform: 'translateY(-4px)',
                            boxShadow: '0 12px 24px rgba(0,0,0,0.08)'
                          }
                        }}
                      >
                        {item.thumbnail_id && (
                          <Box 
                            sx={{ 
                              width: '100%', 
                              height: 180, 
                              bgcolor: '#f5f5f7', 
                              overflow: 'hidden',
                              borderBottom: '1px solid #f0f0f0',
                              cursor: 'pointer'
                            }}
                            onClick={() => {
                              setSelectedNewsletter(item);
                              setModalOpen(true);
                            }}
                          >
                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            <img 
                              src={`${backendUrl}/newsletters/${item.id}/thumbnail`} 
                              alt={item.title || "Newsletter preview"}
                              loading="lazy"
                              style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'top' }}
                            />
                          </Box>
                        )}
                        <Box sx={{ p: 3, display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
                          <Typography variant="overline" color="primary" sx={{ fontWeight: 700 }}>
                            {item.target_sunday ? new Date(item.target_sunday + 'T00:00:00Z').toLocaleDateString(undefined, { 
                              year: 'numeric', 
                              month: 'long', 
                              day: 'numeric',
                              timeZone: 'UTC'
                            }) : item.uploaded_at ? new Date(item.uploaded_at).toLocaleDateString(undefined, {
                              year: 'numeric', 
                              month: 'long', 
                              day: 'numeric'
                            }) : 'Recent'}
                          </Typography>
                          <Typography variant="h6" sx={{ mb: 0.5, fontWeight: 700, lineHeight: 1.3 }}>
                            {item.title || "Weekly Bulletin"}
                          </Typography>

                          {/* Display Tag Pills Inline inside Cards */}
                          {item.tags && (
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1, mb: 2 }}>
                              {item.tags.split(',').map((t: string) => {
                                const trimmed = t.trim().toLowerCase();
                                return (
                                  <Chip
                                    key={trimmed}
                                    label={trimmed.replace(/-/g, ' ')}
                                    size="small"
                                    variant="outlined"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      setSelectedTag(trimmed === selectedTag ? null : trimmed);
                                    }}
                                    sx={{ 
                                      fontSize: '0.7rem', 
                                      height: '20px', 
                                      textTransform: 'capitalize',
                                      borderRadius: '4px',
                                      borderColor: selectedTag === trimmed ? '#0071e3' : '#e5e5ea',
                                      color: selectedTag === trimmed ? '#0071e3' : '#8e8e93',
                                      bgcolor: selectedTag === trimmed ? '#e1f0ff' : 'transparent',
                                      '&:hover': { bgcolor: '#f2f8fc' }
                                    }}
                                  />
                                );
                              })}
                            </Box>
                          )}

                          <Typography variant="body2" color="text.secondary" sx={{ mb: 3, flexGrow: 1, whiteSpace: 'pre-line', lineHeight: 1.6 }}>
                            {item.summary ? item.summary.substring(0, 200) + "..." : "Read the latest news from our parish community."}
                          </Typography>
                          
                          <Stack direction="row" spacing={2} justifyContent="space-between" alignItems="center">
                            <Button 
                              variant="text" 
                              color="primary" 
                              sx={{ p: 0, fontWeight: 600, textTransform: 'none' }}
                              onClick={() => {
                                setSelectedNewsletter(item);
                                setModalOpen(true);
                              }}
                            >
                              Read Summary →
                            </Button>
                            {item.drive_link && (
                              <IconButton 
                                size="small" 
                                color="default" 
                                href={item.drive_link} 
                                target="_blank"
                                title="Download original file"
                              >
                                <DownloadIcon fontSize="small" color="action" />
                              </IconButton>
                            )}
                          </Stack>
                        </Box>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>

                {/* Sentinel Element for Infinite Scroll */}
                <Box 
                  ref={sentinelRef} 
                  sx={{ 
                    display: 'flex', 
                    justifyContent: 'center', 
                    alignItems: 'center', 
                    py: 4,
                    minHeight: 60 
                  }}
                >
                  {loadingMore && (
                    <Stack direction="row" spacing={1.5} alignItems="center">
                      <CircularProgress size={24} />
                      <Typography variant="body2" color="text.secondary" fontWeight={500}>
                        Loading more newsletters...
                      </Typography>
                    </Stack>
                  )}
                  {(!user ? !hasMoreBackend : visibleCount >= allFiltered.length) && allFiltered.length > 6 && (
                    <Typography variant="caption" color="text.secondary">
                      Showing all {allFiltered.length} newsletters
                    </Typography>
                  )}
                </Box>
              </Box>
            );
          })() : (
            <Box sx={{ textAlign: 'center', py: 5, opacity: 0.6 }}>
              <ArticleIcon sx={{ fontSize: 48, mb: 1 }} color="disabled" />
              <Typography variant="body1">No newsletters have been published yet.</Typography>
            </Box>
          )}
        </Box>

      </Container>

      {/* 4. MOBILE FRIENDLY UPLOAD DIALOG MODAL */}
      <Dialog open={uploadModalOpen} onClose={() => setUploadModalOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 700 }}>
          Upload Newsletter File
        </DialogTitle>
        <DialogContent dividers>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Upload parish bulletin PDF or DOCX. The system will compress the document, extract contents, and generate summary details automatically.
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
              {error}
            </Alert>
          )}

          <Box sx={{ textAlign: 'center', py: 4, border: '2px dashed #d0d0d0', borderRadius: 3, bgcolor: '#fafafa' }}>
            <input
              type="file"
              id="modal-file-upload"
              hidden
              onChange={handleFileChange}
              accept=".pdf,.docx"
            />
            <label htmlFor="modal-file-upload">
              <IconButton color="primary" component="span" sx={{ p: 3, bgcolor: '#e8f2ff', mb: 2 }}>
                <CloudUploadIcon fontSize="large" />
              </IconButton>
            </label>
            <Typography variant="subtitle1" fontWeight={600}>
              {file ? file.name : "Select bulletin document"}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              PDF or DOCX files up to 20MB
            </Typography>
          </Box>

          <Paper
            variant="outlined"
            sx={{
              mt: 3,
              p: 2,
              borderRadius: 2,
              borderColor: evalDemoMode ? '#ffa726' : '#e0e0e0',
              bgcolor: evalDemoMode ? '#fff8e1' : '#fafafa',
              transition: 'all 0.2s ease',
            }}
          >
            <FormControlLabel
              control={
                <Switch
                  checked={evalDemoMode}
                  onChange={(e) => setEvalDemoMode(e.target.checked)}
                  color="warning"
                />
              }
              label={
                <Box>
                  <Typography variant="body2" fontWeight={700} color={evalDemoMode ? "warning.dark" : "text.primary"}>
                    🧪 Eval / Demo Mode (Immediate Submission Preview)
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block">
                    Simulates scheduled process in one fell swoop. Sends sample preview email to <strong>{userEmail}</strong> with subject prefixed by <code>[DEMO/PREVIEW]</code>.
                  </Typography>
                </Box>
              }
              sx={{ width: '100%', m: 0 }}
            />
          </Paper>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setUploadModalOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button
            variant="contained"
            disabled={loading || !file}
            onClick={handleUpload}
            sx={{ bgcolor: '#0071e3', textTransform: 'none', px: 4, borderRadius: '980px' }}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Summarize & Save'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* 5. PUBLIC SUMMARY MODAL */}
      <Dialog 
        open={modalOpen} 
        onClose={() => setModalOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3, p: 1 } }}
      >
        <DialogTitle sx={{ pr: 6, fontWeight: 700 }}>
          {selectedNewsletter?.title || "Newsletter Summary"}
          <IconButton
            onClick={() => setModalOpen(false)}
            sx={{ position: 'absolute', right: 16, top: 16 }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          <Typography variant="overline" color="primary" sx={{ fontWeight: 700, mb: 2, display: 'block' }}>
            {selectedNewsletter?.target_sunday ? new Date(selectedNewsletter.target_sunday + 'T00:00:00Z').toLocaleDateString(undefined, { 
              year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC'
            }) : selectedNewsletter?.uploaded_at ? new Date(selectedNewsletter.uploaded_at).toLocaleDateString(undefined, { 
              year: 'numeric', month: 'long', day: 'numeric' 
            }) : ''}
          </Typography>
          
          <Grid container spacing={3}>
            {selectedNewsletter?.thumbnail_id && (
              <Grid size={{ xs: 12, md: 4 }}>
                <Box sx={{ border: '1px solid #e0e0e0', borderRadius: 2, overflow: 'hidden' }}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img 
                    src={`${backendUrl}/newsletters/${selectedNewsletter.id}/thumbnail`} 
                    alt="Newsletter Thumbnail"
                    loading="lazy"
                    style={{ width: '100%', display: 'block' }}
                  />
                </Box>
              </Grid>
            )}
            <Grid size={{ xs: 12, md: selectedNewsletter?.thumbnail_id ? 8 : 12 }}>
              <Typography variant="body1" sx={{ fontSize: '1.1rem', lineHeight: 1.8, whiteSpace: 'pre-line' }}>
                {selectedNewsletter?.summary}
              </Typography>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setModalOpen(false)} variant="outlined" sx={{ borderRadius: '100px', px: 4 }}>
            Close
          </Button>
          {selectedNewsletter && (
            <Button 
              variant="outlined" 
              startIcon={<DownloadIcon />} 
              href={`${backendUrl}/newsletters/${selectedNewsletter.id}/download`} 
              target="_blank"
              sx={{ borderRadius: '100px', px: 4 }}
            >
              Download original
            </Button>
          )}
          {!user && (
            <Link href="/signup" style={{ textDecoration: 'none' }}>
              <Button variant="contained" sx={{ borderRadius: '100px', px: 4 }}>
                Join Mailing List
              </Button>
            </Link>
          )}
        </DialogActions>
      </Dialog>

      {/* 6. EDIT SCHEDULE & CONTENT DIALOG */}
      <Dialog 
        open={editScheduledOpen} 
        onClose={() => setEditScheduledOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3, p: 1 } }}
      >
        <DialogTitle sx={{ pr: 6, fontWeight: 700 }}>
          📅 Edit Schedule & Email Content
          <IconButton
            onClick={() => setEditScheduledOpen(false)}
            sx={{ position: 'absolute', right: 16, top: 16 }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={3}>
            {/* Left Column: Form Inputs */}
            <Grid size={{ xs: 12, md: 6 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, color: '#1d1d1f' }}>
                ✏️ Edit Details
              </Typography>
              <Stack spacing={3}>
                <TextField
                  label="Email Subject"
                  fullWidth
                  value={editScheduledTitle}
                  onChange={(e) => setEditScheduledTitle(e.target.value)}
                  variant="outlined"
                  required
                />
                <TextField
                  label="Email Body / Summary"
                  fullWidth
                  multiline
                  rows={8}
                  value={editScheduledSummary}
                  onChange={(e) => setEditScheduledSummary(e.target.value)}
                  variant="outlined"
                  required
                  helperText="Use newlines to separate paragraphs."
                />
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1, fontWeight: 600 }}>
                    📅 Schedule Delivery Date
                  </Typography>
                  <TextField
                    type="date"
                    fullWidth
                    value={editScheduledDate}
                    onChange={(e) => setEditScheduledDate(e.target.value)}
                    variant="outlined"
                    required
                  />
                </Box>

                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1, fontWeight: 600 }}>
                    ⏱️ Schedule Delivery Time
                  </Typography>
                  <TextField
                    type="time"
                    fullWidth
                    value={editScheduledTime}
                    onChange={(e) => setEditScheduledTime(e.target.value)}
                    variant="outlined"
                    required
                  />
                </Box>
              </Stack>
            </Grid>

            {/* Right Column: Live Email Preview */}
            <Grid size={{ xs: 12, md: 6 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, color: '#1d1d1f' }}>
                📧 Live Email Preview
              </Typography>
              <Box sx={{ 
                border: '1px solid #e0e0e0', 
                borderRadius: 2, 
                p: 2, 
                bgcolor: '#f5f5f7',
                height: '100%',
                maxHeight: 520,
                overflowY: 'auto'
              }}>
                <Box sx={{ 
                  bgcolor: 'white', 
                  p: 3, 
                  borderRadius: 2,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                  lineHeight: 1.6,
                  color: '#333'
                }}>
                  <Typography variant="h6" sx={{ color: '#0071e3', fontWeight: 700, mb: 2, borderBottom: '1px solid #eee', pb: 1, fontSize: '1.1rem' }}>
                    {editScheduledTitle || '(No Subject)'}
                  </Typography>
                  <Box sx={{ fontSize: '14px', whiteSpace: 'pre-line', mb: 3 }}>
                    {editScheduledSummary || '(No Content)'}
                  </Box>
                  <Divider sx={{ my: 3 }} />
                  <Typography variant="caption" sx={{ color: '#86868b', display: 'block', fontSize: '11px' }}>
                    Sent by Newsletter Herald. To unsubscribe, please visit the parish website.
                  </Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setEditScheduledOpen(false)} variant="outlined" sx={{ borderRadius: '100px', px: 4 }}>
            Cancel
          </Button>
          <Button 
            onClick={() => latestScheduled && handleSaveScheduledChanges(latestScheduled.id)} 
            variant="contained" 
            disabled={editScheduledSaving || !editScheduledTitle || !editScheduledSummary || !editScheduledDate || !editScheduledTime}
            sx={{ borderRadius: '100px', px: 4, bgcolor: '#0071e3' }}
          >
            {editScheduledSaving ? <CircularProgress size={24} color="inherit" /> : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
````

## File: backend/main.py
````python
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
    allow_origin_regex=r"https://.*\.vercel\.app",
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
````
