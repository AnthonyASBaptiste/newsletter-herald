import pytest
import html
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from main import app

client = TestClient(app)

@pytest.mark.asyncio
@patch("main.database.execute", new_callable=AsyncMock)
@patch("main.database.fetch_one", new_callable=AsyncMock)
async def test_approve_newsletter_summary_xss(mock_fetch_one, mock_execute):
    # Setup malicious XSS inputs
    malicious_filename = "<script>alert(\"XSS Filename\")</script>.pdf"
    malicious_target_sunday = "<img src=x onerror=alert(\"XSS Sunday\")>"

    # Mock database responses
    mock_fetch_one.return_value = {
        "filename": malicious_filename,
        "target_sunday": malicious_target_sunday
    }

    # Send request to approve endpoint
    # Note: We must not send 'accept: application/json' to get the HTMLResponse
    response = client.get("/newsletters/1/approve", headers={"accept": "text/html"})

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    html_content = response.text

    # Verify malicious inputs are escaped and NOT present in their raw form
    assert malicious_filename not in html_content
    assert malicious_target_sunday not in html_content

    # Verify the escaped entities are present instead
    assert html.escape(malicious_filename) in html_content
    assert html.escape(malicious_target_sunday) in html_content


@pytest.mark.asyncio
@patch("main.notify_agent", new_callable=AsyncMock)
@patch("main.choose_llm_and_summarize")
@patch("main.extract_text_from_file")
@patch("main.download_from_drive")
@patch("main.database.execute", new_callable=AsyncMock)
@patch("main.database.fetch_one", new_callable=AsyncMock)
async def test_regenerate_newsletter_summary_xss(
    mock_fetch_one, mock_execute, mock_download, mock_extract, mock_summarize, mock_notify
):
    # Setup malicious XSS inputs
    malicious_filename = "<script>alert(\"XSS Filename\")</script>.pdf"

    # Mock database / storage responses
    mock_fetch_one.return_value = {
        "drive_file_id": "mock_drive_id",
        "filename": malicious_filename,
        "target_sunday": "2026-02-15",
        "status": "draft"
    }
    mock_download.return_value = b"mock PDF content"
    mock_extract.return_value = "extracted newsletter text"
    mock_summarize.return_value = {
        "title": "Newsletter Title",
        "summary": "Newsletter Summary",
        "liturgical_season": "Ordinary Time",
        "calendar_year": "2026",
        "liturgical_year": "C"
    }

    # Send request to regenerate endpoint with html accept header
    response = client.get("/newsletters/1/regenerate", headers={"accept": "text/html"})

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    html_content = response.text

    # Verify malicious inputs are escaped and NOT present in their raw form
    assert malicious_filename not in html_content

    # Verify the escaped entities are present instead
    assert html.escape(malicious_filename) in html_content
