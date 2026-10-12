import logging
import secrets
import hmac
import hashlib
from fastapi import Request, HTTPException
from config import get_settings

# Get settings from centralized configuration
settings = get_settings()

# Create a logger for this module
logger = logging.getLogger(__name__)


def is_api_key_valid(request: Request) -> bool:
    """
    Check if the request contains a valid API key without raising an exception.

    Args:
        request: The FastAPI request object

    Returns:
        bool: True if the request has a valid API key, False otherwise
    """
    auth_header = request.headers.get("Authorization")
    x_api_key = request.headers.get("X-API-Key")

    if auth_header and secrets.compare_digest(
        auth_header, f"Bearer {settings.api_key}"
    ):
        return True
    if x_api_key and secrets.compare_digest(x_api_key, settings.api_key):
        return True

    return False


def verify_api_key(request: Request):
    """
    Verify that the request contains a valid API key in the Authorization or X-API-Key header.

    Args:
        request: The FastAPI request object

    Raises:
        HTTPException: If the API key is missing or invalid
    """
    if not is_api_key_valid(request):
        logger.warning("Unauthorized API request attempt")
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.debug("API key verified successfully")


def generate_unsubscribe_token(email: str) -> str:
    """
    Generate an unguessable HMAC SHA-256 unsubscribe token for an email address.

    Args:
        email: Subscriber email address

    Returns:
        str: Hex-encoded HMAC digest token
    """
    email_clean = email.strip().lower()
    return hmac.new(
        settings.api_key.encode("utf-8"),
        email_clean.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def verify_unsubscribe_token(email: str, token: str) -> bool:
    """
    Verify an unsubscribe token against an email address using constant-time comparison.

    Args:
        email: Subscriber email address
        token: Unsubscribe token provided in request

    Returns:
        bool: True if token matches expected HMAC for email, False otherwise
    """
    if not token or not email:
        return False
    expected_token = generate_unsubscribe_token(email)
    return secrets.compare_digest(expected_token, token)
