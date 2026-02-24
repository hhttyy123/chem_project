<template>
  <div class="home-page">
    <NavBar />

    <div class="page-layout">
      <!-- 对话历史侧边栏 -->
      <aside class="chat-sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-header">
          <h2 v-show="!sidebarCollapsed">对话历史</h2>
          <button class="new-chat-btn" @click="handleNewChat" title="新建对话">
            <span v-if="!sidebarCollapsed">+ 新建对话</span>
            <span v-else>+</span>
          </button>
          <button class="collapse-btn" @click="toggleSidebar" title="切换侧边栏">
            <span>{{ sidebarCollapsed ? '▶' : '◀' }}</span>
          </button>
        </div>

        <div class="sidebar-content" v-show="!sidebarCollapsed">
          <!-- 按日期分组的对话列表 -->
          <div v-for="(chats, date) in groupedChats" :key="date" class="chat-group">
            <div class="chat-group-title">{{ date }}</div>
            <div
              v-for="chat in chats"
              :key="chat.id"
              class="chat-item"
              :class="{ active: chat.id === currentChatId }"
              @click="handleSwitchChat(chat.id)"
            >
              <div class="chat-item-title">{{ chat.title }}</div>
              <div class="chat-item-time">{{ formatTime(chat.updatedAt) }}</div>
              <button class="chat-item-delete" @click.stop="handleDeleteChat(chat.id)" title="删除对话">
                ×
              </button>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-if="Object.keys(groupedChats).length === 0" class="empty-state">
            <p>暂无对话记录</p>
            <p class="hint">点击上方"新建对话"开始</p>
          </div>
        </div>
      </aside>

      <!-- 主对话区域 -->
      <main class="chat-area">
        <div class="chat-header">
          <h1>ChemTutor</h1>
          <p>高中化学可视化学习助手</p>
        </div>

        <!-- 对话消息列表 -->
        <div class="messages-list" ref="messagesListRef" @click="handleMessageClick">
          <!-- 欢迎消息 -->
          <div class="message message-assistant" v-if="messages.length === 0">
            <div class="message-avatar">🤖</div>
            <div class="message-content">
              <p>你好！我是你的化学学习助手。有什么化学问题可以问我：</p>
              <div class="example-questions">
                <button class="example-btn" @click="sendExample('为什么氨气是极性分子？')">
                  为什么氨气是极性分子？
                </button>
                <button class="example-btn" @click="sendExample('展示甲烷的分子结构')">
                  展示甲烷的分子结构
                </button>
                <button class="example-btn" @click="sendExample('水的电子式是什么？')">
                  水的电子式是什么？
                </button>
              </div>
            </div>
          </div>

          <!-- 消息列表 -->
          <div
            v-for="msg in messages"
            :key="msg.id"
            class="message"
            :class="msg.role === 'user' ? 'message-user' : 'message-assistant'"
          >
            <div class="message-avatar" v-if="msg.role === 'assistant'">🤖</div>
            <div class="message-content">
              <div v-if="msg.role === 'assistant'" class="markdown-content" v-html="formatMessage(msg.content)"></div>
              <p v-else>{{ msg.content }}</p>
            </div>
          </div>

          <!-- 加载中 -->
          <div class="message message-assistant" v-if="isLoading">
            <div class="message-avatar">🤖</div>
            <div class="message-content loading">
              <span class="dots"></span>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="input-area">
          <div class="input-wrapper">
            <input
              type="text"
              v-model="inputText"
              placeholder="请输入你的化学问题..."
              class="chat-input"
              @keyup.enter="sendMessage"
              :disabled="isLoading"
            />
            <button class="send-btn" @click="sendMessage" :disabled="isLoading || !inputText.trim()">
              <span v-if="!isLoading">发送</span>
              <span v-else>...</span>
            </button>
          </div>
        </div>
      </main>

      <!-- 右侧可视化面板 -->
      <aside class="visual-sidebar" :class="{ collapsed: visualCollapsed }">
        <button class="collapse-btn" @click="toggleVisual">
          <span>{{ visualCollapsed ? '◀' : '▶' }}</span>
        </button>

        <div class="sidebar-content" v-show="!visualCollapsed">
          <!-- 3D 分子显示 -->
          <div class="sidebar-section">
            <div class="section-header">
              <h3>🔬 3D 分子模型</h3>
              <span class="molecule-name" v-if="currentMolecule">{{ currentMolecule }}</span>
            </div>
            <MoleculeDisplay :smiles="currentMoleculeSmiles" :name="currentMolecule" />
          </div>

          <!-- 知识点讲解 -->
          <div class="sidebar-section">
            <div class="section-header">
              <h3 v-if="currentMolecule">📖 知识点讲解</h3>
              <h3 v-else>📖 使用说明</h3>
            </div>

            <!-- 书中有知识点 -->
            <div class="explanation-content" v-if="currentMoleculeKnowledge">
              <p>{{ currentMoleculeKnowledge.description }}</p>
              <div class="property-list" v-if="currentMoleculeKnowledge.properties.length > 0">
                <div v-for="(prop, index) in currentMoleculeKnowledge.properties" :key="index" class="property-item">
                  • {{ prop }}
                </div>
              </div>
              <div class="textbook-location" v-if="currentMoleculeKnowledge.textbookLocation">
                <strong>教材位置：</strong>{{ currentMoleculeKnowledge.textbookLocation }}
              </div>
              <div class="chapter-info" v-if="currentMoleculeKnowledge.chapter">
                <strong>所属章节：</strong>{{ currentMoleculeKnowledge.chapter }}
              </div>
            </div>

            <!-- 书中没有，使用 AI 讲解 -->
            <div class="explanation-content" v-else-if="currentMolecule">
              <!-- 加载中 -->
              <div v-if="isLoadingAiExplanation" class="ai-loading">
                <div class="ai-spinner"></div>
                <p>正在生成讲解...</p>
              </div>

              <!-- AI 讲解内容 -->
              <div v-else-if="aiExplanation" class="ai-explanation">
                <div class="ai-explanation-content" v-html="formatAiExplanation(aiExplanation)"></div>
              </div>

              <!-- 错误 -->
              <div v-else-if="aiExplanationError" class="ai-error">
                <p>{{ aiExplanationError }}</p>
              </div>
            </div>

            <!-- 没有选中分子 -->
            <div class="explanation-content" v-else>
              <p>点击对话中的<u class="chem-link">化学物质</u>，即可在此处查看其 3D 分子结构和相关知识点。</p>
              <p>支持的化学物质包括常见有机物、无机物、酸碱盐等。</p>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { defineOptions } from 'vue'

