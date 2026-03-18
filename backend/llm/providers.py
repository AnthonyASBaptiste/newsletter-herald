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


def summarize_with_model(prompt: str, timeout: int = 300) -> Dict[str, str]:
    """
    Summarizes a given text input using a local Ollama model.
    Returns: Dict containing 'title' and 'summary'.
    """
    logger.debug("Sending request to model API")

    system_instruction = (
        "You are a helpful assistant that summarizes Roman Catholic church newsletters into warm, concise 2-paragraph email messages for parishioners. "
        "Return your response in JSON format with two keys: 'title' (a concise subject line like '4th Sunday of Lent – Living as Children of the Light') and 'summary' (the 2-paragraph email body)."
    )
    full_prompt = f"{system_instruction}\n\nUser Request: {prompt}"

    try:
        response = requests.post(
            f"{settings.ollama_base_url}/api/generate",
            timeout=timeout,
            json={
                "model": settings.ollama_model,
                "prompt": full_prompt,
                "stream": False,
                "format": "json"
            }
        )

        if response.status_code != 200:
            error_msg = f"Model error: {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

        data = response.json()
        import json
        resp_data = json.loads(data["response"])
        return {
            "title": resp_data.get("title", "Church Newsletter"),
            "summary": resp_data.get("summary", "")
        }

    except Exception as e:
        error_msg = f"Request to model API failed: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


def summarize_with_claude(prompt: str, timeout: int = 300) -> Dict[str, str]:
    """
    Summarizes using Claude. Returns: Dict containing 'title' and 'summary'.
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
        "system": "Summarize the newsletter. Return ONLY a JSON object with 'title' (a warm subject line) and 'summary' (2-paragraph email body).",
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
        import json
        resp_data = json.loads(data["content"][0]["text"])
        return {
            "title": resp_data.get("title", "Church Newsletter"),
            "summary": resp_data.get("summary", "")
        }

    except Exception as e:
        error_msg = f"Claude API failed: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


def summarize_with_groq(prompt: str, timeout: int = 60) -> Dict[str, str]:
    """
    Summarizes using Groq. Returns: Dict containing 'title' and 'summary'.
    """
    if not settings.groq_api_key:
        error_msg = "GROQ_API_KEY environment variable is not set"
        logger.error(error_msg)
        raise ValueError(error_msg)

    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": settings.groq_model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that summarizes Roman Catholic church newsletters. Return your response as a JSON object with two keys: 'title' (a warm, descriptive subject line) and 'summary' (a warm, 2-paragraph email message)."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.7,
        "max_tokens": 1024
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()

        data = response.json()
        import json
        resp_data = json.loads(data["choices"][0]["message"]["content"])
        return {
            "title": resp_data.get("title", "Church Newsletter"),
            "summary": resp_data.get("summary", "")
        }

    except Exception as e:
        error_msg = f"Groq API failed: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


def choose_llm_and_summarize(text: str) -> Dict[str, Any]:
    """
    Summarizes a given text into a title and a 2-paragraph email message.
    Respects the configured LLM strategy.
    """
    prompt = f"Summarize this church newsletter: {text}"
    token_estimate = count_tokens(prompt)

    logger.info(f"Estimated tokens: {token_estimate}")

    if token_estimate > settings.max_allowed_tokens:
        error_msg = f"Document too long ({token_estimate} tokens). Limit is {settings.max_allowed_tokens}."
        logger.error(error_msg)
        raise ValueError(error_msg)

    strategy = settings.llm_strategy.lower()

    # Explicit strategy overrides
    if strategy == "groq" and settings.groq_api_key:
        model = f"{settings.groq_model} (Groq)"
        logger.info(f"Forcing Groq ({settings.groq_model})")
        res = summarize_with_groq(prompt)
        cost_estimate = 0
    elif strategy == "local":
        model = f"{settings.ollama_model} (Ollama)"
        logger.info(f"Forcing Local Model ({settings.ollama_model})")
        res = summarize_with_model(prompt)
        cost_estimate = 0
    elif strategy == "remote":
        model = "claude (Anthropic)"
        logger.info("Forcing Remote Model (Claude)")
        res = summarize_with_claude(prompt)
        cost_estimate = (token_estimate / 1000) * 0.015
    else:
        # Auto strategy or default fallback
        if token_estimate > 5000:
            model = "claude (Anthropic)"
            logger.info(f"Token count {token_estimate} > 5000, using Claude")
            res = summarize_with_claude(prompt)
            cost_estimate = (token_estimate / 1000) * 0.015
        elif settings.groq_api_key and strategy == "auto":
            model = f"{settings.groq_model} (Groq)"
            logger.info(f"Auto strategy: using Groq ({settings.groq_model})")
            res = summarize_with_groq(prompt)
            cost_estimate = 0
        else:
            model = f"{settings.ollama_model} (Ollama)"
            logger.info(f"Auto strategy: using Local Model ({settings.ollama_model})")
            res = summarize_with_model(prompt)
            cost_estimate = 0

    return {
        "title": res["title"],
        "summary": res["summary"],
        "model": model,
        "tokens": token_estimate,
        "cost_usd_estimate": round(cost_estimate, 4)
    }