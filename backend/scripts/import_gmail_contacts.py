import csv
import asyncio
import os
import sys

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from db.setup import database
from db.models import subscribers
from sqlalchemy import select

async def import_contacts():
    csv_path = r"C:\Users\CBCGaming\Downloads\contacts.csv"
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return
        
    print(f"Reading contacts from: {csv_path}")
    await database.connect()
    try:
        with open(csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            count = 0
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
                    print(f"Updated: {email} ({first_name} {last_name})")
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
                    print(f"Imported: {email} ({first_name} {last_name})")
                count += 1
            print(f"Successfully processed {count} subscribers!")
    except Exception as e:
        print(f"Error importing contacts: {e}")
    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(import_contacts())
