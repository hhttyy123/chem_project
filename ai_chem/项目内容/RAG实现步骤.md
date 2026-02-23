# ChemTutor RAG系统实现步骤

## 项目概述

本文档详细描述了ChemTutor高中化学教育辅助平台的RAG（检索增强生成）系统实现步骤。RAG系统将作为平台的核心能力，为智能问答、化学可视化、反应模拟等功能提供知识支撑。

---

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户交互层                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ 智能问答  │  │分子可视化 │  │反应模拟  │  │虚拟实验  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                       RAG核心服务层                               │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Query理解模块                            │  │
│  │  • 化学术语识别  • 意图分类  • 实体提取  • 问题改写         │  │
│  └────────────────────┬──────────────────────────────────────┘  │
│                       │                                          │
│  ┌────────────────────▼──────────────────────────────────────┐  │
│  │                    混合检索模块                             │  │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐              │  │
│  │  │语义检索   │  │图谱检索   │  │关键词检索  │              │  │
│  │  │(向量DB)   │  │(Neo4j)    │  │(BM25)     │              │  │
│  │  └───────────┘  └───────────┘  └───────────┘              │  │
│  └────────────────────┬──────────────────────────────────────┘  │
│                       │                                          │
│  ┌────────────────────▼──────────────────────────────────────┐  │
│  │                    重排序模块                               │  │
│  │  • BGE-Reranker  • 化学专业相关性加权  • 结果融合          │  │
│  └────────────────────┬──────────────────────────────────────┘  │
│                       │                                          │
│  ┌────────────────────▼──────────────────────────────────────┐  │
│  │                    生成模块                                 │  │
│  │  • Prompt组装  • 上下文注入  • LLM调用  • 答案生成         │  │
│  └───────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                        数据存储层                                 │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐    │
│  │向量数据库  │  │知识图谱   │  │文档存储   │  │缓存层     │    │
│  │(Chroma)   │  │(Neo4j)    │  │(MinIO/S3) │  │(Redis)    │    │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 技术栈选型

| 层级 | 组件 | 推荐技术 | 备选方案 |
|-----|------|---------|---------|
| **嵌入模型** | 文本向量化 | BGE-M3 (多语言) | text-embedding-3-large |
| **向量数据库** | 向量存储 | Chroma | Milvus, Weaviate |
| **图数据库** | 知识图谱 | Neo4j | ArangoDB |
| **重排序** | 结果精排 | BGE-Reranker-v2 | Cohere Rerank |
| **LLM** | 答案生成 | Claude 3.5 Sonnet | GPT-4o |
| **文档解析** | 数据提取 | Unstructured | LangChain Loader |
| **API框架** | 后端服务 | FastAPI | Flask |
| **缓存** | 性能优化 | Redis | Memcached |

---

## 数据准备阶段

### 1. 数据源规划

| 数据类型 | 来源 | 格式 | 预估规模 | 优先级 |
|---------|------|------|---------|--------|
| 化学教材 | 人教版高中化学必修1-3、选修1-6 | PDF | ~2000页 | P0 |
| 化学方程式 | 高中核心方程式数据库 | JSON/CSV | ~500条 | P0 |
| 分子结构 | PubChem API | JSON (SMILES) | ~200个 | P1 |
| 知识点梳理 | 教师整理的知识点列表 | Markdown | ~300条 | P0 |
| 实验手册 | 高中化学实验指导书 | PDF | ~50个实验 | P2 |
| 题库 | 历年高考题 + 模拟题 | JSON | ~1000题 | P1 |

### 2. 数据收集清单

#### 2.1 教材数据收集
- [ ] 人教版高中化学 必修1
- [ ] 人教版高中化学 必修2
- [ ] 人教版高中化学 选择性必修1（化学反应原理）
- [ ] 人教版高中化学 选择性必修2（物质结构与性质）
- [ ] 人教版高中化学 选择性必修3（有机化学基础）

#### 2.2 化学方程式数据
- [ ] 氧化还原反应（~50条）
- [ ] 离子反应（~50条）
- [ ] 化学平衡反应（~30条）
- [ ] 电化学反应（~30条）
- [ ] 有机化学反应（~100条）
- [ ] 元素化合物反应（~240条）

