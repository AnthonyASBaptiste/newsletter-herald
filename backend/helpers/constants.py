import logging
from config import get_settings

# Get settings from centralized configuration
settings = get_settings()

# Create a logger for this module
logger = logging.getLogger(__name__)

# Constants from settings
ANTHROPIC_API_KEY = settings.anthropic_api_key
MAX_ALLOWED_TOKENS = settings.max_allowed_tokens
DATABASE_URL = settings.database_url

logger.debug("Constants loaded from settings")