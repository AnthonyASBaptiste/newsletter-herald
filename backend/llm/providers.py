import requests
import os
from dotenv import load_dotenv

from helpers.constants import MAX_ALLOWED_TOKENS
from helpers.text_utils import count_tokens

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is not set")


def summarize_with_mistral(prompt: str, timeout: int = 30) -> str:
    """
    Summarizes a given text input using the Mistral model by making a POST request to
    a local endpoint. The method expects a text prompt, sends it to the Mistral API for
    processing, and returns the generated summary.

    :param timeout:
    :param prompt: The input text to be summarized.
    :type prompt: str
    :return: The generated summary based on the given prompt.
    :rtype: str
    :raises Exception: If the response status code from the Mistral API is not 200, an
                       exception is raised with the error details from the API.
    """
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
        raise Exception(f"Mistral error: {response.text}")

    data = response.json()
    return data["response"].strip()


def summarize_with_claude(prompt: str, timeout: int = 30) -> str:
    """
    Summarizes Roman Catholic Church newsletters into concise and warm email messages
    using the Claude model via the OpenRouter API. This function leverages the
    Anthropic Claude-3 Opus model to process user-provided newsletter texts and produce
    summarized output with adjusted creativity and token limits.

    :param prompt: The input text to be summarized, typically a Roman Catholic
        Church newsletter in plain text format.
    :type prompt: str
    :param timeout: The maximum time, in seconds, to await a response from the
        OpenRouter API. If not specified, defaults to 30 seconds.
    :type timeout: int
    :return: A summarized version of the input text, formatted as a concise email
        message.
    :rtype: str
    :raises ValueError: If the required `OPENROUTER_API_KEY` environment variable
        is not set.
    :raises Exception: For API-level errors, unexpected response formats, or any
        HTTP request-related failures.
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000/upload-document",
        "X-Title": "Church Newsletter Summarizer"
    }

    payload = {
        "model": "anthropic/claude-3-opus",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes Roman Catholic church newsletters into warm, concise email messages"
            },
            {"role": "user", "content": prompt}
        ],
        "max_tokens": MAX_ALLOWED_TOKENS,
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()

        data = response.json()

        # Check for API-level errors
        if "error" in data:
            raise Exception(f"API error: {data['error']}")

        return data["choices"][0]["message"]["content"].strip()

    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {e}")
    except KeyError as e:
        raise Exception(f"Unexpected response format: {e}")


def choose_llm_and_summarize(text: str) -> dict:
    """
    Summarizes a given text into a 2-paragraph email message using an appropriate language model
    based on token count. Returns the summary, model used, token count, and estimated cost.

    :param text: The text content to be summarized.
    :type text: str

    :return: A dictionary containing the summary, model used, token count, and cost estimate in USD.
    :rtype: dict

    :raises ValueError: If the token count exceeds the maximum allowed limit.
    """
    prompt = f"Summarize this church newsletter into a 2-paragraph email message: {text}"
    token_estimate = count_tokens(prompt)

    print(f"Estimated tokens: {token_estimate}")

    if token_estimate > MAX_ALLOWED_TOKENS:
        raise ValueError(f"Document too long ({token_estimate} tokens). Limit is {MAX_ALLOWED_TOKENS}.")

    if token_estimate > 5000:
        model = "claude"
        summary = summarize_with_claude(prompt)
        cost_estimate = (token_estimate / 1000) * 0.015  # Claude Opus @ ~$15/M tokens
    else:
        model = "mistral"
        summary = summarize_with_mistral(prompt)
        cost_estimate = 0  # Free via Ollama

    return {
        "summary": summary,
        "model": model,
        "tokens": token_estimate,
        "cost_usd_estimate": round(cost_estimate, 4)
    }