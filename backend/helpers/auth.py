import requests
import logging
from typing import Dict, Any, Optional
from config import get_settings

# Get settings from centralized configuration
settings = get_settings()

# Create a logger for this module
logger = logging.getLogger(__name__)


def stack_auth_request(method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
    """
    Make an authenticated request to the Stack Auth API.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        **kwargs: Additional arguments to pass to requests.request
        
    Returns:
        Dict[str, Any]: JSON response from the API
        
    Raises:
        Exception: If the API request fails
    """
    logger.debug(f"Making Stack Auth API request: {method} {endpoint}")
    
    res = requests.request(
        method,
        f'https://api.stack-auth.com/{endpoint}',
        headers={
            'x-stack-access-type': 'server',
            'x-stack-project-id': settings.stack_project_id,
            'x-stack-publishable-client-key': settings.stack_publishable_client_key,
            'x-stack-secret-server-key': settings.stack_secret_server_key,
            **kwargs.pop('headers', {}),
        },
        **kwargs,
    )
    
    if res.status_code >= 400:
        error_msg = f"Stack Auth API request failed with {res.status_code}: {res.text}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    logger.debug("Stack Auth API request successful")
    return res.json()