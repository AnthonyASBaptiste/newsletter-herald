import asyncio
import csv
import os
import sys

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as pg_insert

from db.models import subscribers
from db.setup import database


async def import_contacts(csv_path: str = r"C:\Users\CBCGaming\Downloads\contacts.csv"):
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    print(f"Reading contacts from: {csv_path}")
    was_connected = database.is_connected
    if not was_connected:
        await database.connect()
    try:
        with open(csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            values_to_insert = []
            seen_emails = set()

            for row in reader:
                email = row.get("E-mail 1 - Value", "").strip().lower()
                if not email or "@" not in email:
                    continue

                # Prevent duplicate entries within the same CSV file
                if email in seen_emails:
                    continue
                seen_emails.add(email)

                first_name = row.get("First Name", "").strip() or None
                last_name = row.get("Last Name", "").strip() or None
                phone = row.get("Phone 1 - Value", "").strip() or None

                values_to_insert.append(
                    {
                        "email": email,
                        "first_name": first_name,
                        "last_name": last_name,
                        "phone": phone,
                        "is_active": True,
                    }
                )

            if not values_to_insert:
                print("No valid contacts found in CSV.")
                return

            print(
                f"Loaded {len(values_to_insert)} unique contacts. Bulk importing to database..."
            )

            # Use PostgreSQL bulk upsert (INSERT ... ON CONFLICT DO UPDATE)
            # COALESCE ensures we preserve existing data if the CSV row has a null/empty value for a column.
            stmt = pg_insert(subscribers)
            stmt = stmt.on_conflict_do_update(
                index_elements=["email"],
                set_={
                    "first_name": func.coalesce(
                        stmt.excluded.first_name, subscribers.c.first_name
                    ),
                    "last_name": func.coalesce(
                        stmt.excluded.last_name, subscribers.c.last_name
                    ),
                    "phone": func.coalesce(stmt.excluded.phone, subscribers.c.phone),
                    "is_active": True,
                },
            )

            await database.execute_many(stmt, values_to_insert)
            print(f"Successfully processed {len(values_to_insert)} subscribers!")
    except Exception as e:
        print(f"Error importing contacts: {e}")
    finally:
        if not was_connected:
            await database.disconnect()


if __name__ == "__main__":
    asyncio.run(import_contacts())
