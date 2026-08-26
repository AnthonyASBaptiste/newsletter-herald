import pytest
import re
from fastapi.testclient import TestClient
from main import app

# The CORS origin regex configured in main.py
CORS_ORIGIN_REGEX = r"https://[a-zA-Z0-9-]+\.vercel\.app$"

def test_cors_origin_regex_valid():
    pattern = re.compile(CORS_ORIGIN_REGEX)
    valid_origins = [
        "https://newsletter-herald.vercel.app",
        "https://newsletter-herald-git-main.vercel.app",
        "https://preview-123.vercel.app",
        "https://a-b-c.vercel.app",
    ]
    for origin in valid_origins:
        assert pattern.match(origin) is not None, f"Expected {origin} to match CORS origin regex"

def test_cors_origin_regex_invalid():
    pattern = re.compile(CORS_ORIGIN_REGEX)
    invalid_origins = [
        "https://newsletter-herald.vercel.app.attacker.com",
        "https://attacker.vercel.app.evil.com",
        "http://newsletter-herald.vercel.app",
        "https://evilvercel.app",
        "https://vercel.app.attacker.com",
        "https://newsletter-herald.vercel.app/path",
        "https://sub.domain.vercel.app",
    ]
    for origin in invalid_origins:
        assert pattern.match(origin) is None, f"Expected {origin} NOT to match CORS origin regex"

def test_cors_middleware_integration():
    client = TestClient(app)

    # Valid origin allowed
    valid_resp = client.options(
        "/",
        headers={
            "Origin": "https://newsletter-herald-preview.vercel.app",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert valid_resp.headers.get("access-control-allow-origin") == "https://newsletter-herald-preview.vercel.app"

    # Malicious bypass origin rejected
    invalid_resp = client.options(
        "/",
        headers={
            "Origin": "https://newsletter-herald.vercel.app.attacker.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert invalid_resp.headers.get("access-control-allow-origin") is None
