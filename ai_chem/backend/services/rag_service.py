"""
RAG检索服务 - 快速方案
使用关键词匹配和全文搜索从教材中检索相关内容
"""
import json
import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from jieba import analyse


class TextbookRAG:
    """教材RAG检索器"""

    def __init__(self, data_dir: str = None):
        """
        初始化RAG检索器

        Args:
            data_dir: 教材数据目录，默认为 backend/data/collected/textbok
        """
        if data_dir is None:
            # 默认数据目录
            current_dir = Path(__file__).parent.parent
            data_dir = current_dir / "data" / "collected" / "textbok"

        self.data_dir = Path(data_dir)
        self.chunks = []
        self.index_built = False

        # 初始化时自动加载数据
        self.load_textbooks()

    def load_textbooks(self) -> None:
        """加载所有教材数据并建立索引"""
        try:
            print(f"[RAG] 正在加载教材数据: {self.data_dir}")

            if not self.data_dir.exists():
                print(f"[RAG] 数据目录不存在: {self.data_dir}")
                self.index_built = True
                return

            total_chunks = 0

            # 遍历所有子目录
            for subdir in self.data_dir.iterdir():
                if not subdir.is_dir():
                    continue

                # 查找JSON文件
                json_files = list(subdir.glob("*.json"))

                for json_file in json_files:
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        # 处理不同的数据格式
                        chunks = self._parse_textbook_data(data, json_file.name)
                        self.chunks.extend(chunks)
                        total_chunks += len(chunks)

                        print(f"  [OK] {json_file.name}: {len(chunks)} 个文本块")

                    except Exception as e:
                        print(f"  [ERR] 加载 {json_file.name} 失败: {e}")

            self.index_built = True
            print(f"[RAG] 教材加载完成，共 {total_chunks} 个文本块\n")
        except Exception as e:
            print(f"[RAG] 加载教材数据失败: {e}")
            self.index_built = True

    def _parse_textbook_data(self, data: Any, source: str) -> List[Dict]:
        """
        解析教材数据，提取文本块

        支持两种格式：
        1. 列表格式: [{"metadata": {...}, "content": "..."}]
        2. 嵌套格式: {"sections": [{"chunks": [...]}, ...]}
        """
        chunks = []

        if isinstance(data, list):
            # 格式1: 扁平列表
            for item in data:
                if isinstance(item, dict) and "content" in item:
                    chunks.append({
                        "content": item["content"],
                        "metadata": item.get("metadata", {}),
                        "source": source
                    })

        elif isinstance(data, dict):
            # 格式2: 嵌套结构（处理process_textbook.py的输出）
            if "sections" in data:
                for section in data["sections"]:
                    if "chunks" in section:
                        for chunk in section["chunks"]:
                            chunks.append({
                                "content": chunk.get("text", ""),
                                "metadata": {
                                    "section": section.get("title", ""),
                                    "source": chunk.get("metadata", {}).get("source", source),
                                    "chunk_id": chunk.get("chunk_id", "")
                                },
                                "source": source
                            })

        return chunks

    def extract_keywords(self, question: str, top_k: int = 10) -> List[str]:
        """
        提取问题中的关键词

        Args:
            question: 用户问题
            top_k: 返回关键词数量

        Returns:
            关键词列表
        """
        # 使用TF-IDF提取关键词
        keywords = analyse.extract_tags(question, topK=top_k, withWeight=False)

        # 添加一些化学相关的特殊处理
        # 提取化学式（如 H2O, NH3, CO2）
        chemical_formulas = re.findall(r'\b[A-Z][a-z]?\d*\b', question)
        keywords.extend([f for f in chemical_formulas if len(f) > 1])

        # 去重并保持顺序
        seen = set()
        result = []
        for kw in keywords:
            if kw not in seen and len(kw) > 1:
                seen.add(kw)
                result.append(kw)

        return result

    def search(self, question: str, top_k: int = 5, min_score: float = 0.1) -> List[Dict]:
        """
        根据问题搜索相关教材内容

        Args:
            question: 用户问题
            top_k: 返回结果数量
            min_score: 最小相关分数阈值

        Returns:
            匹配的文本块列表，按相关性排序
        """
        if not self.index_built:
            self.load_textbooks()

        # 提取关键词
        keywords = self.extract_keywords(question)

        if not keywords:
            # 如果没有提取到关键词，返回空列表
            return []

        # 计算每个chunk的相关性分数
        scored_chunks = []

        for chunk in self.chunks:
            content = chunk["content"]
            score = self._calculate_relevance(content, keywords)

            if score >= min_score:
                scored_chunks.append({
                    **chunk,
                    "relevance_score": score
                })

        # 按分数排序，返回top_k
        scored_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)

        return scored_chunks[:top_k]

    def _calculate_relevance(self, content: str, keywords: List[str]) -> float:
        """
        计算内容与关键词的相关性分数

        评分规则：
        - 完全匹配关键词：每个 +2 分
        - 部分匹配（包含关键词）：每个 +1 分
        - 多个关键词在同一句中：额外加分
        """
        score = 0.0
        content_lower = content.lower()

        # 将内容分句（简单按。！？分割）
        sentences = re.split(r'[。！？；\n]', content_lower)

        for keyword in keywords:
            keyword_lower = keyword.lower()

            # 完全匹配
            if keyword_lower in content_lower:
                # 计算出现次数
                count = content_lower.count(keyword_lower)
                score += count * 1.0

                # 检查是否在同一句中（多个关键词）
                for sentence in sentences:
                    if keyword_lower in sentence:
                        # 句子中关键词越多，分数越高
                        other_keywords_in_sentence = sum(
                            1 for kw in keywords if kw.lower() in sentence and kw != keyword
                        )
                        score += other_keywords_in_sentence * 0.5
                        break

        return score

    def get_context(self, question: str, max_length: int = 3000) -> str:
        """
        获取问题相关的上下文内容

        Args:
            question: 用户问题
            max_length: 返回内容的最大长度（字符数）

        Returns:
            格式化的上下文字符串
        """
        results = self.search(question, top_k=5)

        if not results:
            return ""

        # 构建上下文
        context_parts = []

        current_length = 0
        for i, result in enumerate(results):
            content = result["content"]

            # 截断过长的内容
            if current_length + len(content) > max_length:
                remaining = max_length - current_length
                if remaining > 100:  # 至少保留100字符
                    content = content[:remaining] + "..."
                    context_parts.append(f"【来源{i+1}】{content}")
                break

            context_parts.append(f"【来源{i+1}】{content}")
            current_length += len(content)

        return "\n\n".join(context_parts)

    def get_source_info(self, question: str) -> List[Dict]:
        """
        获取检索结果的来源信息

        Returns:
            来源信息列表，用于显示给用户
        """
        results = self.search(question, top_k=5)

        sources = []
        for result in results:
            metadata = result.get("metadata", {})
            sources.append({
                "section": metadata.get("section", "未知章节"),
                "source": metadata.get("source", "未知来源"),
                "score": result.get("relevance_score", 0)
            })

        return sources


