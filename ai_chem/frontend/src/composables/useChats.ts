/**
 * 对话管理 Composable
 */
import { ref, computed, watch } from 'vue'
import type { Chat, Message, ChatsState } from '@/types/chat'
import {
  loadChats,
  saveChats,
  generateChatId,
  generateChatTitle
} from '@/types/chat'

export function useChats() {
  // 状态
  const state = ref<ChatsState>(loadChats())

  // 加载状态：追踪哪个对话正在加载
  const loadingChatId = ref<string | null>(null)

  // 当前对话
  const currentChat = computed(() => {
    if (!state.value.currentChatId) return null
    return state.value.chats.find(c => c.id === state.value.currentChatId) || null
  })

  // 当前对话是否正在加载
  const isLoading = computed(() => {
    return state.value.currentChatId === loadingChatId.value
  })

  // 当前对话的消息
  const currentMessages = computed(() => {
    return currentChat.value?.messages || []
  })

  // 所有对话（按更新时间倒序）
  const sortedChats = computed(() => {
    return [...state.value.chats].sort((a, b) =>
      new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    )
  })

  // 按日期分组的对话
  const groupedChats = computed(() => {
    const groups: Record<string, Chat[]> = {}
    const now = new Date()
    const today = now.toDateString()
    const yesterday = new Date(now)
    yesterday.setDate(yesterday.getDate() - 1)

    sortedChats.value.forEach(chat => {
      const chatDate = new Date(chat.updatedAt)
      const chatDateStr = chatDate.toDateString()

      if (chatDateStr === today) {
        if (!groups['今天']) groups['今天'] = []
        groups['今天'].push(chat)
      } else if (chatDateStr === yesterday.toDateString()) {
        if (!groups['昨天']) groups['昨天'] = []
        groups['昨天'].push(chat)
      } else {
        // 按月分组
        const monthKey = `${chatDate.getFullYear()}年${chatDate.getMonth() + 1}月`
        if (!groups[monthKey]) groups[monthKey] = []
        groups[monthKey].push(chat)
      }
    })

    return groups
  })

  // 自动保存
  watch(
    state,
    (newState) => {
      saveChats(newState)
    },
    { deep: true }
  )

  // 创建新对话
  function createChat(): string {
    const newChat: Chat = {
      id: generateChatId(),
      title: '新对话',
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }

    state.value.chats.unshift(newChat)
    state.value.currentChatId = newChat.id

    return newChat.id
  }

  // 切换对话
  function switchChat(chatId: string): void {
    const chat = state.value.chats.find(c => c.id === chatId)
    if (chat) {
      state.value.currentChatId = chatId
    }
  }

  // 删除对话
  function deleteChat(chatId: string): void {
    state.value.chats = state.value.chats.filter(c => c.id !== chatId)

    // 如果删除的是当前对话，切换到第一个对话或创建新对话
    if (state.value.currentChatId === chatId) {
      if (state.value.chats.length > 0) {
        state.value.currentChatId = state.value.chats[0].id
      } else {
        state.value.currentChatId = null
      }
    }
  }

  // 添加消息
  function addMessage(message: Message, chatId?: string): void {
    // 如果没有指定 chatId，使用当前对话ID
    const targetChatId = chatId || state.value.currentChatId

    const chat = state.value.chats.find(c => c.id === targetChatId)

    if (chat) {
      chat.messages.push(message)
      chat.updatedAt = new Date().toISOString()

      // 如果是第一条用户消息，更新标题
      if (message.role === 'user' && chat.messages.filter(m => m.role === 'user').length === 1) {
        chat.title = generateChatTitle(chat.messages)
      }
    }
  }

  // 更新消息（用于流式更新）
  function updateMessage(messageId: number, content: string): void {
    const chat = state.value.chats.find(c => c.id === state.value.currentChatId)
    if (chat) {
      const message = chat.messages.find(m => m.id === messageId)
      if (message) {
        message.content = content
        chat.updatedAt = new Date().toISOString()
      }
    }
  }

  // 获取对话历史（用于发送给AI）
  function getHistory(): Message[] {
    return currentMessages.value.slice(0, -1).map(msg => ({
      role: msg.role,
      content: msg.content
    }))
  }

  // 清空所有对话
  function clearAllChats(): void {
    state.value = {
      currentChatId: null,
      chats: []
    }
  }

  // 设置加载状态
  function setLoading(chatId: string | null): void {
    loadingChatId.value = chatId
  }

  return {
    // 状态
    state,
    currentChatId: computed(() => state.value.currentChatId),
    currentChat,
    currentMessages,
    sortedChats,
    groupedChats,
    isLoading,

    // 方法
    createChat,
    switchChat,
    deleteChat,
    addMessage,
    updateMessage,
    getHistory,
    clearAllChats,
    setLoading
  }
}