#### 2.3 分子结构数据
- [ ] 无机分子（H2O, CO2, NH3, HCl, ~50个）
- [ ] 简单有机物（CH4, C2H6, C2H4, C2H2, ~50个）
- [ ] 官能团代表物（醇、醛、酸、酯, ~50个）
- [ ] 复杂有机物（葡萄糖、苯、萘, ~50个）

### 3. 数据处理流程

```
原始数据 → 数据清洗 → 文档分块 → 元数据标注 → 向量化 → 存储
   │           │          │           │           │         │
   │           │          │           │           │         ▼
   │           │          │           │           └────→ 向量数据库
   │           │          │           │
   │           │          │           └────────────────→ 知识图谱
   │           │          │
   ▼           ▼          ▼
 格式统一    去噪处理    Chunk处理
              重复去除    Chunk_size=400
                         (中文优化)
```

#### 3.1 文档分块策略

| 文档类型 | 分块策略 | Chunk大小 | Overlap |
|---------|---------|----------|---------|
| 教材章节 | 按知识点分块 | 400-500 tokens | 50 tokens |
| 方程式 | 单条方程式为一块 | N/A | N/A |
| 分子说明 | 单分子为一块 | N/A | N/A |
| 题目 | 单题为一块 | N/A | N/A |

#### 3.2 元数据设计

```json
{
  "chunk_id": "chem_textbook_1_2_3",
  "source": "人教版高中化学必修1",
  "chapter": "第二章 化学物质及其变化",
  "section": "第三节 氧化还原反应",
  "knowledge_point": ["氧化还原反应", "氧化剂", "还原剂"],
  "difficulty": "基础",
  "related_chemicals": ["Fe", "CuSO4", "FeSO4", "Cu"],
  "related_equations": ["eq_oxidation_001"],
  "grade": "高一",
  "tags": ["概念", "反应类型"]
}
```

---

## 分阶段实施步骤

### Phase 1: 基础架构搭建 (Week 1-2)

#### 目标
搭建RAG系统基础框架，实现最基础的文档检索和问答功能。

#### 任务清单

**Week 1: 环境搭建与数据准备**
- [x] Day 1-2: 开发环境配置
  - [x] Python 3.10+ 安装
  - [x] 虚拟环境创建 (venv) - ✅ 已完成
  - [x] 依赖包安装
  ```bash
  # 激活虚拟环境 (Windows)
  venv\Scripts\activate

  # 安装依赖
  pip install -r requirements.txt
  ```
- [ ] Day 3-4: 数据收集与预处理
  - [ ] 收集必修1教材PDF
  - [ ] 提取文本内容 (unstructured库)
  - [ ] 清洗和格式化文本
- [ ] Day 5: 初步分块与向量化
  - [ ] 实现文档分块逻辑
  - [ ] 使用BGE-M3生成嵌入
  - [ ] 测试向量质量

**Week 2: 基础检索与问答**
- [ ] Day 1-2: 向量数据库搭建
  - [ ] Chroma实例配置
  - [ ] Collection创建
  - [ ] 数据写入与索引
- [ ] Day 3-4: 基础检索实现
  - [ ] 语义检索接口
  - [ ] 结果排序与Top-K
  - [ ] 上下文组装
- [ ] Day 5: LLM问答集成
  - [ ] Prompt模板设计
  - [ ] OpenAI/Claude API调用
  - [ ] 答案生成与返回

#### 验收标准
- [ ] 能对基础化学概念问题给出准确回答
- [ ] 检索延迟 < 2秒
- [ ] 支持至少100个知识点的检索

#### 交付物
- [ ] `backend/rag/` 目录结构
  - [ ] `embeddings.py` - 嵌入模型
  - [ ] `vector_store.py` - 向量数据库
  - [ ] `retriever.py` - 检索器
  - [ ] `generator.py` - 生成器
- [ ] 数据处理脚本 `scripts/process_textbook.py`
- [ ] API文档 `docs/api.md`

---

### Phase 2: 知识图谱构建 (Week 3-4)

#### 目标
构建化学知识图谱，实现关系检索和知识推理能力。

#### 任务清单

