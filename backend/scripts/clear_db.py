import asyncio
import os
import sys

# Add backend directory to path
current_script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_script_dir)
sys.path.append(backend_dir)

from db.setup import database
from db.models import newsletters, summaries, model_usage

async def clear_db():
    print(f"Connecting to: {database.url}")
    await database.connect()
    try:
        # Delete in order of dependencies
        await database.execute(model_usage.delete())
        await database.execute(summaries.delete())
        await database.execute(newsletters.delete())
        print("Database cleared successfully.")
    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(clear_db())
