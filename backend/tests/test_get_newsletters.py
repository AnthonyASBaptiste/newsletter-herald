import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from main import app
from config import get_settings

client = TestClient(app)
settings = get_settings()

@patch("main.database.fetch_all", new_callable=AsyncMock)
@patch("main.database.fetch_val", new_callable=AsyncMock)
def test_get_newsletters_query_construction(mock_fetch_val, mock_fetch_all):
    mock_fetch_val.return_value = 1
    mock_fetch_all.return_value = [
        {
            "id": 1,
            "filename": "test.pdf",
            "drive_web_view_link": "http://example.com",
            "thumbnail_drive_id": "thumb1",
            "uploaded_at": None,
            "status": "draft",
            "target_sunday": None,
            "tags": "test",
            "scheduled_at": None,
            "title": "Test Title",
            "summary": "Test Summary",
        }
    ]

    headers = {"X-API-Key": settings.api_key}
    response = client.get("/newsletters?status=draft&limit=10&offset=0", headers=headers)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["total"] == 1
    assert json_data["has_more"] is False
    assert len(json_data["newsletters"]) == 1
    assert json_data["newsletters"][0]["id"] == 1

    # Verify database calls received SQLAlchemy Select objects
    mock_fetch_val.assert_called_once()
    val_args, val_kwargs = mock_fetch_val.call_args
    # The first positional arg is the query
    count_query = val_args[0]
    assert "FROM newsletters" in str(count_query)
    assert "WHERE newsletters.status =" in str(count_query)

    mock_fetch_all.assert_called_once()
    all_args, all_kwargs = mock_fetch_all.call_args
    main_query = all_kwargs.get("query") if "query" in all_kwargs else all_args[0]
    sql_str = str(main_query)
    assert "newsletters.status =" in sql_str
    assert "LIMIT" in sql_str
    assert "OFFSET" in sql_str