**Week 3: 图谱设计**
- [ ] Day 1-2: Schema设计
  ```cypher
  // 节点类型
  (:化合物)
  (:元素)
  (:反应)
  (:概念)
  (:实验)
  (:题库)

  // 关系类型
  (:化合物)-[:由元素组成]->(:元素)
  (:化合物)-[:反应生成]->(:化合物)
  (:反应)-[:属于]->(:概念)
  (:概念)-[:前置知识]->(:概念)
  ```
- [ ] Day 3-4: 实体提取
  - [ ] 化学式识别 (正则 + 规则)
  - [ ] 反应类型分类
  - [ ] 概念层次结构
- [ ] Day 5: 数据导入脚本
  - [ ] CSV/JSON → Cypher
  - [ ] 批量导入工具

**Week 4: 图谱检索集成**
- [ ] Day 1-2: Neo4j部署与配置
  - [ ] Docker部署
  - [ ] Python驱动安装
  - [ ] 连接池配置
- [ ] Day 3-4: 图谱检索实现
  - [ ] 实体查询接口
  - [ ] 关系路径查询
  - [ ] 子图提取
- [ ] Day 5: 混合检索集成
  - [ ] 向量检索 + 图谱检索
  - [ ] 结果融合策略

#### 验收标准
- [ ] 知识图谱包含 > 500 个节点
- [ ] 能回答关系型问题（如"铁的氧化物有哪些"）
- [ ] 图谱查询 < 500ms

#### 交付物
- [ ] `backend/knowledge_graph/` 目录
  - [ ] `schema.py` - 图谱Schema
  - [ ] `builder.py` - 图谱构建
  - [ ] `query.py` - 图谱查询
- [ ] Cypher脚本文件 `cypher/`
- [ ] 图谱可视化 (可选)

---

### Phase 3: 化学特色功能 (Week 5-6)

#### 目标
实现分子3D可视化和反应模拟功能。

#### 任务清单

**Week 5: 分子可视化**
- [ ] Day 1-2: PubChem集成
  - [ ] API对接
  - [ ] 分子数据获取 (SMILES, 3D坐标)
  - [ ] 本地缓存构建
- [ ] Day 3-4: 3D渲染
  - [ ] 3Dmol.js集成
  - [ ] 前端组件开发
  - [ ] 交互控制 (旋转、缩放、样式)
- [ ] Day 5: RAG联动
  - [ ] 问题 → 识别分子 → 调用可视化
  - [ ] 多分子对比展示

**Week 6: 反应模拟**
- [ ] Day 1-2: 反应数据库
  - [ ] 方程式结构化存储
  - [ ] 反应条件 (温度、催化剂)
  - [ ] 反应步骤拆解
- [ ] Day 3-4: 动画生成
  - [ ] 反应过程可视化
  - [ ] 粒子动画效果
  - [ ] 参数调节控制
- [ ] Day 5: 集成测试

#### 验收标准
- [ ] 支持 > 100 个分子的3D展示
- [ ] 支持 > 50 个反应的动态模拟
- [ ] 可视化加载 < 3秒

#### 交付物
- [ ] `backend/molecule/` 目录
  - [ ] `pubchem_client.py` - PubChem API
  - [ ] `molecule_service.py` - 分子服务
- [ ] `backend/reaction/` 目录
  - [ ] `reaction_db.py` - 反应数据库
  - [ ] `animation.py` - 动画生成
- [ ] 前端可视化组件 `frontend/components/`

---

### Phase 4: 优化与增强 (Week 7-8)

#### 目标
提升检索精度和用户体验。

#### 任务清单

**Week 7: 检索优化**
- [ ] Day 1-2: 重排序模型
  - [ ] BGE-Reranker集成
  - [ ] 训练数据准备 (可选)
  - [ ] 微调与评估
- [ ] Day 3-4: 查询优化
  - [ ] 查询改写 (Query Rewriting)
  - [ ] 查询扩展 (同义词、相关概念)
  - [ ] 多轮对话上下文
- [ ] Day 5: 缓存策略
  - [ ] Redis配置
  - [ ] 查询结果缓存
  - [ ] 缓存失效策略

