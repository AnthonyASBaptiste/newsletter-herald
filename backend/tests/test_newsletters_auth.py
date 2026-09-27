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


@patch("main.database.fetch_all", new_callable=AsyncMock)
def test_get_newsletters_valid_x_api_key(mock_fetch_all):
    mock_fetch_all.return_value = []
    headers = {"X-API-Key": settings.api_key}
    response = client.get("/newsletters", headers=headers)
    assert response.status_code == 200
    assert response.json()["newsletters"] == []
    mock_fetch_all.assert_called_once()


@patch("main.database.fetch_all", new_callable=AsyncMock)
def test_get_newsletters_valid_bearer_token(mock_fetch_all):
    mock_fetch_all.return_value = []
    headers = {"Authorization": f"Bearer {settings.api_key}"}
    response = client.get("/newsletters", headers=headers)
    assert response.status_code == 200
    assert response.json()["newsletters"] == []
    mock_fetch_all.assert_called_once()


@patch("main.database.fetch_one", new_callable=AsyncMock)
def test_regenerate_newsletter_unauthenticated(mock_fetch_one):
    response = client.get("/newsletters/123/regenerate")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
    mock_fetch_one.assert_not_called()


@patch("main.database.fetch_one", new_callable=AsyncMock)
def test_regenerate_newsletter_invalid_api_key(mock_fetch_one):
    response = client.get("/newsletters/123/regenerate", headers={"X-API-Key": "invalid_key"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
    mock_fetch_one.assert_not_called()


@patch("main.database.fetch_one", new_callable=AsyncMock)
def test_regenerate_newsletter_valid_api_key(mock_fetch_one):
    mock_fetch_one.return_value = None  # Newsletter not found, returns 404 after passing auth check
    headers = {"X-API-Key": settings.api_key}
    response = client.get("/newsletters/123/regenerate", headers=headers)
    assert response.status_code in (404, 500)
    assert "Newsletter not found" in response.json()["detail"]
    mock_fetch_one.assert_called_once()
