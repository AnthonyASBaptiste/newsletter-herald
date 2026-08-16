# 🤖 Hermes Agent Integration Brief: Automated Newsletter Ingestion & Alerts

## 📌 Executive Summary
This document specifies the integration protocol for **Hermes Agent** to automate weekend bulletin ingestion from parish staff (Irma Carter), transmit documents to the Newsletter Herald backend, and route review requests or validation alerts directly to the admin via WhatsApp, Signal, or Email.

---

## ⚙️ Configuration & Environment

| Property | Value | Notes |
|---|---|---|
| **Backend API URL** | `http://localhost:8000` *(or deployed backend URL)* | Endpoint target |
| **Dashboard URL** | `https://newsletter-herald.vercel.app` | Production frontend |
| **API Header** | `X-API-Key: 85fb0ffd7ff26541e6361e5063bdfbde9299f1938a5ffae44d05ff3f9a4dd630` | Authentication key |
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
API_KEY = "85fb0ffd7ff26541e6361e5063bdfbde9299f1938a5ffae44d05ff3f9a4dd630"

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
