// 分子知识库：包含分子的讲解和书中位置
export interface MoleculeKnowledge {
  name: string
  description: string
  properties: string[]
  textbookLocation: string
  chapter: string
}

const MOLECULE_KNOWLEDGE: Record<string, MoleculeKnowledge> = {
  "水": {
    name: "水",
    description: "水是由氢、氧两种元素组成的无机物，无毒、可饮用。在常温常压下为无色无味的透明液体，被称为人类生命的源泉。",
    properties: [
      "分子式：H₂O",
      "相对分子质量：18",
      "熔点：0℃，沸点：100℃",
      "密度：1g/cm³ (4℃)",
      "极性分子，是良好的溶剂"
    ],
    textbookLocation: "必修第一册 第一章 第2节",
    chapter: "第一章 物质的量"
  },
  "氨": {
    name: "氨",
    description: "氨气是无色、有刺激性气味的气体，易液化，极易溶于水。氨分子呈三角锥形，氮原子位于锥顶，三个氢原子位于锥底。",
    properties: [
      "分子式：NH₃",
      "相对分子质量：17",
      "熔点：-77.7℃，沸点：-33.5℃",
      "密度：0.771g/L (标准状况)",
      "极易溶于水 (1体积水溶解700体积氨气)"
    ],
    textbookLocation: "必修第二册 第五章 第2节",
    chapter: "第五章 氮族元素"
  },
  "甲烷": {
    name: "甲烷",
    description: "甲烷是最简单的有机化合物，是天然气、沼气、坑气等的主要成分。正四面体结构，键角为109°28′。",
    properties: [
      "分子式：CH₄",
      "相对分子质量：16",
      "熔点：-182.5℃，沸点：-161.5℃",
      "密度：0.717g/L (标准状况)",
      "不溶于水，易燃烧"
    ],
    textbookLocation: "必修第二册 第七章 第1节",
    chapter: "第七章 烃"
  },
  "乙烷": {
    name: "乙烷",
    description: "乙烷是烷烃系列中最简单的含碳-碳单键的化合物，存在于天然气中。",
    properties: [
      "分子式：C₂H₆",
      "相对分子质量：30",
      "熔点：-183℃，沸点：-88.6℃",
      "无色无味气体",
      "不溶于水"
    ],
    textbookLocation: "必修第二册 第七章 第1节",
    chapter: "第七章 烷烃"
  },
  "乙烯": {
    name: "乙烯",
    description: "乙烯是石油化工的重要原料，也是植物生长的调节剂（果实催熟剂）。分子中含碳碳双键，平面结构。",
    properties: [
      "分子式：C₂H₄",
      "相对分子质量：28",
      "熔点：-169.2℃，沸点：-103.7℃",
      "密度：1.25g/L (标准状况)",
      "难溶于水，易燃烧"
    ],
    textbookLocation: "必修第二册 第七章 第2节",
    chapter: "第七章 烯烃"
  },
  "乙炔": {
    name: "乙炔",
    description: "乙炔俗名电石气，是最简单的炔烃。分子中含碳碳三键，直线型结构，键角180°。",
    properties: [
      "分子式：C₂H₂",
      "相对分子质量：26",
      "熔点：-80.8℃，沸点：-84℃",
      "密度：1.16g/L (标准状况)",
      "难溶于水，纯乙炔无味"
    ],
    textbookLocation: "必修第二册 第七章 第3节",
    chapter: "第七章 炔烃"
  },
  "苯": {
    name: "苯",
    description: "苯是最简单的芳香烃，具有特殊的香味（苯香味）。平面正六边形结构，碳碳键长介于单键和双键之间。",
    properties: [
      "分子式：C₆H₆",
      "相对分子质量：78",
      "熔点：5.5℃，沸点：80.1℃",
      "密度：0.88g/cm³",
      "不溶于水，易溶于有机溶剂"
    ],
    textbookLocation: "必修第二册 第七章 第4节",
    chapter: "第七章 芳香烃"
  },
  "乙醇": {
    name: "乙醇",
    description: "乙醇俗称酒精，是常用的有机溶剂和消毒剂。羟基(-OH)直接连在链烃基上，可以看作乙烷分子中的一个氢原子被羟基取代。",
    properties: [
      "分子式：C₂H₅OH 或 C₂H₆O",
      "相对分子质量：46",
      "熔点：-114.1℃，沸点：78.3℃",
      "密度：0.79g/cm³",
      "与水以任意比互溶"
    ],
    textbookLocation: "必修第二册 第八章 第2节",
    chapter: "第八章 醇"
  },
  "甲醇": {
    name: "甲醇",
    description: "甲醇是最简单的醇，有剧毒，误饮可使眼睛失明。工业酒精中含有甲醇，不可饮用。",
    properties: [
      "分子式：CH₃OH 或 CH₄O",
      "相对分子质量：32",
      "熔点：-97.8℃，沸点：64.7℃",
      "密度：0.79g/cm³",
      "与水、乙醇互溶"
    ],
    textbookLocation: "必修第二册 第八章 第2节",
    chapter: "第八章 醇"
  },
  "乙酸": {
    name: "乙酸",
    description: "乙酸俗称醋酸，是食醋的主要成分。有强烈的刺激性气味，易溶于水，低于16.6℃时会凝结成冰状固体（冰醋酸）。",
    properties: [
      "分子式：CH₃COOH 或 C₂H₄O₂",
      "相对分子质量：60",
      "熔点：16.6℃，沸点：117.9℃",
      "密度：1.05g/cm³",
      "易溶于水，有腐蚀性"
    ],
    textbookLocation: "必修第二册 第八章 第3节",
    chapter: "第八章 羧酸"
  },
  "乙醛": {
    name: "乙醛",
    description: "乙醛是有刺激性气味的液体，易挥发，易燃烧。是重要的有机合成原料，可用于制造乙酸、乙醇等。",
    properties: [
      "分子式：CH₃CHO 或 C₂H₄O",
      "相对分子质量：44",
      "熔点：-123℃，沸点：20.8℃",
      "密度：0.78g/cm³",
      "与水、乙醇互溶"
    ],
    textbookLocation: "必修第二册 第八章 第2节",
    chapter: "第八章 醛"
  },
  "丙酮": {
    name: "丙酮",
    description: "丙酮是最简单的酮，有特殊香味，易挥发，易燃烧。是重要的有机溶剂和化工原料。",
    properties: [
      "分子式：CH₃COCH₃ 或 C₃H₆O",
      "相对分子质量：58",
      "熔点：-94.6℃，沸点：56.5℃",
      "密度：0.79g/cm³",
      "与水、乙醇互溶"
    ],
    textbookLocation: "必修第二册 第八章 第2节",
    chapter: "第八章 酮"
  },
  "氢氧化钠": {
    name: "氢氧化钠",
    description: "氢氧化钠俗称烧碱、火碱、苛性钠，是强碱。白色固体，极易溶于水，溶于水时放出大量热，有强腐蚀性。",
    properties: [
      "化学式：NaOH",
      "相对分子质量：40",
      "熔点：318.4℃",
      "易潮解，强腐蚀性",
      "易溶于水，水溶液呈强碱性"
    ],
    textbookLocation: "必修第一册 第二章 第2节",
    chapter: "第二章 碱金属"
  },
  "氢氧化钙": {
    name: "氢氧化钙",
    description: "氢氧化钙俗称熟石灰、消石灰，是强碱。白色粉末，微溶于水，其水溶液俗称石灰水。",
    properties: [
      "化学式：Ca(OH)₂",
      "相对分子质量：74",
      "微溶于水，水溶液呈碱性",
      "可用于改良酸性土壤",
      "制取漂白粉的原料"
    ],
    textbookLocation: "必修第一册 第四章 第3节",
    chapter: "第四章 碱金属元素"
  },
  "盐酸": {
    name: "盐酸",
    description: "盐酸是氯化氢气体的水溶液，是强酸。浓盐酸易挥发，在空气中形成白雾。",
    properties: [
      "化学式：HCl",
      "相对分子质量：36.5",
      "浓盐酸浓度约37%",
      "易挥发，有刺激性气味",
      "强酸性，强腐蚀性"
    ],
    textbookLocation: "必修第一册 第四章 第1节",
    chapter: "第四章 卤素"
  },
  "硫酸": {
    name: "硫酸",
    description: "硫酸是重要的化工原料，是强酸。浓硫酸有吸水性、脱水性和强氧化性。",
    properties: [
      "化学式：H₂SO₄",
      "相对分子质量：98",
      "熔点：10.5℃，沸点：338℃",
      "密度：1.84g/cm³",
      "难挥发，强酸性，强腐蚀性"
    ],
    textbookLocation: "必修第一册 第六章 第2节",
    chapter: "第六章 氧族元素"
  },
  "硝酸": {
    name: "硝酸",
    description: "硝酸是重要的化工原料，是强酸。浓硝酸不稳定，见光易分解，应保存在棕色瓶中。",
    properties: [
      "化学式：HNO₃",
      "相对分子质量：63",
      "熔点：-42℃，沸点：83℃",
      "易挥发，有刺激性气味",
      "强酸性，强氧化性"
    ],
    textbookLocation: "必修第一册 第六章 第3节",
    chapter: "第六章 氮族元素"
  },
  "二氧化碳": {
    name: "二氧化碳",
    description: "二氧化碳是碳的氧化物，无色无味气体，密度比空气大，能溶于水。固态二氧化碳俗称干冰。",
    properties: [
      "化学式：CO₂",
      "相对分子质量：44",
      "熔点：-56.6℃ (5.1atm)",
      "密度：1.98g/L (标准状况)",
      "能溶于水，与水反应生成碳酸"
    ],
    textbookLocation: "必修第一册 第六章 第1节",
    chapter: "第六章 碳族元素"
  },
  "一氧化碳": {
    name: "一氧化碳",
    description: "一氧化碳是碳的不完全氧化物，无色无味有毒气体，有可燃性和还原性。",
    properties: [
      "化学式：CO",
      "相对分子质量：28",
      "熔点：-199℃，沸点：-191.5℃",
      "密度：1.25g/L (标准状况)",
      "难溶于水，有剧毒"
    ],
    textbookLocation: "必修第一册 第六章 第1节",
    chapter: "第六章 碳族元素"
  },
  "氯气": {
    name: "氯气",
    description: "氯气是黄绿色有刺激性气味的剧毒气体，密度比空气大，能溶于水。有强氧化性。",
    properties: [
      "化学式：Cl₂",
      "相对分子质量：71",
      "熔点：-101℃，沸点：-34.6℃",
      "密度：3.21g/L (标准状况)",
      "能溶于水，与水反应"
    ],
    textbookLocation: "必修第一册 第四章 第1节",
    chapter: "第四章 卤素"
  },
  "氯化钠": {
    name: "氯化钠",
    description: "氯化钠俗称食盐，白色晶体，易溶于水。是重要的调味品和化工原料。",
    properties: [
      "化学式：NaCl",
      "相对分子质量：58.5",
      "熔点：801℃，沸点：1413℃",
      "白色立方晶体",
      "易溶于水，水溶液呈中性"
    ],
    textbookLocation: "必修第一册 第二章 第1节",
    chapter: "第二章 碱金属"
  },
  "碳酸钙": {
    name: "碳酸钙",
    description: "碳酸钙是石灰石、大理石的主要成分，白色固体，不溶于水。高温分解生成氧化钙和二氧化碳。",
    properties: [
      "化学式：CaCO₃",
      "相对分子质量：100",
      "熔点：1339℃ (分解)",
      "白色固体",
      "不溶于水，溶于盐酸"
    ],
    textbookLocation: "必修第一册 第三章 第1节",
    chapter: "第三章 物质的量"
  },
  "硫酸铜": {
    name: "硫酸铜",
    description: "硫酸铜无水时为白色粉末，常见的五水硫酸铜为蓝色晶体，俗称胆矾。",
    properties: [
      "化学式：CuSO₄",
      "相对分子质量：160",
      "无水物为白色，五水合物为蓝色",
      "易溶于水，水溶液呈蓝色",
      "有毒，用于杀菌剂"
    ],
    textbookLocation: "必修第一册 第三章 第2节",
    chapter: "第三章 物质的分类"
  },
  "高锰酸钾": {
    name: "高锰酸钾",
    description: "高锰酸钾是紫黑色晶体，溶于水呈紫红色溶液，是强氧化剂。",
    properties: [
      "化学式：KMnO₄",
      "相对分子质量：158",
      "紫黑色晶体",
      "溶于水呈紫红色",
      "强氧化性，受热易分解"
    ],
    textbookLocation: "必修第二册 第四章 第2节",
    chapter: "第四章 氧化还原"
  },
}

/**
 * 获取分子的知识点
 */
export function getMoleculeKnowledge(name: string): MoleculeKnowledge | null {
  return MOLECULE_KNOWLEDGE[name] || null
}

/**
 * 检查分子是否有知识点
 */
export function hasMoleculeKnowledge(name: string): boolean {
  return name in MOLECULE_KNOWLEDGE
}

// 导出所有知识
export { MOLECULE_KNOWLEDGE }
