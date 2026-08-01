import asyncio
import time
import os
import sys
from starlette.concurrency import run_in_threadpool

# Add backend directory to path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import sync_extract_text, extract_text_from_file

PDF_PATH = "../test_newsletters/test.pdf"

async def simulate_other_event_loop_activity():
    """
    Simulates lightweight event-loop activity (like handling pings, database queries, or CORS preflights)
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
            latency = (time.perf_counter() - t0 - 0.01) * 1000 # in ms
            ping_latencies.append(latency)

    ping_task = asyncio.create_task(ping_loop())
    return stop_event, ping_task, ping_latencies

async def run_sync_extraction_blocked(pdf_bytes: bytes, num_runs: int = 5):
    """
    Simulates the blocking scenario where synchronous file writing and OCR
    parsing run directly on the async event loop thread.
    Since they block the loop, even when we gather them, they will execute sequentially
    because the event loop thread is completely held hostage by each CPU/IO task.
    """
    def block_loop(b):
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(b)
        try:
            return extract_text_from_file(temp_file_path, file_type="pdf")
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    async def worker():
        return block_loop(pdf_bytes)

    stop_event, ping_task, latencies = await simulate_other_event_loop_activity()

    start_time = time.perf_counter()
    tasks = [worker() for _ in range(num_runs)]
    results = await asyncio.gather(*tasks)
    end_time = time.perf_counter()

    stop_event.set()
    await ping_task

    return end_time - start_time, len(results), max(latencies or [0]), sum(latencies or [0])/len(latencies or [1])

async def run_async_extraction_threadpool(pdf_bytes: bytes, num_runs: int = 5):
    """
    Runs the extraction in the threadpool. Since these run on separate worker threads,
    they can run concurrently, and do not block the event loop thread!
    """
    async def worker():
        return await run_in_threadpool(sync_extract_text, pdf_bytes, "application/pdf")

    stop_event, ping_task, latencies = await simulate_other_event_loop_activity()

    start_time = time.perf_counter()
    tasks = [worker() for _ in range(num_runs)]
    results = await asyncio.gather(*tasks)
    end_time = time.perf_counter()

    stop_event.set()
    await ping_task

    return end_time - start_time, len(results), max(latencies or [0]), sum(latencies or [0])/len(latencies or [1])

async def main():
    if not os.path.exists(PDF_PATH):
        print(f"Error: PDF file not found at {PDF_PATH}")
        sys.exit(1)

    print(f"Reading PDF from {PDF_PATH}...")
    with open(PDF_PATH, "rb") as f:
        pdf_bytes = f.read()

    print(f"Loaded {len(pdf_bytes) / 1024 / 1024:.2f} MB PDF file.\n")
    print("======================================================================")
    print("⚡ Running Benchmarks: Concurrent Document Parsing (5 concurrent tasks)")
    print("======================================================================\n")

    # Warmup
    print("Warming up...")
    await run_async_extraction_threadpool(pdf_bytes, num_runs=1)
    print("Warmup done.\n")

    # 1. Blocked Event Loop (Old Sync approach)
    print("1. Running old synchronous extraction (event loop blocked)...")
    sync_duration, sync_count, sync_max_lat, sync_avg_lat = await run_sync_extraction_blocked(pdf_bytes, num_runs=5)
    print(f"   Done. Took {sync_duration:.4f} seconds for {sync_count} runs.")
    print(f"   Max event loop delay: {sync_max_lat:.2f} ms | Avg delay: {sync_avg_lat:.2f} ms\n")

    # 2. Async Threadpool (New Optimized approach)
    print("2. Running optimized async threadpool extraction (event loop free)...")
    async_duration, async_count, async_max_lat, async_avg_lat = await run_async_extraction_threadpool(pdf_bytes, num_runs=5)
    print(f"   Done. Took {async_duration:.4f} seconds for {async_count} runs.")
    print(f"   Max event loop delay: {async_max_lat:.2f} ms | Avg delay: {async_avg_lat:.2f} ms\n")

    # Calculate Speedup and Responsiveness boost
    latency_reduction = (sync_max_lat - async_max_lat)
    latency_reduction_percent = (sync_max_lat / async_max_lat) if async_max_lat > 0 else 0

    print("======================================================================")
    print("📊 BENCHMARK RESULTS SUMMARY")
    print("======================================================================")
    print(f"{'Metric':<38} | {'Synchronous (Blocked)':<22} | {'Threadpool (Optimized)':<22}")
    print("-" * 88)
    print(f"{'Total execution time (5 runs)':<38} | {sync_duration:19.4f}s | {async_duration:19.4f}s")
    print(f"{'Average extraction time / doc':<38} | {sync_duration / 5:19.4f}s | {async_duration / 5:19.4f}s")
    print(f"{'Worst-case event loop latency':<38} | {sync_max_lat:17.2f} ms | {async_max_lat:17.2f} ms")
    print(f"{'Average event loop latency':<38} | {sync_avg_lat:17.2f} ms | {async_avg_lat:17.2f} ms")
    print("-" * 88)
    print(f"{'Worst-case Event Loop Speedup':<38} | {'0.0% (Baseline)':<22} | {latency_reduction_percent:20.1f}x faster")
    print("======================================================================")
    print(f"💡 Explanation: Running CPU-bound OCR and I/O inside threadpool")
    print(f"   prevents event-loop starvation, allowing concurrent API requests (e.g.,")
    print(f"   health checks, dashboard pings) to respond {latency_reduction_percent:.1f}x faster")
    print(f"   under load, with maximum response lag reduced by {latency_reduction:.1f} ms!")
    print("======================================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
