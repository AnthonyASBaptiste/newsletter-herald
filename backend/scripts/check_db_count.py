import asyncio
import sys
import os

# Add backend directory to path
current_script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_script_dir)
sys.path.append(backend_dir)

from db.setup import database

async def check_db():
    print(f"Connecting to: {database.url}")
    await database.connect()
    try:
        count = await database.fetch_val("SELECT count(*) FROM newsletters")
        print(f"Newsletters in DB: {count}")
    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(check_db())
