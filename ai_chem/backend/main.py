"""
ChemTutor Backend API
FastAPI 主服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入路由
from api import rag

app = FastAPI(
    title="ChemTutor API",
    description="高中化学AI助教后端服务",
    version="1.0.0"
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite开发服务器
        "http://localhost:3000",  # 其他可能的端口
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(rag.router, prefix="/api", tags=["RAG"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "ChemTutor API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    # 运行服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式自动重载
        log_level="info"
    )
