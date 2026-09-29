import json
import pytest
from unittest.mock import patch, AsyncMock
from helpers.agent_bridge import notify_agent


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.mark.anyio
async def test_notify_agent_event_id_resolution_newsletter_id():
    data = {"newsletter_id": 42, "title": "Test Title"}
    with patch("db.setup.database.execute", new_callable=AsyncMock) as mock_execute:
        result = await notify_agent("review_request", data)
        assert result is True
        mock_execute.assert_called_once()
        query = mock_execute.call_args[0][0]
        assert "agent_notifications" in str(query)


@pytest.mark.anyio
async def test_notify_agent_event_id_resolution_id_fallback():
    data = {"id": 100, "title": "Fallback ID"}
    with patch("db.setup.database.execute", new_callable=AsyncMock) as mock_execute:
        result = await notify_agent("review_request", data)
        assert result is True
        query_values = mock_execute.call_args[0][0].compile().params
        payload = json.loads(query_values["payload"])
        assert payload["event_id"] == 100


@pytest.mark.anyio
async def test_notify_agent_event_id_resolution_timestamp_fallback():
    data = {"title": "Timestamp Fallback"}
    with patch("db.setup.database.execute", new_callable=AsyncMock) as mock_execute:
        result = await notify_agent("review_request", data)
        assert result is True
        query_values = mock_execute.call_args[0][0].compile().params
        payload = json.loads(query_values["payload"])
        assert isinstance(payload["event_id"], int)
        assert payload["event_id"] > 0


@pytest.mark.anyio
async def test_notify_agent_review_request_with_sanity_id():
    data = {
        "newsletter_id": 10,
        "title": "26th Sunday in Ordinary Time",
        "summary": "Sample summary text",
        "target_sunday": "2026-09-27",
        "sanity_edition_id": "edition-10"
    }
    with patch("helpers.agent_bridge.settings") as mock_settings, \
         patch("db.setup.database.execute", new_callable=AsyncMock) as mock_execute:
        mock_settings.r2_public_domain = "r2.example.com"
        mock_settings.sanity_studio_url = "http://localhost:3333"

        result = await notify_agent("review_request", data)
        assert result is True

        query_values = mock_execute.call_args[0][0].compile().params
        assert query_values["event_type"] == "review_request"
        payload = json.loads(query_values["payload"])

        assert payload["event_id"] == 10
        assert payload["title"] == "26th Sunday in Ordinary Time"
        assert payload["summary"] == "Sample summary text"
        assert payload["target_sunday"] == "2026-09-27"
        assert payload["actions"]["approve_url"] == "https://r2.example.com/newsletters/10/approve"
        assert payload["actions"]["regenerate_url"] == "https://r2.example.com/newsletters/10/regenerate"
        assert payload["actions"]["sync_sanity_url"] == "https://r2.example.com/newsletters/10/sync-sanity"
        assert payload["actions"]["sanity_url"] == "http://localhost:3333/structure/newsletterEdition;edition-10"
        assert "Sanity Studio:" in payload["formatted_message"]
        assert "New Newsletter Summary for Review" in payload["formatted_message"]


@pytest.mark.anyio
async def test_notify_agent_review_request_without_r2_domain_and_sanity_id():
    data = {
        "newsletter_id": 11,
        "title": "No R2 Domain",
        "summary": "Summary without Sanity"
    }
    with patch("helpers.agent_bridge.settings") as mock_settings, \
         patch("db.setup.database.execute", new_callable=AsyncMock) as mock_execute:
        mock_settings.r2_public_domain = None
        mock_settings.api_port = 8000

        result = await notify_agent("review_request", data)
        assert result is True

        query_values = mock_execute.call_args[0][0].compile().params
        payload = json.loads(query_values["payload"])

        assert payload["actions"]["approve_url"] == "http://localhost:8000/newsletters/11/approve"
        assert "sanity_url" not in payload["actions"]
        assert "Sanity Studio:" not in payload["formatted_message"]


