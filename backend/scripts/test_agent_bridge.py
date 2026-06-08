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
