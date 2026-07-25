import requests
import logging
from typing import Dict, Any, Optional

from config import get_settings
from helpers.text_utils import count_tokens

# Get settings from centralized configuration
settings = get_settings()

# Create a logger for this module
logger = logging.getLogger(__name__)

# Core Prompt Instruction for Sanitization
# This is shared across all providers to ensure consistent PII/PHI filtering.
SANITIZATION_INSTRUCTION = (
    "CRITICAL: YOUR SUMMARY MUST NOT INCLUDE ANY PERSONALLY IDENTIFIABLE INFORMATION (PII) OR PROTECTED HEALTH INFORMATION (PHI). "
    "Do NOT include names of parishioners, specific home addresses, personal phone numbers, or personal email addresses. "
    "Do NOT include details about medical conditions, hospitalizations, or specific health requests for individuals. "
    "If you mention upcoming events, refer to them by the event name or group, not by the names of the individuals hosting them (unless they are official church staff like the Priest). "
    "The goal is a public-facing summary that protects the privacy of all individuals mentioned in the original newsletter."
)

GROQ_SYSTEM_INSTRUCTION = (
    "You are a helpful assistant that summarizes Roman Catholic church newsletters. Return your response as a JSON object with the following keys:\n"
    "1. 'title': A warm, descriptive subject line.\n"
    "2. 'summary': A warm, 2-paragraph email message.\n"
    "3. 'schedule_date': Newsletter date in YYYY-MM-DD format.\n"
    "4. 'liturgical_season': Liturgical season (e.g., 'Ordinary Time', 'Lent', 'Advent', 'Christmas', 'Easter').\n"
    "5. 'calendar_year': Calendar year (e.g., '2025').\n"
    "6. 'liturgical_year': Liturgical year (e.g., 'Year A', 'Year B', 'Year C')."
    f"\n\n{SANITIZATION_INSTRUCTION}"
)


def summarize_with_model(prompt: str, timeout: int = 300) -> Dict[str, str]:
    """
    Summarizes a given text input using a local Ollama model.
    Returns: Dict containing 'title' and 'summary'.
    """
    logger.debug("Sending request to model API")

    system_instruction = (
        "You are a helpful assistant that summarizes Roman Catholic church newsletters into warm, concise 2-paragraph email messages for parishioners. "
        "Return your response in JSON format with the following keys:\n"
        "1. 'title': A concise subject line (e.g., '4th Sunday of Lent – Living as Children of the Light')\n"
        "2. 'summary': The 2-paragraph email body.\n"
        "3. 'schedule_date': The date the newsletter is for, in YYYY-MM-DD format.\n"
        "4. 'liturgical_season': The liturgical season (e.g., 'Ordinary Time', 'Lent', 'Advent', 'Christmas', 'Easter').\n"
        "5. 'calendar_year': The calendar year (e.g., '2025').\n"
        "6. 'liturgical_year': The liturgical year (e.g., 'Year A', 'Year B', 'Year C')."
        f"\n{SANITIZATION_INSTRUCTION}"
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
            "summary": resp_data.get("summary", ""),
            "schedule_date": resp_data.get("schedule_date"),
            "liturgical_season": resp_data.get("liturgical_season"),
            "calendar_year": resp_data.get("calendar_year"),
            "liturgical_year": resp_data.get("liturgical_year")
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
        "system": (
            "Summarize the newsletter. Return ONLY a JSON object with the following keys:\n"
            "1. 'title': A warm subject line.\n"
            "2. 'summary': 2-paragraph email body.\n"
            "3. 'schedule_date': Newsletter date in YYYY-MM-DD format.\n"
            "4. 'liturgical_season': Liturgical season (e.g., 'Ordinary Time', 'Lent', 'Advent', 'Christmas', 'Easter').\n"
            "5. 'calendar_year': Calendar year (e.g., '2025').\n"
            "6. 'liturgical_year': Liturgical year (e.g., 'Year A', 'Year B', 'Year C')."
            f"\n\n{SANITIZATION_INSTRUCTION}"
        ),
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
            "summary": resp_data.get("summary", ""),
            "schedule_date": resp_data.get("schedule_date"),
            "liturgical_season": resp_data.get("liturgical_season"),
            "calendar_year": resp_data.get("calendar_year"),
            "liturgical_year": resp_data.get("liturgical_year")
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
            {
                "role": "system", 
                "content": GROQ_SYSTEM_INSTRUCTION
            },
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.7,
        "max_tokens": 1024
    }

    import time
    max_retries = 5
    retry_delay = 70
    last_exception = None

    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=timeout
            )
            if response.status_code == 429:
                logger.warning(f"Groq API returned 429 (Too Many Requests). Retrying in {retry_delay}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(retry_delay)
                # Keep delay high to clear the 60-second window
                continue

            response.raise_for_status()

            data = response.json()
            import json
            resp_data = json.loads(data["choices"][0]["message"]["content"])
            return {
                "title": resp_data.get("title", "Church Newsletter"),
                "summary": resp_data.get("summary", ""),
                "schedule_date": resp_data.get("schedule_date"),
                "liturgical_season": resp_data.get("liturgical_season"),
                "calendar_year": resp_data.get("calendar_year"),
                "liturgical_year": resp_data.get("liturgical_year")
            }
        except Exception as e:
            last_exception = e
            logger.warning(f"Groq API call attempt {attempt+1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)

    error_msg = f"Groq API failed after {max_retries} attempts: {last_exception}"
    logger.error(error_msg)
    raise Exception(error_msg)



def choose_llm_and_summarize(text: str) -> Dict[str, Any]:
    """
    Summarizes a given text into a title and a 2-paragraph email message.
    Respects the configured LLM strategy.
    """
    # Truncate text if it's extremely long to avoid 413 Payload Too Large and stay within context limits
    max_chars = 18000
    if len(text) > max_chars:
        logger.info(f"Truncating text from {len(text)} to {max_chars} characters to fit context limits.")
        text = text[:max_chars] + "\n...[TRUNCATED FOR LENGTH]..."

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

    # Defensive sanitization for local LLM nested dictionary structures
    title_val = res.get("title", "Church Newsletter")
    if isinstance(title_val, dict):
        title_val = title_val.get("title") or title_val.get("text") or str(title_val)
    elif not isinstance(title_val, str):
        title_val = str(title_val)

    summary_val = res.get("summary", "")
    if isinstance(summary_val, dict):
        summary_val = summary_val.get("summary") or summary_val.get("text") or str(summary_val)
    elif not isinstance(summary_val, str):
        summary_val = str(summary_val)

    return {
        "title": title_val,
        "summary": summary_val,
        "schedule_date": res.get("schedule_date"),
        "liturgical_season": res.get("liturgical_season"),
        "calendar_year": res.get("calendar_year"),
        "liturgical_year": res.get("liturgical_year"),
        "model": model,
        "tokens": token_estimate,
        "cost_usd_estimate": round(cost_estimate, 4)
    }
