import asyncio
import time
from unittest.mock import MagicMock, AsyncMock

# Simulate the original delivery loop logic
async def run_original_logic(subscribers, send_email_fn, db_execute_fn):
    sent_count = 0
    failed_count = 0

    for sub in subscribers:
        recipient = sub['email']
        success = send_email_fn(
            to_email=recipient,
            subject="Test Newsletter",
            html_content="<p>Test</p>"
        )

        status = "sent" if success else "failed"
        err_msg = None if success else "SMTP delivery failure"

        await db_execute_fn(recipient, status, err_msg)

        if success:
            sent_count += 1
        else:
            failed_count += 1

    return sent_count, failed_count

# Simulate the optimized logic (using asyncio.gather, to_thread, Semaphore and execute_many)
async def run_optimized_logic(subscribers, send_email_fn, db_execute_many_fn, semaphore_limit=10):
    semaphore = asyncio.Semaphore(semaphore_limit)

    async def deliver_to_subscriber(sub):
        async with semaphore:
            recipient = sub['email']
            # Run the synchronous send_email in a thread pool
            success = await asyncio.to_thread(
                send_email_fn,
                to_email=recipient,
                subject="Test Newsletter",
                html_content="<p>Test</p>"
            )
            return recipient, success

    # Trigger deliveries concurrently
    tasks = [deliver_to_subscriber(sub) for sub in subscribers]
    results = await asyncio.gather(*tasks)

    # Collect values for bulk insert
    log_values = []
    sent_count = 0
    failed_count = 0

    for recipient, success in results:
        status = "sent" if success else "failed"
        err_msg = None if success else "SMTP delivery failure"
        log_values.append({
            "recipient": recipient,
            "status": status,
            "error_message": err_msg
        })
        if success:
            sent_count += 1
        else:
            failed_count += 1

    # Bulk insert
    if log_values:
        await db_execute_many_fn(log_values)

    return sent_count, failed_count

# Mock email send with 0.05 seconds of artificial latency
def mock_send_email(to_email, subject, html_content):
    time.sleep(0.05)
    return True

# Mock DB operations
async def mock_db_execute(recipient, status, error_message):
    await asyncio.sleep(0.005) # Simulate database query latency

async def mock_db_execute_many(values):
    await asyncio.sleep(0.01) # Bulk insert takes a tiny bit of time once

async def main():
    print("=== STARTING BENCHMARK ===")
    num_subscribers = 50
    subscribers = [{"email": f"user{i}@example.com"} for i in range(num_subscribers)]

    print(f"Scenario: Delivering newsletter to {num_subscribers} subscribers.")
    print("Each email delivery has a simulated SMTP latency of 50ms.")
    print("Each DB insert has a simulated DB query latency of 5ms.\n")

    # 1. Benchmark Original Logic
    print("Running Original Logic (sequential, blocking SMTP, N+1 DB inserts)...")
    start_time = time.perf_counter()
    sent, failed = await run_original_logic(subscribers, mock_send_email, mock_db_execute)
    original_duration = time.perf_counter() - start_time
    print(f"Original Logic Complete: Sent={sent}, Failed={failed}")
    print(f"Original Logic Time: {original_duration:.4f} seconds\n")

    # 2. Benchmark Optimized Logic
    print("Running Optimized Logic (concurrent threads, batch DB insert)...")
    start_time = time.perf_counter()
    sent, failed = await run_optimized_logic(subscribers, mock_send_email, mock_db_execute_many, semaphore_limit=10)
    optimized_duration = time.perf_counter() - start_time
    print(f"Optimized Logic Complete: Sent={sent}, Failed={failed}")
    print(f"Optimized Logic Time: {optimized_duration:.4f} seconds\n")

    # 3. Calculate Speedup
    speedup = original_duration / optimized_duration
    improvement = ((original_duration - optimized_duration) / original_duration) * 100
    print("=== BENCHMARK RESULTS ===")
    print(f"Original Duration:  {original_duration:.4f}s")
    print(f"Optimized Duration: {optimized_duration:.4f}s")
    print(f"Speedup Factor:     {speedup:.2f}x faster")
    print(f"Time Reduction:     {improvement:.2f}%")
    print("=========================")

if __name__ == "__main__":
    asyncio.run(main())
