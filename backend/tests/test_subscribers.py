import pytest
import json
from fastapi.testclient import TestClient
from main import app, BatchSubscribersRequest, batch_subscribe_users
from db.setup import database
from db.models import subscribers
from sqlalchemy import delete, select
from helpers.key_utils import generate_unsubscribe_token
from config import get_settings

settings = get_settings()
client = TestClient(app)

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
        if database.is_connected:
            await database.disconnect()


@pytest.mark.anyio
async def test_unsubscribe_security(anyio_backend):
    if not database.is_connected:
        await database.connect()

    target_email = "security-test@subscriber-test.com"

    try:
        # Clean up and insert an active subscriber
        await database.execute(
            delete(subscribers).where(subscribers.c.email == target_email)
        )
        await database.execute(
            subscribers.insert().values(email=target_email, is_active=True)
        )

        # 1. Unsubscribe attempt without token or API key should fail (401)
        res_unauth = client.post(
            "/subscribers/unsubscribe",
            json={"email": target_email}
        )
        assert res_unauth.status_code == 401
        assert "Unauthorized" in res_unauth.json()["detail"]

        # 2. Unsubscribe attempt with invalid token should fail (401)
        res_invalid = client.post(
            "/subscribers/unsubscribe",
            json={"email": target_email, "token": "invalid_token_123"}
        )
        assert res_invalid.status_code == 401

        # 3. Unsubscribe attempt with valid HMAC token should succeed (200)
        valid_token = generate_unsubscribe_token(target_email)
        res_valid_token = client.post(
            "/subscribers/unsubscribe",
            json={"email": target_email, "token": valid_token}
        )
        assert res_valid_token.status_code == 200
        assert res_valid_token.json()["message"] == "You have been successfully unsubscribed."

        # Verify DB state: is_active should now be False
        row = await database.fetch_one(
            select(subscribers).where(subscribers.c.email == target_email)
        )
        assert row["is_active"] is False

        # Reactivate subscriber for next test
        await database.execute(
            subscribers.update()
            .where(subscribers.c.email == target_email)
            .values(is_active=True)
        )

        # 4. GET request with valid token in query params should also succeed (200)
        res_get = client.get(
            f"/subscribers/unsubscribe?email={target_email}&token={valid_token}"
        )
        assert res_get.status_code == 200

        # Verify DB state: is_active should again be False
        row = await database.fetch_one(
            select(subscribers).where(subscribers.c.email == target_email)
        )
        assert row["is_active"] is False

        # Reactivate subscriber
        await database.execute(
            subscribers.update()
            .where(subscribers.c.email == target_email)
            .values(is_active=True)
        )

        # 5. Unsubscribe attempt with valid API Key header should succeed (200)
        res_api_key = client.post(
            "/subscribers/unsubscribe",
            json={"email": target_email},
            headers={"X-API-Key": settings.api_key}
        )
        assert res_api_key.status_code == 200

        row = await database.fetch_one(
            select(subscribers).where(subscribers.c.email == target_email)
        )
        assert row["is_active"] is False

    finally:
        await database.execute(
            delete(subscribers).where(subscribers.c.email == target_email)
        )
        if database.is_connected:
            await database.disconnect()
