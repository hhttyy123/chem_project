# Backend 目录结构设计

**版本**: v1.0
**日期**: 2026-01-31
**项目**: ChemTutor - 高中化学教育辅助RAG系统

---

## 目录结构概览

```
backend/
├── main.py                      # FastAPI 入口，启动服务
│
├── api/                         # API 接口层
│   ├── __init__.py
│   ├── chat.py                  # 问答接口
│   ├── molecule.py              # 分子可视化接口
│   ├── reaction.py              # 反应模拟接口
│   └── practice.py              # 练习题接口
│
├── rag/                         # RAG 核心模块
│   ├── __init__.py
│   ├── embeddings.py            # 向量化（BGE-M3）
│   ├── vector_store.py          # 向量数据库（Chroma）
│   ├── retriever.py             # 检索器
│   ├── reranker.py              # 重排序（BGE-Reranker）
│   ├── generator.py             # LLM 生成
│   └── prompts.py               # Prompt 模板
│
├── knowledge_graph/             # 知识图谱
│   ├── __init__.py
│   ├── schema.py                # 图谱结构设计
│   ├── builder.py               # 图谱构建
│   └── query.py                 # 图谱查询（Neo4j）
│
├── data/                        # 数据目录
│   ├── raw/                     # 原始数据（手动放入PDF）
│   │   ├── textbooks/           # 教材PDF
│   │   └── experiments/         # 实验手册PDF
│   │
│   ├── collected/               # 采集后的结构化数据
│   │   ├── textbooks/           # 教材解析结果（JSON）
│   │   ├── molecules/           # 分子数据（JSON + SDF）
│   │   ├── reactions/           # 反应数据（JSON）
│   │   ├── knowledge/           # 知识点树（JSON）
│   │   └── questions/           # 题库（JSON）
│   │
│   └── processed/               # 预处理后（分块、向量化）
│       ├── chunks/              # 文档块（JSON）
│       └── embeddings/          # 向量数据
│
├── scripts/                     # 数据采集与处理脚本
│   ├── collect_molecules.py     # 采集分子数据（PubChem API）
│   ├── collect_reactions.py     # 采集反应数据
│   ├── process_textbook.py      # 处理教材PDF
│   ├── build_knowledge_graph.py # 构建知识图谱
│   └── ingest_data.py           # 数据入库（向量化+存储）
│
├── models/                      # 数据模型
│   ├── __init__.py
│   └── schemas.py               # Pydantic 模型定义
│
├── services/                    # 业务服务层
│   ├── __init__.py
│   ├── llm.py                   # LLM 调用（OpenAI/Claude）
│   ├── chemistry_ner.py         # 化学实体识别
│   └── equation_balancer.py     # 方程式配平
│
├── config.py                    # 配置文件
├── requirements.txt             # Python依赖
└── .env                         # 环境变量（API Key等）
```

---

## 各模块说明

### 1. API 接口层 (`api/`)

| 文件 | 职责 | 主要接口 |
|-----|------|---------|
| `chat.py` | 智能问答 | `POST /api/chat`, `POST /api/chat/stream` |
| `molecule.py` | 分子可视化 | `GET /api/molecule/{formula}`, `GET /api/molecule/search` |
| `reaction.py` | 反应模拟 | `GET /api/reaction/{id}`, `POST /api/reaction/generate` |
| `practice.py` | 练习题 | `POST /api/practice/generate`, `POST /api/practice/submit` |

---

### 2. RAG 核心模块 (`rag/`)

| 文件 | 职责 | 说明 |
|-----|------|------|
| `embeddings.py` | 文本向量化 | 使用 BGE-M3 模型生成嵌入向量 |
| `vector_store.py` | 向量数据库 | 封装 ChromaDB 操作 |
| `retriever.py` | 检索器 | 实现混合检索（向量+图谱+关键词） |
| `reranker.py` | 重排序 | 使用 BGE-Reranker 精排结果 |
| `generator.py` | 答案生成 | 调用 LLM 生成最终答案 |
| `prompts.py` | Prompt 模板 | 存储各类 Prompt 模板 |

---

