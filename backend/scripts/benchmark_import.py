import csv
import time
import asyncio
import os
import sys

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from db.setup import database
from db.models import subscribers
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import func

# Generate a mock contacts.csv for benchmarking
def create_mock_csv(file_path, num_rows=100):
    with open(file_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["First Name", "Last Name", "E-mail 1 - Value", "Phone 1 - Value"])
        for i in range(num_rows):
            writer.writerow([
                f"First{i}",
                f"Last{i}",
                f"bench_user_{i}@example.com",
                f"+12345678{i:02d}"
            ])

async def cleanup_bench_users():
    try:
        query = subscribers.delete().where(subscribers.c.email.like("bench_user_%"))
        await database.execute(query)
        print("Cleaned up benchmark subscribers from DB")
    except Exception as e:
        print(f"Cleanup error: {e}")

async def run_legacy_method(csv_path):
    print("\n--- Running current slow import method (legacy) ---")
    try:
        with open(csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            count = 0
            start_time = time.time()
            for row in reader:
                email = row.get("E-mail 1 - Value", "").strip().lower()
                if not email or "@" not in email:
                    continue

                first_name = row.get("First Name", "").strip() or None
                last_name = row.get("Last Name", "").strip() or None
                phone = row.get("Phone 1 - Value", "").strip() or None

                # Check if subscriber already exists
                query = select(subscribers).where(subscribers.c.email == email)
                existing = await database.fetch_one(query)

                if existing:
                    # Update details if changed
                    update_query = subscribers.update().where(subscribers.c.email == email).values(
                        first_name=first_name or existing["first_name"],
                        last_name=last_name or existing["last_name"],
                        phone=phone or existing["phone"],
                        is_active=True
                    )
                    await database.execute(update_query)
                else:
                    # Insert new subscriber
                    insert_query = subscribers.insert().values(
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        phone=phone,
                        is_active=True
                    )
                    await database.execute(insert_query)
                count += 1
            duration = time.time() - start_time
            print(f"Legacy import took: {duration:.4f} seconds for {count} rows")
            return duration
    except Exception as e:
        print(f"Legacy import error: {e}")
        return 0

async def run_optimized_method(csv_path):
    print("\n--- Running optimized bulk import method ---")
    try:
        with open(csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            values_to_insert = []
            seen_emails = set()
            start_time = time.time()

            for row in reader:
                email = row.get("E-mail 1 - Value", "").strip().lower()
                if not email or "@" not in email:
                    continue

                if email in seen_emails:
                    continue
                seen_emails.add(email)

                first_name = row.get("First Name", "").strip() or None
                last_name = row.get("Last Name", "").strip() or None
                phone = row.get("Phone 1 - Value", "").strip() or None

                values_to_insert.append({
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone": phone,
                    "is_active": True
                })

            if not values_to_insert:
                print("No valid contacts found in CSV.")
                return 0

            stmt = pg_insert(subscribers)
            stmt = stmt.on_conflict_do_update(
                index_elements=['email'],
                set_={
                    'first_name': func.coalesce(stmt.excluded.first_name, subscribers.c.first_name),
                    'last_name': func.coalesce(stmt.excluded.last_name, subscribers.c.last_name),
                    'phone': func.coalesce(stmt.excluded.phone, subscribers.c.phone),
                    'is_active': True
                }
            )

            await database.execute_many(stmt, values_to_insert)
            duration = time.time() - start_time
            print(f"Optimized import took: {duration:.4f} seconds for {len(values_to_insert)} rows")
            return duration
    except Exception as e:
        print(f"Optimized import error: {e}")
        return 0

async def main():
    csv_path = "bench_contacts.csv"
    create_mock_csv(csv_path, num_rows=100)

    await database.connect()
    try:
        # Measure legacy
        await cleanup_bench_users()
        leg_ins = await run_legacy_method(csv_path)
        leg_upd = await run_legacy_method(csv_path)

        # Measure optimized
        await cleanup_bench_users()
        opt_ins = await run_optimized_method(csv_path)
        opt_upd = await run_optimized_method(csv_path)

        # Final cleanup
        await cleanup_bench_users()

        print("\n================ BENCHMARK RESULTS ================")
        print(f"{'Operation':<15} | {'Legacy Time (s)':<15} | {'Optimized Time (s)':<18} | {'Speedup':<10}")
        print("-" * 68)
        print(f"{'100 Inserts':<15} | {leg_ins:<15.4f} | {opt_ins:<18.4f} | {leg_ins/opt_ins:<10.2f}x")
        print(f"{'100 Updates':<15} | {leg_upd:<15.4f} | {opt_upd:<18.4f} | {leg_upd/opt_upd:<10.2f}x")
        print("===================================================")

    finally:
        await database.disconnect()
        if os.path.exists(csv_path):
            os.remove(csv_path)

if __name__ == "__main__":
    asyncio.run(main())
