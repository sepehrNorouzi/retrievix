# Retrievix

A Retrieval-Augmented Generation (RAG) application built with FastAPI that enables document upload, indexing, and intelligent question-answering over your document corpus.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   FastAPI   │────▶│   Qdrant    │     │  PostgreSQL │
│   (API)     │     │  (Vectors)  │     │  (Metadata) │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Redis    │     │   Ollama    │     │   Ollama    │
│   (Cache)   │     │ (Embedding) │     │    (LLM)    │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Features

- **Document Ingestion**: Upload PDF, DOCX, HTML, Markdown, and text files
- **Text Extraction**: Automatic content extraction from multiple formats
- **Intelligent Chunking**: Token-aware document splitting
- **Vector Search**: Semantic search using Qdrant vector database
- **RAG-powered Q&A**: Generate answers from document context using LLM
- **Source Citations**: Returns source document references with similarity scores
- **Async Architecture**: Fully asynchronous for high throughput
- **Health Monitoring**: Comprehensive health checks for all dependencies

## Tech Stack

- **Framework**: FastAPI + Uvicorn
- **Database**: PostgreSQL (SQLAlchemy + Alembic)
- **Vector DB**: Qdrant
- **Cache**: Redis
- **AI**: Ollama (nomic-embed-text, llama3.2:1b)
- **Containerization**: Docker + Docker Compose

## Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development only)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd search-app
```

### 2. Configure Environment

```bash
cp env.sample .env
```

Edit `.env` with your configuration:

```env
# Postgres
POSTGRES_USER=retrievix
POSTGRES_PASSWORD=retrievix
POSTGRES_DB=retrievix

# Qdrant
QDRANT_VECTOR_SIZE=768
QDRANT_COLLECTION=retrievix

# Ollama
OLLAMA_MODEL=nomic-embed-text
OLLAMA_LLM_MODEL=llama3.2:1b

# App
EXPOSED_PORT=8000
DEBUG=false
```

### 3. Start Services

```bash
make up
```

This starts:
- **App** — `http://localhost:8000`
- **PostgreSQL** — `localhost:5432`
- **Redis** — `localhost:6379`
- **Qdrant** — `http://localhost:6333` (HTTP) / `localhost:6334` (gRPC)
- **Ollama** — `http://localhost:11434`

### 4. Pull Ollama Models

```bash
make pull-models
```

### 5. Run Database Migrations

```bash
make migrate
```

### 6. Access API Documentation

Open your browser to: `http://localhost:8000/docs`

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make up` | Start all services |
| `make down` | Stop all services |
| `make restart` | Restart all services |
| `make logs` | Tail logs for all services |
| `make logs-app` | Tail app logs only |
| `make status` | Show service status |
| `make pull-models` | Pull Ollama models |
| `make migrations msg="..."` | Generate a new migration |
| `make migrate` | Run database migrations |
| `make shell` | Open a shell in app container |
| `make psql` | Connect to PostgreSQL |
| `make clean` | Remove all containers, volumes, images |

## Local Development

For development without Docker:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Ensure PostgreSQL, Redis, and Qdrant are running locally
# Update .env accordingly (DATABASE_URL, REDIS_HOST, QDRANT_HOST)

alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/documents/` | Upload a document |
| `GET` | `/documents/` | List all documents |
| `GET` | `/documents/{doc_id}` | Get document details |
| `GET` | `/documents/{doc_id}/chunks` | Get document chunks |

### Ask

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ask/` | Ask a question about your documents |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Check system health status |

## Usage Examples

### Upload a Document

```bash
curl -X POST "http://localhost:8000/documents/" \
  -F "file=@example.pdf" \
  -F "title=My Document"
```

### Ask a Question

```bash
curl -X POST "http://localhost:8000/ask/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic of the document?",
    "top_k": 5,
    "include_sources": true
  }'
```

### Response Example

```json
{
  "answer": "The document discusses...",
  "sources": [
    {
      "chunk_id": "uuid",
      "document_id": "uuid",
      "text": "relevant text chunk...",
      "chunk_index": 0,
      "score": 0.85
    }
  ],
  "model": "llama3.2:1b"
}
```

## Project Structure

```
search-app/
├── app/
│   ├── ai/                    # AI components
│   │   ├── embedding/         # Embedding providers (Ollama)
│   │   └── llm/               # LLM clients
│   ├── api/                   # API routes
│   │   ├── document.py        # Document endpoints
│   │   └── ask.py             # Question-answering endpoint
│   ├── middleware/             # Custom middleware
│   ├── models/                # SQLAlchemy models
│   ├── repositories/          # Data access layer
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   │   ├── document.py        # Document service
│   │   ├── ask.py             # RAG query service
│   │   ├── chunking/          # Text chunking logic
│   │   └── extractors/        # Document extractors (PDF, DOCX, etc.)
│   ├── shared/                # Shared utilities
│   │   ├── database.py        # Database connection
│   │   ├── qdrant.py          # Qdrant client
│   │   └── redis.py           # Redis client
│   ├── utils/                 # Utility functions
│   ├── main.py                # Application entry point
│   └── settings.py            # Configuration management
├── alembic/                   # Database migrations
├── Dockerfile                 # Container image definition
├── docker-compose.yml         # Multi-service orchestration
├── requirements.txt           # Python dependencies
└── env.sample                 # Environment variables template
```

## Supported File Types

| Format | Extractor |
|--------|-----------|
| PDF | pdfplumber + pdfminer |
| DOCX | python-docx |
| HTML | BeautifulSoup4 |
| Markdown | markdown-it-py |
| Text | Plain text |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | PostgreSQL username | `retrievix` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `retrievix` |
| `POSTGRES_DB` | PostgreSQL database name | `retrievix` |
| `QDRANT_VECTOR_SIZE` | Embedding vector dimension | `768` |
| `QDRANT_COLLECTION` | Qdrant collection name | `retrievix` |
| `OLLAMA_MODEL` | Embedding model name | `nomic-embed-text` |
| `OLLAMA_LLM_MODEL` | LLM model name | `llama3_2` |
| `EXPOSED_PORT` | Application port | `8000` |
| `DEBUG` | Enable debug mode | `false` |

## License

[Add your license here]
