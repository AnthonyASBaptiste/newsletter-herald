import asyncio
import os
import sys
import pytest
from starlette.concurrency import run_in_threadpool

# Add backend directory to path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import sync_extract_text

PDF_PATH = "../test_newsletters/test.pdf"

@pytest.fixture
def anyio_backend():
    return 'asyncio'

def test_sync_extract_text_pdf():
    assert os.path.exists(PDF_PATH), f"PDF not found at {PDF_PATH}"
    with open(PDF_PATH, "rb") as f:
        pdf_bytes = f.read()

    # Run sync_extract_text directly (synchronously)
    text = sync_extract_text(pdf_bytes, "application/pdf")

    # Assertions
    assert isinstance(text, str)
    assert len(text) > 0
    # Let us print the first 100 characters to verify
    print(f"Extracted PDF text length: {len(text)}")
    print(f"Sample: {text[:100]}...")

@pytest.mark.anyio
async def test_async_extract_text_pdf_threadpool(anyio_backend):
    assert os.path.exists(PDF_PATH), f"PDF not found at {PDF_PATH}"
    with open(PDF_PATH, "rb") as f:
        pdf_bytes = f.read()

    # Run via threadpool
    text = await run_in_threadpool(sync_extract_text, pdf_bytes, "application/pdf")

    # Assertions
    assert isinstance(text, str)
    assert len(text) > 0
    print("Async threadpool test passed!")

if __name__ == "__main__":
    print("Running synchronous extraction test...")
    test_sync_extract_text_pdf()
    print("Running asynchronous threadpool extraction test...")
    asyncio.run(test_async_extract_text_pdf_threadpool('asyncio'))
    print("All functional tests passed successfully!")
