# RAG 快速参考

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ZHIPUAI_API_KEY` | - | 智谱 AI GLM-4 API 密钥 |
| `GEMINI_API_KEY` | - | Google Gemini API 密钥 |
| `LLM_PROVIDER` | `gemini` | LLM 提供商 (gemini/zhipuai) |
| `CHUNK_SIZE` | `500` | 文本分块大小（字符数） |
| `CHUNK_OVERLAP` | `50` | 分块之间的重叠 |
| `TOP_K` | `5` | 检索文档数量 |
| `USE_RERANKER` | `true` | 启用 BGE 重排序 |

## RAG 模式

| 模式 | 说明 | 使用场景 |
|------|------|----------|
| `quick` | 简洁回答 | 快速查询 |
| `deep` | 详细解释 | 学习新主题 |
| `exam` | 考试复习 | 考试准备 |

## 关键文件位置

```
backend/
├── app/core/config.py          # 配置
├── app/services/               # 业务逻辑
├── data/processed/chunks.json  # 处理后的分块
├── data/vector_db/chroma/      # ChromaDB 存储
└── .env                        # 环境变量
```

## 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `Model not found` | 嵌入模型未下载 | 检查网络，重新运行 |
| `No results found` | 向量数据库为空 | 运行 `vectorize_textbooks.py` |
| `API key invalid` | LLM API 密钥错误 | 检查 `.env` 文件 |
| `Out of memory` | 分块过多 | 减少 `chunk_size` 或 `top_k` |
| `CORS error` | 前端无法访问 API | 更新 `main.py` 中的 CORS 源 |

## 模型信息

| 组件 | 模型 | 用途 |
|------|------|------|
| 嵌入 | BAAI/bge-base-zh-v1.5 | 中文文本嵌入 |
| 重排序 | BAAI/bge-reranker-base | 结果重排序 |
| LLM | gemini-1.5-flash | 答案生成 |
| LLM | GLM-4 | 备用 LLM（智谱 AI） |

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/chat/` | POST | 问答 |
| `/api/chat/stream` | POST | 流式响应 |
| `/api/textbook/info` | GET | 文档元数据 |
| `/api/textbook/chapters` | GET | 章节列表 |
| `/docs` | GET | Swagger API 文档 |
| `/health` | GET | 健康检查 |

## ChromaDB 命令

```python
# 连接到现有数据库
client = chromadb.PersistentClient(path="data/vector_db/chroma")
collection = client.get_collection("documents")

# 计算文档数
collection.count()

# 删除并重新创建
client.delete_collection("documents")
collection = client.create_collection("documents")
```

## 测试 RAG 流程

```python
# 测试检索
from app.services.retriever import HybridRetriever
retriever = HybridRetriever()
results = retriever.retrieve("测试查询", top_k=5)

# 测试 LLM
from app.services.llm import LLMService
llm = LLMService()
answer = llm.generate("测试提示")

# 测试完整 RAG
from app.services.rag import RAGService
rag = RAGService()
result = rag.answer("测试问题", mode="quick")
```

## 性能调优

| 目标 | 设置 |
|------|------|
| 更快的检索 | 减少 `top_k`，禁用重排序 |
| 更好的准确性 | 增加 `top_k`，启用重排序 |
| 更少的内存 | 减少 `chunk_size`，使用量化 |
| 中文优化 | 使用 BGE-zh，jieba 分词 |

## 中文文本处理

```python
# 中文推荐分隔符
separators = ["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]

# 使用 jieba 进行 BM25
from jieba import lcut
tokenized = lcut("中文分词测试")
```

## 会话管理

```python
# 清除会话
rag_service.clear_session(session_id)

# 获取历史
history = rag_service.get_session_history(session_id)

# 清除所有
rag_service.clear_all_sessions()
```

## 常用命令

```bash
# 处理文档
python scripts/process_textbooks.py

# 向量化
python scripts/vectorize_textbooks.py

# 启动服务器
python start.py

# 运行测试
pytest backend/tests/

# 检查 ChromaDB
python -c "import chromadb; print(chromadb.PersistentClient('data/vector_db/chroma').get_collection('documents').count())"
```

## 文件依赖

```
SKILL.md (本文件)
├── templates.md     # 所有服务的代码模板
├── examples.md      # 使用示例和场景
└── reference.md     # 本快速参考指南
```