# 全局单例
_rag_instance: Optional[TextbookRAG] = None


def get_rag_instance() -> TextbookRAG:
    """获取RAG单例实例"""
    global _rag_instance
    if _rag_instance is None:
        try:
            _rag_instance = TextbookRAG()
        except Exception as e:
            print(f"[RAG] 初始化失败: {e}")
            _rag_instance = TextbookRAG.__new__(TextbookRAG)
            _rag_instance.data_dir = Path("")
            _rag_instance.chunks = []
            _rag_instance.index_built = False
    return _rag_instance


def reset_rag_instance():
    """重置RAG实例"""
    global _rag_instance
    _rag_instance = None


if __name__ == "__main__":
    # 测试代码
    rag = TextbookRAG()

    # 测试搜索
    test_questions = [
        "什么是化学键？",
        "氨气为什么是极性分子？",
        "水的化学式是什么？",
        "氧化还原反应的本质是什么？"
    ]

    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"问题: {question}")
        print(f"{'='*60}")

        results = rag.search(question, top_k=3)

        if results:
            print(f"找到 {len(results)} 个相关结果:\n")
            for i, result in enumerate(results):
                print(f"【结果 {i+1}】(相关度: {result['relevance_score']:.2f})")
                content = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
                print(f"{content}\n")
        else:
            print("未找到相关内容")
