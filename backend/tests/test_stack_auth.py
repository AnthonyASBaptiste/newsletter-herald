from unittest.mock import MagicMock, patch
import pytest
import requests
from helpers.auth import stack_auth_request


@patch("helpers.auth.settings")
@patch("helpers.auth.requests.request")
def test_stack_auth_request_success(mock_request, mock_settings):
    mock_settings.stack_project_id = "proj_123"
    mock_settings.stack_publishable_client_key = "pub_key"
    mock_settings.stack_secret_server_key = "secret_key"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "user_123", "email": "test@example.com"}
    mock_request.return_value = mock_response

    result = stack_auth_request("GET", "api/v1/users/me")

    assert result == {"id": "user_123", "email": "test@example.com"}
    mock_request.assert_called_once_with(
        "GET",
        "https://api.stack-auth.com/api/v1/users/me",
        headers={
            "x-stack-access-type": "server",
            "x-stack-project-id": "proj_123",
            "x-stack-publishable-client-key": "pub_key",
            "x-stack-secret-server-key": "secret_key",
        },
    )


@patch("helpers.auth.settings")
@patch("helpers.auth.requests.request")
def test_stack_auth_request_custom_headers_and_kwargs(mock_request, mock_settings):
    mock_settings.stack_project_id = "proj_123"
    mock_settings.stack_publishable_client_key = "pub_key"
    mock_settings.stack_secret_server_key = "secret_key"

    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"status": "created"}
    mock_request.return_value = mock_response

    custom_headers = {"Content-Type": "application/json", "x-custom-header": "value"}
    json_payload = {"name": "Test User"}

    result = stack_auth_request(
        "POST",
        "api/v1/users",
        headers=custom_headers,
        json=json_payload,
    )

    assert result == {"status": "created"}
    mock_request.assert_called_once_with(
        "POST",
        "https://api.stack-auth.com/api/v1/users",
        headers={
            "x-stack-access-type": "server",
            "x-stack-project-id": "proj_123",
            "x-stack-publishable-client-key": "pub_key",
            "x-stack-secret-server-key": "secret_key",
            "Content-Type": "application/json",
            "x-custom-header": "value",
        },
        json=json_payload,
    )


@patch("helpers.auth.settings")
@patch("helpers.auth.requests.request")
def test_stack_auth_request_error_response(mock_request, mock_settings):
    mock_settings.stack_project_id = "proj_123"
    mock_settings.stack_publishable_client_key = "pub_key"
    mock_settings.stack_secret_server_key = "secret_key"

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = '{"error": "Unauthorized"}'
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        stack_auth_request("GET", "api/v1/protected")

    assert 'Stack Auth API request failed with 401: {"error": "Unauthorized"}' in str(
        exc_info.value
    )


@patch("helpers.auth.settings")
@patch("helpers.auth.requests.request")
def test_stack_auth_request_connection_error(mock_request, mock_settings):
    mock_settings.stack_project_id = "proj_123"
    mock_settings.stack_publishable_client_key = "pub_key"
    mock_settings.stack_secret_server_key = "secret_key"

    mock_request.side_effect = requests.exceptions.RequestException("Connection failed")

    with pytest.raises(requests.exceptions.RequestException) as exc_info:
        stack_auth_request("GET", "api/v1/users")

    assert "Connection failed" in str(exc_info.value)
