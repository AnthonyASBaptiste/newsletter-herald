from sqlalchemy import MetaData
from databases import Database
from config import get_settings

settings = get_settings()

database = Database(settings.database_url)
metadata = MetaData()
