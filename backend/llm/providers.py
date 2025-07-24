import requests
import logging
from typing import Dict, Any, Optional

from config import get_settings
from helpers.constants import ANTHROPIC_API_KEY
from helpers.text_utils import count_tokens

# Get settings from centralized configuration
settings = get_settings()

# Create a logger for this module
logger = logging.getLogger(__name__)


def summarize_with_mistral(prompt: str, timeout: int = 30) -> str:
    """
    Summarizes a given text input using the Mistral model by making a POST request to
    a local endpoint. The method expects a text prompt, sends it to the Mistral API for
    processing, and returns the generated summary.

    Args:
        prompt: The input text to be summarized.
        timeout: The maximum time, in seconds, to await a response from the
            Mistral API. If not specified, defaults to 30 seconds.

    Returns:
        str: The generated summary based on the given prompt.

    Raises:
        Exception: If the response status code from the Mistral API is not 200, an
            exception is raised with the error details from the API.
    """
    logger.debug("Sending request to Mistral API")
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            timeout=timeout,
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False,
            }
        )

        if response.status_code != 200:
            error_msg = f"Mistral error: {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

        data = response.json()
        logger.debug("Successfully received response from Mistral API")
        return data["response"].strip()
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Request to Mistral API failed: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


def summarize_with_claude(prompt: str, timeout: int = 30) -> str:
    """
    Summarizes Roman Catholic Church newsletters into concise and warm email messages
    using the Claude model via the Anthropic API. This function leverages the
    Anthropic Claude-3 Opus model to process user-provided newsletter texts and produce
    summarized output with adjusted creativity and token limits.

    Args:
        prompt: The input text to be summarized, typically a Roman Catholic
            Church newsletter in plain text format.
        timeout: The maximum time, in seconds, to await a response from the
            Anthropic API. If not specified, defaults to 30 seconds.

    Returns:
        str: A summarized version of the input text, formatted as a concise email
            message.

    Raises:
        ValueError: If the required `ANTHROPIC_API_KEY` environment variable
            is not set.
        Exception: For API-level errors, unexpected response formats, or any
            HTTP request-related failures.
    """
    if not settings.anthropic_api_key:
        error_msg = "ANTHROPIC_API_KEY environment variable is not set"
        logger.error(error_msg)
        raise ValueError(error_msg)

    headers = {
        "x-api-key": settings.anthropic_api_key,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }

    payload = {
        "model": "claude-opus-4-20250514",
        "max_tokens": settings.max_allowed_tokens,
        "temperature": 0.7,
        "system": "You are a helpful assistant that summarizes Roman Catholic church newsletters into warm, concise email messages",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()

        data = response.json()

        # Check for API-level errors
        if "error" in data:
            error_msg = f"Claude API error: {data['error']}"
            logger.error(error_msg)
            raise Exception(error_msg)

        return data["content"][0]["text"].strip()

    except requests.exceptions.RequestException as e:
        error_msg = f"Request to Claude API failed: {str(e)}"
        logger.error(error_msg)
        # Log the response content for debugging
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")

        raise Exception(error_msg)
    except KeyError as e:
        error_msg = f"Unexpected response format from Claude API: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


def choose_llm_and_summarize(text: str) -> Dict[str, Any]:
    """
    Summarizes a given text into a 2-paragraph email message using an appropriate language model
    based on token count. Returns the summary, model used, token count, and estimated cost.

    Args:
        text: The text content to be summarized.

    Returns:
        Dict[str, Any]: A dictionary containing the summary, model used, token count, and cost estimate in USD.

    Raises:
        ValueError: If the token count exceeds the maximum allowed limit.
    """
    prompt = f"Summarize this church newsletter into a 2-paragraph email message: {text}"
    token_estimate = count_tokens(prompt)

    logger.info(f"Estimated tokens: {token_estimate}")

    if token_estimate > settings.max_allowed_tokens:
        error_msg = f"Document too long ({token_estimate} tokens). Limit is {settings.max_allowed_tokens}."
        logger.error(error_msg)
        raise ValueError(error_msg)

    if token_estimate > 5000:
        model = "claude"
        logger.info(f"Using Claude model for summarization (tokens: {token_estimate})")
        summary = summarize_with_claude(prompt)
        cost_estimate = (token_estimate / 1000) * 0.015  # Claude Opus @ ~$15/M tokens
    else:
        model = "mistral"
        logger.info(f"Using Mistral model for summarization (tokens: {token_estimate})")
        summary = summarize_with_mistral(prompt)
        cost_estimate = 0  # Free via Ollama

    logger.debug(f"Summary generated successfully using {model} model")
    
    return {
        "summary": summary,
        "model": model,
        "tokens": token_estimate,
        "cost_usd_estimate": round(cost_estimate, 4)
    }