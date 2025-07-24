import logging
from fastapi import Request, HTTPException
from config import get_settings

# Get settings from centralized configuration
settings = get_settings()

# Create a logger for this module
logger = logging.getLogger(__name__)

def verify_api_key(request: Request):
    """
    Verify that the request contains a valid API key in the Authorization header.
    
    Args:
        request: The FastAPI request object
        
    Raises:
        HTTPException: If the API key is missing or invalid
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != f"Bearer {settings.api_key}":
        logger.warning("Unauthorized API request attempt")
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    logger.debug("API key verified successfully")
