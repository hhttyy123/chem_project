# ChemTutor

<div align="center">

  ![ChemTutor Logo](https://img.shields.io/badge/ChemTutor-Education-blue)
  ![Python](https://img.shields.io/badge/Python-3.8+-green.svg)
  ![Vue.js](https://img.shields.io/badge/Vue.js-3.x-brightgreen.svg)
  ![License](https://img.shields.io/badge/License-MIT-yellow.svg)

  **一个综合性的化学教育平台**

  [功能介绍](#-核心功能) &bull; [快速开始](#-快速开始) &bull; [技术栈](#-技术栈) &bull; [贡献](#-贡献)

</div>

---

## 项目简介

ChemTutor 是一个面向高中化学教育的综合性学习平台，集成了 AI 智能问答、3D 分子可视化、图像识别等多种功能，旨在提供直观、交互式的化学学习体验。

## 核心功能

### AI 智能问答
- 基于教材内容的智能问答系统
- 关键词搜索与相关性排序
- 来源信息追溯
- 对话历史记录

### 3D 分子可视化
- 支持分子和晶体结构展示
- 多种输入格式（SMILES、化学名称、化学式）
- 交互式操作（旋转、缩放、平移）
- 晶胞复制功能

### 图像识别
- 上传化学结构图片自动识别
- 基于 DECIMER 深度学习模型
- 输出标准 SMILES 字符串

## 项目结构

```
chem_project/
├── ai_chem/              # ChemTutor - RAG 问答系统
│   ├── backend/          # FastAPI 后端服务
│   ├── frontend/         # Vue.js 前端应用
│   └── rag-builder/      # RAG 内容构建工具
│
├── 3D_test/              # 分子与晶体可视化系统
│   ├── api.py            # FastAPI 后端
│   ├── index.html        # 3Dmol.js 可视化界面
│   └── data/             # 化学名称映射数据
│
└── image_identity/       # 图像分子识别系统
    ├── app.py            # Flask Web应用
    ├── identify.py       # 识别逻辑
    └── outputImage.py    # 图像处理工具
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 安装

#### 1. 克隆项目

```bash
git clone https://github.com/yourusername/chem_project.git
cd chem_project
```

#### 2. ChemTutor 安装

```bash
# 后端
cd ai_chem/backend
pip install -r requirements.txt

# 前端
cd ../frontend
npm install
```

#### 3. 3D可视化系统安装

```bash
cd ../../3D_test
pip install -r requirements.txt
```

#### 4. 图像识别系统安装

```bash
cd ../image_identity
pip install -r requirements.txt
```

### 运行

#### ChemTutor

```bash
# 后端 (端口 8000)
cd ai_chem/backend
python main.py

# 前端 (端口 5173)
cd ../frontend
npm run dev
```

#### 3D可视化系统

```bash
cd 3D_test
python api.py
# 访问 http://localhost:8000
```

#### 图像识别系统

```bash
cd image_identity
python app.py
# 访问 http://localhost:5000
```

## 技术栈

### 后端

| 技术 | 用途 |
|------|------|
| FastAPI | Web 框架 |
| Flask | 轻量级 Web 服务 |
| RDKit | 化学信息学 |
| PyTorch | 深度学习 |

### 前端

| 技术 | 用途 |
|------|------|
| Vue.js 3 | 前端框架 |
| TypeScript | 类型系统 |
| Vite | 构建工具 |
| 3Dmol.js | 3D 可视化 |

## 功能演示

### AI 问答界面

提问：*"什么是化学键？"*

系统会基于教材内容返回准确答案，并标注来源。

### 3D 可视化

输入化学名称（如"苯"），系统自动生成 3D 结构模型，支持交互操作。

### 图像识别

上传化学结构式图片，系统自动识别并输出 SMILES 字符串。

## 开发路线图

- [ ] 向量数据库集成 (ChromaDB)
- [ ] 知识图谱构建
- [ ] 用户系统与收藏功能
- [ ] 移动端适配
- [ ] 多语言支持

## 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [Issue](https://github.com/yourusername/chem_project/issues)
- 发送邮件至 your.email@example.com

---

<div align="center">

**Made with ❤️ for Chemistry Education**

</div>
