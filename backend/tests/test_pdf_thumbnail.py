import io
import os
import sys
import pytest

# Ensure helpers module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from helpers.text_utils import generate_pdf_thumbnail

PDF_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../test_newsletters/test.pdf"))
PNG_MAGIC_HEADER = b"\x89PNG\r\n\x1a\n"

def test_generate_pdf_thumbnail_file_path():
    """Test thumbnail generation using a valid file path string."""
    assert os.path.exists(PDF_PATH), f"PDF file not found at {PDF_PATH}"
    thumbnail = generate_pdf_thumbnail(PDF_PATH)
    assert isinstance(thumbnail, bytes)
    assert len(thumbnail) > 0
    assert thumbnail.startswith(PNG_MAGIC_HEADER)

def test_generate_pdf_thumbnail_bytes():
    """Test thumbnail generation using raw bytes."""
    assert os.path.exists(PDF_PATH), f"PDF file not found at {PDF_PATH}"
    with open(PDF_PATH, "rb") as f:
        pdf_bytes = f.read()

    thumbnail = generate_pdf_thumbnail(pdf_bytes)
    assert isinstance(thumbnail, bytes)
    assert len(thumbnail) > 0
    assert thumbnail.startswith(PNG_MAGIC_HEADER)

def test_generate_pdf_thumbnail_bytesio():
    """Test thumbnail generation using a BytesIO file-like stream."""
    assert os.path.exists(PDF_PATH), f"PDF file not found at {PDF_PATH}"
    with open(PDF_PATH, "rb") as f:
        stream = io.BytesIO(f.read())

    thumbnail = generate_pdf_thumbnail(stream)
    assert isinstance(thumbnail, bytes)
    assert len(thumbnail) > 0
    assert thumbnail.startswith(PNG_MAGIC_HEADER)

def test_generate_pdf_thumbnail_invalid_file_path():
    """Test error handling when providing a non-existent file path."""
    with pytest.raises(Exception):
        generate_pdf_thumbnail("non_existent_file.pdf")

def test_generate_pdf_thumbnail_corrupt_stream():
    """Test error handling when providing corrupted PDF stream data."""
    corrupt_stream = io.BytesIO(b"Not a valid PDF content")
    with pytest.raises(Exception):
        generate_pdf_thumbnail(corrupt_stream)
