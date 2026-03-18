# Newsletter Herald Backend API

FastAPI-based service designed to automate document processing, text extraction, and AI-powered summarization of church newsletters.

## Tech Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLAlchemy (async) with Neon.tech (PostgreSQL)
- **LLM Integrations**:
  - **Ollama**: Local processing (Llama 3.3 70B recommended)
  - **Groq**: High-speed cloud API (Llama 3.3 70B)
  - **Anthropic**: Claude 3 Opus for complex documents
- **Storage**:
  - **Cloudflare R2**: Primary storage for newsletter PDFs and thumbnails
  - **Google Drive**: Fallback storage and backup
- **Auth**: Stack Auth for user management and secure API access

## Project Structure
- `main.py`: FastAPI entry point
- `config.py`: Configuration and environment variable management
- `db/`: Database models and connection setup
- `llm/`: LLM provider logic and summarization orchestration
- `helpers/`: Utilities for text extraction (OCR), storage, and auth
- `scripts/`: Batch processing and maintenance scripts

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: Using a virtual environment (`python -m venv venv`) is recommended.*

2. **Configuration**:
   Copy `.env.example` to `.env` and configure your API keys, database URLs, and cloud storage credentials.

3. **Initialize Database**:
   ```bash
   python scripts/create_tables.py
   ```

4. **Run the API**:
   ```bash
   uvicorn main:app --reload
   ```

## Key Scripts

### Batch Upload
Process all PDF/DOCX files in `newsletters_to_upload/`:
```bash
python scripts/upload_local_files.py
```

### Drive Synchronization
Process existing files in the configured Google Drive folder:
```bash
python scripts/process_existing_drive_files.py
```

## LLM Configuration

The backend supports multiple strategies configured in `.env` via `LLM_STRATEGY`:
- **`local`**: Uses the local Ollama instance at `OLLAMA_BASE_URL`.
- **`groq`**: Forces usage of Groq's high-performance inference.
- **`remote`**: Forces usage of Anthropic's Claude.
- **`auto`**: Uses local models for standard documents and remote models for large ones.

## API Documentation
Interactive docs are available at `http://localhost:8000/docs`.
