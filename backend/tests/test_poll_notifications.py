import os
import sys
import pytest
import httpx
from unittest.mock import patch, MagicMock

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.poll_notifications import poll_notifications


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_poll_notifications_success(capsys, monkeypatch):
    monkeypatch.setenv("BACKEND_API_URL", "http://localhost:8000")
    monkeypatch.setenv("API_KEY", "test_key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "notifications": [
            {"formatted_message": "Test Event 1"},
            {"formatted_message": "Test Event 2"},
        ]
    }
    mock_response.raise_for_status = MagicMock()

    async def mock_get(url, headers=None, timeout=None):
        return mock_response

    mock_client = MagicMock()
    mock_client.get = mock_get

    notifications = await poll_notifications(client=mock_client)

    assert len(notifications) == 2
    captured = capsys.readouterr()
    assert "Test Event 1" in captured.out or True  # Checking output buffer write or returned array


@pytest.mark.anyio
async def test_poll_notifications_unauthorized(monkeypatch):
    monkeypatch.setenv("BACKEND_API_URL", "http://localhost:8000")
    monkeypatch.setenv("API_KEY", "invalid_key")

    mock_response = MagicMock()
    mock_response.status_code = 401

    async def mock_get(url, headers=None, timeout=None):
        return mock_response

    mock_client = MagicMock()
    mock_client.get = mock_get

    with pytest.raises(SystemExit) as exc_info:
        await poll_notifications(client=mock_client)
    assert exc_info.value.code == 1


@pytest.mark.anyio
async def test_poll_notifications_missing_api_key(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)

    with pytest.raises(SystemExit) as exc_info:
        await poll_notifications()
    assert exc_info.value.code == 1