@pytest.mark.anyio
async def test_notify_agent_validation_alert():
    data = {
        "newsletter_id": 12,
        "filename": "bulletin.pdf",
        "error_message": "Date mismatch",
        "target_sunday": "2026-10-04"
    }
    with patch("db.setup.database.execute", new_callable=AsyncMock) as mock_execute:
        result = await notify_agent("validation_alert", data)
        assert result is True

        query_values = mock_execute.call_args[0][0].compile().params
        payload = json.loads(query_values["payload"])

        assert "Newsletter Validation Failed" in payload["formatted_message"]
        assert "bulletin.pdf" in payload["formatted_message"]
        assert "Date mismatch" in payload["formatted_message"]


@pytest.mark.anyio
async def test_notify_agent_delivery_report():
    data = {
        "newsletter_id": 13,
        "title": "Weekly Bulletin",
        "sent_count": 150,
        "failed_count": 2
    }
    with patch("db.setup.database.execute", new_callable=AsyncMock) as mock_execute:
        result = await notify_agent("delivery_report", data)
        assert result is True

        query_values = mock_execute.call_args[0][0].compile().params
        payload = json.loads(query_values["payload"])

        assert "Newsletter Delivery Report" in payload["formatted_message"]
        assert "Sent:* 150" in payload["formatted_message"]
        assert "Failed/Bounced:* 2" in payload["formatted_message"]


@pytest.mark.anyio
async def test_notify_agent_bounce_alert():
    data = {
        "recipient": "user@example.com",
        "error_message": "Mailbox full"
    }
    with patch("db.setup.database.execute", new_callable=AsyncMock) as mock_execute:
        result = await notify_agent("bounce_alert", data)
        assert result is True

        query_values = mock_execute.call_args[0][0].compile().params
        payload = json.loads(query_values["payload"])

        assert "Email Bounce Detected" in payload["formatted_message"]
        assert "user@example.com" in payload["formatted_message"]
        assert "Mailbox full" in payload["formatted_message"]


@pytest.mark.anyio
async def test_notify_agent_sanity_sync_failed():
    data = {
        "newsletter_id": 14,
        "title": "Failed Sync Title",
        "target_sunday": "2026-10-11",
        "error_message": "Sanity API 500 error"
    }
    with patch("db.setup.database.execute", new_callable=AsyncMock) as mock_execute:
        result = await notify_agent("sanity_sync_failed", data)
        assert result is True

        query_values = mock_execute.call_args[0][0].compile().params
        payload = json.loads(query_values["payload"])

        assert "Sanity Editorial Sync Failed" in payload["formatted_message"]
        assert "Failed Sync Title" in payload["formatted_message"]
        assert "Sanity API 500 error" in payload["formatted_message"]
        assert "Retry Sanity Sync" in payload["formatted_message"]


@pytest.mark.anyio
async def test_notify_agent_custom_event_type():
    data = {
        "newsletter_id": 15,
        "title": "Custom Event Title"
    }
    with patch("db.setup.database.execute", new_callable=AsyncMock) as mock_execute:
        result = await notify_agent("custom_event", data)
        assert result is True

        query_values = mock_execute.call_args[0][0].compile().params
        payload = json.loads(query_values["payload"])

        assert payload["formatted_message"] == "Notification Alert: custom_event - Custom Event Title"


@pytest.mark.anyio
async def test_notify_agent_db_exception_returns_false():
    data = {"newsletter_id": 99, "title": "Error test"}
    with patch("db.setup.database.execute", side_effect=Exception("Database connection timeout")):
        result = await notify_agent("review_request", data)
        assert result is False


@pytest.mark.anyio
async def test_notify_agent_settings_none_fallback():
    data = {"newsletter_id": 20, "title": "Settings None"}
    with patch("helpers.agent_bridge.settings", None), \
         patch("db.setup.database.execute", new_callable=AsyncMock) as mock_execute:
        result = await notify_agent("review_request", data)
        assert result is True

        query_values = mock_execute.call_args[0][0].compile().params
        payload = json.loads(query_values["payload"])

        assert payload["actions"]["approve_url"] == "http://localhost:8000/newsletters/20/approve"
