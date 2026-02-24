/**
 * GLM-4 API 客户端
 * 智谱 AI 接口
 */

const API_KEY = 'a70bc62616f94298a2825a72fd2a53d3.g6tzYCptWLsQUzLt'
const API_URL = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
const BACKEND_API_URL = 'http://localhost:8000/api'

interface Message {
  role: 'system' | 'user' | 'assistant'
  content: string
}

interface ChatRequest {
  model: string
  messages: Message[]
  temperature?: number
  top_p?: number
  max_tokens?: number
}

interface ChatResponse {
  id: string
  created: number
  model: string
  choices: Array<{
    index: number
    message: {
      role: string
      content: string
    }
    finish_reason: string
  }>
  usage: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}

/**
 * 调用 GLM-4 API
 */
export async function chatWithGLM(messages: Message[]): Promise<string> {
  try {
    // 直接使用 API Key（智谱支持 Bearer 认证）
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`,
      },
      body: JSON.stringify({
        model: 'glm-4.6',
        messages,
        temperature: 0.7,
        top_p: 0.9,
        max_tokens: 8192,
      } as ChatRequest),
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(`API 请求失败: ${response.status} - ${error}`)
    }

    const data: ChatResponse = await response.json()

    if (data.choices?.[0]?.message?.content) {
      return data.choices[0].message.content
    }

    throw new Error('API 返回数据格式错误')
  } catch (error) {
    console.error('GLM API 调用失败:', error)
    throw error
  }
}

/**
 * 从后端检索教材内容
 */
async function searchTextbooks(question: string): Promise<string> {
  try {
    const response = await fetch(`${BACKEND_API_URL}/search?question=${encodeURIComponent(question)}&top_k=3`)
    if (!response.ok) return ''

    const data = await response.json()
    if (!data.results || data.results.length === 0) return ''

    // 格式化教材内容作为参考资料
    const textbookContent = data.results
      .map((r: any) => `【${r.metadata?.source || '教材'}】\n${r.content}`)
      .join('\n\n')

    return textbookContent
  } catch (error) {
    console.error('检索教材失败:', error)
    return ''
  }
}

/**
 * 化学助教对话（带教材参考）
 */
export async function chatWithChemistryTutor(question: string, history: Message[] = []): Promise<string> {
  // 1. 先检索教材内容作为参考
  const textbookContent = await searchTextbooks(question)

  // 2. 构建 system prompt
  let systemPrompt = `你是一个专业的高中化学AI助教，名字叫"ChemTutor"。

你的职责：
1. 帮助学生理解化学概念，使用简洁清晰的语言
2. 解释时可以列举关键步骤，不要一次性输出太多内容
3. 鼓励学生思考，适当提问引导
4. 如果问题超出高中化学范围，礼貌说明

回答风格：
- 简洁明了，重点突出
- 不要使用表情符号
- 列举内容用数字序号
- 重要概念可以用加粗强调

请用中文回答。`

  // 3. 如果有教材内容，添加为参考资料
  if (textbookContent) {
    systemPrompt = `你是一个专业的高中化学AI助教，名字叫"ChemTutor"。

【参考资料】以下是从教材中找到的相关内容，仅供参考：
${textbookContent}

回答要求：
1. 优先使用参考资料中的概念和表述
2. 如果参考资料不够完整，可以用自己的知识补充
3. 不要被参考资料限制，可以扩展讲解
4. 简洁明了，不要用表情符号
5. 列举内容用数字序号，重要概念加粗强调

请用中文回答。`
  }

  const messages: Message[] = [
    { role: 'system', content: systemPrompt },
    ...history,
    { role: 'user', content: question },
  ]

  return chatWithGLM(messages)
}
