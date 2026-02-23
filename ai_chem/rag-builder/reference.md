# RAG Quick Reference

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ZHIPUAI_API_KEY` | - | ZhipuAI GLM-4 API key |
| `GEMINI_API_KEY` | - | Google Gemini API key |
| `LLM_PROVIDER` | `gemini` | LLM provider (gemini/zhipuai) |
| `CHUNK_SIZE` | `500` | Text chunk size in characters |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `TOP_K` | `5` | Number of documents to retrieve |
| `USE_RERANKER` | `true` | Enable BGE reranker |

## RAG Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `quick` | Concise answers | Quick lookups |
| `deep` | Detailed explanations | Learning new topics |
| `exam` | Exam-focused review | Test preparation |

## Key File Locations

```
backend/
├── app/core/config.py          # Configuration
├── app/services/               # Business logic
├── data/processed/chunks.json  # Processed chunks
├── data/vector_db/chroma/      # ChromaDB storage
└── .env                        # Environment variables
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Model not found` | Embedding model not downloaded | Check internet, run again |
| `No results found` | Empty vector DB | Run `vectorize_textbooks.py` |
| `API key invalid` | Wrong LLM API key | Check `.env` file |
| `Out of memory` | Too many chunks | Reduce `chunk_size` or `top_k` |
| `CORS error` | Frontend can't reach API | Update CORS origins in `main.py` |

## Model Information

| Component | Model | Purpose |
|-----------|-------|---------|
| Embedding | BAAI/bge-base-zh-v1.5 | Chinese text embeddings |
| Reranker | BAAI/bge-reranker-base | Result reranking |
| LLM | gemini-1.5-flash | Answer generation |
| LLM | GLM-4 | Alternative LLM (ZhipuAI) |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat/` | POST | Question answering |
| `/api/chat/stream` | POST | Streaming response |
| `/api/textbook/info` | GET | Document metadata |
| `/api/textbook/chapters` | GET | Chapter list |
| `/docs` | GET | Swagger API docs |
| `/health` | GET | Health check |

## ChromaDB Commands

```python
# Connect to existing database
client = chromadb.PersistentClient(path="data/vector_db/chroma")
collection = client.get_collection("documents")

# Count documents
collection.count()

# Delete and recreate
client.delete_collection("documents")
collection = client.create_collection("documents")
```

## Testing RAG Pipeline

```python
# Test retrieval
from app.services.retriever import HybridRetriever
retriever = HybridRetriever()
results = retriever.retrieve("test query", top_k=5)

# Test LLM
from app.services.llm import LLMService
llm = LLMService()
answer = llm.generate("test prompt")

# Test full RAG
from app.services.rag import RAGService
rag = RAGService()
result = rag.answer("test question", mode="quick")
```

## Performance Tuning

| Goal | Setting |
|------|---------|
| Faster retrieval | Decrease `top_k`, disable reranker |
| Better accuracy | Increase `top_k`, enable reranker |
| Less memory | Decrease `chunk_size`, use quantization |
| Chinese optimization | Use BGE-zh, jieba tokenization |

## Chinese Text Processing

```python
# Recommended separators for Chinese
separators = ["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]

# BM25 with jieba
from jieba import lcut
tokenized = lcut("中文分词测试")
```

## Session Management

```python
# Clear session
rag_service.clear_session(session_id)

# Get history
history = rag_service.get_session_history(session_id)

# Clear all
rag_service.clear_all_sessions()
```

## Useful Commands

```bash
# Process documents
python scripts/process_textbooks.py

# Vectorize
python scripts/vectorize_textbooks.py

# Start server
python start.py

# Run tests
pytest backend/tests/

# Check ChromaDB
python -c "import chromadb; print(chromadb.PersistentClient('data/vector_db/chroma').get_collection('documents').count())"
```

## File Dependencies

```
SKILL.md (this file)
├── templates.md     # Code templates for all services
├── examples.md      # Usage examples and scenarios
└── reference.md     # This quick reference guide
```
