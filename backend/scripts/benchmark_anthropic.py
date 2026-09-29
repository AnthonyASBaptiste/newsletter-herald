import asyncio
import time
import unittest.mock as mock
import httpx
import requests

# Mock response data for Anthropic API
MOCK_RESPONSE_JSON = {
    "content": [
        {
            "text": '{"title": "Test Title", "summary": "Test summary text.", "schedule_date": "2025-03-30", "liturgical_season": "Lent", "calendar_year": "2025", "liturgical_year": "Year C"}'
        }
    ]
}

def sync_requests_call(delay=0.1):
    # Simulates what requests.post did inside summarize_with_claude
    time.sleep(delay)
    class MockResp:
        status_code = 200
        def raise_for_status(self): pass
        def json(self): return MOCK_RESPONSE_JSON
    return MockResp()

async def async_httpx_call(delay=0.1):
    # Simulates what httpx.AsyncClient().post does
    await asyncio.sleep(delay)
    class MockResp:
        status_code = 200
        def raise_for_status(self): pass
        def json(self): return MOCK_RESPONSE_JSON
    return MockResp()

async def ping_loop(stop_event, latencies):
    while not stop_event.is_set():
        t0 = time.perf_counter()
        await asyncio.sleep(0.005)
        latencies.append((time.perf_counter() - t0 - 0.005) * 1000)

async def test_concurrent_requests(num_concurrent=5, call_delay=0.1):
    # 1. Sync Requests approach (even if run in threadpool or directly)
    latencies_sync = []
    stop_event = asyncio.Event()
    ping_task = asyncio.create_task(ping_loop(stop_event, latencies_sync))
    await asyncio.sleep(0.01)

    start = time.perf_counter()
    # If 5 requests are made synchronously or serially on event loop:
    for _ in range(num_concurrent):
        sync_requests_call(call_delay)
    sync_duration = time.perf_counter() - start

    stop_event.set()
    await ping_task
    max_lat_sync = max(latencies_sync) if latencies_sync else 0

    # 2. Async httpx approach
    latencies_async = []
    stop_event = asyncio.Event()
    ping_task = asyncio.create_task(ping_loop(stop_event, latencies_async))
    await asyncio.sleep(0.01)

    start = time.perf_counter()
    tasks = [async_httpx_call(call_delay) for _ in range(num_concurrent)]
    await asyncio.gather(*tasks)
    async_duration = time.perf_counter() - start

    stop_event.set()
    await ping_task
    max_lat_async = max(latencies_async) if latencies_async else 0

    print("======================================================================")
    print("⚡ ANTHROPIC HTTP CLIENT BENCHMARK (Sync requests vs Async httpx)")
    print("======================================================================")
    print(f"Concurrent requests: {num_concurrent} | Network latency per req: {call_delay*1000:.0f}ms")
    print(f"Sync requests total time:  {sync_duration:.4f}s | Max event loop delay: {max_lat_sync:.2f}ms")
    print(f"Async httpx total time:    {async_duration:.4f}s | Max event loop delay: {max_lat_async:.2f}ms")
    if async_duration > 0:
        print(f"Speedup for concurrent calls: {sync_duration / async_duration:.2f}x faster")
    print("======================================================================")

if __name__ == "__main__":
    asyncio.run(test_concurrent_requests())
