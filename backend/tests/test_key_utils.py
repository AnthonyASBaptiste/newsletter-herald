import pytest
from unittest.mock import Mock
from fastapi import Request, HTTPException
from helpers.key_utils import verify_api_key, settings

def create_mock_request(headers: dict):
    request = Mock(spec=Request)
    request.headers = headers
    return request

def test_verify_api_key_bearer_success():
    api_key = settings.api_key
    headers = {"Authorization": f"Bearer {api_key}"}
    request = create_mock_request(headers)

    # Should run without raising an exception
    verify_api_key(request)

def test_verify_api_key_x_api_key_success():
    api_key = settings.api_key
    headers = {"X-API-Key": api_key}
    request = create_mock_request(headers)

    # Should run without raising an exception
    verify_api_key(request)

def test_verify_api_key_missing_headers():
    headers = {}
    request = create_mock_request(headers)

    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Unauthorized"

def test_verify_api_key_invalid_bearer():
    headers = {"Authorization": "Bearer invalid_key"}
    request = create_mock_request(headers)

    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(request)
    assert exc_info.value.status_code == 401

def test_verify_api_key_invalid_x_api_key():
    headers = {"X-API-Key": "invalid_key"}
    request = create_mock_request(headers)

    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(request)
    assert exc_info.value.status_code == 401
