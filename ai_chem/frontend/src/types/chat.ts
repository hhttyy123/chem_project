/**
 * 对话相关类型定义
 */

export interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

export interface Chat {
  id: string
  title: string
  messages: Message[]
  createdAt: string
  updatedAt: string
}

export interface ChatsState {
  currentChatId: string | null
  chats: Chat[]
}

const STORAGE_KEY = 'chemtutor_chats'

/**
 * 从 LocalStorage 加载对话数据
 */
export function loadChats(): ChatsState {
  try {
    const data = localStorage.getItem(STORAGE_KEY)
    if (data) {
      return JSON.parse(data)
    }
  } catch (error) {
    console.error('加载对话数据失败:', error)
  }

  return {
    currentChatId: null,
    chats: []
  }
}

/**
 * 保存对话数据到 LocalStorage
 */
export function saveChats(state: ChatsState): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch (error) {
    console.error('保存对话数据失败:', error)
  }
}

/**
 * 生成对话ID
 */
export function generateChatId(): string {
  return `chat_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
}

/**
 * 从对话内容生成标题
 */
export function generateChatTitle(messages: Message[]): string {
  if (messages.length === 0) return '新对话'

  const firstUserMessage = messages.find(m => m.role === 'user')
  if (firstUserMessage) {
    // 取前30个字符作为标题
    return firstUserMessage.content.slice(0, 30) + (firstUserMessage.content.length > 30 ? '...' : '')
  }

  return '新对话'
}
