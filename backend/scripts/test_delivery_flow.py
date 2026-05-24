import sys
import os
import asyncio
import datetime
import json

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from db.setup import database
from db.models import newsletters, summaries, subscribers, delivery_logs
from scripts.delivery_worker import check_and_deliver
from helpers.agent_bridge import QUEUE_FILE_PATH

async def run_integration_test():
    print("Connecting to DB for integration test...")
    await database.connect()
    
    try:
        # 1. Add a test subscriber
        print("Inserting test subscriber...")
        test_email = "test_parishioner@example.com"
        
        # Clean up existing if any
        await database.execute(subscribers.delete().where(subscribers.c.email == test_email))
        
        await database.execute(
            subscribers.insert().values(
                email=test_email,
                is_active=True
            )
        )
        
        # 2. Add a mock newsletter scheduled for today with status='scheduled'
        print("Inserting mock newsletter scheduled for today...")
        today = datetime.date.today()
        
        # Clean up existing test ones by resolving foreign key first
        find_query = select(newsletters.c.id).where(newsletters.c.filename == "test_weekly_bulletin.pdf")
        existing_rows = await database.fetch_all(find_query)
        for row in existing_rows:
            nl_id = row["id"]
            await database.execute(delivery_logs.delete().where(delivery_logs.c.newsletter_id == nl_id))
            await database.execute(summaries.delete().where(summaries.c.newsletter_id == nl_id))
            await database.execute(newsletters.delete().where(newsletters.c.id == nl_id))
        
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
                target_sunday=today
            )
        )
        
        # Add summary
        await database.execute(
            summaries.insert().values(
                newsletter_id=newsletter_id,
                title="Mock 5th Sunday bulletin summary",
                summary="Paragraph 1 of the mock summary.\nParagraph 2 of the mock summary."
            )
        )
        
        # 3. Clean queue file
        if os.path.exists(QUEUE_FILE_PATH):
            os.remove(QUEUE_FILE_PATH)
            
        print("Setup complete. Disconnecting temporarily so delivery worker can run...")
        await database.disconnect()
        
        # 4. Run delivery worker
        print("Running delivery worker...")
        await check_and_deliver()
        
        # 5. Reconnect to verify side-effects
        print("Reconnecting to verify database state...")
        await database.connect()
        
        # Verify newsletter was updated
        query = newsletters.select().where(newsletters.c.id == newsletter_id)
        nl = await database.fetch_one(query)
        print(f"Newsletter Status after delivery: {nl['status']} (Expected: delivered)")
        print(f"Newsletter Delivered flag: {nl['delivered']} (Expected: True)")
        assert nl['status'] == "delivered", "Status was not updated to delivered"
        assert nl['delivered'] == True, "Delivered flag was not set to True"
        
        # Verify delivery logs
        log_query = delivery_logs.select().where(delivery_logs.c.newsletter_id == newsletter_id)
        logs = await database.fetch_all(log_query)
        print(f"Delivery logs recorded: {len(logs)} (Expected: 1)")
        assert len(logs) == 1, f"Expected 1 delivery log, got {len(logs)}"
        print(f"Recipient: {logs[0]['recipient']} | Status: {logs[0]['status']}")
        
        # Verify agent bridge notification
        print(f"Verifying agent queue at: {QUEUE_FILE_PATH}")
        assert os.path.exists(QUEUE_FILE_PATH), "Queue file was not created"
        with open(QUEUE_FILE_PATH, "r", encoding="utf-8") as f:
            queue = json.load(f)
        print(f"Events in queue: {len(queue)} (Expected: 1)")
        assert len(queue) == 1, "Expected 1 event in queue"
        print(f"Event type: {queue[0]['type']} (Expected: delivery_report)")
        assert queue[0]['type'] == "delivery_report", "Event type was not delivery_report"
        
        # Clean up
        print("Cleaning up test data...")
        await database.execute(delivery_logs.delete().where(delivery_logs.c.newsletter_id == newsletter_id))
        await database.execute(summaries.delete().where(summaries.c.newsletter_id == newsletter_id))
        await database.execute(newsletters.delete().where(newsletters.c.id == newsletter_id))
        await database.execute(subscribers.delete().where(subscribers.c.email == test_email))
        if os.path.exists(QUEUE_FILE_PATH):
            os.remove(QUEUE_FILE_PATH)
            
        print("All delivery worker integration tests passed successfully!")
        
    except Exception as err:
        print(f"Test failed with error: {err}")
        sys.exit(1)
    finally:
        if database.is_connected:
            await database.disconnect()

if __name__ == "__main__":
    asyncio.run(run_integration_test())
