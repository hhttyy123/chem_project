# ChemTutor - 高中化学RAG问答系统

基于教材的检索增强生成(RAG)化学学习助手。

## 快速开始

### 1. 启动后端

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

后端将运行在 `http://localhost:8000`

API文档: `http://localhost:8000/docs`

### 2. 启动前端

```bash
# 进入前端目录
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

前端将运行在 `http://localhost:5173`

## 功能特性

- ✅ 基于教材的智能问答
- ✅ 关键词检索 + 相关度排序
- ✅ 来源信息展示
- ✅ GLM-4 AI增强

## 项目结构

```
ai_chem/
├── backend/
│   ├── main.py              # FastAPI主服务
│   ├── api/
│   │   └── rag.py          # RAG API路由
│   ├── services/
│   │   └── rag_service.py  # RAG检索服务
│   ├── data/
│   │   └── collected/textbok/  # 教材数据
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── views/Home.vue  # 主问答界面
    │   └── api/rag.ts      # RAG API客户端
    └── package.json
```

## API 接口

### POST /api/rag-chat
RAG增强聊天接口

**请求体:**
```json
{
  "question": "什么是化学键？",
  "history": [],
  "use_rag": true
}
```

**响应:**
```json
{
  "answer": "化学键是...",
  "sources": [
    {"section": "专题1", "source": "cleaned_chem.json", "score": 5.5}
  ],
  "rag_used": true,
  "keywords": ["化学键", "键"]
}
```

### GET /api/search
搜索教材内容

### GET /api/rag/status
获取RAG服务状态

## 下一步计划

- [ ] 集成向量数据库（ChromaDB）
- [ ] 添加3D分子可视化
- [ ] 实现知识图谱
- [ ] 添加用户收藏功能
