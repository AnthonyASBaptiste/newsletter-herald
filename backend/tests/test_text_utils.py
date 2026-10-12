import pytest
from unittest.mock import patch
import helpers.text_utils as text_utils
from helpers.text_utils import count_tokens


def test_count_tokens_default_model():
    """Test count_tokens with default model gpt-3.5-turbo."""
    text = "Hello world! This is a test string."
    count = count_tokens(text)
    assert isinstance(count, int)
    assert count > 0


def test_count_tokens_empty_string():
    """Test count_tokens with an empty string."""
    count = count_tokens("")
    assert count == 0


def test_count_tokens_different_models():
    """Test count_tokens with different supported models."""
    text = "Testing token count across different OpenAI model encodings."
    count_gpt3 = count_tokens(text, model="gpt-3.5-turbo")
    count_gpt4 = count_tokens(text, model="gpt-4")
    count_gpt4o = count_tokens(text, model="gpt-4o")

    assert count_gpt3 > 0
    assert count_gpt4 > 0
    assert count_gpt4o > 0


def test_count_tokens_tiktoken_missing():
    """Test fallback behavior when tiktoken is None."""
    with patch.object(text_utils, "tiktoken", None):
        # When text is empty, split() gives [] so max(1, 0) returns 1
        assert count_tokens("") == 1

        # When text has words, word count is returned
        text = "One two three four five"
        assert count_tokens(text) == 5


def test_count_tokens_invalid_model():
    """Test count_tokens handling when model name is invalid or unknown to tiktoken."""
    with pytest.raises(Exception):
        count_tokens("Some text", model="non-existent-model-xyz")
