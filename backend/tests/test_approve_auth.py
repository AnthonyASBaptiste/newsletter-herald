import os
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient

# Ensure required environment variables are set before main is imported
os.environ.setdefault("API_KEY", "test-secret-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from main import app
from config import get_settings

settings = get_settings()

client = TestClient(app)


def test_approve_newsletter_unauthorized_missing_headers():
    response = client.get("/newsletters/123/approve")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_approve_newsletter_unauthorized_invalid_bearer_key():
    headers = {"Authorization": "Bearer wrong-key"}
    response = client.get("/newsletters/123/approve", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_approve_newsletter_unauthorized_invalid_x_api_key():
    headers = {"X-API-Key": "wrong-key"}
    response = client.get("/newsletters/123/approve", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


@patch("main.database.execute", new_callable=AsyncMock)
@patch("main.database.fetch_one", new_callable=AsyncMock)
def test_approve_newsletter_authorized_bearer(mock_fetch_one, mock_execute):
    mock_execute.return_value = None
    mock_fetch_one.return_value = {
        "filename": "test_bulletin.pdf",
        "target_sunday": "2026-10-04",
    }

    headers = {"Authorization": f"Bearer {settings.api_key}"}
    response = client.get(
        "/newsletters/123/approve?format=json",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Approved successfully"
    assert data["newsletter_id"] == 123
    assert data["filename"] == "test_bulletin.pdf"
    assert data["target_sunday"] == "2026-10-04"


@patch("main.database.execute", new_callable=AsyncMock)
@patch("main.database.fetch_one", new_callable=AsyncMock)
def test_approve_newsletter_authorized_x_api_key(mock_fetch_one, mock_execute):
    mock_execute.return_value = None
    mock_fetch_one.return_value = {
        "filename": "test_bulletin.pdf",
        "target_sunday": "2026-10-04",
    }

    headers = {"X-API-Key": settings.api_key}
    response = client.get(
        "/newsletters/123/approve?format=json",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Approved successfully"
    assert data["newsletter_id"] == 123
