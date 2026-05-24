# Newsletter Herald

An automated pipeline for summarizing Roman Catholic church newsletters into warm, concise email messages for parishioners.

## Project Overview

Newsletter Herald is a full-stack application that automates the extraction, summarization, and management of church newsletters. It features a robust FastAPI backend for document processing and an interactive Next.js frontend for visualization and management.

### Key Features
- **Multi-Source Support**: Processes PDF and DOCX files.
- **Intelligent Summarization**: Integrated with multiple LLM providers:
  - **Local**: Ollama (Llama 3.3 70B recommended for high quality).
  - **Remote**: Groq (Llama 3.3 70B) and Anthropic (Claude 3 Opus).
- **Hybrid Storage**: Uses Cloudflare R2 for file storage and Google Drive for backups.
- **Automated Workflow**: Batch processing scripts for local files and Google Drive integration.
- **Modern UI**: Clean, responsive dashboard built with Next.js and Material UI.

## Repository Structure

- **`backend/`**: FastAPI service handling OCR, LLM orchestration, database management, and cloud storage.
- **`frontend/`**: Next.js application for users to view summaries and manage newsletters.
- **`newsletters_to_upload/`**: Local staging directory for batch newsletter processing. only needed for a one time upload of all newsletters.

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.ai/) (for local LLM processing)
- PostgreSQL (Neon.tech recommended)

### Quick Start

Run both services with a single command from the root:
```bash
npm start
```
*Note: This uses `concurrently` to run the FastAPI backend and Next.js frontend simultaneously.*

### Manual Setup

1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env  # Fill in your API keys
   uvicorn main:app --reload
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Batch Processing**:
   Place newsletters in `newsletters_to_upload/` and run:
   ```bash
   python backend/scripts/upload_local_files.py
   ```

## LLM Strategy

The project supports a flexible LLM strategy configured via `.env`:
- `local`: Forces usage of local Ollama (Llama 3.3).
- `groq`: Forces high-speed Groq API.
- `remote`: Forces Claude 3 (Anthropic).
- `auto`: Automatically switches based on document size and availability.

## License
[MIT](LICENSE)