**Week 8: 用户体验**
- [ ] Day 1-2: 追问功能
  - [ ] 上下文管理
  - [ ] 问题推荐
  - [ ] 知识点关联
- [ ] Day 3-4: 准确性保障
  - [ ] 答案验证机制
  - [ ] 不确定性标注
  - [ ] 专家审核流程
- [ ] Day 5: 性能优化
  - [ ] 并发处理
  - [ ] 响应时间优化
  - [ ] 监控指标

#### 验收标准
- [ ] 检索准确率 > 85%
- [ ] 端到端响应 < 5秒
- [ ] 用户满意度 > 80%

#### 交付物
- [ ] `backend/rag/advanced/` 目录
  - [ ] `reranker.py` - 重排序
  - [ ] `query_optimization.py` - 查询优化
  - [ ] `cache_manager.py` - 缓存管理
- [ ] 性能测试报告
- [ ] 优化文档

---

## 数据结构设计

### 1. 向量数据库Schema

```python
# Chroma Collection Schema
collection = {
    "name": "chemistry_knowledge",
    "metadata": {
        "hnsw:space": "cosine",
        "hnsw:construction_ef": 200,
        "hnsw:M": 16
    },
    "documents": [
        {
            "id": "doc_001",
            "text": "氧化还原反应是化学反应的一种类型...",
            "metadata": {
                "source": "人教版必修1",
                "chapter": "第二章",
                "section": "第三节",
                "knowledge_points": ["氧化还原反应"],
                "difficulty": "基础",
                "chemicals": ["Fe", "CuSO4"],
                "equations": ["eq_001"]
            },
            "embedding": [0.1, 0.2, ...]  # 1024维向量
        }
    ]
}
```

### 2. 知识图谱Schema

```cypher
// 创建约束
CREATE CONSTRAINT chem_name IF NOT EXISTS FOR (c:化合物) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT element_symbol IF NOT EXISTS FOR (e:元素) REQUIRE e.symbol IS UNIQUE;

// 化合物节点
CREATE (:化合物 {
    name: "硫酸",
    formula: "H2SO4",
    smiles: "O=S(=O)(O)O",
    type: "酸",
    cas: "7664-93-9",
    pubchem_id: "1118"
});

// 元素节点
CREATE (:元素 {
    symbol: "H",
    name: "氢",
    atomic_number: 1,
    period: 1,
    group: 1
});

// 反应节点
CREATE (:反应 {
    id: "eq_001",
    equation: "Fe + CuSO4 → FeSO4 + Cu",
    type: "置换反应",
    reaction_type: "氧化还原反应"
});

// 关系
MATCH (a:化合物 {name: "硫酸"}), (b:元素 {symbol: "H"})
CREATE (a)-[:包含元素 {count: 2}]->(b);
```

### 3. API数据结构

```python
# 请求
class QueryRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None
    user_id: str
    options: Optional[dict] = {
        "include_visualization": False,
        "top_k": 5,
        "temperature": 0.7
    }

# 响应
class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]
    visualizations: List[Visualization]
    related_questions: List[str]
    confidence: float
    usage: TokenUsage
```

---

## 关键实现细节

### 1. 化学术语识别

```python
import re

# 化学式正则
CHEMICAL_FORMULA_PATTERN = r'''
    (?:
        [A-Z][a-z]?\d*  # 元素符号
        (?:\([^)]+\)\d*)?  # 括号分组
        [+\-]?\d*  # 电荷
    )+
'''

# 提取问题中的化学实体
def extract_chemical_entities(question: str) -> List[str]:
    formulas = re.findall(CHEMICAL_FORMULA_PATTERN, question)
    keywords = extract_chemical_keywords(question)
    return formulas + keywords
```

### 2. Prompt模板设计

```python
CHEMISTRY_QA_PROMPT = """
你是一个专业的高中化学助教。请根据以下上下文回答学生的问题。

上下文信息：
{context}

学生问题：{question}

要求：
1. 答案要准确、清晰，适合高中生理解
2. 如涉及化学概念，先解释概念
3. 如涉及反应，说明反应类型和条件
4. 必要时举例说明
5. 如果需要可视化，在答案末尾标注 [VISUALIZE:分子/反应]

回答：
"""
```

