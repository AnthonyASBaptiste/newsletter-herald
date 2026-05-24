import os
import json
import sys

# Get root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QUEUE_FILE_PATH = os.path.join(PROJECT_ROOT, "notifications_queue.json")
ARCHIVE_FILE_PATH = os.path.join(PROJECT_ROOT, "notifications_archive.json")

def poll_notifications():
    if not os.path.exists(QUEUE_FILE_PATH):
        return
        
    try:
        # 1. Read queue
        queue = []
        with open(QUEUE_FILE_PATH, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                queue = json.loads(content)
                
        if not queue:
            return
            
        # 2. Output messages to stdout (using utf-8 write to avoid Windows cp1252 encoding errors)
        for event in queue:
            msg = event.get("formatted_message", "")
            if msg:
                sys.stdout.buffer.write((msg + "\n---\n").encode("utf-8"))
                
        # 3. Move queued events to archive
        archive = []
        if os.path.exists(ARCHIVE_FILE_PATH):
            try:
                with open(ARCHIVE_FILE_PATH, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        archive = json.loads(content)
            except Exception:
                pass
                
        archive.extend(queue)
        
        with open(ARCHIVE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(archive, f, indent=2, ensure_ascii=False)
            
        # 4. Clear queue
        with open(QUEUE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
            
    except Exception as e:
        sys.stderr.write(f"Error polling notifications: {e}\n")

if __name__ == "__main__":
    poll_notifications()
