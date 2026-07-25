import asyncio
import sys
import os
import time
from sqlalchemy import select

# Add backend directory to path
current_script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_script_dir)
sys.path.append(backend_dir)

from db.setup import database
from db.models import newsletters

async def run_benchmark():
    print("Connecting to DB...")
    await database.connect()

    try:
        # Generate 150 mock drive files
        print("Generating mock drive files...")
        drive_files = []
        for i in range(150):
            drive_files.append({
                "id": f"benchmark_file_{i}",
                "name": f"newsletter_bulletin_{i}.pdf",
                "mimeType": "application/pdf"
            })

        # Add 10 non-pdf files to test filtering
        for i in range(10):
            drive_files.append({
                "id": f"benchmark_ignored_{i}",
                "name": f"image_{i}.png",
                "mimeType": "image/png"
            })

        # Clean up any existing benchmark files in DB just in case
        await database.execute(newsletters.delete().where(newsletters.c.uploader == "benchmark_temp"))

        # Insert 75 of them into DB to simulate "already processed" files
        print("Inserting mock newsletters to database to simulate existing files...")
        for i in range(75):
            await database.execute(
                newsletters.insert().values(
                    filename=f"newsletter_bulletin_{i}.pdf",
                    drive_file_id=f"benchmark_file_{i}",
                    drive_web_view_link="http://drive.google.com/mock",
                    thumbnail_drive_id="mock_thumb",
                    uploader="benchmark_temp",
                    delivered=False
                )
            )

        # 1. Baseline Benchmark (N+1 Queries)
        print("\n--- Running Baseline Check (N+1 queries) ---")
        start_time = time.perf_counter()

        skipped_base = 0
        processed_base = 0
        for df in drive_files:
            file_id = df['id']
            filename = df['name']
            mime_type = df['mimeType']

            if mime_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                continue

            query = newsletters.select().where(newsletters.c.drive_file_id == file_id)
            existing = await database.fetch_one(query)
            if existing:
                skipped_base += 1
            else:
                processed_base += 1

        end_time = time.perf_counter()
        baseline_duration = end_time - start_time
        print(f"Baseline: Processed {processed_base}, Skipped {skipped_base} in {baseline_duration:.4f} seconds")

        # 2. Optimized Benchmark (Bulk Query + Set Check)
        print("\n--- Running Optimized Check (Bulk query + Set) ---")
        start_time = time.perf_counter()

        skipped_opt = 0
        processed_opt = 0

        # We only care about matching mime types
        filtered_files = [
            df for df in drive_files
            if df.get('mimeType') in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        ]

        file_ids = [df['id'] for df in filtered_files]
        if file_ids:
            # Query all matching IDs at once
            query = select(newsletters.c.drive_file_id).where(newsletters.c.drive_file_id.in_(file_ids))
            rows = await database.fetch_all(query)
            existing_drive_ids = {row['drive_file_id'] for row in rows}
        else:
            existing_drive_ids = set()

        for df in filtered_files:
            file_id = df['id']
            if file_id in existing_drive_ids:
                skipped_opt += 1
            else:
                processed_opt += 1

        end_time = time.perf_counter()
        optimized_duration = end_time - start_time
        print(f"Optimized: Processed {processed_opt}, Skipped {skipped_opt} in {optimized_duration:.4f} seconds")

        speedup = baseline_duration / optimized_duration if optimized_duration > 0 else float('inf')
        print(f"\n--- Results Summary ---")
        print(f"Baseline Time: {baseline_duration:.4f}s (performed {len(filtered_files)} DB queries)")
        print(f"Optimized Time: {optimized_duration:.4f}s (performed 1 DB query)")
        print(f"Speedup: {speedup:.2f}x faster!")

        # Verify correctness
        assert skipped_base == skipped_opt, "Skipped count mismatch!"
        assert processed_base == processed_opt, "Processed count mismatch!"
        print("Success: Correctness verified (both strategies yielded identical results)!")

    finally:
        # Clean up benchmark files from DB
        print("\nCleaning up mock data from DB...")
        await database.execute(newsletters.delete().where(newsletters.c.uploader == "benchmark_temp"))
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(run_benchmark())