### 3. 混合检索融合

```python
def hybrid_search(query: str, top_k: int = 5):
    # 并行执行
    vector_results = vector_store.similarity_search(query, k=top_k*2)
    graph_results = graph_store.entity_search(query, k=top_k*2)
    keyword_results = keyword_store.search(query, k=top_k*2)

    # 重排序
    all_results = vector_results + graph_results + keyword_results
    reranked = reranker.rank(query, all_results)

    # 去重
    unique_results = deduplicate(reranked)

    return unique_results[:top_k]
```

---

## 测试与验证

### 1. 功能测试

| 测试项 | 测试用例 | 预期结果 |
|-------|---------|---------|
| 基础问答 | "什么是氧化还原反应？" | 准确解释概念 |
| 方程式查询 | "铁和硫酸铜反应方程式" | Fe + CuSO4 → FeSO4 + Cu |
| 分子查询 | "水的分子结构" | 展示H2O 3D模型 |
| 关系查询 | "哪些物质可以和酸反应？" | 列举相关物质 |
| 追问 | "为什么铁会生锈？" → "如何防止生锈？" | 保持上下文 |

### 2. 性能指标

| 指标 | 目标值 |
|-----|--------|
| 检索延迟 | < 2秒 |
| 生成延迟 | < 3秒 |
| 总响应时间 | < 5秒 |
| 并发支持 | > 100 QPS |
| 准确率 | > 85% |

### 3. 准确性验证

- [ ] 化学专家抽查 100 个问题
- [ ] 与标准答案对比
- [ ] 收集用户反馈
- [ ] 持续迭代优化

---

## 风险与应对

| 风险 | 影响 | 应对措施 |
|-----|------|---------|
| 化学知识幻觉 | 高 | 知识图谱约束 + 专家审核 |
| 数据版权问题 | 中 | 使用公开教材/自建数据 |
| 性能瓶颈 | 中 | 缓存 + 异步处理 |
| 3D渲染性能 | 低 | 懒加载 + CDN |
| API成本 | 中 | 缓存策略 + 批处理 |

---

## 附录

### A. 依赖清单

```
# requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
chromadb==0.4.22
neo4j==5.15.0
redis==5.0.1
langchain==0.1.0
langchain-community==0.0.10
openai==1.10.0
anthropic==0.18.0
sentence-transformers==2.3.1
unstructured==0.11.6
python-multipart==0.0.6
pydantic==2.5.3
pydantic-settings==2.1.0
```

### B. 目录结构

```
backend/
├── rag/
│   ├── __init__.py
│   ├── embeddings.py          # 嵌入模型
│   ├── vector_store.py        # 向量数据库
│   ├── retriever.py           # 检索器
│   ├── generator.py           # 生成器
│   ├── reranker.py            # 重排序
│   └── prompts.py             # Prompt模板
├── knowledge_graph/
│   ├── __init__.py
│   ├── schema.py              # 图谱Schema
│   ├── builder.py             # 图谱构建
│   └── query.py               # 图谱查询
├── molecule/
│   ├── __init__.py
│   ├── pubchem_client.py      # PubChem API
│   └── molecule_service.py    # 分子服务
├── reaction/
│   ├── __init__.py
│   ├── reaction_db.py         # 反应数据库
│   └── animation.py           # 动画生成
├── api/
│   ├── __init__.py
│   └── routes.py              # API路由
├── models/
│   ├── __init__.py
│   └── schemas.py             # 数据模型
├── scripts/                   # 脚本
│   ├── process_textbook.py
│   ├── build_graph.py
│   └── ingest_data.py
└── main.py                    # 应用入口
```

### C. 参考资源

- [LangChain RAG教程](https://python.langchain.com/docs/tutorials/rag/)
- [Chroma文档](https://docs.trychroma.com/)
- [Neo4j图数据库](https://neo4j.com/docs/)
- [PubChem API](https://pubchemdocs.ncbi.nlm.nih.gov/)
- [3Dmol.js](https://3dmol.csb.pitt.edu/)

---

**文档版本**: v1.0
**创建日期**: 2026-01-31
**最后更新**: 2026-01-31
