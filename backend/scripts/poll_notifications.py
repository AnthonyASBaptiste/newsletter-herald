import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def poll_notifications(
    client: httpx.AsyncClient | None = None,
    poll_interval: float | None = None,
    max_polls: int | None = 1,
) -> list[dict]:
    """
    Asynchronously polls the backend endpoint for pending notifications using httpx.AsyncClient.

    :param client: Optional external httpx.AsyncClient instance for connection reuse.
    :param poll_interval: Optional sleep duration in seconds between poll iterations.
    :param max_polls: Maximum number of polling iterations. Pass None for continuous polling.
    :return: List of retrieved notification dictionaries.
    """
    backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
    api_key = os.getenv("API_KEY")

    if not api_key:
        sys.stderr.write("Error: API_KEY environment variable is not set.\n")
        sys.exit(1)

    url = f"{backend_url.rstrip('/')}/notifications/poll"
    headers = {
        "X-API-Key": api_key,
        "Authorization": f"Bearer {api_key}",  # Provide both formats for compatibility
    }

    async def _fetch_and_process(httpx_client: httpx.AsyncClient) -> list[dict]:
        try:
            response = await httpx_client.get(url, headers=headers, timeout=30.0)

            if response.status_code == 401:
                sys.stderr.write("Error: Unauthorized. Check your API_KEY configuration.\n")
                sys.exit(1)

            response.raise_for_status()
            data = response.json()

            notifications = data.get("notifications", [])
            if not notifications:
                return []

            for event in notifications:
                msg = event.get("formatted_message", "")
                if msg:
                    sys.stdout.buffer.write((msg + "\n---\n").encode("utf-8"))

            return notifications

        except SystemExit:
            raise
        except Exception as e:
            sys.stderr.write(f"Error polling notifications from {url}: {e}\n")
            return []

    all_notifications = []
    polls_count = 0

    if client is not None:
        while max_polls is None or polls_count < max_polls:
            res = await _fetch_and_process(client)
            all_notifications.extend(res)
            polls_count += 1
            if poll_interval is not None and (max_polls is None or polls_count < max_polls):
                await asyncio.sleep(poll_interval)
    else:
        async with httpx.AsyncClient(timeout=30.0) as default_client:
            while max_polls is None or polls_count < max_polls:
                res = await _fetch_and_process(default_client)
                all_notifications.extend(res)
                polls_count += 1
                if poll_interval is not None and (max_polls is None or polls_count < max_polls):
                    await asyncio.sleep(poll_interval)

    return all_notifications


if __name__ == "__main__":
    asyncio.run(poll_notifications())
