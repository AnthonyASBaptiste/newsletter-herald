import pytest
from unittest.mock import patch, MagicMock
import httpx
from llm.providers import summarize_with_claude

def test_summarize_with_claude_success():
    mock_response_json = {
        "content": [
            {
                "text": '{"title": "Lenten Reflection", "summary": "Join us for Lent.", "schedule_date": "2025-03-30", "liturgical_season": "Lent", "calendar_year": "2025", "liturgical_year": "Year C"}'
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_response_json

    with patch("llm.providers.settings.anthropic_api_key", "test-key"):
        with patch("httpx.post", return_value=mock_resp) as mock_post:
            result = summarize_with_claude("Test prompt")

            assert result["title"] == "Lenten Reflection"
            assert result["summary"] == "Join us for Lent."
            assert result["schedule_date"] == "2025-03-30"
            assert result["liturgical_season"] == "Lent"
            assert result["calendar_year"] == "2025"
            assert result["liturgical_year"] == "Year C"

            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            assert args[0] == "https://api.anthropic.com/v1/messages"
            assert kwargs["headers"]["x-api-key"] == "test-key"

def test_summarize_with_claude_missing_api_key():
    with patch("llm.providers.settings.anthropic_api_key", ""):
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY environment variable is not set"):
            summarize_with_claude("Test prompt")

def test_summarize_with_claude_http_error():
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError("500 Internal Server Error", request=MagicMock(), response=mock_resp)

    with patch("llm.providers.settings.anthropic_api_key", "test-key"):
        with patch("httpx.post", return_value=mock_resp):
            with pytest.raises(Exception, match="Claude API failed"):
                summarize_with_claude("Test prompt")