// 定义组件名称，供 keep-alive 使用
defineOptions({
  name: 'Home'
})
import NavBar from '@/components/NavBar.vue'
import MoleculeDisplay from '@/components/MoleculeDisplay.vue'
import { chatWithChemistryTutor } from '@/api/glm'
import { useChats } from '@/composables/useChats'
import { getMoleculeSmiles, findMoleculesInText } from '@/data/molecules'
import { getMoleculeKnowledge } from '@/data/moleculeKnowledge'
import type { Message } from '@/types/chat'

// 使用对话管理
const {
  currentChatId,
  currentMessages,
  groupedChats,
  isLoading,
  createChat,
  switchChat,
  deleteChat,
  addMessage,
  getHistory,
  setLoading
} = useChats()

// UI状态
const inputText = ref('')
const sidebarCollapsed = ref(false)
const visualCollapsed = ref(false)
const messagesListRef = ref<HTMLElement | null>(null)

// 当前选中的分子
const currentMolecule = ref('')
const currentMoleculeSmiles = ref('')

// 当前对话的消息
const messages = computed(() => currentMessages.value)

// 当前分子的知识
const currentMoleculeKnowledge = computed(() => {
  if (currentMolecule.value) {
    return getMoleculeKnowledge(currentMolecule.value)
  }
  return null
})

// AI 讲解状态
const aiExplanation = ref('')
const isLoadingAiExplanation = ref(false)
const aiExplanationError = ref('')

// 当选中分子变化时，获取 AI 讲解
watch(currentMolecule, async (newMolecule) => {
  if (newMolecule) {
    const knowledge = getMoleculeKnowledge(newMolecule)
    if (!knowledge) {
      // 书中没有知识点，调用 AI 获取讲解
      isLoadingAiExplanation.value = true
      aiExplanationError.value = ''
      try {
        const response = await chatWithChemistryTutor(
          `请简要讲解一下${newMolecule}这种物质。包括：
1. 基本信息和化学式
2. 主要性质（2-3条）
3. 在高中化学中的重要性

请用简洁的语言回答，不要用表情符号。`
        )
        aiExplanation.value = response
      } catch (error) {
        console.error('获取 AI 讲解失败:', error)
        aiExplanationError.value = '暂时无法获取讲解'
      } finally {
        isLoadingAiExplanation.value = false
      }
    } else {
      // 书中有知识点，清空 AI 讲解
      aiExplanation.value = ''
      aiExplanationError.value = ''
    }
  } else {
    // 清空状态
    aiExplanation.value = ''
    aiExplanationError.value = ''
    isLoadingAiExplanation.value = false
  }
})

