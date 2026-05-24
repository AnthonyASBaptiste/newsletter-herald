import os
import json
import logging
import datetime
from typing import Dict, Any
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Path to the notifications queue at the root of the project
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QUEUE_FILE_PATH = os.path.join(PROJECT_ROOT, "notifications_queue.json")

def notify_agent(event_type: str, data: Dict[str, Any]):
    """
    Appends a new notification event to the local queue file.
    Your local agent can poll this file to forward messages to WhatsApp/Signal.
    """
    event_id = data.get("newsletter_id") or data.get("id") or int(datetime.datetime.now().timestamp())
    
    # Base URLs for callbacks
    base_url = f"http://localhost:{settings.api_port}"
    
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
    
    # Format a human-readable message for easy agent parsing
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
        # Load existing queue or create new
        queue = []
        if os.path.exists(QUEUE_FILE_PATH):
            try:
                with open(QUEUE_FILE_PATH, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        queue = json.loads(content)
            except Exception as read_err:
                logger.error(f"Failed to read existing queue file: {read_err}")
                
        # Append and save
        queue.append(event)
        
        with open(QUEUE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Agent notification written to queue: {event_type} (ID: {event_id})")
        return True
    except Exception as e:
        logger.error(f"Failed to write agent notification: {e}")
        return False
