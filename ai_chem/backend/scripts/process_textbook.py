"""
教材PDF解析脚本
从PDF教材中提取文本内容，按章节分块，保存为结构化JSON
"""
import json
import re
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

# 设置控制台编码为 UTF-8（Windows 兼容）
if sys.platform == "win32":
    try:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")
    except:
        os.system("chcp 65001 > nul 2>&1")


def safe_import_unstructured():
    """安全导入 PDF 解析库，按稳定性排序"""
    # 优先使用 pdfplumber (最稳定，无额外依赖)
    try:
        import pdfplumber
        return pdfplumber, "pdfplumber"
    except ImportError:
        pass

    # 备选：使用 PyPDF2
    try:
        import PyPDF2
        return PyPDF2, "pypdf2"
    except ImportError:
        pass

    # 最后尝试 unstructured (可能有 nltk 等依赖问题)
    try:
        from unstructured.partition.pdf import partition_pdf
        return partition_pdf, "unstructured"
    except ImportError:
        pass

    return None, None


# 导入PDF解析库
partition_pdf, LIB_TYPE = safe_import_unstructured()


def get_element_text(element) -> str:
    """统一获取元素文本的接口"""
    if LIB_TYPE == "unstructured":
        return str(element) if element else ""
    elif LIB_TYPE == "pdfplumber":
        return element.get("text", "") if isinstance(element, dict) else str(element)
    else:
        return str(element) if element else ""


def get_element_category(element) -> str:
    """获取元素类别"""
    if LIB_TYPE == "unstructured":
        return getattr(element, "category", "")
    else:
        return ""


def clean_text(text: str) -> str:
    """清理文本：去除多余空白、标准化化学式"""
    if not text:
        return ""

    # 去除多余空白
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    # 标准化化学式下标 (如 H₂O → H2O)
    # 注意：这个简单替换可能不够完善，实际可能需要更复杂的处理
    text = re.sub(r'₀', '0', text)
    text = re.sub(r'₁', '1', text)
    text = re.sub(r'₂', '2', text)
    text = re.sub(r'₃', '3', text)
    text = re.sub(r'₄', '4', text)
    text = re.sub(r'₅', '5', text)
    text = re.sub(r'₆', '6', text)
    text = re.sub(r'₇', '7', text)
    text = re.sub(r'₈', '8', text)
    text = re.sub(r'₉', '9', text)

    # 标准化化学式上标
    text = re.sub(r'⁰', '0', text)
    text = re.sub(r'¹', '1', text)
    text = re.sub(r'²', '2', text)
    text = re.sub(r'³', '3', text)
    text = re.sub(r'⁴', '4', text)
    text = re.sub(r'⁵', '5', text)
    text = re.sub(r'⁶', '6', text)
    text = re.sub(r'⁷', '7', text)
    text = re.sub(r'⁸', '8', text)
    text = re.sub(r'⁹', '9', text)

    return text


def extract_chapter_number(title: str) -> str:
    """从标题中提取章节号"""
    # 匹配 "第x章" 或 "第一章" 等模式
    patterns = [
        r'第([一二三四五六七八九十\d]+)章',
        r'([一二三四五六七八九十\d+])、',
        r'Chapter\s*(\d+)',
        r'(\d+)\s*[\.、]',
    ]

    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            num = match.group(1)
            # 转换中文数字
            chinese_nums = {'一': '1', '二': '2', '三': '3', '四': '4',
                          '五': '5', '六': '6', '七': '7', '八': '8',
                          '九': '9', '十': '10'}
            return chinese_nums.get(num, num)

    return ""


def split_into_chunks(text: str, chunk_size: int = 400, overlap_sentences: int = 2) -> List[str]:
    """将文本分成块，按chunk_size分块，overlap_sentences为重叠句子数"""
    if not text:
        return []

    # 按句子分割（保留标点）
    sentences = re.split(r'([。！？；\n])', text)
    sentences = [s + t for s, t in zip(sentences[::2], sentences[1::2] + [''])]
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return [text] if text.strip() else []

    chunks = []
    i = 0  # 当前句子索引

    while i < len(sentences):
        # 开始一个新的chunk
        current_sentences = []
        current_size = 0

        # 添加句子直到超过chunk_size
        while i < len(sentences):
            sentence = sentences[i]
            sentence_tokens = len(sentence) / 1.5

            # 如果添加此句子会超限且chunk不为空，则停止
            if current_size + sentence_tokens > chunk_size and current_sentences:
                break

            current_sentences.append(sentence)
            current_size += sentence_tokens
            i += 1

        # 保存当前chunk
        if current_sentences:
            chunks.append(''.join(current_sentences))

        # 回退overlap_sentences个句子，作为下一块的开头
        if i < len(sentences):
            i = max(0, i - overlap_sentences)

    return chunks


def extract_chemical_entities(text: str) -> Dict[str, List[str]]:
    """简单的化学实体提取"""
    entities = {
        "formulas": [],
        "elements": [],
        "compounds": []
    }

    # 常见元素符号
    common_elements = [
        'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
        'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca',
        'Fe', 'Cu', 'Zn', 'Ag', 'Ba', 'Hg', 'Mn'
    ]

    # 提取化学式（简单模式：大写字母+数字/小写字母+数字）
    formula_pattern = r'\b[A-Z][a-z]?\d*\b'
    formulas = re.findall(formula_pattern, text)

    # 过滤并分类
    for f in set(formulas):
        if f in common_elements:
            entities["elements"].append(f)
        elif len(f) > 1:  # 可能是化合物
            entities["formulas"].append(f)

    return entities