// 消息ID计数器
let messageIdCounter = 0

// 初始化：如果没有当前对话，创建一个
onMounted(() => {
  if (!currentChatId.value) {
    createChat()
  }
  scrollToBottom()

  // 设置全局函数
  window.handleMoleculeClick = (smiles: string, name: string) => {
    selectMolecule(smiles, name)
  }
})

onUnmounted(() => {
  // 清理全局函数
  delete window.handleMoleculeClick
})

// 监听消息变化，自动滚动
watch(messages, () => {
  scrollToBottom()
}, { deep: true })

// 切换对话侧边栏
function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 切换可视化侧边栏
function toggleVisual() {
  visualCollapsed.value = !visualCollapsed.value
}

// 新建对话
function handleNewChat() {
  createChat()
  inputText.value = ''
  messageIdCounter = 0
}

// 切换对话
function handleSwitchChat(chatId: string) {
  switchChat(chatId)
  messageIdCounter = messages.value.length > 0 ? Math.max(...messages.value.map(m => m.id)) : 0
  scrollToBottom()
}

// 删除对话
function handleDeleteChat(chatId: string) {
  if (confirm('确定要删除这个对话吗？')) {
    deleteChat(chatId)
    messageIdCounter = messages.value.length > 0 ? Math.max(...messages.value.map(m => m.id)) : 0
  }
}

// 发送示例问题
function sendExample(question: string) {
  inputText.value = question
  sendMessage()
}

// 格式化消息（简单的 markdown 处理 + 化学物质高亮）
function formatMessage(content: string) {
  let formatted = content

  // 使用前端匹配查找化学物质
  const molecules = findMoleculesInText(content)

  // 从后往前替换，避免索引变化
  for (let i = molecules.length - 1; i >= 0; i--) {
    const mol = molecules[i]
    const before = formatted.substring(0, mol.start)
    const moleculeText = formatted.substring(mol.start, mol.end)
    const after = formatted.substring(mol.end)

    // 使用 data 属性存储编码后的数据，通过事件委托处理点击
    const escapedSmiles = encodeURIComponent(mol.smiles)
    const escapedName = encodeURIComponent(mol.name)

    const linkHtml = `<u class="chem-link" data-smiles="${mol.smiles}" data-name="${mol.name}" data-smiles-safe="${escapedSmiles}" data-name-safe="${escapedName}">${moleculeText}</u>`
    formatted = before + linkHtml + after
  }

  // 处理粗体
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

  // 处理换行
  formatted = formatted.replace(/\n/g, '<br>')
  formatted = formatted.replace(/(\d+)\.\s/g, '<br>$1. ')
  formatted = formatted.replace(/- /g, '<br>• ')

  return formatted
}

// 格式化 AI 讲解内容
function formatAiExplanation(content: string) {
  let formatted = content

  // 处理粗体
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

  // 处理换行
  formatted = formatted.replace(/\n/g, '<br>')

  return formatted
}

// 选中分子
function selectMolecule(smiles: string, name: string) {
  currentMolecule.value = name
  currentMoleculeSmiles.value = smiles

  // 自动展开右侧栏
  if (visualCollapsed.value) {
    visualCollapsed.value = false
  }
}

// 处理消息区域的点击事件（事件委托）
function handleMessageClick(event: MouseEvent) {
  const target = event.target as HTMLElement

  // 检查是否点击了化学物质链接
  if (target.classList.contains('chem-link')) {
    event.preventDefault()

    // 从 data 属性获取编码后的值
    const smilesSafe = target.getAttribute('data-smiles-safe')
    const nameSafe = target.getAttribute('data-name-safe')

    if (smilesSafe && nameSafe) {
      // 解码并选中分子
      const smiles = decodeURIComponent(smilesSafe)
      const name = decodeURIComponent(nameSafe)
      selectMolecule(smiles, name)
    }
  }
}

// 处理化学物质点击（全局函数，保留兼容性）
declare global {
  interface Window {
    handleMoleculeClick: (smiles: string, name: string) => void
  }
}

window.handleMoleculeClick = (smiles: string, name: string) => {
  selectMolecule(smiles, name)
}

// 格式化时间
function formatTime(dateString: string) {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  // 小于1小时显示"刚刚"
  if (diff < 3600000) return '刚刚'

  // 今天显示时间
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  // 昨天显示"昨天"
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) {
    return '昨天'
  }

  // 其他显示日期
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

// 滚动到底部
function scrollToBottom() {
  setTimeout(() => {
    if (messagesListRef.value) {
      messagesListRef.value.scrollTop = messagesListRef.value.scrollHeight
    }
  }, 100)
}

