import asyncio
import time
import sys
import os

# Add backend directory to path
current_script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_script_dir)
sys.path.append(backend_dir)

from db.setup import database
from db.models import subscribers
from main import batch_subscribe_users, BatchSubscribersRequest
from sqlalchemy import select, delete

async def setup_subscribers(num_active: int, num_inactive: int):
    # Clean up benchmark test emails first
    print("Cleaning up previous benchmark data...")
    query = delete(subscribers).where(subscribers.c.email.like("%@benchmark-test.com"))
    await database.execute(query)

    print(f"Seeding {num_active} active and {num_inactive} inactive subscribers...")

    # Seed active ones
    for i in range(num_active):
        email = f"active_{i}@benchmark-test.com"
        query = subscribers.insert().values(email=email, is_active=True)
        await database.execute(query)

    # Seed inactive ones
    for i in range(num_inactive):
        email = f"inactive_{i}@benchmark-test.com"
        query = subscribers.insert().values(email=email, is_active=False)
        await database.execute(query)

async def run_benchmark():
    print(f"Connecting to database...")
    await database.connect()

    try:
        # We will seed 50 active and 50 inactive subscribers
        num_active = 50
        num_inactive = 50
        await setup_subscribers(num_active, num_inactive)

        # Prepare a large batch of 200 emails:
        # - 50 existing active emails
        # - 50 existing inactive emails (to reactivate)
        # - 100 brand new emails
        emails_batch = []
        for i in range(num_active):
            emails_batch.append(f"active_{i}@benchmark-test.com")
        for i in range(num_inactive):
            emails_batch.append(f"inactive_{i}@benchmark-test.com")
        for i in range(100):
            emails_batch.append(f"new_{i}@benchmark-test.com")

        print(f"Preparing batch subscription for {len(emails_batch)} emails...")
        request_data = BatchSubscribersRequest(emails=emails_batch)

        # Run and measure time
        start_time = time.perf_counter()
        response = await batch_subscribe_users(request_data)
        end_time = time.perf_counter()

        duration = end_time - start_time
        print("\n==================================================")
        print("📊 BENCHMARK RESULT")
        print("==================================================")
        print(f"Execution time: {duration:.4f} seconds")
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.body.decode()}")
        print("==================================================\n")

    finally:
        # Clean up benchmark test emails
        print("Cleaning up benchmark data...")
        query = delete(subscribers).where(subscribers.c.email.like("%@benchmark-test.com"))
        await database.execute(query)
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(run_benchmark())
