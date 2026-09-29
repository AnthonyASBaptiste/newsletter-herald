from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from main import app
from config import get_settings

client = TestClient(app)
settings = get_settings()

@patch("main.database.fetch_all", new_callable=AsyncMock)
def test_get_newsletters_unauthenticated(mock_fetch_all):
    response = client.get("/newsletters")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
    mock_fetch_all.assert_not_called()


@patch("main.database.fetch_all", new_callable=AsyncMock)
def test_get_newsletters_invalid_api_key(mock_fetch_all):
    response = client.get("/newsletters", headers={"X-API-Key": "invalid_key"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
    mock_fetch_all.assert_not_called()


@patch("main.database.fetch_val", new_callable=AsyncMock)
@patch("main.database.fetch_all", new_callable=AsyncMock)
def test_get_newsletters_valid_x_api_key(mock_fetch_all, mock_fetch_val):
    mock_fetch_val.return_value = 0
    mock_fetch_all.return_value = []
    headers = {"X-API-Key": settings.api_key}
    response = client.get("/newsletters", headers=headers)
    assert response.status_code == 200
    assert response.json()["newsletters"] == []
    mock_fetch_all.assert_called_once()


@patch("main.database.fetch_val", new_callable=AsyncMock)
@patch("main.database.fetch_all", new_callable=AsyncMock)
def test_get_newsletters_valid_bearer_token(mock_fetch_all, mock_fetch_val):
    mock_fetch_val.return_value = 0
    mock_fetch_all.return_value = []
    headers = {"Authorization": f"Bearer {settings.api_key}"}
    response = client.get("/newsletters", headers=headers)
    assert response.status_code == 200
    assert response.json()["newsletters"] == []
    mock_fetch_all.assert_called_once()


@patch("main.database.execute", new_callable=AsyncMock)
@patch("main.database.fetch_one", new_callable=AsyncMock)
def test_approve_newsletter_unauthenticated(mock_fetch_one, mock_execute):
    response = client.get("/newsletters/1/approve")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
    mock_execute.assert_not_called()
    mock_fetch_one.assert_not_called()


@patch("main.database.execute", new_callable=AsyncMock)
@patch("main.database.fetch_one", new_callable=AsyncMock)
def test_approve_newsletter_invalid_api_key(mock_fetch_one, mock_execute):
    response = client.get("/newsletters/1/approve", headers={"X-API-Key": "invalid_key"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
    mock_execute.assert_not_called()
    mock_fetch_one.assert_not_called()


@patch("main.database.execute", new_callable=AsyncMock)
@patch("main.database.fetch_one", new_callable=AsyncMock)
def test_approve_newsletter_valid_x_api_key(mock_fetch_one, mock_execute):
    mock_fetch_one.return_value = {"filename": "test.pdf", "target_sunday": "2026-03-01"}
    headers = {"X-API-Key": settings.api_key, "accept": "application/json"}
    response = client.get("/newsletters/1/approve", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Approved successfully"
    mock_execute.assert_called_once()
    mock_fetch_one.assert_called_once()


@patch("main.database.execute", new_callable=AsyncMock)
@patch("main.database.fetch_one", new_callable=AsyncMock)
def test_approve_newsletter_valid_bearer_token(mock_fetch_one, mock_execute):
    mock_fetch_one.return_value = {"filename": "test.pdf", "target_sunday": "2026-03-01"}
    headers = {"Authorization": f"Bearer {settings.api_key}", "accept": "application/json"}
    response = client.get("/newsletters/1/approve", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Approved successfully"
    mock_execute.assert_called_once()
    mock_fetch_one.assert_called_once()
