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
