# ChemTutor 转 AhaTutor 插件平台 — 实施计划

> 本文档为 ChemTutor 项目改造为 AhaTutor 插件的完整实施计划。
> 严格遵循 `plugin-development-guide.md` 规范，**不包含出题/答题系统**。

---

## 目录

1. [背景与目标](#1-背景与目标)
2. [总体架构](#2-总体架构)
3. [Phase 1：基础设施搭建](#3-phase-1基础设施搭建)
4. [Phase 2：chem-3d-molecule 插件](#4-phase-2chem-3d-molecule-插件)
5. [Phase 3：chem-image-recognizer 插件](#5-phase-3chem-image-recognizer-插件)
6. [Phase 4：chem-knowledge-qa 插件](#6-phase-4chem-knowledge-qa-插件)
7. [Phase 5：集成测试与优化](#7-phase-5集成测试与优化)
8. [关键文件映射](#8-关键文件映射)
9. [验证方式](#9-验证方式)

---

## 1. 背景与目标

ChemTutor 是一个高中化学 AI 教育平台，包含 3D 分子可视化、化学结构图像识别、教材知识库问答等功能（Vue 3 + Python 微服务架构）。现需要将这些功能改造为 AhaTutor 平台的 React 插件。

### 核心挑战

| 挑战 | 解决方案 |
|------|---------|
| 现有前端是 Vue 3，插件规范要求 React 组件 | 全部用 React + TypeScript 重写前端组件 |
| 3D 渲染依赖 3Dmol.js，规范禁止外部依赖（除 React） | 用 Canvas 2D 透视投影手动实现 3D 渲染 |
| 现有 Python 后端服务（RDKit/DECIMER/RAG）需保留 | 通过 API Gateway 转发，插件用 fetch 通信 |

### 不包含的功能

- 出题/答题系统（`question/` 目录）不在本次改造范围内

---

## 2. 总体架构

### 2.1 插件划分（3 个独立插件）

| 插件 ID | 功能 | 核心组件 | 复杂度 |
|---------|------|---------|--------|
| `chem-3d-molecule` | 3D 分子可视化 | `MoleculeViewer3D` | 高 |
| `chem-image-recognizer` | 化学结构图像识别 | `StructureRecognizer` | 中 |
| `chem-knowledge-qa` | 教材知识库检索 | `ChemKnowledgeSearch` | 低 |

**分拆理由**：三个功能的 LLM 意图路由关键词差异大（"展示分子结构" vs "识别这张图" vs "什么是化学键"），独立后 tags 更精准、路由更准确。三个功能的 props_schema 完全不同，没有共享参数。

### 2.2 后端通信架构

插件（前端 React 组件）通过 AhaTutor 后端的 API Gateway 与现有 Python 微服务通信：

```
AhaTutor 前端
  │
  ├── chem-3d-molecule 插件 ──fetch──→ /api/chem/mol/parse
  │                                    /api/chem/mol/info
  │                                         │
  │                                    [API Gateway 转发]
  │                                         │
  │                                    3D_test/api.py (RDKit, :8001)
  │
  ├── chem-image-recognizer 插件 ──fetch──→ /api/chem/img/identify
  │                                         │
  │                                    [API Gateway 转发]
  │                                         │
  │                                    image_identity/app.py (DECIMER, :5000)
  │
  └── chem-knowledge-qa 插件 ──fetch──→ /api/chem/kb/search
                                          │
                                     [API Gateway 转发]
                                          │
                                     ai_chem/backend (RAG, :8000)
```

### 2.3 3D 渲染方案

**决策：使用 Canvas 2D 透视投影替代 3Dmol.js**

理由：
1. 插件指南明确禁止外部依赖（除 React）
2. 后端 `api.py` 的 `/parse` 接口已返回 PDB 和 SDF 格式数据，包含完整原子 3D 坐标
3. 教育场景下球棍模型足以表达分子结构
4. Canvas 2D 可以实现：透视投影、Z-buffer 画家排序、鼠标拖拽旋转、球棍/空间填充两种模式

实现要点：
- 解析后端返回的 PDB 格式，提取原子坐标和键连接信息
- 手动实现 3D 数学：旋转矩阵（绕 X/Y 轴）、透视投影
- Canvas 2D 绘制：按 Z 深度排序（画家算法），先画远处再画近处
- 鼠标/触摸事件：拖拽旋转、滚轮缩放
- 原子颜色表：内联 CPK/Jmol 颜色映射（约 20 种常见元素）

---

## 3. Phase 1：基础设施搭建

> 预估工期：2-3 天

### 3.1 创建插件目录结构

```
plugins/
├── _template/                         # 脚手架模板
│   ├── manifest.json                  # 空 manifest 模板
│   ├── manifest-prompt.md             # AI 生成 manifest 的提示词
│   ├── package.json                   # 构建配置
│   ├── vite.config.ts                 # ESM 输出，React external
│   ├── tsconfig.json                  # TypeScript 配置
│   └── src/
│       └── index.ts                   # 入口模板
│
├── chem-3d-molecule/                  # 插件 1：3D 分子可视化
│   ├── manifest.json
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── index.ts                   # 导出 { components: { MoleculeViewer3D } }
│       ├── MoleculeViewer3D.tsx       # 主组件（Canvas 2D 3D 渲染）
│       ├── pdb-parser.ts              # PDB 格式解析器
│       ├── projection.ts              # 3D 透视投影和旋转矩阵
│       └── atom-colors.ts             # CPK 原子颜色表
│
├── chem-image-recognizer/             # 插件 2：化学结构图像识别
│   ├── manifest.json
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── index.ts                   # 导出 { components: { StructureRecognizer } }
│       └── StructureRecognizer.tsx    # 图像上传 + 识别结果展示
│
└── chem-knowledge-qa/                 # 插件 3：教材知识库检索
    ├── manifest.json
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── src/
    │   ├── index.ts                   # 导出 { components: { ChemKnowledgeSearch } }
    │   └── ChemKnowledgeSearch.tsx    # 知识搜索结果展示
    └── knowledge/
        └── vector.db                  # 教材向量知识库（可选）
```

### 3.2 脚手架模板文件

**vite.config.ts**（三个插件共用）：

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    lib: {
      entry: 'src/index.ts',
      formats: ['es'],
      fileName: () => 'index.esm.js',
    },
    rollupOptions: {
      external: ['react', 'react-dom'],
    },
  },
})
```

**package.json**（三个插件共用结构）：

```json
{
  "name": "<plugin-id>",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "build": "vite build",
    "dev": "vite build --watch"
  },
  "peerDependencies": {
    "react": ">=18",
    "react-dom": ">=18"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

**tsconfig.json**（三个插件共用）：

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "dist"
  },
  "include": ["src"]
}
```

**src/index.ts**（脚手架模板）：

```typescript
// 在此导入你的组件并导出
// import { MyComponent } from './MyComponent'

export default {
  components: {
    // MyComponent,
  },
}
```

### 3.3 注册到 CatalogRegistry.ts

编辑 AhaTutor 前端的 `frontend/src/a2ui-engine/CatalogRegistry.ts`，在 `pluginModules` 中添加：

```typescript
const pluginModules: Record<string, { default: ComponentType }> = {
  // ... 已有插件 ...
  'chem-3d-molecule': await import('@plugins/chem-3d-molecule/src/index'),
  'chem-image-recognizer': await import('@plugins/chem-image-recognizer/src/index'),
  'chem-knowledge-qa': await import('@plugins/chem-knowledge-qa/src/index'),
}
```

> `@plugins` 是前端 `vite.config.ts` 中配置的别名，指向 `../plugins/`。

### 3.4 后端 API Gateway

在 AhaTutor 后端新增 `api/chem_gateway.py`，用 `httpx` 转发请求到现有微服务：

```python
from fastapi import APIRouter, UploadFile, File, Request
import httpx

router = APIRouter()

# 服务地址（从环境变量读取，此处为默认值）
MOL_SERVICE = "http://localhost:8001"   # 3D_test/api.py
IMG_SERVICE = "http://localhost:5000"   # image_identity/app.py
KB_SERVICE  = "http://localhost:8000"   # ai_chem/backend

@router.post("/api/chem/mol/parse")
async def mol_parse(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{MOL_SERVICE}/parse", json=body)
        return resp.json()

@router.post("/api/chem/mol/info")
async def mol_info(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{MOL_SERVICE}/info", json=body)
        return resp.json()

@router.post("/api/chem/img/identify")
async def img_identify(image: UploadFile = File(...)):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{IMG_SERVICE}/identify",
            files={"image": (image.filename, await image.read(), image.content_type)}
        )
        return resp.json()

@router.post("/api/chem/kb/search")
async def kb_search(question: str, top_k: int = 3):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{KB_SERVICE}/api/search",
            params={"question": question, "top_k": top_k}
        )
        return resp.json()
```

将此路由注册到 FastAPI 主应用中，并添加 `httpx` 依赖。

### 3.5 验证标准

- [ ] 三个空插件 `npm install && npm run build` 成功生成 `dist/index.esm.js`
- [ ] CatalogRegistry 注册无报错
- [ ] API Gateway 启动成功，health check 通过

---

## 4. Phase 2：chem-3d-molecule 插件

> 预估工期：5-7 天（核心，最复杂）

### 4.1 manifest.json

```json
{
  "id": "chem-3d-molecule",
  "version": "1.0.0",
  "subject": "chemistry",
  "name": "3D分子可视化",
  "keywords": [
    "分子结构", "3D模型", "分子可视化", "球棍模型", "空间填充",
    "分子式", "SMILES", "化学键", "共价键", "分子构型",
    "甲烷", "苯", "乙醇", "水分子", "二氧化碳", "氨气"
  ],
  "entry": {
    "js": "dist/index.esm.js"
  },
  "capabilities": [
    {
      "component_id": "MoleculeViewer3D",
      "name": "3D分子可视化器",
      "tags": [
        "分子结构", "3D模型", "分子可视化", "球棍模型",
        "空间填充", "分子构型", "化学键", "共价键"
      ],
      "props_schema": {
        "molecule": {
          "type": "string",
          "default": "",
          "description": "分子标识（SMILES字符串、中文名称、英文名称或化学式），如 'C2H5OH'、'乙醇'、'benzene'"
        },
        "render_style": {
          "type": "string",
          "default": "stick",
          "description": "渲染样式：'stick'（球棍模型）或 'sphere'（空间填充模型）"
        },
        "auto_rotate": {
          "type": "boolean",
          "default": false,
          "description": "是否自动旋转"
        }
      },
      "a2ui_hint": "MoleculeViewer3D 组件已内置球棍/空间填充切换按钮和分子信息面板，不需要额外生成 Slider 或 Button 组件。只需通过 properties 传入 molecule（分子名称/SMILES/化学式）即可，组件会自动调用后端 API 获取 3D 结构并渲染。当学生说'展示甲烷的分子结构'时，传入 molecule='甲烷'；当学生说'用球棍模型展示苯'时，传入 molecule='苯', render_style='stick'。",
      "expresses": [
        "有机/无机分子的3D空间结构",
        "球棍模型与空间填充模型",
        "化学键类型（单键、双键、三键）的空间排布",
        "分子的空间构型（四面体、平面三角形、三角锥形等）",
        "原子间的空间距离和角度关系"
      ],
      "educational_use": "帮助学生直观理解分子的三维空间结构，观察化学键的方向性和分子的空间构型",
      "cannot_express": [
        "化学反应过程和机理",
        "电子云和轨道形状",
        "分子间的相互作用力（氢键、范德华力等）",
        "晶体的周期性结构",
        "分子的动态振动"
      ]
    }
  ]
}
```

### 4.2 组件实现要点

#### MoleculeViewer3D.tsx — 主组件

核心流程：

```
node.properties.molecule
       │
       ▼
fetch('/api/chem/mol/parse', { body: { smiles: molecule } })
       │
       ▼
后端返回 PDB 文本
       │
       ▼
parsePDB(pdbText) → { atoms, bonds }
       │
       ▼
Canvas 2D 渲染循环：
  1. 旋转所有原子坐标（rotateY + rotateX）
  2. 透视投影到 2D（project）
  3. Z-buffer 画家排序
  4. 绘制键（线条）
  5. 绘制原子（圆形 + 颜色）
       │
       ▼
鼠标拖拽 → 更新旋转角度 → 重绘
滚轮缩放 → 更新相机距离 → 重绘
```

组件接口遵循 A2UI 规范：

```typescript
interface A2UINode { properties?: Record<string, unknown> }

function parseNum(val: unknown, fallback: number): number {
  const n = Number(val)
  return Number.isFinite(n) ? n : fallback
}

function parseStr(val: unknown, fallback: string): string {
  return typeof val === 'string' ? val : fallback
}

export default function MoleculeViewer3D({ node }: { node: A2UINode }) {
  const props = node.properties ?? {}
  const initMolecule = parseStr(props.molecule, '')
  const initStyle = parseStr(props.render_style, 'stick')
  const initRotate = parseNum(props.auto_rotate, 0) === 1

  const [molecule, setMolecule] = useState(initMolecule)
  const [renderStyle, setRenderStyle] = useState(initStyle)
  const [autoRotate, setAutoRotate] = useState(initRotate)

  useEffect(() => { setMolecule(initMolecule) }, [initMolecule])
  useEffect(() => { setRenderStyle(initStyle) }, [initStyle])
  useEffect(() => { setAutoRotate(initRotate) }, [initRotate])

  // ... Canvas 渲染逻辑 ...
}
```

#### pdb-parser.ts — PDB 格式解析器

解析后端返回的 PDB 文本，提取原子和键信息：

```typescript
interface Atom {
  index: number
  element: string
  x: number
  y: number
  z: number
}

interface Bond {
  atom1: number   // 原子索引（0-based）
  atom2: number
  order: number   // 键级：1=单键, 2=双键, 3=三键
}

function parsePDB(pdbText: string): { atoms: Atom[]; bonds: Bond[] }
```

PDB 格式关键行：
- `ATOM` / `HETATM` 行：原子序号（列 7-11）、元素符号（列 77-78 或 13-14）、3D 坐标（列 31-54）
- `CONECT` 行：键连接关系

> PDB 的 CONECT 行不包含键级信息。如需区分单/双/三键，可改为解析 SDF 格式（MolBlock），其中包含键级。后端 `/parse` 接口同时返回 `pdb` 和 `sdf` 两种格式。

#### projection.ts — 3D 数学核心

```typescript
interface Point3D { x: number; y: number; z: number }

// 绕 Y 轴旋转
function rotateY(p: Point3D, angle: number): Point3D

// 绕 X 轴旋转
function rotateX(p: Point3D, angle: number): Point3D

// 透视投影
function project(
  p: Point3D,
  width: number,
  height: number,
  cameraDistance: number
): { x: number; y: number; z: number }

// 坐标归一化（将 PDB 坐标缩放到适合 Canvas 的范围）
function normalize(atoms: Atom[]): { atoms: Atom[]; scale: number }
```

#### atom-colors.ts — CPK 原子颜色表

内联约 20 种常见元素的颜色和半径，无需外部依赖：

```typescript
const ATOM_COLORS: Record<string, string> = {
  H:  '#FFFFFF', He: '#D9FFFF',
  C:  '#909090', N:  '#3050F8', O:  '#FF0D0D',
  F:  '#90E050', Ne: '#B3E3F5',
  Na: '#AB5CF2', Mg: '#8AFF00', Al: '#BFA6A6',
  Si: '#F0C8A0', P:  '#FF8000', S:  '#FFFF30',
  Cl: '#1FF01F', Ar: '#80D1E3',
  K:  '#8F40D4', Ca: '#3DFF00',
  Fe: '#E06633', Cu: '#C88033', Zn: '#7D80B0',
  Br: '#A62929', I:  '#940094',
}

const ATOM_RADII_STICK: Record<string, number> = {
  H: 0.31, C: 0.77, N: 0.75, O: 0.73,
  F: 0.64, P: 1.07, S: 1.05, Cl: 0.99,
  Br: 1.14, I: 1.33,
  // ... 其余元素
}
```

### 4.3 样式规范

所有 inline style 严格遵循 AhaTutor 设计规范：

| 属性 | 值 |
|------|-----|
| 背景色 | `#faf9f5` |
| 文字色 | `#1b1c1a` |
| 主色 | `#182544` |
| 强调色 | `#775a19` |
| 圆角 | `12px` |
| 字体 | `Manrope, sans-serif` |
| Canvas 尺寸 | 360px x 280px |

### 4.4 改造对照（现有 → 插件）

| 现有实现 (`3D_test/index.html`) | 插件实现 (`MoleculeViewer3D.tsx`) |
|-------------------------------|----------------------------------|
| `3Dmol.createViewer()` | Canvas 2D + 手动透视投影 |
| `viewer.addModel(data, "pdb")` | `parsePDB(pdbText)` 自定义解析 |
| `viewer.setStyle({}, {stick:{}})` | Canvas 绘制球/棍 |
| `viewer.zoomTo()` | `cameraDistance` 参数 |
| `viewer.addModel(data, "sdf")` | SDF 解析器（可选） |
| `document.getElementById('status')` | React `useState` |
| `document.getElementById('info')` | React state 驱动信息面板 |
| `document.getElementById('resetBtn')` | React `<button onClick={...}>` |
| 硬编码颜色 `#333` | `#182544`（项目主色） |
| 无外层容器 | `<div style={{ background: '#faf9f5', borderRadius: 12, padding: 12 }}>` |

### 4.5 验证标准

- [ ] Gallery 预览正常显示默认分子
- [ ] 对话测试 "展示甲烷的分子结构" → 渲染甲烷 3D 模型
- [ ] 对话测试 "用空间填充模型看苯" → 切换渲染模式
- [ ] 对话测试 "乙醇的 3D 结构" → 正确渲染
- [ ] 鼠标拖拽旋转流畅
- [ ] 滚轮缩放正常
- [ ] 球棍/空间填充切换正常
- [ ] 分子信息面板正确显示原子数、键数、分子量、分子式
- [ ] 多种输入格式（SMILES、中文名、英文名、化学式）均支持

---

## 5. Phase 3：chem-image-recognizer 插件

> 预估工期：2-3 天

### 5.1 manifest.json

```json
{
  "id": "chem-image-recognizer",
  "version": "1.0.0",
  "subject": "chemistry",
  "name": "化学结构图像识别",
  "keywords": [
    "图像识别", "化学结构", "分子识别", "结构式", "图片识别",
    "SMILES", "化学式识别", "拍照识别"
  ],
  "entry": {
    "js": "dist/index.esm.js"
  },
  "capabilities": [
    {
      "component_id": "StructureRecognizer",
      "name": "化学结构图像识别器",
      "tags": [
        "图像识别", "化学结构", "结构式", "图片识别",
        "SMILES识别", "拍照识别", "分子式图片"
      ],
      "props_schema": {
        "auto_start": {
          "type": "boolean",
          "default": false,
          "description": "是否自动弹出上传界面。默认 false，等待用户主动上传"
        }
      },
      "a2ui_hint": "StructureRecognizer 组件自带图片上传区域（支持拖拽和点击上传），以及识别结果展示（SMILES + 2D分子结构图）。不需要额外生成任何外部控件。当学生说'识别这张化学结构图'、'这是什么分子'并附带图片时，设置 auto_start=true 弹出上传界面。注意：本组件需要学生主动上传图片，LLM 无法直接传入图片，因此只需在对话中提示学生使用该工具即可。",
      "expresses": [
        "从图片中识别化学分子结构式",
        "将识别结果转换为标准 SMILES 字符串",
        "展示识别后的 2D 分子结构图",
        "SMILES 字符串的复制功能"
      ],
      "educational_use": "帮助学生将纸质或截图中的化学结构式快速转换为可编辑、可搜索的数字格式",
      "cannot_express": [
        "化学反应方程式的识别",
        "手写化学式的识别（仅支持印刷体/电子版结构式）",
        "复杂立体化学（R/S构型）的识别",
        "非化学结构图片的识别"
      ]
    }
  ]
}
```

### 5.2 组件实现要点

#### StructureRecognizer.tsx — 主组件

核心流程：

```
用户拖拽/点击上传图片
       │
       ▼
图片预览 + "开始识别" 按钮
       │
       ▼
fetch('/api/chem/img/identify', {
  method: 'POST',
  body: FormData (图片文件)
})
       │
       ▼
后端返回 { success, smiles, image_data (base64) }
       │
       ▼
展示识别结果：
  - SMILES 字符串 + 复制按钮
  - 2D 分子结构图（base64 图片）
```

组件接口：

```typescript
interface A2UINode { properties?: Record<string, unknown> }

export default function StructureRecognizer({ node }: { node: A2UINode }) {
  const props = node.properties ?? {}
  const initAutoStart = props.auto_start === true

  const [autoStart, setAutoStart] = useState(initAutoStart)
  const [preview, setPreview] = useState<string | null>(null)
  const [result, setResult] = useState<{ smiles: string; imageData: string } | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => { setAutoStart(initAutoStart) }, [initAutoStart])

  // 拖拽上传处理
  const handleDrop = (e: React.DragEvent) => { /* ... */ }

  // 点击上传处理
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => { /* ... */ }

  // 识别 API 调用
  const handleIdentify = async () => {
    setLoading(true)
    const formData = new FormData()
    formData.append('image', selectedFile)
    const res = await fetch('/api/chem/img/identify', {
      method: 'POST',
      body: formData,
    })
    const data = await res.json()
    setResult({ smiles: data.smiles, imageData: data.image_data })
    setLoading(false)
  }

  // 复制 SMILES
  const handleCopy = () => { navigator.clipboard.writeText(result.smiles) }

  // ... 渲染逻辑 ...
}
```

### 5.3 改造对照

| 现有实现 (`image_identity/`) | 插件实现 (`StructureRecognizer.tsx`) |
|---------------------------|-------------------------------------|
| `script.js` 中 `dropZone.addEventListener` | React `onDragOver` / `onDrop` 事件处理 |
| `document.getElementById('preview')` | React `useState` + `<img src={preview}>` |
| `document.getElementById('resultImage')` | React state 驱动 `<img src={result.imageData}>` |
| `fetch('/identify', {body: formData})` | `fetch('/api/chem/img/identify', ...)` |
| `resultImage.src = data.image_data` | `<img src={result.image_data}>` |
| `navigator.clipboard.writeText(smiles)` | 保留，绑定为 `onClick` |
| `style.css` 暗色主题（#0f172a 背景） | AhaTutor 设计规范（#faf9f5 背景，inline style） |

### 5.4 验证标准

- [ ] Gallery 预览显示上传区域
- [ ] 拖拽上传正常
- [ ] 点击上传正常
- [ ] 图片预览正确
- [ ] 识别返回 SMILES 和 2D 分子图
- [ ] 复制 SMILES 功能正常
- [ ] 加载状态和错误处理正常

---

## 6. Phase 4：chem-knowledge-qa 插件

> 预估工期：2-3 天

### 6.1 manifest.json

```json
{
  "id": "chem-knowledge-qa",
  "version": "1.0.0",
  "subject": "chemistry",
  "name": "化学知识库检索",
  "keywords": [
    "化学知识", "教材", "知识点", "化学概念", "定义",
    "化学原理", "化学性质", "物理性质", "化学方程式",
    "氧化还原", "离子反应", "有机化学", "无机化学",
    "元素周期表", "化学键", "摩尔", "物质的量"
  ],
  "entry": {
    "js": "dist/index.esm.js",
    "vector_db": "knowledge/vector.db"
  },
  "capabilities": [
    {
      "component_id": "ChemKnowledgeSearch",
      "name": "化学知识检索卡片",
      "tags": [
        "化学知识", "教材内容", "知识点", "化学概念",
        "定义", "化学原理", "化学性质", "教材原文"
      ],
      "props_schema": {
        "query": {
          "type": "string",
          "default": "",
          "description": "搜索查询关键词或问题，如 '什么是化学键'、'氧化还原反应的本质'"
        },
        "max_results": {
          "type": "number",
          "default": 3,
          "min": 1,
          "max": 5,
          "description": "返回的最大结果数量"
        }
      },
      "a2ui_hint": "ChemKnowledgeSearch 组件用于展示从教材中检索到的知识内容。当学生提出化学概念问题时（如'什么是化学键'、'氧化还原反应的本质是什么'），通过 properties 传入 query 问题文本，组件会调用后端 RAG 检索并展示教材原文片段。组件自带折叠/展开功能，不需要额外生成外部控件。当 LLM 已经能完整回答问题时，不需要调用此组件；仅在需要引用教材原文作为佐证时使用。",
      "expresses": [
        "从高中化学教材中检索相关知识点原文",
        "展示知识点的教材出处和章节信息",
        "多段相关内容的聚合展示",
        "知识点的相关性评分"
      ],
      "educational_use": "帮助学生和教师快速定位教材中的相关知识原文，辅助学习和教学",
      "cannot_express": [
        "化学问题的 AI 智能解答（这是 LLM 本身的能力）",
        "实时计算（如摩尔计算、化学方程式配平）",
        "分子结构的可视化展示",
        "化学反应的动态模拟"
      ]
    }
  ]
}
```

### 6.2 组件实现要点

#### ChemKnowledgeSearch.tsx — 主组件

核心流程：

```
node.properties.query
       │
       ▼
fetch('/api/chem/kb/search', {
  body: { question: query, top_k: max_results }
})
       │
       ▼
后端返回 { question, keywords, results, total }
results: [{ content, metadata: { section, source, chunk_id }, relevance_score }]
       │
       ▼
渲染可折叠知识卡片列表：
  ┌─────────────────────────────┐
  │ 📖 必修第一册 > 物质的分类   │
  │ 相关度: 0.85               │
  │                             │
  │ 化学键是指在分子或晶体中，   │
  │ 相邻原子（或离子）之间强烈   │
  │ 的相互作用...               │
  │                    [展开/收起]│
  └─────────────────────────────┘
```

组件接口：

```typescript
interface A2UINode { properties?: Record<string, unknown> }

export default function ChemKnowledgeSearch({ node }: { node: A2UINode }) {
  const props = node.properties ?? {}
  const initQuery = parseStr(props.query, '')
  const initMaxResults = parseNum(props.max_results, 3)

  const [query, setQuery] = useState(initQuery)
  const [maxResults, setMaxResults] = useState(initMaxResults)
  const [results, setResults] = useState<KnowledgeResult[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => { setQuery(initQuery) }, [initQuery])
  useEffect(() => { setMaxResults(initMaxResults) }, [initMaxResults])

  useEffect(() => {
    if (!query) return
    setLoading(true)
    fetch('/api/chem/kb/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: query, top_k: maxResults }),
    })
      .then(res => res.json())
      .then(data => setResults(data.results || []))
      .finally(() => setLoading(false))
  }, [query, maxResults])

  // ... 渲染知识卡片列表 ...
}
```

### 6.3 知识库准备

使用 AhaTutor 的 `build-knowledge.py` 工具，将现有教材数据转换为向量数据库：

```bash
python tools/build-knowledge.py \
  --input plugins/chem-knowledge-qa/knowledge/raw \
  --output plugins/chem-knowledge-qa/knowledge/vector.db
```

数据来源：`ai_chem/backend/data/collected/textbok/` 下的 JSON/MD 文件。

工具会将文档分块（约 500 字，50 字重叠）存入 SQLite，支持 FTS5 全文检索。

> 如果不需要知识库增强 LLM，可以删除 `entry.vector_db` 字段或保持 `knowledge/` 目录为空。组件本身的 API 检索不依赖 vector.db。

### 6.4 验证标准

- [ ] Gallery 预览显示知识卡片
- [ ] "什么是化学键" 查询返回教材原文
- [ ] "氧化还原反应的本质" 查询返回正确结果
- [ ] 知识卡片可折叠/展开
- [ ] 来源章节信息正确显示
- [ ] 空结果和加载状态处理正常

---

## 7. Phase 5：集成测试与优化

> 预估工期：2-3 天

### 7.1 LLM 意图路由测试

验证不同自然语言表述下，LLM 是否正确选择插件：

| 用户表述 | 期望调用插件 | 说明 |
|---------|------------|------|
| "展示甲烷的分子结构" | `chem-3d-molecule` | molecule='甲烷' |
| "用球棍模型看苯" | `chem-3d-molecule` | molecule='苯', render_style='stick' |
| "乙醇的 3D 结构" | `chem-3d-molecule` | molecule='乙醇' |
| "识别这张图里的化学结构" | `chem-image-recognizer` | auto_start=true |
| "这是什么分子"（附图） | `chem-image-recognizer` | auto_start=true |
| "什么是共价键" | `chem-knowledge-qa` 或 LLM 直接回答 | 取决于 LLM 判断 |
| "氧化还原反应的本质" | `chem-knowledge-qa` | query='氧化还原反应的本质' |
| "苯的 3D 结构是什么样" | `chem-3d-molecule` | molecule='苯' |
| "给我看看二氧化碳" | `chem-3d-molecule` | molecule='CO2' |
| "钠的原子结构" | LLM 直接回答 | 不应调用任何插件 |

### 7.2 性能优化

| 优化项 | 方法 |
|--------|------|
| 3D 渲染性能 | 超过 100 个原子时显示简化模型；避免每帧重算不变部分 |
| API 响应缓存 | 相同 molecule 输入缓存 PDB 解析结果（Map<string, PDBData>） |
| 资源清理 | 组件卸载时 `cancelAnimationFrame`，清除缓存 |

### 7.3 错误处理

| 场景 | 处理方式 |
|------|---------|
| 后端不可用 | 显示 "服务暂不可用，请稍后重试" |
| 无效分子输入 | 显示 "无法识别该分子，请检查输入" + 建议正确格式 |
| 网络超时 | 30s 超时 + "请求超时" 提示 + 重试按钮 |
| 图片识别失败 | 显示 DECIMER 返回的错误信息 |
| 知识库无结果 | 显示 "未找到相关教材内容" |

### 7.4 样式一致性检查

所有组件遵循 AhaTutor 设计规范：

```typescript
const THEME = {
  bg: '#faf9f5',
  text: '#1b1c1a',
  primary: '#182544',
  accent: '#775a19',
  radius: 12,
  font: 'Manrope, sans-serif',
}
```

---

## 8. 关键文件映射

### 现有代码 → 插件代码

| 现有文件 | 插件文件 | 改造方式 |
|---------|---------|---------|
| `3D_test/index.html` | `chem-3d-molecule/src/MoleculeViewer3D.tsx` | HTML+JS → React 组件，3Dmol.js → Canvas 2D |
| `3D_test/api.py` `/parse` | API Gateway `/api/chem/mol/parse` | 后端保留，新增转发路由 |
| `3D_test/api.py` `/info` | API Gateway `/api/chem/mol/info` | 后端保留，新增转发路由 |
| `3D_test/data/name_mapping.json` | 后端服务内部使用 | 不变，后端 API 已封装名称解析 |
| `image_identity/static/script.js` | `chem-image-recognizer/src/StructureRecognizer.tsx` | 原生 JS → React hooks |
| `image_identity/static/style.css` | inline style | 暗色主题 → AhaTutor 设计规范 |
| `image_identity/app.py` `/identify` | API Gateway `/api/chem/img/identify` | 后端保留，新增转发路由 |
| `ai_chem/backend/services/rag_service.py` | API Gateway `/api/chem/kb/search` | 后端保留，新增转发路由 |
| `ai_chem/backend/data/collected/textbok/` | `chem-knowledge-qa/knowledge/` (vector.db) | JSON → SQLite FTS5 |

### 实施过程中需重点参考的文件

1. `plugin-development-guide.md` — 插件开发规范，所有组件必须遵循
2. `3D_test/api.py` — PDB/SDF 输出格式定义，前端解析器需匹配
3. `3D_test/index.html` — 现有 3D 交互逻辑的参考基准
4. `image_identity/app.py` — FormData 上传格式定义
5. `image_identity/static/script.js` — 现有上传/识别交互的参考基准
6. `ai_chem/backend/services/rag_service.py` — RAG 检索返回格式定义

---

## 9. 验证方式

### 9.1 构建验证

```bash
cd plugins/chem-3d-molecule && npm run build    # 生成 dist/index.esm.js
cd plugins/chem-image-recognizer && npm run build
cd plugins/chem-knowledge-qa && npm run build
```

### 9.2 Gallery 验证

```
http://localhost:5173/?gallery=1
```

确认三个组件预览正常显示。

### 9.3 对话验证

| 测试用例 | 期望行为 |
|---------|---------|
| "展示甲烷的分子结构" | 调用 MoleculeViewer3D，传入 molecule='甲烷' |
| "用空间填充模型看苯" | 调用 MoleculeViewer3D，传入 molecule='苯', render_style='sphere' |
| "识别这张图里的化学结构" | 调用 StructureRecognizer，auto_start=true |
| "氧化还原反应的本质" | 调用 ChemKnowledgeSearch，传入 query='氧化还原反应的本质' |
| "钠的原子结构" | LLM 直接回答，不调用任何插件 |

### 9.4 后端验证

```bash
curl -X POST http://localhost:8000/api/chem/mol/parse \
  -H "Content-Type: application/json" \
  -d '{"smiles": "甲烷"}'
# 应返回 { success: true, smiles: "C", pdb: "...", sdf: "..." }

curl -X POST http://localhost:8000/api/chem/kb/search \
  -H "Content-Type: application/json" \
  -d '{"question": "什么是化学键", "top_k": 3}'
# 应返回检索结果数组
```
