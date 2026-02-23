"""
教材搜索 API
提供教材内容检索接口
"""
from fastapi import APIRouter
from services.rag_service import get_rag_instance

router = APIRouter()


@router.post("/search")
async def search_textbooks(question: str, top_k: int = 5):
    """
    搜索教材内容

    - **question**: 搜索问题
    - **top_k**: 返回结果数量（默认5）
    """
    rag = get_rag_instance()
    results = rag.search(question, top_k=top_k)

    return {
        "question": question,
        "keywords": rag.extract_keywords(question),
        "results": results,
        "total": len(results)
    }