def parse_textbook(pdf_path: Path, output_dir: Path) -> Optional[Dict[str, Any]]:
    """解析单个教材PDF"""
    print(f"\n{'='*60}")
    print(f"📖 正在处理: {pdf_path.name}")
    print(f"{'='*60}")

    if partition_pdf is None:
        print(f"❌ 错误: 未找到可用的PDF解析库")
        print(f"   请安装: pip install unstructured[local-inference] pdfplumber PyPDF2")
        return None

    # 解析PDF
    print(f"⏳ 正在解析PDF (使用 {LIB_TYPE})...")

    try:
        if LIB_TYPE == "unstructured":
            elements = partition_pdf(
                filename=str(pdf_path),
                strategy="fast",  # 使用 fast 策略，不需要 poppler
                extract_images_in_pdf=False,
                extract_tables=False,
            )
            # 转换为统一格式
            parsed_elements = [{"text": str(e), "category": getattr(e, "category", "Text")} for e in elements]

        elif LIB_TYPE == "pdfplumber":
            parsed_elements = []
            with partition_pdf.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    if text.strip():
                        # 按行分割
                        for line in text.split('\n'):
                            line = line.strip()
                            if line:
                                parsed_elements.append({"text": line, "category": "Text"})

        elif LIB_TYPE == "pypdf2":
            parsed_elements = []
            reader = partition_pdf.PdfReader(str(pdf_path))
            for page in reader.pages:
                text = page.extract_text() or ""
                # 按行分割
                for line in text.split('\n'):
                    line = line.strip()
                    if line:
                        parsed_elements.append({"text": line, "category": "Text"})

        print(f"✅ 解析完成，共 {len(parsed_elements)} 个元素")

    except Exception as e:
        print(f"❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return None

    # 提取文本内容
    print("⏳ 正在提取文本内容...")
    full_text = ""
    current_section = None
    sections = []

    for element in parsed_elements:
        text = clean_text(element.get("text", ""))
        if not text:
            continue

        # 检测标题（简单判断：短且独立成行）
        category = element.get("category", "")
        if category in ["Title", "Header"]:
            if current_section:
                sections.append(current_section)
            current_section = {
                "title": text,
                "content": "",
                "chunks": []
            }
        elif current_section is not None:
            current_section["content"] += text + "\n"
        else:
            full_text += text + "\n"

    # 添加最后一个section
    if current_section:
        sections.append(current_section)

    # 如果没有检测到section，将全文作为一个section
    if not sections:
        sections = [{"title": "全文", "content": full_text, "chunks": []}]

    print(f"✅ 提取到 {len(sections)} 个章节/部分")

    # 分块处理
    print("⏳ 正在分块处理...")
    chunk_id = 0
    all_chunks = []

    for section in sections:
        chunks = split_into_chunks(section["content"])
        section["chunks"] = []

        for i, chunk_text in enumerate(chunks):
            # 提取化学实体
            entities = extract_chemical_entities(chunk_text)

            chunk_data = {
                "chunk_id": f"{pdf_path.stem}_chunk_{chunk_id:04d}",
                "section_title": section["title"],
                "chunk_index": i,
                "text": chunk_text,
                "entities": entities,
                "metadata": {
                    "source": pdf_path.name,
                    "section": section["title"],
                    "chunk_size": len(chunk_text),
                }
            }

            section["chunks"].append(chunk_data)
            all_chunks.append(chunk_data)
            chunk_id += 1

    print(f"✅ 分块完成，共 {len(all_chunks)} 个文本块")

    # 构建结果
    result = {
        "source": pdf_path.name,
        "source_type": "textbook",
        "total_sections": len(sections),
        "total_chunks": len(all_chunks),
        "sections": [
            {
                "title": s["title"],
                "chunk_count": len(s["chunks"]),
                "chunks": s["chunks"]
            }
            for s in sections
        ]
    }

    # 保存JSON
    output_file = output_dir / f"{pdf_path.stem}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"💾 已保存到: {output_file}")

    return result


def main():
    """主函数"""
    # 检查PDF解析库是否可用
    if partition_pdf is None:
        print("="*60)
        print("❌ 错误: 未找到可用的PDF解析库！")
        print("="*60)
        print("\n请安装以下任一库：")
        print("  pip install pdfplumber                     # 推荐")
        print("  pip install PyPDF2                          # 备选")
        print("  pip install unstructured[local-inference]  # 备选")
        print("="*60)
        sys.exit(1)

    print(f"✅ 使用PDF解析库: {LIB_TYPE}")

    # 定义路径
    raw_dir = Path("backend/data/raw/textbooks")
    output_dir = Path("backend/data/collected/textbooks")

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # 获取所有PDF文件
    pdf_files = list(raw_dir.glob("*.pdf"))

    if not pdf_files:
        print("❌ 未找到PDF文件，请将教材PDF放入 backend/data/raw/textbooks/ 目录")
        return

    print(f"📚 找到 {len(pdf_files)} 本教材")

    # 处理每本教材
    all_results = []
    for pdf_file in pdf_files:
        result = parse_textbook(pdf_file, output_dir)
        if result:
            all_results.append(result)

    # 生成汇总报告
    print(f"\n{'='*60}")
    print("📊 处理汇总")
    print(f"{'='*60}")

    for result in all_results:
        print(f"\n📖 {result['source']}")
        print(f"   章节: {result['total_sections']}")
        print(f"   文本块: {result['total_chunks']}")

    print(f"\n{'='*60}")
    print(f"✅ 全部完成！共处理 {len(all_results)} 本教材")
    print(f"📁 输出目录: {output_dir.absolute()}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
