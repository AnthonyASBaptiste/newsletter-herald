import asyncio
import io
import os
import tempfile
import sys
import docx
import pytest
from starlette.concurrency import run_in_threadpool

# Add backend directory to path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import sync_extract_text
from helpers.text_utils import extract_text_from_docx, extract_text_from_file

PDF_PATH = "../test_newsletters/test.pdf"

@pytest.fixture
def anyio_backend():
    return 'asyncio'

def create_sample_docx_bytes(paragraphs=None) -> bytes:
    if paragraphs is None:
        paragraphs = ["Parish Newsletter", "Welcome to Sunday Service.", "Community Announcements"]
    doc = docx.Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

def test_extract_text_from_docx_valid():
    paragraphs = ["First Paragraph", "Second Paragraph", "Third Paragraph"]
    docx_bytes = create_sample_docx_bytes(paragraphs)
    text = extract_text_from_docx(io.BytesIO(docx_bytes))
    assert text == "First Paragraph\nSecond Paragraph\nThird Paragraph"

def test_extract_text_from_docx_invalid():
    invalid_file = io.BytesIO(b"This is not a valid docx file content")
    with pytest.raises(IOError) as exc_info:
        extract_text_from_docx(invalid_file)
    assert "Error extracting text from DOCX" in str(exc_info.value)

def test_sync_extract_text_docx():
    docx_bytes = create_sample_docx_bytes(["Docx test line 1", "Docx test line 2"])
    text = sync_extract_text(docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    assert "Docx test line 1" in text
    assert "Docx test line 2" in text

def test_extract_text_from_file_docx_buffer_and_path():
    paragraphs = ["Heading", "Body text for test file"]
    docx_bytes = create_sample_docx_bytes(paragraphs)

    # Test file_type='docx' with buffer
    extracted_buffer = extract_text_from_file(io.BytesIO(docx_bytes), file_type="docx")
    assert "Body text for test file" in extracted_buffer

    # Test path string with extension
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(docx_bytes)
        tmp_path = tmp.name

    try:
        extracted_path = extract_text_from_file(tmp_path)
        assert "Body text for test file" in extracted_path
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

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
    print("Running docx extraction test...")
    test_extract_text_from_docx_valid()
    test_extract_text_from_docx_invalid()
    test_sync_extract_text_docx()
    test_extract_text_from_file_docx_buffer_and_path()
    print("Running synchronous PDF extraction test...")
    test_sync_extract_text_pdf()
    print("Running asynchronous threadpool extraction test...")
    asyncio.run(test_async_extract_text_pdf_threadpool('asyncio'))
    print("All functional tests passed successfully!")