### 3. 知识图谱 (`knowledge_graph/`)

| 文件 | 职责 | 说明 |
|-----|------|------|
| `schema.py` | 图谱结构设计 | 定义节点类型（元素、化合物、反应、概念等） |
| `builder.py` | 图谱构建 | 从数据构建 Neo4j 图谱 |
| `query.py` | 图谱查询 | Cypher 查询封装 |

**图谱节点类型**：
- `(:元素)` - 元素周期表元素
- `(:化合物)` - 化合物（含分子式、SMILES等）
- `(:反应)` - 化学反应
- `(:概念)` - 化学概念
- `(:实验)` - 化学实验

---

### 4. 数据目录 (`data/`)

#### `data/raw/` - 原始数据
需要手动放入的 PDF 文件

#### `data/collected/` - 采集后的数据
结构化 JSON 数据，由 `scripts/` 脚本生成

#### `data/processed/` - 预处理后的数据
分块后的文档块、向量嵌入，用于 RAG 检索

---

### 5. 脚本目录 (`scripts/`)

| 脚本 | 功能 | 输入 | 输出 |
|-----|------|------|------|
| `collect_molecules.py` | 采集分子数据 | 化学式列表 | `data/collected/molecules/` |
| `collect_reactions.py` | 采集反应数据 | 反应描述/方程式 | `data/collected/reactions/` |
| `process_textbook.py` | 解析教材PDF | PDF文件 | `data/collected/textbooks/` |
| `build_knowledge_graph.py` | 构建知识图谱 | 采集的数据 | Neo4j 数据库 |
| `ingest_data.py` | 数据入库 | 所有数据 | 向量数据库 |

---

### 6. 业务服务层 (`services/`)

| 文件 | 职责 | 说明 |
|-----|------|------|
| `llm.py` | LLM 调用 | 统一封装 OpenAI/Claude API |
| `chemistry_ner.py` | 化学实体识别 | 识别化学式、化合物、反应类型 |
| `equation_balancer.py` | 方程式配平 | 自动配平化学方程式 |

---

### 7. 配置文件

#### `config.py`
```python
# 数据库配置
CHROMA_PERSIST_DIR = "data/chroma"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

# 模型配置
EMBEDDING_MODEL = "BAAI/bge-m3"
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"
LLM_MODEL = "gpt-4"  # 或 "claude-3-5-sonnet"

# RAG 参数
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
TOP_K_RETRIEVAL = 5
```

#### `.env`
```
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
NEO4J_PASSWORD=your_password
```

---

## 核心数据流

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户请求                                  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  API 层 (api/chat.py)                                           │
│  • 解析请求                                                      │
│  • 参数验证                                                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  RAG 检索层 (rag/)                                              │
│  • 查询理解 (实体提取、意图识别)                                  │
│  • 混合检索 (向量+图谱+关键词)                                    │
│  • 重排序                                                        │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  生成层 (rag/generator.py)                                      │
│  • Prompt 组装                                                   │
│  • LLM 调用                                                      │
│  • 答案生成                                                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         返回结果                                 │
│  { answer, sources, visualizations, related_questions }         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 依赖关系

```
api/
  ├── services/llm.py
  ├── rag/
  │   ├── retriever.py
  │   │   ├── embeddings.py
  │   │   ├── vector_store.py
  │   │   └── knowledge_graph/query.py
  │   └── generator.py
  └── models/schemas.py

scripts/
  ├── data/ (读写)
  ├── rag/embeddings.py
  └── knowledge_graph/builder.py
```

---

## 开发顺序建议

```
第一阶段：数据采集
  1. 创建目录结构
  2. scripts/collect_molecules.py
  3. scripts/collect_reactions.py
  4. scripts/process_textbook.py

第二阶段：RAG 基础
  5. rag/embeddings.py
  6. rag/vector_store.py
  7. rag/retriever.py
  8. rag/generator.py

第三阶段：API 接口
  9. api/chat.py
  10. main.py (启动服务)

第四阶段：完善功能
  11. knowledge_graph/
  12. rag/reranker.py
  13. api/molecule.py, api/reaction.py
```

---

**文档结束**
