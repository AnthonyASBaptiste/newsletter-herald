import os
import sys
import time
import asyncio
import requests
import httpx
from uvicorn import Config, Server
from fastapi import FastAPI, Header, HTTPException

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup dummy app for benchmark
benchmark_app = FastAPI()

@benchmark_app.get("/notifications/poll")
async def poll_endpoint(x_api_key: str = Header(None, alias="X-API-Key")):
    if x_api_key != "benchmark_key":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"notifications": [{"formatted_message": "Benchmark notification event"}]}

class MockServer(Server):
    def install_signal_handlers(self):
        pass

async def run_server(server):
    await server.serve()

def _do_sync_get(url: str, headers: dict) -> int:
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        return len(data.get("notifications", []))
    return 0

async def sync_poll_baseline(url: str, headers: dict, iterations: int):
    """Baseline polling using synchronous requests library (offloaded to threadpool)."""
    start_time = time.perf_counter()
    count = 0
    for _ in range(iterations):
        res = await asyncio.to_thread(_do_sync_get, url, headers)
        count += res
    elapsed = time.perf_counter() - start_time
    return elapsed, count

async def async_poll_optimized(url: str, headers: dict, iterations: int):
    """Optimized polling using persistent httpx AsyncClient."""
    start_time = time.perf_counter()
    count = 0
    async with httpx.AsyncClient(timeout=10.0) as client:
        for _ in range(iterations):
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                count += len(data.get("notifications", []))
    elapsed = time.perf_counter() - start_time
    return elapsed, count

async def main():
    port = 8899
    config = Config(app=benchmark_app, host="127.0.0.1", port=port, log_level="error")
    server = MockServer(config=config)
    server_task = asyncio.create_task(run_server(server))

    # Give server time to bind
    await asyncio.sleep(0.5)

    url = f"http://127.0.0.1:{port}/notifications/poll"
    headers = {"X-API-Key": "benchmark_key", "Authorization": "Bearer benchmark_key"}
    iterations = 50

    print("=" * 60)
    print("⚡ POLL NOTIFICATIONS BENCHMARK SUMMARY ⚡")
    print(f"Running {iterations} iterations against local mock server...")
    print("=" * 60)

    # Benchmark sync baseline
    sync_time, sync_count = await sync_poll_baseline(url, headers, iterations)
    sync_rps = iterations / sync_time
    print(f"1. Baseline (Sync requests.get via thread pool):")
    print(f"   - Total Time: {sync_time:.4f}s")
    print(f"   - Average Latency: {(sync_time/iterations)*1000:.2f}ms/req")
    print(f"   - Throughput: {sync_rps:.2f} req/s")

    # Benchmark async optimized
    async_time, async_count = await async_poll_optimized(url, headers, iterations)
    async_rps = iterations / async_time
    print(f"\n2. Optimized (Async httpx.AsyncClient with persistent session):")
    print(f"   - Total Time: {async_time:.4f}s")
    print(f"   - Average Latency: {(async_time/iterations)*1000:.2f}ms/req")
    print(f"   - Throughput: {async_rps:.2f} req/s")

    speedup = sync_time / async_time
    pct_reduction = ((sync_time - async_time) / sync_time) * 100

    print("-" * 60)
    print(f"🚀 Speedup Factor: {speedup:.2f}x faster")
    print(f"⏱️ Latency Reduction: {pct_reduction:.2f}%")
    print("=" * 60)

    server.should_exit = True
    await server_task

if __name__ == "__main__":
    asyncio.run(main())
