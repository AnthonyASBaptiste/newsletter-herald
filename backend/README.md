# SALLTO Herald API Gateway
The API Gateway acts as a single entry point that manages client requests and delegates them to the appropriate backend services for document processing and summarization.
## Overview
SALLTO Herald API Gateway is a FastAPI-based service designed to process and summarize document files (PDF and DOCX) using large language models. It's specifically optimized for summarizing Roman Catholic church newsletters into warm, concise email messages.
## Features
- **Document Processing**: Supports PDF and DOCX file uploads
- **Text Extraction**: Automatically extracts text content from uploaded documents
- **AI-Powered Summarization**: Uses LLM providers to generate concise summaries
- **API Key Authentication**: Secure endpoint access with API key verification
- **RESTful API**: Clean, well-documented API endpoints
- **Modular Architecture**: Organized codebase with separate modules for different functionalities

## Project Structure
``` 
├── main.py                # FastAPI application entry point
├── config.py              # Configuration settings
├── helpers/               # Utility functions
│   ├── __init__.py
│   ├── constants.py       # Application constants
│   ├── key_utils.py       # API key verification utilities
│   └── text_utils.py      # Text extraction utilities
├── llm/                   # LLM provider integrations
│   └── providers.py       # LLM provider selection and summarization
├── pyproject.toml         # Python project configuration
└── .gitignore             # Git ignore rules
```
## Installation
1. **Clone the repository**:
``` bash
   git clone <repository-url>
   cd sallto-herald-api-gateway
```
1. **Install dependencies**:
``` bash
   pip install -r requirements.txt
```
Or if using Poetry:
``` bash
   poetry install
```
1. **Set up environment variables**: Create a file in the project root and add your API keys: `.env`
``` env
   OPENAI_API_KEY=your_openai_api_key_here
   API_KEY=your_service_api_key_here
```
## Usage
### Running the Application
Start the FastAPI server:
``` bash
uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`
### API Documentation
Once the server is running, you can access:
- **Interactive API Documentation**: `http://127.0.0.1:8000/docs`
- **Alternative Documentation**: `http://127.0.0.1:8000/redoc`

### API Endpoints
#### GET `/`
Simple health check endpoint to confirm the API is running.
**Response:**
``` json
{
  "message": "Welcome to your SALLTO Herald API Gateway"
}
```
#### POST `/upload-document`
Uploads and processes a document file for summarization.
**Headers:**
- `X-API-Key`: Required API key for authentication

**Request:**
- **Content-Type**: `multipart/form-data`
- **Body**: File upload (PDF or DOCX)

**Supported File Types:**
- `application/pdf`
- `application/vnd.openxmlformats-officedocument.wordprocessingml.document`

**Response:**
``` json
{
  "summary": "Generated summary of the document content..."
}
```
**Error Responses:**
- `400`: Unsupported file type
- `401`: Invalid or missing API key
- `500`: Internal server error (file processing or LLM error)

## Dependencies
- **FastAPI**: Web framework for building APIs
- **PyMuPDF (fitz)**: PDF text extraction
- **python-docx**: DOCX document processing
- **OpenAI**: LLM integration
- **python-dotenv**: Environment variable management
- **pydantic-settings**: Configuration management
- **uvicorn**: ASGI server

## Configuration
The application uses environment variables for configuration:
- `OPENAI_API_KEY`: Your OpenAI API key
- : API key for endpoint authentication `API_KEY`

## Development
### Running Tests
``` bash
pytest
```
### Code Structure
- : Contains the FastAPI application and endpoint definitions **main.py**
- **helpers/**: Utility modules for text processing and authentication
- **llm/**: LLM provider integrations and summarization logic
- : Application configuration management **config.py**

## Security
- API key authentication is required for document upload endpoints
- File type validation prevents processing of unsupported formats
- Error handling prevents sensitive information leakage

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License
[Add your license information here]
## Support
For issues and questions, please create an issue in the project repository.
