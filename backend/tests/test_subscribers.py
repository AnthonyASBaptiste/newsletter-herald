import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from config import get_settings
from db.models import subscribers
from db.setup import database
from helpers.key_utils import generate_unsubscribe_token
from main import BatchSubscribersRequest, app, batch_subscribe_users

settings = get_settings()
client = TestClient(app)


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


def test_batch_subscribe_unauthenticated():
    response = client.post("/subscribers/batch", json={"emails": ["test@example.com"]})
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"


def test_batch_subscribe_invalid_api_key():
    response = client.post(
        "/subscribers/batch",
        headers={"X-API-Key": "invalid_key"},
        json={"emails": ["test@example.com"]},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"


@pytest.mark.anyio
async def test_batch_subscribe_endpoint(anyio_backend):
    if not database.is_connected:
        await database.connect()

    try:
        await database.execute(
            delete(subscribers).where(subscribers.c.email.like("%@subscriber-test.com"))
        )
        await database.execute(
            subscribers.insert().values(email="inactive@subscriber-test.com", is_active=False)
        )
        await database.execute(
            subscribers.insert().values(email="active@subscriber-test.com", is_active=True)
        )

        emails = [
            "  New@subscriber-test.com  ",
            "active@subscriber-test.com",
            "inactive@subscriber-test.com",
            "invalid_email",
            "new@subscriber-test.com",
        ]
        response = await batch_subscribe_users(BatchSubscribersRequest(emails=emails))
        assert response.status_code == 200
        result = json.loads(response.body.decode())
        assert result["added"] == 1
        assert result["reactivated"] == 1
        assert result["skipped"] == 3
    finally:
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
        await database.execute(delete(subscribers).where(subscribers.c.email == target_email))
        await database.execute(
            subscribers.insert().values(email=target_email, is_active=True)
        )

        unauthenticated = client.post("/subscribers/unsubscribe", json={"email": target_email})
        assert unauthenticated.status_code == 401
        assert "Unauthorized" in unauthenticated.json()["detail"]

        invalid_token = client.post(
            "/subscribers/unsubscribe",
            json={"email": target_email, "token": "invalid_token_123"},
        )
        assert invalid_token.status_code == 401

        token = generate_unsubscribe_token(target_email)
        valid_token = client.post(
            "/subscribers/unsubscribe",
            json={"email": target_email, "token": token},
        )
        assert valid_token.status_code == 200
        assert valid_token.json()["message"] == "You have been successfully unsubscribed."
        row = await database.fetch_one(
            select(subscribers).where(subscribers.c.email == target_email)
        )
        assert row["is_active"] is False

        await database.execute(
            subscribers.update()
            .where(subscribers.c.email == target_email)
            .values(is_active=True)
        )
        get_response = client.get(
            f"/subscribers/unsubscribe?email={target_email}&token={token}"
        )
        assert get_response.status_code == 200
        row = await database.fetch_one(
            select(subscribers).where(subscribers.c.email == target_email)
        )
        assert row["is_active"] is False

        await database.execute(
            subscribers.update()
            .where(subscribers.c.email == target_email)
            .values(is_active=True)
        )
        api_key_response = client.post(
            "/subscribers/unsubscribe",
            json={"email": target_email},
            headers={"X-API-Key": settings.api_key},
        )
        assert api_key_response.status_code == 200
        row = await database.fetch_one(
            select(subscribers).where(subscribers.c.email == target_email)
        )
        assert row["is_active"] is False
    finally:
        await database.execute(delete(subscribers).where(subscribers.c.email == target_email))
        if database.is_connected:
            await database.disconnect()


@patch("main.database.fetch_one", new_callable=AsyncMock)
def test_delete_subscriber_unauthenticated(mock_fetch_one):
    response = client.delete("/subscribers/123")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
    mock_fetch_one.assert_not_called()


@patch("main.database.fetch_one", new_callable=AsyncMock)
def test_delete_subscriber_invalid_api_key(mock_fetch_one):
    response = client.delete("/subscribers/123", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
    mock_fetch_one.assert_not_called()


@patch("main.database.execute", new_callable=AsyncMock)
@patch("main.database.fetch_one", new_callable=AsyncMock)
def test_delete_subscriber_authenticated_success(mock_fetch_one, mock_execute):
    mock_fetch_one.return_value = {"id": 123, "email": "test@subscriber.com"}
    response = client.delete("/subscribers/123", headers={"X-API-Key": settings.api_key})
    assert response.status_code == 200
    assert response.json()["message"] == "Subscriber removed successfully"
    mock_fetch_one.assert_called_once()
    mock_execute.assert_called_once()
