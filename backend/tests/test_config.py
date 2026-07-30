import unittest
import os
from unittest import mock
from config import Settings

class TestConfigCORS(unittest.TestCase):
    def test_cors_origins_default(self):
        """Test that cors_origins defaults to an empty list."""
        env_vars = {
            "API_KEY": "test_key",
            "ANTHROPIC_API_KEY": "test_anthropic",
            "STACK_PROJECT_ID": "test_stack",
            "STACK_PUBLISHABLE_CLIENT_KEY": "test_pub",
            "STACK_SECRET_SERVER_KEY": "test_secret",
            "DATABASE_URL": "postgresql://localhost/db",
        }
        with mock.patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            self.assertEqual(settings.cors_origins, [
                "https://newsletter-herald.vercel.app",
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ])

    def test_cors_origins_comma_separated(self):
        """Test that cors_origins parses a comma-separated string."""
        env_vars = {
            "API_KEY": "test_key",
            "ANTHROPIC_API_KEY": "test_anthropic",
            "STACK_PROJECT_ID": "test_stack",
            "STACK_PUBLISHABLE_CLIENT_KEY": "test_pub",
            "STACK_SECRET_SERVER_KEY": "test_secret",
            "DATABASE_URL": "postgresql://localhost/db",
            "CORS_ORIGINS": "http://localhost:3000, https://newsletter-herald.vercel.app , http://127.0.0.1:3000",
        }
        with mock.patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            self.assertEqual(settings.cors_origins, [
                "http://localhost:3000",
                "https://newsletter-herald.vercel.app",
                "http://127.0.0.1:3000"
            ])

    def test_cors_origins_json_list(self):
        """Test that cors_origins parses a JSON encoded list."""
        env_vars = {
            "API_KEY": "test_key",
            "ANTHROPIC_API_KEY": "test_anthropic",
            "STACK_PROJECT_ID": "test_stack",
            "STACK_PUBLISHABLE_CLIENT_KEY": "test_pub",
            "STACK_SECRET_SERVER_KEY": "test_secret",
            "DATABASE_URL": "postgresql://localhost/db",
            "CORS_ORIGINS": '["http://localhost:3000", "https://newsletter-herald.vercel.app"]',
        }
        with mock.patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            self.assertEqual(settings.cors_origins, [
                "http://localhost:3000",
                "https://newsletter-herald.vercel.app"
            ])

    def test_cors_origins_empty_string(self):
        """Test that cors_origins handles an empty string environment variable."""
        env_vars = {
            "API_KEY": "test_key",
            "ANTHROPIC_API_KEY": "test_anthropic",
            "STACK_PROJECT_ID": "test_stack",
            "STACK_PUBLISHABLE_CLIENT_KEY": "test_pub",
            "STACK_SECRET_SERVER_KEY": "test_secret",
            "DATABASE_URL": "postgresql://localhost/db",
            "CORS_ORIGINS": "   ",
        }
        with mock.patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            self.assertEqual(settings.cors_origins, [])

if __name__ == "__main__":
    unittest.main()
