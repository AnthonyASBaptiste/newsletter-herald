import asyncio
import time
import os
import sys
from starlette.concurrency import run_in_threadpool

# Add backend directory to path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# A simulated mock of choose_llm_and_summarize that blocks the thread for 1 second.
# This represents a slow API request or a retry-delay sleep (e.g., time.sleep(retry_delay))
def mock_choose_llm_and_summarize(text: str) -> dict:
    time.sleep(1.0)  # Simulates blocking I/O or sleep
    return {
        "title": "Simulated Newsletter Title",
        "summary": "This is a simulated summary.",
        "model": "mock-model",
        "tokens": 100,
        "cost_usd_estimate": 0.0
    }

async def simulate_other_event_loop_activity():
    """
    Simulates lightweight event-loop activity (like handling pings or health checks)
    by running a periodic async ping every 10ms. We measure the maximum latency of these pings.
    If the event loop is blocked, the ping latency will spike to the duration of the block!
    If the event loop is free, the ping latency will remain extremely low (< 15ms).
    """
    ping_latencies = []
    stop_event = asyncio.Event()

    async def ping_loop():
        while not stop_event.is_set():
            t0 = time.perf_counter()
            await asyncio.sleep(0.01)
            latency = (time.perf_counter() - t0 - 0.01) * 1000  # in ms
            ping_latencies.append(latency)

    ping_task = asyncio.create_task(ping_loop())
    return stop_event, ping_task, ping_latencies

async def run_sync_mock(text: str):
    """
    Simulates the blocking scenario where choose_llm_and_summarize
    runs directly on the async event loop thread.
    """
    stop_event, ping_task, latencies = await simulate_other_event_loop_activity()

    # Give the ping loop a moment to start
    await asyncio.sleep(0.02)

    start_time = time.perf_counter()
    # Synchronous call directly blocking the event loop thread
    result = mock_choose_llm_and_summarize(text)
    end_time = time.perf_counter()

    # Crucial: let the event loop run once so the blocked ping can resume and record its delay!
    await asyncio.sleep(0.02)

    stop_event.set()
    try:
        await ping_task
    except Exception:
        pass

    return end_time - start_time, result, max(latencies or [0]), sum(latencies or [0])/len(latencies or [1])

async def run_async_threadpool_mock(text: str):
    """
    Runs the choose_llm_and_summarize mock in a threadpool.
    """
    stop_event, ping_task, latencies = await simulate_other_event_loop_activity()

    # Give the ping loop a moment to start
    await asyncio.sleep(0.02)

    start_time = time.perf_counter()
    # Offloaded to threadpool, allowing the event loop to continue pings
    result = await run_in_threadpool(mock_choose_llm_and_summarize, text)
    end_time = time.perf_counter()

    # Let the event loop run once
    await asyncio.sleep(0.02)

    stop_event.set()
    try:
        await ping_task
    except Exception:
        pass

    return end_time - start_time, result, max(latencies or [0]), sum(latencies or [0])/len(latencies or [1])

async def main():
    text = "Some church newsletter text..."
    print("======================================================================")
    print("⚡ Running LLM Summarization Event Loop Block Benchmarks")
    print("======================================================================\n")

    # 1. Blocked Event Loop (Old Sync approach)
    print("1. Running old synchronous choose_llm_and_summarize (event loop blocked)...")
    sync_duration, _, sync_max_lat, sync_avg_lat = await run_sync_mock(text)
    print(f"   Done. Took {sync_duration:.4f} seconds.")
    print(f"   Max event loop delay: {sync_max_lat:.2f} ms | Avg delay: {sync_avg_lat:.2f} ms\n")

    # 2. Async Threadpool (New Optimized approach)
    print("2. Running optimized async threadpool choose_llm_and_summarize (event loop free)...")
    async_duration, _, async_max_lat, async_avg_lat = await run_async_threadpool_mock(text)
    print(f"   Done. Took {async_duration:.4f} seconds.")
    print(f"   Max event loop delay: {async_max_lat:.2f} ms | Avg delay: {async_avg_lat:.2f} ms\n")

    # Calculate Speedup and Responsiveness boost
    latency_reduction = (sync_max_lat - async_max_lat)
    latency_reduction_percent = (sync_max_lat / async_max_lat) if async_max_lat > 0 else 0

    print("======================================================================")
    print("📊 BENCHMARK RESULTS SUMMARY")
    print("======================================================================")
    print(f"{'Metric':<38} | {'Synchronous (Blocked)':<22} | {'Threadpool (Optimized)':<22}")
    print("-" * 88)
    print(f"{'Total execution time':<38} | {sync_duration:19.4f}s | {async_duration:19.4f}s")
    print(f"{'Worst-case event loop latency':<38} | {sync_max_lat:17.2f} ms | {async_max_lat:17.2f} ms")
    print(f"{'Average event loop latency':<38} | {sync_avg_lat:17.2f} ms | {async_avg_lat:17.2f} ms")
    print("-" * 88)
    print(f"{'Worst-case Event Loop Speedup':<38} | {'0.0% (Baseline)':<22} | {latency_reduction_percent:20.1f}x faster")
    print("======================================================================")
    print(f"💡 Explanation: Running blocking choose_llm_and_summarize inside a threadpool")
    print(f"   prevents event-loop starvation, allowing concurrent API requests (e.g.,")
    print(f"   health checks, dashboard pings) to respond {latency_reduction_percent:.1f}x faster")
    print(f"   under load, with maximum response lag reduced by {latency_reduction:.1f} ms!")
    print("======================================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
