import logging
import sys
import os
from sqlalchemy import create_engine

# Add backend directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

# Drop all tables
logger.info("Dropping all tables...")
metadata.drop_all(engine)

# Create tables
logger.info("Creating database tables...")
metadata.create_all(engine)

# Log created tables
logger.info(f"Created tables: {', '.join(metadata.tables.keys())}")
logger.info("✅ Tables created successfully")
