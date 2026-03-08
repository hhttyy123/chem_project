# 化学智能出题系统优化方案

## 📋 目录

1. [问题分析](#问题分析)
2. [解决方案架构](#解决方案架构)
3. [实施方案](#实施方案)
4. [技术实现细节](#技术实现细节)
5. [预期效果](#预期效果)
6. [实施计划](#实施计划)

---

## 问题分析

### 当前问题

根据 `error.md` 记录，系统存在以下问题：

1. **多选题无法选择多个选项** - 前端问题
2. **选择题每次出来的题目数量少，且几乎一样** - 核心问题
3. **题目的选项和正确选项不匹配** - 提示词问题
4. **AI出题的准确率很低** - 提示词问题
5. **前端页面的交互体验不是很好** - 前端问题

### 核心问题根源分析

**题目单一性问题的根本原因：**

```
当前数据库章节内容:
  content = "第一单元 物质及其反应的分类" (仅12字)
     ↓
AI收到的信息极少，只能根据"反应分类"自由发挥
     ↓
AI知道化学反应分类包括：化合、分解、置换、复分解
     ↓
置换反应是最常见、最容易出的题型
     ↓
AI反复出置换反应的题目
```

**具体数据验证：**

| 字段 | 当前值 | 问题 |
|------|--------|------|
| `chapter_title` | 物质的分类及计量 | ✅ 正常 |
| `content` | 第一单元 物质及其反应的分类 | ❌ 仅12字 |
| `knowledge_points` | NULL | ❌ 从未使用 |

---

## 解决方案架构

### 整体方案图

```
┌─────────────────────────────────────────────────────────────┐
│                    课本内容文件                              │
│  textbok/one/cleaned_chem.md (281KB)                        │
│  textbok/one_e/one_e.md                                     │
│  textbok/two/cleaned_chem.md                                │
│  ...                                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  【方案A】AI知识点提取器                                     │
│  ─────────────────────────────────────────────────────────  │
│  功能: 从课本原始内容自动提取知识点                          │
│  输出: 详细内容 + 知识点列表(JSON)                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  数据库更新                                                 │
│  UPDATE chapters                                            │
│  SET content = '详细内容...',                                │
│      knowledge_points = '[{...}]'                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  【方案B】改进的出题提示词                                    │
│  ─────────────────────────────────────────────────────────  │
│  增强: 多样性指导 + 知识点选择策略                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  【方案C】历史题目去重机制                                    │
│  ─────────────────────────────────────────────────────────  │
│  功能: 统计已出题知识点，避免重复                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  最终效果                                                    │
│  ✅ 题目多样性大幅提升                                        │
│  ✅ 覆盖更多知识点                                           │
│  ✅ 避免重复出题                                             │
│  ✅ 题目质量提高                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 实施方案

### 方案A：丰富章节内容（核心）

#### 目标
将数据库中的章节内容从12字扩展为500-1000字的详细内容，并提取5-10个知识点。

#### 实施方式

**1. AI知识点提取提示词**

```
你是一位高中化学教材分析专家。请分析以下课本内容，提取知识点信息。

课本内容：
{课本原始内容}

章节标题：{chapter_title}

要求：
1. 阅读并理解章节内容
2. 提取章节包含的主要知识点（5-10个）
3. 为每个知识点标注重要性（high/medium/low）
4. 返回JSON格式：

{
  "detailed_content": "章节详细内容摘要（300-500字），包含主要知识点概述",
  "knowledge_points": [
    {
      "id": "kp_1",
      "name": "物质分类",
      "priority": "high",
      "description": "纯净物vs混合物、单质vs化合物、酸碱盐分类",
      "question_angles": ["分类标准", "实例判断", "性质特点"]
    },
    {
      "id": "kp_2",
      "name": "酸碱盐的性质",
      "priority": "high",
      "description": "酸的通性、碱的通性、盐的性质",
      "question_angles": ["通性应用", "反应类型", "鉴别方法"]
    }
  ]
}
```

**2. 更新数据库字段**

```python
# 更新前
chapter.content = "第一单元 物质及其反应的分类"
chapter.knowledge_points = None

# 更新后
chapter.content = """
第一单元 物质及其反应的分类

本单元主要内容：
1. 物质的分类：根据物质的组成和性质，可以将物质分为纯净物和混合物。
   纯净物又可分为单质和化合物，化合物进一步分为酸、碱、盐、氧化物等。

2. 酸、碱、盐的分类和性质：
   - 酸：HCl、H2SO4、HNO3等，具有酸的通性
   - 碱：NaOH、Ca(OH)2等，具有碱的通性
   - 盐：NaCl、Na2CO3等

3. 化学反应的四种基本类型：
   - 化合反应：A + B → AB
   - 分解反应：AB → A + B
   - 置换反应：A + BC → AC + B
   - 复分解反应：AB + CD → AD + CB

4. 氧化还原反应：有电子转移的反应
5. 离子反应：在水溶液中有离子参与的反应
"""

chapter.knowledge_points = json.dumps([
    {"id": "kp_1", "name": "物质分类", "priority": "high"},
    {"id": "kp_2", "name": "酸碱盐", "priority": "high"},
    {"id": "kp_3", "name": "化合反应", "priority": "medium"},
    {"id": "kp_4", "name": "分解反应", "priority": "medium"},
    {"id": "kp_5", "name": "置换反应", "priority": "medium"},
    {"id": "kp_6", "name": "复分解反应", "priority": "medium"},
    {"id": "kp_7", "name": "氧化还原反应", "priority": "medium"},
    {"id": "kp_8", "name": "离子反应", "priority": "medium"}
])
```

---

### 方案B：改进出题提示词

#### 当前提示词问题

```python
# 当前提示词 (ai_service.py 第45-63行)
prompt = f"""你是一位专业的高中化学教师。请根据以下章节内容生成一道{difficulty}难度的{type}。

章节：{chapter_title}
内容：{content}

要求：
1. 题目要紧扣知识点，考察核心概念
2. 选项要有干扰性，但不能有明显错误
3. 提供详细的答案解析
4. 直接返回JSON格式，不要有任何其他文字
```

**问题：**
- 没有多样性要求
- 没有知识点选择指导
- 容易重复出题

#### 改进后的提示词

```python
# 新提示词
knowledge_points = json.loads(chapter.knowledge_points)
kp_list = "\n".join([f"- {kp['name']}({kp['priority']})" for kp in knowledge_points])

prompt = f"""你是一位专业的高中化学教师。请根据以下章节内容生成一道{difficulty}难度的{type}。

章节：{chapter_title}
内容：{content}

本章节知识点：
{kp_list}

出题要求：
1. 【多样性】优先选择尚未考查的知识点出题
2. 【角度不同】即使同一知识点，也要从不同角度出题（概念、应用、计算、辨析等）
3. 【选项质量】选项要有合理的干扰性，常见错误答案作为干扰项
4. 【答案验证】生成后验证选项与答案的一致性
5. 【解析详细】解析要包含知识点回顾、解题思路、易错点提醒

已出题目统计：
{recent_questions_summary}

请直接返回JSON格式：
{{
  "question_text": "题目内容",
  "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
  "correct_answer": "A"或"AB"(多选),
  "explanation": "详细解析",
  "knowledge_point": "本题考查的知识点名称"
}}

注意：
- 多选题的正确答案格式如 "AB" 或 "ABC"
- 确保correct_answer中的选项在options中存在
- 选项A/B/C/D必须与答案中的字母对应"""
```

---

### 方案C：历史题目去重机制

#### 数据库扩展

```sql
-- 为 questions 表添加字段
ALTER TABLE questions ADD COLUMN knowledge_point_tag TEXT;
ALTER TABLE questions ADD COLUMN question_angle TEXT;

-- 添加索引
CREATE INDEX idx_questions_kp_tag ON questions(knowledge_point_tag);
CREATE INDEX idx_questions_chapter_kp ON questions(chapter_id, knowledge_point_tag);
```

#### 去重逻辑实现

```python
def get_knowledge_point_statistics(chapter_id: int) -> dict:
    """
    统计各知识点的出题数量
    """
    query = """
    SELECT knowledge_point_tag, COUNT(*) as count
    FROM questions
    WHERE chapter_id = ? AND knowledge_point_tag IS NOT NULL
    GROUP BY knowledge_point_tag
    ORDER BY count DESC
    """
    results = db.execute(query, [chapter_id]).fetchall()

    # 格式化统计结果
    summary = ", ".join([f"{row[0]}({row[1]}题)" for row in results])
    return summary

# 调用AI前获取统计
recent_questions_summary = get_knowledge_point_statistics(chapter_id)
# 输出示例: "置换反应(5题), 物质分类(1题), 酸碱盐(2题)"
```

#### 出题策略优化

```python
def prioritize_knowledge_points(chapter: Chapter) -> list:
    """
    根据出题历史，确定优先考查的知识点
    """
    knowledge_points = json.loads(chapter.knowledge_points)

    # 获取已出题统计
    stats = get_knowledge_point_statistics(chapter.id)

    # 按出题次数排序，优先出题少的
    for kp in knowledge_points:
        kp['question_count'] = stats.get(kp['name'], 0)

    # 排序：出题少的优先
    knowledge_points.sort(key=lambda x: x['question_count'])

    return knowledge_points
```

---

## 技术实现细节

### 文件结构

```
backend/
├── services/
│   ├── ai_service.py           # 修改：改进提示词
│   ├── knowledge_extractor.py  # 新增：知识点提取服务
│   └── quiz_service.py         # 修改：添加去重逻辑
├── scripts/
│   ├── init_sample_data.py     # 修改：更新章节内容
│   └── extract_knowledge.py    # 新增：知识点提取脚本
└── models/
    ├── chapter.py              # 修改：确认knowledge_points字段
    └── question.py             # 修改：添加knowledge_point_tag字段
```

### API接口变更

#### 1. 新增接口：知识点提取

```
POST /api/chapters/{id}/extract-knowledge
功能：从课本内容自动提取知识点
返回：更新后的章节信息
```

#### 2. 修改接口：AI生成题目

```
POST /api/ai/generate
变更：传入avoid_knowledge_points参数
请求体：
{
  "chapter_id": 1,
  "difficulty": "medium",
  "question_type": "single",
  "avoid_knowledge_points": ["置换反应"]  // 新增
}
```

#### 3. 新增接口：知识点统计

```
GET /api/chapters/{id}/knowledge-stats
功能：获取各知识点的出题统计
返回：
{
  "stats": [
    {"knowledge_point": "置换反应", "count": 5},
    {"knowledge_point": "物质分类", "count": 1}
  ]
}
```

---

## 预期效果

### 对比表格

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 章节内容字数 | 12字 | 500-1000字 | 50-80倍 |
| 可识别知识点 | 0个 | 5-10个 | 新增 |
| 题目类型多样性 | 1种 | 5+种 | 5倍+ |
| 题目重复率 | 80%+ | <20% | 降低75% |
| 选项答案一致性 | 60% | 95%+ | 提升58% |
| 单次出题数量 | 1题 | 可批量5-10题 | 10倍 |

### 效果示例

#### 改进前
```
专题1 - 物质的分类及计量的题目：
1. 下列属于置换反应的是？(D)
2. 下列属于置换反应的是？(B)
3. 下列属于置换反应的是？(D)
4. 置换反应的特点是？(D)
5. 置换反应与分解反应的区别？(D)
→ 全部是置换反应！
```

#### 改进后
```
专题1 - 物质的分类及计量的题目：
1. 下列物质属于纯净物的是？(物质分类)
2. 下列关于酸的通性说法正确的是？(酸碱盐)
3. 下列反应属于化合反应的是？(化合反应)
4. 下列反应属于置换反应的是？(置换反应)
5. 下列关于氧化还原反应判断正确的是？(氧化还原)
→ 覆盖5个不同知识点！
```

---

## 实施计划

### 阶段一：知识点提取（1-2天）

**任务清单：**
- [ ] 创建 `knowledge_extractor.py` 服务
- [ ] 编写知识点提取提示词
- [ ] 实现课本内容读取功能
- [ ] 测试提取效果
- [ ] 更新数据库chapters表

**交付物：**
- 知识点提取服务
- 更新后的数据库（包含详细内容和知识点）

---

### 阶段二：提示词优化（1天）

**任务清单：**
- [ ] 修改 `ai_service.py` 中的提示词
- [ ] 添加知识点选择逻辑
- [ ] 添加答案验证要求
- [ ] 测试新提示词效果

**交付物：**
- 优化后的AI出题服务
- 测试报告

---

### 阶段三：去重机制（1天）

**任务清单：**
- [ ] 数据库添加字段
- [ ] 实现知识点统计功能
- [ ] 实现出题优先级逻辑
- [ ] 添加知识点标签到题目
- [ ] 测试去重效果

**交付物：**
- 完整的去重机制
- 统计API接口

---

### 阶段四：测试验证（1天）

**测试项：**
- [ ] 连续出题10道，检查知识点覆盖
- [ ] 验证选项答案一致性
- [ ] 检查题目质量
- [ ] 性能测试

---

## 附录

### A. 知识点JSON格式

```json
{
  "detailed_content": "章节详细内容摘要...",
  "knowledge_points": [
    {
      "id": "kp_1",
      "name": "物质分类",
      "priority": "high",
      "description": "纯净物vs混合物、单质vs化合物",
      "question_angles": ["分类标准", "实例判断", "性质特点"],
      "example_count": 3
    },
    {
      "id": "kp_2",
      "name": "置换反应",
      "priority": "medium",
      "description": "置换反应的特征和判断",
      "question_angles": ["反应判断", "方程式书写", "应用"],
      "example_count": 2
    }
  ]
}
```

### B. 出题历史统计格式

```json
{
  "chapter_id": 1,
  "total_questions": 20,
  "knowledge_point_stats": [
    {"name": "置换反应", "count": 5, "percentage": 25},
    {"name": "物质分类", "count": 3, "percentage": 15},
    {"name": "酸碱盐", "count": 4, "percentage": 20},
    {"name": "氧化还原", "count": 2, "percentage": 10}
  ],
  "recommended": ["离子反应", "复分解反应"]
}
```

### C. 改进后的完整出题流程

```python
async def generate_question_with_smart_selection(chapter_id, difficulty, question_type):
    # 1. 获取章节信息（包含详细内容和知识点）
    chapter = get_chapter_with_knowledge_points(chapter_id)

    # 2. 获取历史出题统计
    stats = get_knowledge_point_statistics(chapter_id)

    # 3. 确定优先考查的知识点
    priority_kps = prioritize_knowledge_points(chapter, stats)

    # 4. 构建增强提示词
    prompt = build_enhanced_prompt(
        chapter=chapter,
        difficulty=difficulty,
        question_type=question_type,
        priority_kps=priority_kps,
        stats=stats
    )

    # 5. 调用AI生成
    result = await call_ai_api(prompt)

    # 6. 解析并保存
    question = parse_and_save(result, chapter_id)

    return question
```

---

## 总结

本方案通过**三个维度**同时优化：

1. **数据层面**（方案A）：丰富章节内容，提供充足的知识点信息
2. **提示词层面**（方案B）：改进AI指令，增加多样性约束
3. **逻辑层面**（方案C）：智能去重，避免重复出题

三者结合，可以从根本上解决题目单一、重复率高的问题。

---

*文档版本：v1.0*
*创建日期：2026-03-06*
*作者：Claude Code*
