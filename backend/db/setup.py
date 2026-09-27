from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.pool import StaticPool
from config import get_settings

settings = get_settings()
metadata = MetaData()

try:
    from databases import Database
    database = Database(settings.database_url)
except Exception:
    class DummyDatabase:
        def __init__(self):
            self.engine = create_engine(
                "sqlite:///:memory:",
                poolclass=StaticPool,
                connect_args={"check_same_thread": False},
            )
            self.is_connected = False

        async def connect(self):
            self.is_connected = True
            metadata.create_all(self.engine)

        async def disconnect(self):
            self.is_connected = False

        async def fetch_one(self, query, values=None):
            metadata.create_all(self.engine)
            with self.engine.connect() as conn:
                q = text(query) if isinstance(query, str) else query
                res = conn.execute(q, values or {})
                row = res.mappings().first()
                return dict(row) if row else None

        async def fetch_all(self, query, values=None):
            metadata.create_all(self.engine)
            with self.engine.connect() as conn:
                q = text(query) if isinstance(query, str) else query
                res = conn.execute(q, values or {})
                return [dict(r) for r in res.mappings().all()]

        async def fetch_val(self, query, values=None):
            metadata.create_all(self.engine)
            with self.engine.connect() as conn:
                q = text(query) if isinstance(query, str) else query
                res = conn.execute(q, values or {})
                return res.scalar()

        async def execute(self, query, values=None):
            metadata.create_all(self.engine)
            with self.engine.begin() as conn:
                q = text(query) if isinstance(query, str) else query
                res = conn.execute(q, values or {})
                return res.lastrowid or res.rowcount or 1

        async def execute_many(self, query, values):
            metadata.create_all(self.engine)
            with self.engine.begin() as conn:
                q = text(query) if isinstance(query, str) else query
                res = conn.execute(q, values)
                return res.rowcount or len(values)

    database = DummyDatabase()
