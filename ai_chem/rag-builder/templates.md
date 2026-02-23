# RAG Service Templates

## Document Loader Template

```python
# backend/app/services/document_loader.py
from pathlib import Path
from typing import List, Dict
import json

class MarkdownLoader:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)

    def load_all_textbooks(self) -> List[Dict]:
        documents = []
        for md_file in self.base_path.rglob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            documents.append({
                "content": content,
                "metadata": {
                    "source": md_file.stem,
                    "path": str(md_file)
                }
            })
        return documents
```

## Text Splitter Template

```python
# backend/app/services/text_splitter.py
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter

class TextSplitter:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )

    def split(self, documents: List[Dict]) -> List[Dict]:
        chunks = []
        for doc in documents:
            texts = self.splitter.split_text(doc["content"])
            for i, text in enumerate(texts):
                chunks.append({
                    "text": text,
                    "metadata": {
                        **doc["metadata"],
                        "chunk_id": f"{doc['metadata']['source']}-{i}"
                    }
                })
        return chunks
```

## Embedding Service Template

```python
# backend/app/services/embedding.py
from sentence_transformers import SentenceTransformer
from typing import List

class EmbeddingService:
    def __init__(self, model_name: str = "BAAI/bge-base-zh-v1.5"):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self, query: str) -> List[float]:
        return self.model.encode(query, normalize_embeddings=True).tolist()
```

## Vector Store Template

```python
# backend/app/services/vector_store.py
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from pathlib import Path

class VectorStore:
    def __init__(self, path: str):
        self.client = chromadb.PersistentClient(
            path=path,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, chunks: List[Dict], embeddings: List[List[float]]):
        self.collection.add(
            documents=[c["text"] for c in chunks],
            embeddings=embeddings,
            metadatas=[c["metadata"] for c in chunks],
            ids=[c["metadata"]["chunk_id"] for c in chunks]
        )

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return [
            {
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": results["distances"][0][i]
            }
            for i in range(len(results["documents"][0]))
        ]
```

## Reranker Template

```python
# backend/app/services/reranker.py
from sentence_transformers import CrossEncoder
from typing import List, Dict

class Reranker:
    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, docs: List[Dict], top_k: int = 5) -> List[Dict]:
        pairs = [[query, doc["text"]] for doc in docs]
        scores = self.model.predict(pairs)

        for i, doc in enumerate(docs):
            doc["reranker_score"] = float(scores[i])

        return sorted(docs, key=lambda x: x["reranker_score"], reverse=True)[:top_k]
```

## Hybrid Retriever Template

```python
# backend/app/services/retriever.py
from app.services.vector_store import VectorStore
from app.services.embedding import EmbeddingService
from app.services.reranker import Reranker
from rank_bm25 import BM25Okapi
from jieba import lcut
from typing import List, Dict

class HybridRetriever:
    def __init__(self, vector_store: VectorStore, embedding_service: EmbeddingService):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.bm25 = None
        self.documents = []

    def build_bm25_index(self, chunks: List[Dict]):
        self.documents = chunks
        tokenized_corpus = [lcut(doc["text"]) for doc in chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        # Dense retrieval
        query_emb = self.embedding_service.embed_query(query)
        dense_results = self.vector_store.search(query_emb, top_k=top_k * 2)

        # Sparse retrieval (BM25)
        if self.bm25:
            tokenized_query = lcut(query)
            sparse_scores = self.bm25.get_scores(tokenized_query)
            sparse_docs = [
                {**self.documents[i], "bm25_score": float(sparse_scores[i])}
                for i in range(len(self.documents))
            ]
            sparse_docs = sorted(sparse_docs, key=lambda x: x["bm25_score"], reverse=True)[:top_k * 2]

            # Combine scores
            combined = {}
            for doc in dense_results:
                combined[doc["metadata"]["chunk_id"]] = {**doc, "combined_score": doc["score"]}
            for doc in sparse_docs:
                cid = doc["metadata"]["chunk_id"]
                if cid in combined:
                    combined[cid]["combined_score"] += doc["bm25_score"] * 0.1
                else:
                    combined[cid] = {**doc, "combined_score": doc["bm25_score"] * 0.1}

            return sorted(combined.values(), key=lambda x: x["combined_score"], reverse=True)[:top_k]

        return dense_results[:top_k]
```

## LLM Service Template (Gemini)

```python
# backend/app/services/llm.py
import google.generativeai as genai
from typing import Generator
from app.core.config import get_settings

settings = get_settings()

class LLMService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.sessions = {}

    def generate(self, prompt: str, session_id: str = "default") -> str:
        if session_id not in self.sessions:
            self.sessions[session_id] = self.model.start_chat()

        response = self.sessions[session_id].send_message(prompt)
        return response.text

    def generate_stream(self, prompt: str, session_id: str = "default") -> Generator[str, None, None]:
        if session_id not in self.sessions:
            self.sessions[session_id] = self.model.start_chat()

        response = self.sessions[session_id].send_message(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    def clear_session(self, session_id: str = "default"):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def clear_all_sessions(self):
        self.sessions.clear()

    def get_session_history(self, session_id: str = "default") -> list:
        if session_id in self.sessions:
            return self.sessions[session_id].history
        return []
```

## Prompt Templates

```python
# backend/app/services/prompts.py
from typing import List, Dict, Optional

class PromptTemplates:
    @staticmethod
    def get_qa_prompt(question: str, docs: List[Dict], mode: str = "quick", history: Optional[list] = None) -> str:
        context = "\n\n".join([
            f"[来源: {d['metadata'].get('source', 'unknown')}]\n{d['text']}"
            for d in docs
        ])

        mode_instructions = {
            "quick": "简洁回答，突出重点",
            "deep": "详细解释，提供深入分析",
            "exam": "适合考试复习，强调公式和概念"
        }

        instruction = mode_instructions.get(mode, "简洁回答")

        return f"""你是一个专业的研究助手。基于以下参考资料回答问题。

参考资料：
{context}

问题：{question}

要求：
- {instruction}
- 答案必须基于参考资料
- 在重要概念后标注来源
- 如果参考资料不足以回答问题，明确说明"""
```

## FastAPI Main App Template

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="RAG API",
    description="Retrieval-Augmented Generation API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port, reload=settings.debug)
```

## Data Models Template

```python
# backend/app/models/__init__.py
from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    question: str
    mode: str = "quick"
    top_k: int = 5
    history: Optional[List[dict]] = None
    session_id: str = "default"

class Source(BaseModel):
    source: str
    chapter: str = ""
    relevance: float = 0.0

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    mode: str
```
