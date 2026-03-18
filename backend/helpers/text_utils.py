import fitz
import docx
import tiktoken
import logging
import os
import io
import re
import datetime
from typing import Union, BinaryIO, Optional, IO

# Create a logger for this module
logger = logging.getLogger(__name__)


def sanitize_filename(filename: str) -> str:
    """
    Standardizes and sanitizes a filename by extracting a date from it.
    Format: YYYY-MM-DD-SALLTO-Newsletter.pdf
    """
    _, ext = os.path.splitext(filename)
    
    # Common month names mapping
    months_map = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    found_date = None
    
    # Patterns to try (ordered by specificity)
    patterns = [
        # DD Month YYYY (e.g., 15 Feb 2026, 8Dec2024, 15th March 2025)
        r'(\d{1,2})(?:st|nd|rd|th)?\s*([A-Za-z]{3,})\s*(\d{4})',
        # Month DD YYYY (e.g., Feb 1 2026)
        r'([A-Za-z]{3,})\s*(\d{1,2})(?:st|nd|rd|th)?\s*(\d{4})',
        # DD.MM.YY or DD.MM.YYYY
        r'(\d{1,2})[._/](\d{1,2})[._/](\d{2,4})',
    ]
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            try:
                if i == 0: # DD Month YYYY
                    day = int(match.group(1))
                    month_str = match.group(2)[:3].lower()
                    year = int(match.group(3))
                    if month_str in months_map:
                        found_date = datetime.date(year, months_map[month_str], day)
                elif i == 1: # Month DD YYYY
                    month_str = match.group(1)[:3].lower()
                    day = int(match.group(2))
                    year = int(match.group(3))
                    if month_str in months_map:
                        found_date = datetime.date(year, months_map[month_str], day)
                elif i == 2: # DD.MM.YY
                    day = int(match.group(1))
                    month = int(match.group(2))
                    year = int(match.group(3))
                    if year < 100:
                        year += 2000
                    found_date = datetime.date(year, month, day)
                
                if found_date:
                    break
            except Exception as e:
                logger.debug(f"Failed to parse date with pattern {pattern}: {e}")
                continue

    if not found_date:
        # Fallback to today if no date found in filename
        found_date = datetime.date.today()
        logger.warning(f"No date found in filename '{filename}', falling back to {found_date}")
    
    date_str = found_date.strftime('%Y-%m-%d')
    return f"{date_str}-SALLTO-Newsletter{ext.lower()}"

def compress_pdf(pdf_bytes: bytes) -> bytes:
    """
    Compresses a PDF to save space while keeping it looking good.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        out_stream = io.BytesIO()
        # garbage=4: remove unused objects, compact xref, etc.
        # deflate=True: compress streams
        doc.save(out_stream, garbage=4, deflate=True, clean=True)
        compressed = out_stream.getvalue()
        doc.close()
        
        orig_size = len(pdf_bytes)
        comp_size = len(compressed)
        reduction = (1 - comp_size / orig_size) * 100 if orig_size > 0 else 0
        logger.info(f"PDF compressed: {orig_size/1024:.1f}KB -> {comp_size/1024:.1f}KB ({reduction:.1f}% reduction)")
        
        return compressed
    except Exception as e:
        logger.error(f"Error compressing PDF: {e}")
        return pdf_bytes

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Estimate token count for a given string and model.
    """
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))


def extract_text_from_file(file: Union[str, BinaryIO, IO], file_type: Optional[str] = None) -> str:
    """
    Extract text from a file. Supports PDF and DOCX formats.
    """
    if file_type is None:
        if isinstance(file, str):
            _, ext = os.path.splitext(file)
            file_type = ext.lower().lstrip('.')
        else:
            raise ValueError("file_type must be specified when file is not a path string")
    
    if file_type == 'pdf':
        return extract_text_from_pdf(file)
    elif file_type == 'docx':
        return extract_text_from_docx(file)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def extract_text_from_pdf(file: Union[str, BinaryIO, IO]) -> str:
    """
    Extract text from a PDF file.
    """
    try:
        text = ""
        if isinstance(file, (str, bytes)):
            doc = fitz.open(file)
        else:
            # Handle BytesIO or file stream
            doc = fitz.open(stream=file.read(), filetype="pdf")
            
        with doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        error_msg = f"Error extracting text from PDF: {str(e)}"
        logger.error(error_msg)
        raise IOError(error_msg)


def extract_text_from_docx(file: Union[str, BinaryIO, IO]) -> str:
    """
    Extract text from a DOCX file.
    """
    try:
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        error_msg = f"Error extracting text from DOCX: {str(e)}"
        logger.error(error_msg)
        raise IOError(error_msg)

def generate_pdf_thumbnail(file: Union[str, BinaryIO, IO]) -> bytes:
    """
    Generates a PNG image of the first page of a PDF.
    """
    try:
        if isinstance(file, (str, bytes)):
            doc = fitz.open(file)
        else:
            file.seek(0)
            doc = fitz.open(stream=file.read(), filetype="pdf")
            
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_data = pix.tobytes("png")
        doc.close()
        return img_data
    except Exception as e:
        logger.error(f"Error generating PDF thumbnail: {e}")
        raise
