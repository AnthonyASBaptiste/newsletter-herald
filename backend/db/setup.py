
from sqlalchemy import MetaData
from databases import Database
from helpers.constants import DATABASE_URL


database = Database(DATABASE_URL)
metadata = MetaData()
