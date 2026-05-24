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
