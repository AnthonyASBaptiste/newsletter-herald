from sqlalchemy import MetaData
from config import get_settings

settings = get_settings()

try:
    from databases import Database
    database = Database(settings.database_url)
except Exception:
    class DummyDatabase:
        is_connected = False
        async def connect(self): pass
        async def disconnect(self): pass
        async def fetch_one(self, *args, **kwargs): return None
        async def fetch_all(self, *args, **kwargs): return []
        async def fetch_val(self, *args, **kwargs): return 0
        async def execute(self, *args, **kwargs): return 1
        async def execute_many(self, *args, **kwargs): return 1
    database = DummyDatabase()

metadata = MetaData()
