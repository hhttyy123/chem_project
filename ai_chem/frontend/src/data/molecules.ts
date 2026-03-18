// 化学物质名称到 SMILES 的映射
// 从 name_mapping.json 加载
import nameMappingData from './name_mapping.json'

// 展平后的映射表
const MOLECULE_MAP: Record<string, string> = {}

// 常见误匹配词黑名单（这些词不应该被匹配）
const BLACKLIST = new Set([
  '酸', '碱', '盐', '氧化物', '氢化物', '硫化物',
  '氯化物', '硝酸盐', '硫酸盐', '碳酸盐',
  '溶液', '气体', '液体', '固体',
  '反应', '化合物', '单质', '元素',
  '电子', '质子', '中子', '原子', '分子', '离子',
  '化学键', '共价键', '离子键', '金属键',
  '氧化', '还原', '氧化剂', '还原剂',
  '催化剂', '指示剂', '溶剂', '溶质',
  '摩尔', '摩尔质量', '摩尔数',
  '浓度', '质量', '体积', '密度',
  '熔点', '沸点', '燃点',
  '酸碱', '中性', '酸性', '碱性',
  '有机', '无机', '芳香', '脂肪',
  '饱和', '不饱和',
  '一个', '两个', '三种', '多种',
  '物质', '化学', '物理',
])

// 检查是否是 SMILES 格式
function isSMILES(str: string): boolean {
  // SMILES 通常包含这些字符，长度合理
  const hasValidChars = /^[CNOPSFClBrI()\[\]=.#@+\-H0-9a-z]+$/i.test(str)
  const validLength = str.length > 0 && str.length < 500
  // 不是纯数字
  const notAllNumbers = !/^\d+$/.test(str)
  return hasValidChars && validLength && notAllNumbers
}

// 递归展平映射表
function flattenMapping(obj: any): void {
  if (!obj || typeof obj !== 'object') return

  for (const key in obj) {
    if (key === '_metadata') continue

    const value = obj[key]

    if (typeof value === 'string' && isSMILES(value)) {
      // 这是一个 SMILES 值，添加到映射表
      MOLECULE_MAP[key] = value
    } else if (typeof value === 'object' && value !== null) {
      // 递归处理嵌套对象
      flattenMapping(value)
    }
  }
}

// 展平映射表
flattenMapping(nameMappingData)

// 判断名称是否为纯公式（只含字母、数字、+、-）
function isFormulaOnly(name: string): boolean {
  return /^[a-zA-Z0-9+\-]+$/.test(name)
}

// 创建按长度排序的名称列表（从长到短），确保优先匹配更长的词
const sortedNames = Object.keys(MOLECULE_MAP)
  .filter(name => {
    // 纯公式（如 CO、NO、H2、O2）至少需要 2 个字符
    // 注意：过短的公式可能误匹配，但常见气体分子需要支持
    if (isFormulaOnly(name)) return name.length >= 2
    // 中文或混合名称保持 2 字符最低限制
    return name.length >= 2
  })
  .filter(name => !BLACKLIST.has(name)) // 过滤黑名单
  .sort((a, b) => b.length - a.length) // 按长度降序排序

// 允许的边界字符（用于判断词边界）
const BOUNDARY_CHARS = new Set([
  ' ', '\t', '\n', '\r',
  '(', ')', '[', ']', '{', '}',
  '，', '。', '！', '？', '；', '：',
  ',', '.', '!', '?', ';', ':',
  '"', "'", '`',
  '、', '《', '》', '【', '】',
  '·', '〜', '～', '—', '–',
  // Unicode 下标数字（CO₂ 中的 ₂ 等）
  '₀', '₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉',
  // Unicode 上标数字
  '⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹',
])

/**
 * 检查字符是否是词边界
 */
function isBoundary(char: string): boolean {
  return BOUNDARY_CHARS.has(char)
}

/**
 * 检查字符是否是字母或数字（用于判断是否在单词内部）
 */
function isAlphanumeric(char: string): boolean {
  return /[a-zA-Z0-9]/.test(char)
}

/**
 * 检查字符是否是中文字符
 */
function isChineseChar(char: string): boolean {
  return /[\u4e00-\u9fff\u3400-\u4dbf]/.test(char)
}

/**
 * 检查是否在单词内部（避免部分匹配）
 * - 对中文名称：前后不能紧邻其他中文字符（防止截断匹配，如在"苯乙烯"中匹配"乙烯"）
 * - 对英文/公式名称：前后不能紧邻字母数字
 */
function isInWord(text: string, start: number, end: number): boolean {
  const before = start > 0 ? text[start - 1] : ''
  const after = end < text.length ? text[end] : ''
  const matchedText = text.substring(start, end)

  const hasChinese = /[\u4e00-\u9fff\u3400-\u4dbf]/.test(matchedText)

  if (hasChinese) {
    // 中文名称：若首字或末字与相邻中文字符紧连，则视为在词内部
    const firstChar = matchedText[0] ?? ''
    const lastChar = matchedText[matchedText.length - 1] ?? ''
    const beforeIsChinese = before && isChineseChar(before) && isChineseChar(firstChar)
    const afterIsChinese = after && isChineseChar(after) && isChineseChar(lastChar)
    return !!(beforeIsChinese || afterIsChinese)
  }

  // 英文/公式名称：前后不能紧邻字母数字
  const beforeIsWord = before && isAlphanumeric(before) && !isBoundary(before)
  const afterIsWord = after && isAlphanumeric(after) && !isBoundary(after)
  return !!(beforeIsWord || afterIsWord)
}

/**
 * 获取分子的 SMILES
 */
export function getMoleculeSmiles(name: string): string | undefined {
  return MOLECULE_MAP[name]
}

/**
 * 在文本中查找所有化学物质
 */
export function findMoleculesInText(text: string): Array<{
  name: string
  smiles: string
  start: number
  end: number
}> {
  const results: Array<{ name: string; smiles: string; start: number; end: number }> = []
  const matchedRanges: Array<[number, number]> = []

  for (const name of sortedNames) {
    let searchStart = 0

    while (true) {
      const index = text.indexOf(name, searchStart)
      if (index === -1) break

      const endIndex = index + name.length

      // 检查是否已经匹配过（重叠）
      const overlaps = matchedRanges.some(([start, end]) =>
        !(endIndex <= start || index >= end)
      )

      if (overlaps) {
        searchStart = endIndex
        continue
      }

      // 检查是否在单词内部
      if (isInWord(text, index, endIndex)) {
        searchStart = endIndex
        continue
      }

      // 找到一个有效的匹配
      const smiles = MOLECULE_MAP[name]
      if (smiles) {
        results.push({
          name,
          smiles,
          start: index,
          end: endIndex
        })
        matchedRanges.push([index, endIndex])
      }

      searchStart = endIndex
    }
  }

  // 按起始位置排序
  return results.sort((a, b) => a.start - b.start)
}

// 导出映射表供其他模块使用
export { MOLECULE_MAP }
