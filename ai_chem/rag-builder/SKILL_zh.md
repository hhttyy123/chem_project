---
name: rag-builder
description: 构建和配置 RAG（检索增强生成）应用程序。用于设置新的 RAG 项目、配置文档处理、实现检索系统或排查 RAG 流程问题。
argument-hint: [component]
---

# RAG Builder

帮助使用 FastAPI、LangChain、ChromaDB 和针对中文内容优化的 BGE 嵌入来构建、配置和排查 RAG 应用程序。

## 架构概览

典型的 RAG 流程包括：
1. **文档加载** - 通过 `MarkdownLoader` 加载 Markdown/文本文件
2. **分块** - 使用可配置的 `chunk_size` 和 `chunk_overlap` 的 `TextSplitter`
3. **嵌入** - BGE-base-zh 用于中文文本嵌入
4. **存储** - ChromaDB 用于向量存储
5. **检索** - 混合模式：向量（密集）+ BM25（稀疏）+ 重排序
6. **生成** - LLM（智谱 AI GLM-4 或 Google Gemini）

## 项目结构

```
rag/
├── backend/
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── core/        # 配置 (config.py)
│   │   ├── models/      # Pydantic 模型
│   │   ├── services/    # 业务逻辑
│   │   └── main.py      # FastAPI 应用
│   ├── data/
│   │   ├── raw/         # 源文档
│   │   ├── processed/   # chunks.json
│   │   └── vector_db/   # ChromaDB
│   ├── scripts/         # 处理脚本
│   ├── requirements.txt
│   ├── .env             # API 密钥
│   └── start.py
└── frontend/            # 可选的 React 前端
```

## 设置步骤

### 1. 初始化后端

创建 `backend/requirements.txt`：

```txt
# Web 框架
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# RAG 框架
langchain==0.1.0
langchain-community==0.0.10
langchain-openai==0.0.2

# 向量数据库
chromadb==0.4.22

# 文档处理
pypdf==3.17.4
pdfplumber==0.10.3
unstructured==0.11.6

# 嵌入
sentence-transformers==2.3.1

# 检索
rank-bm25==0.2.2

# LLM（选择一个或两个）
zhipuai==2.1.5.20250825
google-genai==1.9.0

# 工具
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
httpx==0.26.0
jieba==0.42.1
numpy>=1.24.0
torch>=2.0.0
```

### 2. 配置 (`backend/app/core/config.py`)

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
    llm_provider: str = "gemini"  # 或 "zhipuai"

    # 数据路径
    textbook_path: str = "../data/raw"
    processed_path: str = "../data/processed"
    vector_db_path: str = "../data/vector_db/chroma"

    # 分块
    chunk_size: int = 500
    chunk_overlap: int = 50

    # 检索
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

### 3. 核心服务

在 `backend/app/services/` 中创建这些服务：

**document_loader.py** - 加载 markdown/文本文件
**text_splitter.py** - 带重叠的分块文档
**embedding.py** - BGE 中文嵌入
**vector_store.py** - ChromaDB 操作
**retriever.py** - 混合检索（向量 + BM25）
**reranker.py** - BGE 重排序
**llm.py** - 带会话管理的 LLM 服务
**prompts.py** - 问答提示模板
**rag.py** - 主编排逻辑

### 4. API 路由

创建 `backend/app/api/chat.py`：

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

### 5. 环境变量

创建 `backend/.env`：

```env
# LLM API 密钥（选择一个）
ZHIPUAI_API_KEY=your_zhipuai_key
GEMINI_API_KEY=your_gemini_key
LLM_PROVIDER=gemini

# 可选覆盖
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K=5
USE_RERANKER=true
```

## 常用命令

```bash
# 安装依赖
cd backend
pip install -r requirements.txt

# 处理文档
python scripts/process_textbooks.py

# 向量化文档
python scripts/vectorize_textbooks.py

# 启动服务器
python start.py

# 运行测试
python tests/test_api.py
```

## 故障排除

### 嵌入模型未找到
- 模型会自动下载到 `models--BAAI--bge-base-zh-v1.5/`
- 检查首次运行时的网络连接

### ChromaDB 错误
- 删除 `data/vector_db/chroma/` 并重新运行 `vectorize_textbooks.py`

### 检索结果为空
- 检查 `chunk_size` - 太小可能会丢失上下文
- 验证文档已处理（检查 `data/processed/chunks.json`）
- 尝试增加 `top_k`

### 答案质量差
- 启用重排序：`USE_RERANKER=true`
- 尝试不同模式：`quick`、`deep`、`exam`
- 检查 LLM API 密钥是否有效

### 内存问题
- 减少 `chunk_size` 或 `top_k`
- 如不需要则禁用重排序
- 使用更小的嵌入模型

## 多轮对话

RAG 服务使用 Gemini 聊天会话来维护对话历史：
- 每个 `session_id` 维护自己的上下文
- 历史用于增强检索查询，但不用于 LLM 提示
- 清除会话：`rag_service.clear_session(session_id)`

## 支持文件

- **[templates.md](templates.md)** - 所有 RAG 服务的完整代码模板（document_loader、text_splitter、embedding、vector_store、retriever、reranker、llm、prompts、主应用和数据模型）
- **[examples.md](examples.md)** - 使用示例和常见场景（初始化项目、创建脚本、故障排除、添加功能、部署检查清单）
- **[reference.md](reference.md)** - 快速参考指南，包含环境变量、API 端点、错误解决方案和常用命令

## 外部资源

- ChromaDB 文档：https://docs.trychroma.com/
- LangChain 文档：https://python.langchain.com/
- BGE 嵌入：https://huggingface.co/BAAI/bge-base-zh-v1.5
