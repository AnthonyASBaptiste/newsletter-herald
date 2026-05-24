import sys
import os
import json
import datetime

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.agent_bridge import notify_agent, QUEUE_FILE_PATH

def main():
    print("Testing local agent bridge...")
    
    # 1. Clean previous queue file if exists
    if os.path.exists(QUEUE_FILE_PATH):
        try:
            os.remove(QUEUE_FILE_PATH)
            print("Removed old queue file for clean testing.")
        except Exception as e:
            print(f"Failed to remove old queue: {e}")
            
    # 2. Add validation alert event
    print("Queuing validation alert...")
    notify_agent("validation_alert", {
        "newsletter_id": 999,
        "filename": "invalid_newsletter.docx",
        "target_sunday": datetime.date(2026, 5, 24),
        "status": "failed_validation",
        "error_message": "Date mismatch: Expected 2026-05-24 but found 2026-05-17"
    })
    
    # 3. Add review request event
    print("Queuing review request...")
    notify_agent("review_request", {
        "newsletter_id": 1000,
        "title": "4th Sunday of Easter Bulletin",
        "summary": "This is a warm test summary of parish events. Join us for Sunday Mass and our parish fundraising bake sale this weekend.",
        "target_sunday": datetime.date(2026, 5, 24),
        "status": "draft"
    })
    
    # 4. Verify queue file contents
    print(f"Verifying queue file at: {QUEUE_FILE_PATH}")
    if not os.path.exists(QUEUE_FILE_PATH):
        print("Error: Queue file was not created!")
        sys.exit(1)
        
    try:
        with open(QUEUE_FILE_PATH, "r", encoding="utf-8") as f:
            queue = json.load(f)
            
        print(f"Queue file loaded successfully. Contains {len(queue)} events.")
        assert len(queue) == 2, f"Expected 2 events, got {len(queue)}"
        
        # Verify event structures
        assert queue[0]["type"] == "validation_alert", "First event type incorrect"
        assert queue[1]["type"] == "review_request", "Second event type incorrect"
        assert "actions" in queue[1], "Review request event is missing actions URL"
        assert "approve_url" in queue[1]["actions"], "Review request is missing approve_url"
        
        # Print without emojis
        print("First event type: " + queue[0]["type"])
        print("Second event type: " + queue[1]["type"])
        print("Approve URL: " + queue[1]["actions"]["approve_url"])
        
        print("All local agent bridge tests completed successfully!")
        
    except Exception as err:
        print(f"Error validating queue file: {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()
