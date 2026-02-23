# RAG Builder 使用示例

## 示例 1：初始化新的 RAG 项目

**用户输入：** `/rag-builder init`

**结果：** 创建包含所有必要文件的基础项目结构。

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
└── frontend/ (可选)
```

## 示例 2：创建文档处理脚本

**用户输入：** `/rag-builder script process`

**结果：** 创建 `backend/scripts/process_textbooks.py`

```python
#!/usr/bin/env python
"""处理 RAG 流程的文档"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.pipeline import DocumentPipeline
from app.core.config import get_settings

def main():
    settings = get_settings()
    pipeline = DocumentPipeline()

    print("正在处理文档...")
    chunks = pipeline.process_all()

    print(f"已生成 {len(chunks)} 个分块")
    print(f"已保存到 {settings.processed_path}/chunks.json")

if __name__ == "__main__":
    main()
```

## 示例 3：创建向量化脚本

**用户输入：** `/rag-builder script vectorize`

**结果：** 创建 `backend/scripts/vectorize_textbooks.py`

```python
#!/usr/bin/env python
"""向量化文档并存储到 ChromaDB"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.pipeline import DocumentPipeline
from app.services.embedding import EmbeddingService
from app.services.vector_store import VectorStore
from app.core.config import get_settings

def main():
    settings = get_settings()

    # 加载分块
    pipeline = DocumentPipeline()
    chunks = pipeline.load_processed_chunks()

    if not chunks:
        print("未找到分块。请先运行 process_textbooks.py。")
        return

    # 生成嵌入
    print(f"正在为 {len(chunks)} 个分块生成嵌入...")
    embedding_service = EmbeddingService()
    embeddings = embedding_service.embed_texts([c["text"] for c in chunks])

    # 存储到向量数据库
    print("正在存储到 ChromaDB...")
    vector_store = VectorStore(settings.vector_db_path)
    vector_store.add_documents(chunks, embeddings)

    print(f"完成！已存储 {len(chunks)} 个文档到 {settings.vector_db_path}")

if __name__ == "__main__":
    main()
```

## 示例 4：排查空检索结果

**用户输入：** "我的 RAG 系统查询时没有返回结果"

**结果：** Claude 运行诊断检查清单：

1. 检查文档是否已处理：
   ```bash
   ls backend/data/processed/chunks.json
   ```

2. 检查向量数据库是否存在：
   ```bash
   ls backend/data/vector_db/chroma/
   ```

3. 测试嵌入服务：
   ```python
   from app.services.embedding import EmbeddingService
   emb = EmbeddingService()
   print(emb.embed_query("test"))  # 应返回浮点数列表
   ```

4. 检查 chunk_size 配置 - 可能太小

5. 如果使用混合检索，验证 BM25 索引是否已构建

## 示例 5：添加流式输出支持

**用户输入：** `/rag-builder add streaming`

**结果：** 向 `app/api/chat.py` 添加流式端点：

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

## 示例 6：针对中文语言优化

**用户输入：** "优化我的 RAG 系统处理中文文档"

**结果：** 配置建议：

```python
# config.py
chunk_size = 400  # 中文需要更小的分块
chunk_overlap = 80  # 更多重叠以保留上下文
separator = ["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
```

```python
# embedding.py - 使用 BGE 中文模型
model_name = "BAAI/bge-base-zh-v1.5"
```

```python
# retriever.py - 使用 jieba 进行 BM25
from jieba import lcut
tokenized_corpus = [lcut(doc["text"]) for doc in chunks]
```

## 示例 7：切换 LLM 提供商

**用户输入：** "从智谱 AI 切换到 Gemini"

**结果：** 更新 `.env` 并可能修改 `llm.py`：

```env
# .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_key
# ZHIPUAI_API_KEY=  # 可以保留作为备用
```

`llm.py` 服务应该已经通过 `LLM_PROVIDER` 配置支持两个提供商。

## 示例 8：添加文档来源跟踪

**用户输入：** "跟踪每个答案来自哪个章节"

**结果：** 确保保留元数据：

```python
# 在 document_loader.py 中
documents.append({
    "content": content,
    "metadata": {
        "source": md_file.stem,
        "chapter": extract_chapter_name(md_file),  # 从文件名解析
        "path": str(md_file)
    }
})

# 在 rag.py 中 - 响应包含来源
sources = [
    {
        "source": doc["metadata"]["source"],
        "chapter": doc["metadata"].get("chapter", "未知"),
        "relevance": doc.get("score", 0)
    }
    for doc in docs[:top_k]
]
```

## 示例 9：创建测试脚本

**用户输入：** `/rag-builder test`

**结果：** 创建 `backend/tests/test_rag.py`：

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

运行测试：`pytest backend/tests/`

## 示例 10：部署检查清单

**用户输入：** "生产部署检查清单"

**结果：**

- [ ] 在配置中设置 `debug=False`
- [ ] 所有密钥使用环境变量
- [ ] 在生产服务器上构建向量数据库
- [ ] 为特定域名设置 CORS
- [ ] 添加速率限制
- [ ] 配置适当的日志记录
- [ ] 设置 API 健康监控
- [ ] 使用生产数据量测试
- [ ] 记录 API 端点文档
- [ ] 设置向量数据库备份
