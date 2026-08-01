import csv
import os
import sys

import pytest

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from db.models import subscribers
from db.setup import database
from scripts.import_gmail_contacts import import_contacts


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
async def cleanup_test_contacts():
    # Setup - make sure we connect to database
    if not database.is_connected:
        await database.connect()
    # Delete before test
    await database.execute(
        subscribers.delete().where(subscribers.c.email.like("test_import_%"))
    )
    yield
    # Cleanup after test
    await database.execute(
        subscribers.delete().where(subscribers.c.email.like("test_import_%"))
    )
    if database.is_connected:
        await database.disconnect()


@pytest.mark.anyio
async def test_bulk_import_and_upsert(anyio_backend, tmp_path):
    # 1. Create temporary CSV with some contacts
    csv_file = tmp_path / "contacts.csv"
    with open(csv_file, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["First Name", "Last Name", "E-mail 1 - Value", "Phone 1 - Value"]
        )
        writer.writerow(["John", "Doe", "test_import_john@example.com", "12345"])
        writer.writerow(["Jane", "Smith", "test_import_jane@example.com", "67890"])
        writer.writerow(["SkipInvalid", "", "invalid_email", ""])  # Should be ignored

    # 2. Run import (this will re-use the connected database state)
    await import_contacts(str(csv_file))

    # 3. Verify they were inserted
    query = (
        select(subscribers)
        .where(subscribers.c.email.like("test_import_%"))
        .order_by(subscribers.c.email)
    )
    results = await database.fetch_all(query)
    assert len(results) == 2

    contacts_map = {r["email"]: dict(r) for r in results}
    assert "test_import_john@example.com" in contacts_map
    assert "test_import_jane@example.com" in contacts_map

    assert contacts_map["test_import_john@example.com"]["first_name"] == "John"
    assert contacts_map["test_import_john@example.com"]["last_name"] == "Doe"
    assert contacts_map["test_import_john@example.com"]["phone"] == "12345"
    assert contacts_map["test_import_john@example.com"]["is_active"] is True

    # 4. Now perform an upsert update using a new CSV where we update John's phone number, Keep Jane's first_name/last_name using empty values (fallback testing)
    with open(csv_file, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["First Name", "Last Name", "E-mail 1 - Value", "Phone 1 - Value"]
        )
        # John updates last name and phone
        writer.writerow(["", "Doe-Updated", "test_import_john@example.com", "99999"])
        # Jane updates nothing (all other columns empty)
        writer.writerow(["", "", "test_import_jane@example.com", ""])

    # Run import_contacts again
    await import_contacts(str(csv_file))

    # 5. Verify the updates
    results_updated = await database.fetch_all(query)
    assert len(results_updated) == 2

    updated_map = {r["email"]: dict(r) for r in results_updated}

    # John's first_name should still be "John" (coalesced), last_name updated to "Doe-Updated", phone updated to "99999"
    assert updated_map["test_import_john@example.com"]["first_name"] == "John"
    assert updated_map["test_import_john@example.com"]["last_name"] == "Doe-Updated"
    assert updated_map["test_import_john@example.com"]["phone"] == "99999"

    # Jane's details should all remain exactly as they were (coalesced)
    assert updated_map["test_import_jane@example.com"]["first_name"] == "Jane"
    assert updated_map["test_import_jane@example.com"]["last_name"] == "Smith"
    assert updated_map["test_import_jane@example.com"]["phone"] == "67890"
