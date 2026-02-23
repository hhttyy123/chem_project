---
name: rag-builder
description: Build and configure RAG (Retrieval-Augmented Generation) applications. Use when setting up a new RAG project, configuring document processing, implementing retrieval systems, or troubleshooting RAG pipelines.
argument-hint: [component]
---

# RAG Builder

Helps build, configure, and troubleshoot RAG applications using FastAPI, LangChain, ChromaDB, and BGE embeddings optimized for Chinese language content.

## Architecture Overview

A typical RAG pipeline consists of:
1. **Document Loading** - Markdown/text files via `MarkdownLoader`
2. **Chunking** - `TextSplitter` with configurable `chunk_size` and `chunk_overlap`
3. **Embedding** - BGE-base-zh for Chinese text embeddings
4. **Storage** - ChromaDB for vector storage
5. **Retrieval** - Hybrid: Vector (dense) + BM25 (sparse) + Reranker
6. **Generation** - LLM (ZhipuAI GLM-4 or Google Gemini)

## Project Structure

```
rag/
├── backend/
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Config (config.py)
│   │   ├── models/      # Pydantic models
│   │   ├── services/    # Business logic
│   │   └── main.py      # FastAPI app
│   ├── data/
│   │   ├── raw/         # Source documents
│   │   ├── processed/   # chunks.json
│   │   └── vector_db/   # ChromaDB
│   ├── scripts/         # Processing scripts
│   ├── requirements.txt
│   ├── .env             # API keys
│   └── start.py
└── frontend/            # Optional React frontend
```

## Setup Steps

### 1. Initialize Backend

Create `backend/requirements.txt`:

```txt
# Web framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# RAG framework
langchain==0.1.0
langchain-community==0.0.10
langchain-openai==0.0.2

# Vector database
chromadb==0.4.22

# Document processing
pypdf==3.17.4
pdfplumber==0.10.3
unstructured==0.11.6

# Embedding
sentence-transformers==2.3.1

# Retrieval
rank-bm25==0.2.2

# LLM (choose one or both)
zhipuai==2.1.5.20250825
google-genai==1.9.0

# Utilities
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
httpx==0.26.0
jieba==0.42.1
numpy>=1.24.0
torch>=2.0.0
```

### 2. Configuration (`backend/app/core/config.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # LLM
    zhipuai_api_key: str = ""
    gemini_api_key: str = ""
    llm_provider: str = "gemini"  # or "zhipuai"

    # Data paths
    textbook_path: str = "../data/raw"
    processed_path: str = "../data/processed"
    vector_db_path: str = "../data/vector_db/chroma"

    # Chunking
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Retrieval
    top_k: int = 5
    use_reranker: bool = True

    class Config:
        env_file = ".env"

_settings = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
```

### 3. Core Services

Create these services in `backend/app/services/`:

**document_loader.py** - Load markdown/text files
**text_splitter.py** - Chunk documents with overlap
**embedding.py** - BGE embeddings for Chinese
**vector_store.py** - ChromaDB operations
**retriever.py** - Hybrid retrieval (vector + BM25)
**reranker.py** - BGE reranker
**llm.py** - LLM service with session management
**prompts.py** - QA prompt templates
**rag.py** - Main orchestration

### 4. API Routes

Create `backend/app/api/chat.py`:

```python
from fastapi import APIRouter
from app.services.rag import RAGService
from app.models import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])
rag_service = RAGService()

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    result = rag_service.answer(
        question=request.question,
        mode=request.mode,
        top_k=request.top_k,
        history=request.history,
        session_id=request.session_id
    )
    return result
```

### 5. Environment Variables

Create `backend/.env`:

```env
# LLM API Keys (choose one)
ZHIPUAI_API_KEY=your_zhipuai_key
GEMINI_API_KEY=your_gemini_key
LLM_PROVIDER=gemini

# Optional overrides
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K=5
USE_RERANKER=true
```

## Common Commands

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Process documents
python scripts/process_textbooks.py

# Vectorize documents
python scripts/vectorize_textbooks.py

# Start server
python start.py

# Run tests
python tests/test_api.py
```

## Troubleshooting

### Embedding model not found
- Models auto-download to `models--BAAI--bge-base-zh-v1.5/`
- Check internet connection on first run

### ChromaDB errors
- Delete `data/vector_db/chroma/` and re-run `vectorize_textbooks.py`

### Empty retrieval results
- Check `chunk_size` - too small may lose context
- Verify documents were processed (check `data/processed/chunks.json`)
- Try increasing `top_k`

### Poor answer quality
- Enable reranker: `USE_RERANKER=true`
- Try different modes: `quick`, `deep`, `exam`
- Check LLM API key is valid

### Memory issues
- Reduce `chunk_size` or `top_k`
- Disable reranker if not needed
- Use smaller embedding model

## Multi-turn Conversation

The RAG service uses Gemini Chat Sessions for conversation history:
- Each `session_id` maintains its own context
- History enhances retrieval queries but NOT LLM prompts
- Clear sessions: `rag_service.clear_session(session_id)`

## Supporting Files

- **[templates.md](templates.md)** - Complete code templates for all RAG services (document_loader, text_splitter, embedding, vector_store, retriever, reranker, llm, prompts, main app, and data models)
- **[examples.md](examples.md)** - Usage examples and common scenarios (init project, create scripts, troubleshoot, add features, deployment checklist)
- **[reference.md](reference.md)** - Quick reference guide with environment variables, API endpoints, error solutions, and useful commands

## External Resources

- ChromaDB docs: https://docs.trychroma.com/
- LangChain docs: https://python.langchain.com/
- BGE embeddings: https://huggingface.co/BAAI/bge-base-zh-v1.5
