# RAG Builder Usage Examples

## Example 1: Initialize a New RAG Project

**User input:** `/rag-builder init`

**Result:** Creates the basic project structure with all necessary files.

```
rag/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── chat.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── document_loader.py
│   │   │   ├── text_splitter.py
│   │   │   ├── embedding.py
│   │   │   ├── vector_store.py
│   │   │   ├── retriever.py
│   │   │   ├── reranker.py
│   │   │   ├── llm.py
│   │   │   ├── prompts.py
│   │   │   └── rag.py
│   │   └── main.py
│   ├── data/
│   │   ├── raw/
│   │   ├── processed/
│   │   └── vector_db/
│   ├── scripts/
│   │   ├── process_textbooks.py
│   │   └── vectorize_textbooks.py
│   ├── requirements.txt
│   ├── .env.example
│   └── start.py
└── frontend/ (optional)
```

## Example 2: Create Document Processing Script

**User input:** `/rag-builder script process`

**Result:** Creates `backend/scripts/process_textbooks.py`

```python
#!/usr/bin/env python
"""Process documents for RAG pipeline"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.pipeline import DocumentPipeline
from app.core.config import get_settings

def main():
    settings = get_settings()
    pipeline = DocumentPipeline()

    print("Processing documents...")
    chunks = pipeline.process_all()

    print(f"Generated {len(chunks)} chunks")
    print(f"Saved to {settings.processed_path}/chunks.json")

if __name__ == "__main__":
    main()
```

## Example 3: Create Vectorization Script

**User input:** `/rag-builder script vectorize`

**Result:** Creates `backend/scripts/vectorize_textbooks.py`

```python
#!/usr/bin/env python
"""Vectorize documents and store in ChromaDB"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.pipeline import DocumentPipeline
from app.services.embedding import EmbeddingService
from app.services.vector_store import VectorStore
from app.core.config import get_settings

def main():
    settings = get_settings()

    # Load chunks
    pipeline = DocumentPipeline()
    chunks = pipeline.load_processed_chunks()

    if not chunks:
        print("No chunks found. Run process_textbooks.py first.")
        return

    # Generate embeddings
    print(f"Generating embeddings for {len(chunks)} chunks...")
    embedding_service = EmbeddingService()
    embeddings = embedding_service.embed_texts([c["text"] for c in chunks])

    # Store in vector database
    print("Storing in ChromaDB...")
    vector_store = VectorStore(settings.vector_db_path)
    vector_store.add_documents(chunks, embeddings)

    print(f"Done! Stored {len(chunks)} documents in {settings.vector_db_path}")

if __name__ == "__main__":
    main()
```

## Example 4: Troubleshoot Empty Retrieval

**User input:** "My RAG system returns no results when I query"

**Result:** Claude runs through the diagnostic checklist:

1. Check if documents were processed:
   ```bash
   ls backend/data/processed/chunks.json
   ```

2. Check if vector database exists:
   ```bash
   ls backend/data/vector_db/chroma/
   ```

3. Test embedding service:
   ```python
   from app.services.embedding import EmbeddingService
   emb = EmbeddingService()
   print(emb.embed_query("test"))  # Should return a list of floats
   ```

4. Check chunk_size configuration - may be too small

5. Verify BM25 index is built if using hybrid retrieval

## Example 5: Add Streaming Support

**User input:** `/rag-builder add streaming`

**Result:** Adds streaming endpoint to `app/api/chat.py`:

```python
from fastapi.responses import StreamingResponse

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    def generate():
        for chunk in rag_service.answer_stream(
            question=request.question,
            mode=request.mode,
            top_k=request.top_k,
            history=request.history,
            session_id=request.session_id
        ):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

## Example 6: Optimize for Chinese Language

**User input:** "Optimize my RAG for Chinese documents"

**Result:** Configuration recommendations:

```python
# config.py
chunk_size = 400  # Chinese needs smaller chunks
chunk_overlap = 80  # More overlap for context
separator = ["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
```

```python
# embedding.py - Use BGE Chinese model
model_name = "BAAI/bge-base-zh-v1.5"
```

```python
# retriever.py - Use jieba for BM25
from jieba import lcut
tokenized_corpus = [lcut(doc["text"]) for doc in chunks]
```

## Example 7: Switch Between LLM Providers

**User input:** "Switch from ZhipuAI to Gemini"

**Result:** Update `.env` and potentially modify `llm.py`:

```env
# .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_key
# ZHIPUAI_API_KEY=  # Can be kept as backup
```

The `llm.py` service should already support both providers via `LLM_PROVIDER` config.

## Example 8: Add Document Source Tracking

**User input:** "Track which chapter each answer comes from"

**Result:** Ensure metadata is preserved:

```python
# In document_loader.py
documents.append({
    "content": content,
    "metadata": {
        "source": md_file.stem,
        "chapter": extract_chapter_name(md_file),  # Parse from filename
        "path": str(md_file)
    }
})

# In rag.py - Response includes sources
sources = [
    {
        "source": doc["metadata"]["source"],
        "chapter": doc["metadata"].get("chapter", "未知"),
        "relevance": doc.get("score", 0)
    }
    for doc in docs[:top_k]
]
```

## Example 9: Create Test Script

**User input:** `/rag-builder test`

**Result:** Creates `backend/tests/test_rag.py`:

```python
import pytest
from app.services.rag import RAGService

def test_basic_answer():
    rag = RAGService()
    result = rag.answer("什么是贝叶斯定理？", mode="quick", top_k=3)
    assert "answer" in result
    assert "sources" in result
    assert len(result["sources"]) > 0

def test_session_history():
    rag = RAGService()
    session_id = "test_session"

    rag.answer("你好", session_id=session_id)
    history = rag.get_session_history(session_id)
    assert len(history) > 0

    rag.clear_session(session_id)
    history = rag.get_session_history(session_id)
    assert len(history) == 0
```

Run tests: `pytest backend/tests/`

## Example 10: Deploy Checklist

**User input:** "Production deployment checklist"

**Result:**

- [ ] Set `debug=False` in config
- [ ] Use environment variables for all secrets
- [ ] Build vector database on production server
- [ ] Set up CORS for specific domains only
- [ ] Add rate limiting
- [ ] Configure proper logging
- [ ] Set up monitoring for API health
- [ ] Test with production data volume
- [ ] Document API endpoints
- [ ] Set up backup for vector database
