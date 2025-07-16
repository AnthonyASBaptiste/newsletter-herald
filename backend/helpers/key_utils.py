from dotenv import load_dotenv
from fastapi import Request, HTTPException
import os

load_dotenv()

API_KEY = os.getenv("API_KEY", "super-secret-key")
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set")

def verify_api_key(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")
