import os
import fitz
import pytest
from helpers.text_utils import compress_pdf


@pytest.fixture
def sample_pdf_bytes():
    """Generates a simple PDF in memory using fitz."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello World! This is a test PDF document for compression tests.")
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.fixture
def newsletter_pdf_bytes():
    """Loads test.pdf if present."""
    file_path = os.path.join(os.path.dirname(__file__), "../../test_newsletters/test.pdf")
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return f.read()
    return None


def test_compress_pdf_valid_generated(sample_pdf_bytes):
    """Test compressing a valid generated PDF."""
    compressed_bytes = compress_pdf(sample_pdf_bytes)

    assert isinstance(compressed_bytes, bytes)
    assert len(compressed_bytes) > 0

    # Verify that compressed_bytes is a valid PDF readable by fitz
    doc = fitz.open(stream=compressed_bytes, filetype="pdf")
    assert len(doc) == 1
    text = doc[0].get_text()
    assert "Hello World!" in text
    doc.close()


def test_compress_pdf_newsletter_file(newsletter_pdf_bytes):
    """Test compressing a real sample PDF file if available."""
    if newsletter_pdf_bytes is None:
        pytest.skip("test_newsletters/test.pdf not found")

    compressed_bytes = compress_pdf(newsletter_pdf_bytes)

    assert isinstance(compressed_bytes, bytes)
    assert len(compressed_bytes) > 0

    # Verify that compressed_bytes is a valid PDF
    doc = fitz.open(stream=compressed_bytes, filetype="pdf")
    assert len(doc) > 0
    doc.close()


def test_compress_pdf_invalid_bytes():
    """Test compress_pdf handles invalid/corrupted bytes gracefully by returning original bytes."""
    corrupted_bytes = b"Not a valid PDF file content"
    result = compress_pdf(corrupted_bytes)

    # Should return original bytes without raising an exception
    assert result == corrupted_bytes


def test_compress_pdf_empty_bytes():
    """Test compress_pdf handles empty bytes gracefully."""
    empty_bytes = b""
    result = compress_pdf(empty_bytes)

    assert result == empty_bytes
