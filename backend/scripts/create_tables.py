
import logging
from sqlalchemy import create_engine
from db.models import metadata
from config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Get settings from centralized configuration
settings = get_settings()

# Create database engine
engine = create_engine(settings.database_url)

# Create tables
logger.info("Creating database tables...")
metadata.create_all(engine)

# Log created tables
logger.info(f"Created tables: {', '.join(metadata.tables.keys())}")
logger.info("✅ Tables created successfully")