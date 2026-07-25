import asyncio
import time
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from db.setup import database
from db.models import newsletters
from helpers.text_utils import sanitize_filename


async def run_benchmark():
    await database.connect()

    # Let's get some existing filenames from DB to query
    query = newsletters.select().limit(50)
    rows = await database.fetch_all(query)
    filenames = [row["filename"] for row in rows]

    # If DB is empty, let's generate some dummy filenames to simulate
    if not filenames:
        filenames = [f"2024-12-{i:02d}-Trinity-Newsletter.pdf" for i in range(1, 21)]

    print(f"Benchmarking with {len(filenames)} filenames.")

    # ------------------ N+1 Implementation ------------------
    print("\n--- Running N+1 Query Baseline ---")
    start_time = time.perf_counter()

    n_plus_one_results = []
    for filename in filenames:
        # Check if already in DB (N+1 query)
        q = newsletters.select().where(newsletters.c.filename == filename)
        existing = await database.fetch_one(q)
        if existing:
            n_plus_one_results.append(existing["filename"])

    n_plus_one_duration = time.perf_counter() - start_time
    print(f"N+1 baseline duration: {n_plus_one_duration:.4f} seconds")
    print(f"Found {len(n_plus_one_results)} matching records.")

    # ------------------ Optimized Implementation ------------------
    print("\n--- Running Bulk Query Optimized ---")
    start_time = time.perf_counter()

    # Bulk query
    q = newsletters.select().where(newsletters.c.filename.in_(filenames))
    existing_rows = await database.fetch_all(q)
    existing_filenames = {row["filename"] for row in existing_rows}

    optimized_results = []
    for filename in filenames:
        if filename in existing_filenames:
            optimized_results.append(filename)

    optimized_duration = time.perf_counter() - start_time
    print(f"Optimized bulk query duration: {optimized_duration:.4f} seconds")
    print(f"Found {len(optimized_results)} matching records.")

    # Verification
    assert set(n_plus_one_results) == set(optimized_results), "Results do not match!"
    print("\n✅ Verification PASSED: Both implementations returned identical results.")

    # Calculate improvement
    speedup = n_plus_one_duration / optimized_duration
    reduction = (1 - (optimized_duration / n_plus_one_duration)) * 100
    print(f"🚀 Speedup: {speedup:.2f}x faster")
    print(f"⚡ Time reduction: {reduction:.2f}%")

    await database.disconnect()


if __name__ == "__main__":
    asyncio.run(run_benchmark())
