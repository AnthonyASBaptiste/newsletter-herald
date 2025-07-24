import fitz
import docx
import tiktoken
import logging
import os
from typing import Union, BinaryIO, Optional, IO

# Create a logger for this module
logger = logging.getLogger(__name__)


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Estimate token count for a given string and model.
    
    Args:
        text: The text to count tokens for
        model: The model to use for token counting
        
    Returns:
        int: The number of tokens in the text
    """
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))


def extract_text_from_file(file: Union[str, BinaryIO, IO], file_type: Optional[str] = None) -> str:
    """
    Extract text from a file. Supports PDF and DOCX formats.
    
    Args:
        file: Either a file path (str) or a file-like object
        file_type: The type of file ('pdf' or 'docx'). If None, will be inferred from file path
        
    Returns:
        str: The extracted text
        
    Raises:
        ValueError: If the file type is not supported or cannot be determined
        IOError: If there is an error reading the file
    """
    # Determine file type if not provided
    if file_type is None:
        if isinstance(file, str):
            _, ext = os.path.splitext(file)
            file_type = ext.lower().lstrip('.')
        else:
            raise ValueError("file_type must be specified when file is not a path string")
    
    logger.debug(f"Extracting text from {file_type} file")
    
    if file_type == 'pdf':
        return extract_text_from_pdf(file)
    elif file_type == 'docx':
        return extract_text_from_docx(file)
    else:
        error_msg = f"Unsupported file type: {file_type}"
        logger.error(error_msg)
        raise ValueError(error_msg)


def extract_text_from_pdf(file: Union[str, BinaryIO]) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        file: Either a file path (str) or a file-like object
        
    Returns:
        str: The extracted text
        
    Raises:
        IOError: If there is an error reading the file
    """
    try:
        text = ""
        with fitz.open(file) as doc:
            for page in doc:
                text += page.get_text()
        logger.debug(f"Successfully extracted text from PDF ({len(text)} characters)")
        return text
    except Exception as e:
        error_msg = f"Error extracting text from PDF: {str(e)}"
        logger.error(error_msg)
        raise IOError(error_msg)


def extract_text_from_docx(file: Union[str, BinaryIO]) -> str:
    """
    Extract text from a DOCX file.
    
    Args:
        file: Either a file path (str) or a file-like object
        
    Returns:
        str: The extracted text
        
    Raises:
        IOError: If there is an error reading the file
    """
    try:
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        logger.debug(f"Successfully extracted text from DOCX ({len(text)} characters)")
        return text
    except Exception as e:
        error_msg = f"Error extracting text from DOCX: {str(e)}"
        logger.error(error_msg)
        raise IOError(error_msg)
