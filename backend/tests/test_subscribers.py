import pytest
from main import BatchSubscribersRequest, batch_subscribe_users
from db.setup import database
from db.models import subscribers
from sqlalchemy import delete

@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"

@pytest.mark.anyio
async def test_batch_subscribe_endpoint(anyio_backend):
    # Connect database if not connected
    if not database.is_connected:
        await database.connect()

    try:
        # Clean up any prior test emails
        await database.execute(
            delete(subscribers).where(subscribers.c.email.like("%@subscriber-test.com"))
        )

        # 1. Insert a subscriber as inactive first so we can test reactivation
        await database.execute(
            subscribers.insert().values(email="inactive@subscriber-test.com", is_active=False)
        )
        # 2. Insert a subscriber as active so we can test skip/duplicate
        await database.execute(
            subscribers.insert().values(email="active@subscriber-test.com", is_active=True)
        )

        # Prepare test batch
        emails = [
            "  New@subscriber-test.com  ",    # Should be cleaned to "new@subscriber-test.com"
            "active@subscriber-test.com",      # Should be skipped
            "inactive@subscriber-test.com",    # Should be reactivated
            "invalid_email",                   # Should be skipped (no @)
            "new@subscriber-test.com",         # Duplicate in batch, should be skipped
        ]

        request_data = BatchSubscribersRequest(emails=emails)
        response = await batch_subscribe_users(request_data)

        # Verify response structure and correctness
        assert response.status_code == 200
        import json
        res_data = json.loads(response.body.decode())

        # 1 new added: new@subscriber-test.com
        # 1 reactivated: inactive@subscriber-test.com
        # 3 skipped: active@subscriber-test.com (duplicate), invalid_email (invalid), second new@subscriber-test.com (internal duplicate)
        assert res_data["added"] == 1
        assert res_data["reactivated"] == 1
        assert res_data["skipped"] == 3

    finally:
        # Clean up test emails
        await database.execute(
            delete(subscribers).where(subscribers.c.email.like("%@subscriber-test.com"))
        )
        await database.disconnect()