// 发送消息
async function sendMessage() {
  const question = inputText.value.trim()
  if (!question || isLoading.value) return

  // 确保有当前对话
  if (!currentChatId.value) {
    createChat()
  }

  // 保存当前对话ID（用于异步操作后添加消息）
  const chatId = currentChatId.value

  // 添加用户消息
  const userMessage: Message = {
    id: ++messageIdCounter,
    role: 'user',
    content: question,
    timestamp: new Date().toISOString()
  }
  addMessage(userMessage, chatId)

  inputText.value = ''
  scrollToBottom()

  // 开始加载
  setLoading(chatId)

  try {
    // 调用 GLM API
    const history = getHistory()
    const response = await chatWithChemistryTutor(question, history)

    // 添加助手回复（使用保存的对话ID）
    const assistantMessage: Message = {
      id: ++messageIdCounter,
      role: 'assistant',
      content: response,
      timestamp: new Date().toISOString()
    }
    addMessage(assistantMessage, chatId)
  } catch (error) {
    console.error('发送消息失败:', error)
    const errorMessage: Message = {
      id: ++messageIdCounter,
      role: 'assistant',
      content: '抱歉，我遇到了一些问题。请稍后再试。',
      timestamp: new Date().toISOString()
    }
    addMessage(errorMessage, chatId)
  } finally {
    setLoading(null)
    scrollToBottom()
  }
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f8fafc;
}

.page-layout {
  display: flex;
  height: calc(100vh - 60px);
}

/* ========== 对话历史侧边栏 ========== */
.chat-sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: width 0.3s ease;
}

.chat-sidebar.collapsed {
  width: 50px;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sidebar-header h2 {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  flex: 1;
}

.new-chat-btn {
  padding: 0.5rem 1rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.2s;
}

.new-chat-btn:hover {
  background: #1d4ed8;
}

.collapse-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: #f1f5f9;
  border: none;
  color: #64748b;
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.2s;
}

.collapse-btn:hover {
  background: #e2e8f0;
  color: #2563eb;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.chat-group {
  margin-bottom: 1rem;
}

.chat-group-title {
  padding: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
}

.chat-item {
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  margin-bottom: 0.25rem;
}

.chat-item:hover {
  background: #f8fafc;
}

.chat-item.active {
  background: #eff6ff;
  border-left: 3px solid #2563eb;
}

.chat-item-title {
  font-size: 0.875rem;
  color: #1e293b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 1.5rem;
}

.chat-item-time {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.25rem;
}

.chat-item-delete {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: #94a3b8;
  font-size: 1.25rem;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s;
}

.chat-item:hover .chat-item-delete {
  opacity: 1;
}

.chat-item-delete:hover {
  color: #ef4444;
}

.empty-state {
  padding: 2rem 1rem;
  text-align: center;
  color: #94a3b8;
}

.empty-state p {
  margin: 0.25rem 0;
}

.empty-state .hint {
  font-size: 0.875rem;
}

/* ========== 主对话区域 ========== */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
}

.chat-header {
  text-align: center;
  padding: 1.5rem 1rem;
  border-bottom: 1px solid #e2e8f0;
  background: white;
}

.chat-header h1 {
  font-size: 1.5rem;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.chat-header p {
  font-size: 0.875rem;
  color: #64748b;
}

.messages-list {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.message {
  display: flex;
  gap: 0.75rem;
  max-width: 80%;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-assistant {
  align-self: flex-start;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #dbeafe;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.message-content {
  padding: 1rem 1.25rem;
  border-radius: 16px;
  line-height: 1.6;
}

.message-user .message-content {
  background: #2563eb;
  color: white;
  border-bottom-right-radius: 4px;
}

.message-assistant .message-content {
  background: white;
  color: #1e293b;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-bottom-left-radius: 4px;
}

.message-content.loading {
  padding: 0.75rem 1rem;
}

.dots {
  display: inline-flex;
  gap: 4px;
}

.dots::before,
.dots::after {
  content: '';
  width: 8px;
  height: 8px;
  background: #64748b;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dots::before {
  animation-delay: -0.32s;
}

.dots::after {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.example-questions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1rem;
}

.example-btn {
  padding: 0.5rem 0.75rem;
  background: #f1f5f9;
  border: none;
  border-radius: 8px;
  text-align: left;
  font-size: 0.875rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.example-btn:hover {
  background: #e2e8f0;
  color: #2563eb;
}

.markdown-content {
  line-height: 1.8;
}

.markdown-content :deep(strong) {
  color: #2563eb;
  font-weight: 600;
}

/* ========== 输入区域 ========== */
.input-area {
  padding: 1rem 1.5rem;
  background: white;
  border-top: 1px solid #e2e8f0;
}

.input-wrapper {
  display: flex;
  gap: 0.75rem;
}

.chat-input {
  flex: 1;
  padding: 0.875rem 1.25rem;
  border: 1px solid #e2e8f0;
  border-radius: 24px;
  font-size: 1rem;
  outline: none;
  transition: all 0.2s;
}

.chat-input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.chat-input:disabled {
  background: #f8fafc;
  cursor: not-allowed;
}

.send-btn {
  padding: 0.875rem 2rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 24px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.send-btn:hover:not(:disabled) {
  background: #1d4ed8;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ========== 可视化侧边栏 ========== */
.visual-sidebar {
  width: 380px;
  background: white;
  border-left: 1px solid #e2e8f0;
  display: flex;
  position: relative;
  transition: width 0.3s ease;
}

.visual-sidebar.collapsed {
  width: 40px;
}

.visual-sidebar .collapse-btn {
  position: absolute;
  left: -16px;
  top: 50%;
  transform: translateY(-50%);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.sidebar-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.sidebar-section:last-child {
  border-bottom: none;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h3 {
  font-size: 1rem;
  color: #1e293b;
}

.molecule-name {
  padding: 0.25rem 0.5rem;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 4px;
  font-size: 0.75rem;
}

.molecule-canvas {
  margin-bottom: 1rem;
}

.canvas-placeholder {
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 12px;
  color: #64748b;
}

.molecule-emoji {
  font-size: 3rem;
  margin-top: 0.5rem;
}

.hint {
  font-size: 0.75rem !important;
  color: #94a3b8 !important;
  margin-top: 0.25rem;
}

.molecule-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  padding: 0.5rem;
  background: #f8fafc;
  border-radius: 6px;
}

.info-row span:first-child {
  color: #64748b;
}

.info-row span:last-child {
  color: #1e293b;
  font-weight: 500;
}

.explanation-content h4 {
  font-size: 0.875rem;
  color: #2563eb;
  margin-bottom: 0.5rem;
  margin-top: 1rem;
}

.explanation-content h4:first-child {
  margin-top: 0;
}

.explanation-content p {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

.explanation-content ul {
  padding-left: 1.25rem;
}

.explanation-content li {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 0.25rem;
}

.explanation-content p {
  margin-bottom: 0.75rem;
  line-height: 1.6;
}

.property-list {
  margin: 1rem 0;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
}

.property-item {
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 0.4rem;
  line-height: 1.5;
}

.property-item:last-child {
  margin-bottom: 0;
}

.textbook-location {
  margin-top: 1rem;
  padding: 0.5rem 0.75rem;
  background: #dbeafe;
  border-left: 3px solid #2563eb;
  border-radius: 4px;
  font-size: 0.8rem;
}

.textbook-location strong {
  color: #1e40af;
}

.chapter-info {
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: #fef3c7;
  border-left: 3px solid #f59e0b;
  border-radius: 4px;
  font-size: 0.8rem;
}

.chapter-info strong {
  color: #92400e;
}

/* AI 讲解 */
.ai-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1.5rem 1rem;
}

.ai-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: ai-spin 1s linear infinite;
}

@keyframes ai-spin {
  to { transform: rotate(360deg); }
}

.ai-loading p {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
}

.ai-explanation {
  padding: 0;
}

.ai-explanation-content {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.6;
}

.ai-explanation-content :deep(strong) {
  color: #2563eb;
  font-weight: 600;
}

.ai-error {
  padding: 0.75rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid #ef4444;
  border-radius: 8px;
  text-align: center;
}

.ai-error p {
  font-size: 0.875rem;
  color: #ef4444;
  margin: 0;
}

/* ========== 化学物质链接 ========== */
:deep(.chem-link) {
  color: #2563eb;
  text-decoration: underline;
  text-decoration-style: dotted;
  text-decoration-thickness: 2px;
  text-underline-offset: 2px;
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(37, 99, 235, 0.05);
  padding: 0 2px;
  border-radius: 2px;
}

:deep(.chem-link:hover) {
  color: #1d4ed8;
  background: rgba(37, 99, 235, 0.1);
  text-decoration-style: solid;
}

/* ========== 响应式 ========== */
@media (max-width: 1024px) {
  .visual-sidebar {
    width: 320px;
  }
}

@media (max-width: 768px) {
  .chat-sidebar {
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    z-index: 100;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  }

  .visual-sidebar {
    display: none;
  }

  .message {
    max-width: 95%;
  }
}
</style>
