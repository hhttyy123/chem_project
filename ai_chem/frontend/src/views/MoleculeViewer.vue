<template>
  <div class="molecule-viewer-page">
    <NavBar />

    <div class="viewer-container">
      <!-- Status Bar -->
      <div class="status-bar">
        <div class="status-indicator">
          <div :class="['status-dot', statusClass]"></div>
          <span class="status-text">{{ statusText }}</span>
        </div>
      </div>

      <!-- Sidebar -->
      <aside class="sidebar">
        <!-- Input Section -->
        <div class="sidebar-section">
          <div class="section-label">分子输入</div>

          <div class="input-group">
            <label class="input-label">SMILES 字符串</label>
            <div class="input-wrapper">
              <input
                type="text"
                class="smiles-input"
                v-model="smilesInput"
                @keypress.enter="visualizeMolecule"
                placeholder="例如: CCO (乙醇)"
              />
              <button class="clear-btn" @click="clearInput" v-show="smilesInput" title="清除">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                  <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
                </svg>
              </button>
            </div>
          </div>

          <button class="btn btn-primary" @click="visualizeMolecule" :disabled="!apiConnected">
            生成分子
          </button>
        </div>

        <!-- Examples -->
        <div class="sidebar-section">
          <div class="section-label">示例分子</div>
          <div class="examples-grid">
            <div
              class="example-card"
              v-for="example in exampleMolecules"
              :key="example.smiles"
              @click="selectExample(example)"
            >
              <div class="example-name">{{ example.name }}</div>
              <div class="example-formula">{{ example.formula }}</div>
            </div>
          </div>
        </div>

        <!-- Style Controls -->
        <div class="sidebar-section">
          <div class="section-label">显示样式</div>
          <div class="control-group">
            <button
              class="style-btn"
              :class="{ active: currentStyle === 'stick' }"
              @click="setStyle('stick')"
            >
              球棍模型
            </button>
            <button
              class="style-btn"
              :class="{ active: currentStyle === 'sphere' }"
              @click="setStyle('sphere')"
            >
              空间填充
            </button>
          </div>
        </div>

        <!-- Molecule Info -->
        <div class="sidebar-section" v-show="moleculeInfo">
          <div class="section-label">分子信息</div>
          <div class="molecule-info">
            <div class="info-row">
              <span class="info-label">原子数</span>
              <span class="info-value">{{ moleculeInfo?.num_atoms || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">键数</span>
              <span class="info-value">{{ moleculeInfo?.num_bonds || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">分子量</span>
              <span class="info-value">{{ moleculeInfo?.molecular_weight ? moleculeInfo.molecular_weight + ' Da' : '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">分子式</span>
              <span class="info-value">{{ moleculeInfo?.formula || '-' }}</span>
            </div>
          </div>
        </div>
      </aside>

      <!-- Viewport -->
      <main class="viewport">
        <div ref="molContainer" class="mol-container"></div>

        <!-- Empty State -->
        <div class="empty-state" v-show="!hasMolecule">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm0 18c-4.4 0-8-3.6-8-8s3.6-8 8-8 8 3.6 8 8-3.6 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/></svg>
          </div>
          <div class="empty-text">输入 SMILES 或选择示例分子开始</div>
        </div>

        <!-- Loading Overlay -->
        <div class="loading-overlay" v-show="isLoading">
          <div class="spinner"></div>
          <div class="loading-text">正在生成分子结构...</div>
        </div>

        <!-- Error Message -->
        <div class="error-message" v-show="errorMessage">
          <svg class="error-icon" viewBox="0 0 24 24"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
          <span class="error-text">{{ errorMessage }}</span>
        </div>

        <!-- Viewport Controls -->
        <div class="viewport-controls">
          <button class="control-btn" @click="resetView" title="重置视图">
            <svg viewBox="0 0 24 24"><path d="M12 5V1L7 6l5 5V7c3.3 0 6 2.7 6 6s-2.7 6-6 6-6-2.7-6-6H4c0 4.4 3.6 8 8 8s8-3.6 8-8-3.6-8-8-8z"/></svg>
          </button>
          <button class="control-btn" @click="takeScreenshot" title="截图">
            <svg viewBox="0 0 24 24"><path d="M12 12c2.2 0 4-1.8 4-4s-1.8-4-4-4-4 1.8-4 4 1.8 4 4 4zm0 2c-2.7 0-8 1.3-8 4v2h16v-2c0-2.7-5.3-4-8-4z"/></svg>
          </button>
          <button class="control-btn" @click="toggleFullscreen" title="全屏">
            <svg viewBox="0 0 24 24"><path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg>
          </button>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import NavBar from '@/components/NavBar.vue'
import { getMoleculeSmiles } from '@/data/molecules'

// API Configuration
const API_BASE = 'http://localhost:8001'

// Types
interface MoleculeInfo {
  num_atoms: number
  num_bonds: number
  molecular_weight: number
  formula: string
}

interface ExampleMolecule {
  name: string
  formula: string
  smiles: string
}

// Reactive state
const smilesInput = ref('')
const apiConnected = ref(false)
const currentStyle = ref<'stick' | 'sphere'>('stick')
const isLoading = ref(false)
const errorMessage = ref('')
const moleculeInfo = ref<MoleculeInfo | null>(null)
const hasMolecule = ref(false)

// DOM refs
const molContainer = ref<HTMLElement | null>(null)

// 3Dmol viewer
let viewer: any = null

// Example molecules
const exampleMolecules: ExampleMolecule[] = [
  { name: '乙醇', formula: 'C₂H₅OH', smiles: 'CCO' },
  { name: '苯', formula: 'C₆H₆', smiles: 'c1ccccc1' },
  { name: '乙酸', formula: 'CH₃COOH', smiles: 'CC(=O)O' },
  { name: '异辛烷', formula: 'C₈H₁₈', smiles: 'CC(C)CC(C)C' },
  { name: '环己烷', formula: 'C₆H₁₂', smiles: 'C1CCCCC1' },
  { name: '苯丙醇', formula: 'C₉H₁₂O', smiles: 'C[C@H](O)C1=CC=CC=C1' },
]

// Computed
const statusClass = computed(() => {
  if (!apiConnected.value) return 'error'
  return ''
})

const statusText = computed(() => {
  if (!apiConnected.value) return '后端未连接 - 请启动 3D_test/api.py'
  return '后端已连接'
})

// Initialize 3Dmol viewer
function initViewer() {
  if (!molContainer.value) return
  // @ts-ignore - 3Dmol is loaded via CDN
  viewer = $3Dmol.createViewer(molContainer.value, {
    backgroundColor: '#f8fafc'
  })
  if (viewer) {
    viewer.setBackgroundColor('#f8fafc')
  }
}

// Check API connection
async function checkAPIConnection() {
  try {
    const response = await fetch(`${API_BASE}/health`)
    if (response.ok) {
      apiConnected.value = true
    } else {
      apiConnected.value = false
    }
  } catch (e) {
    apiConnected.value = false
  }
}

// Parse SMILES using API
async function parseSMILES(smiles: string) {
  const response = await fetch(`${API_BASE}/parse`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ smiles: smiles })
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to parse SMILES')
  }

  return await response.json()
}

// Get molecule info
async function getMoleculeInfo(smiles: string) {
  const response = await fetch(`${API_BASE}/info`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ smiles: smiles })
  })

  if (!response.ok) {
    return null
  }

  return await response.json()
}

// Visualize molecule
async function visualizeMolecule() {
  let smiles = smilesInput.value.trim()
  if (!smiles) return
  if (!apiConnected.value) {
    showError('后端未连接，请先启动 3D_test/api.py')
    return
  }

  // 检查输入是否是化学物质名称，如果是则转换为 SMILES
  const mappedSmiles = getMoleculeSmiles(smiles)
  if (mappedSmiles) {
    smiles = mappedSmiles
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const result = await parseSMILES(smiles)

    if (!result.success || !result.sdf) {
      throw new Error('Failed to generate 3D structure')
    }

    viewer.clear()
    viewer.addModel(result.sdf, 'sdf')

    applyStyle()
    viewer.zoomTo()
    viewer.render()

    hasMolecule.value = true

    const info = await getMoleculeInfo(smiles)
    if (info) {
      moleculeInfo.value = info
    }

    isLoading.value = false
  } catch (e: any) {
    console.error('Visualization error:', e)
    isLoading.value = false
    showError(e.message || '无效的 SMILES 字符串')
  }
}

// Apply rendering style
function applyStyle() {
  if (!viewer) return

  switch (currentStyle.value) {
    case 'stick':
      viewer.setStyle({}, {
        sphere: { scale: 0.25, colorscheme: 'Jmol' },
        stick: { radius: 0.12, colorscheme: 'Jmol' }
      })
      break
    case 'sphere':
      viewer.setStyle({}, {
        sphere: { scale: 0.8, colorscheme: 'Jmol' }
      })
      break
  }

  viewer.render()
}

// Set style
function setStyle(style: 'stick' | 'sphere') {
  currentStyle.value = style
  applyStyle()
}

// Select example molecule
function selectExample(example: ExampleMolecule) {
  smilesInput.value = example.smiles
  visualizeMolecule()
}

// Clear input
function clearInput() {
  smilesInput.value = ''
}

// Reset view
function resetView() {
  if (viewer) {
    viewer.zoomTo()
  }
}

// Take screenshot
function takeScreenshot() {
  if (viewer) {
    viewer.pngURI().then((uri: string) => {
      const link = document.createElement('a')
      link.href = uri
      link.download = 'molecule.png'
      link.click()
    })
  }
}

// Toggle fullscreen
function toggleFullscreen() {
  if (document.fullscreenElement) {
    document.exitFullscreen()
  } else {
    document.documentElement.requestFullscreen()
  }
}

// Show error
function showError(message: string) {
  errorMessage.value = message
  setTimeout(() => {
    errorMessage.value = ''
  }, 5000)
}

// Lifecycle
let connectionCheckInterval: number

onMounted(() => {
  // Load 3Dmol.js script
  const script = document.createElement('script')
  script.src = 'https://3dmol.org/build/3Dmol-min.js'
  script.onload = () => {
    initViewer()
  }
  document.head.appendChild(script)

  // Check API connection
  checkAPIConnection()
  connectionCheckInterval = window.setInterval(checkAPIConnection, 5000)
})

onUnmounted(() => {
  if (connectionCheckInterval) {
    clearInterval(connectionCheckInterval)
  }
})
</script>

<style scoped>
.molecule-viewer-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
  overflow: hidden;
}

.viewer-container {
  display: grid;
  grid-template-columns: 360px 1fr;
  flex: 1;
  overflow: hidden;
}

/* Status Bar */
.status-bar {
  grid-column: 1 / -1;
  display: flex;
  justify-content: flex-end;
  padding: 0.5rem 1rem;
  background: white;
  border-bottom: 1px solid #e2e8f0;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: #64748b;
  font-family: monospace;
}

.status-text {
  font-size: 0.75rem;
  color: #64748b;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  flex-shrink: 0;
}

.status-dot.error {
  background: #ef4444;
}

/* Sidebar */
.sidebar {
  background: white;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  height: 100%;
}

.sidebar::-webkit-scrollbar {
  width: 6px;
}

.sidebar::-webkit-scrollbar-track {
  background: white;
}

.sidebar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 3px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}

.sidebar-section {
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.section-label {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #94a3b8;
  margin-bottom: 1rem;
  font-family: monospace;
}

/* Input */
.input-group {
  margin-bottom: 1rem;
}

.input-label {
  display: block;
  font-size: 0.8rem;
  font-weight: 500;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.input-wrapper {
  position: relative;
}

.smiles-input {
  width: 100%;
  padding: 0.5rem 1rem;
  padding-right: 3rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-family: monospace;
  font-size: 0.85rem;
  color: #1e293b;
  transition: all 0.2s;
}

.smiles-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.clear-btn {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem;
  transition: color 0.2s;
}

.clear-btn:hover {
  color: #64748b;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  width: 100%;
}

.btn-primary {
  background: linear-gradient(135deg, #2563eb, #6366f1);
  color: white;
  padding: 0.75rem;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
}

.btn-primary:hover:not(:disabled) {
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.35);
  transform: translateY(-1px);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Examples */
.examples-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
}

.example-card {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.example-card:hover {
  border-color: #2563eb;
  background: rgba(37, 99, 235, 0.05);
}

.example-name {
  font-size: 0.75rem;
  font-weight: 500;
}

.example-formula {
  font-family: monospace;
  font-size: 0.65rem;
  color: #94a3b8;
  margin-top: 2px;
}

/* Style Controls */
.control-group {
  display: flex;
  gap: 0.5rem;
}

.style-btn {
  flex: 1;
  padding: 0.75rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.style-btn:hover {
  border-color: #cbd5e1;
  background: white;
}

.style-btn.active {
  background: #2563eb;
  border-color: #2563eb;
  color: white;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
}

/* Molecule Info */
.molecule-info {
  background: #f1f5f9;
  border-radius: 8px;
  padding: 1rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 0.25rem 0;
  border-bottom: 1px solid #e2e8f0;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 0.8rem;
  color: #94a3b8;
}

.info-value {
  font-family: monospace;
  font-size: 0.8rem;
  color: #1e293b;
}

/* Viewport */
.viewport {
  position: relative;
  background: #f8fafc;
  overflow: hidden;
  height: 100%;
}

.mol-container {
  width: 100%;
  height: 100%;
  position: absolute;
  inset: 0;
}

/* Empty State */
.empty-state {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  pointer-events: none;
}

.empty-icon {
  width: 72px;
  height: 72px;
  opacity: 0.4;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
  fill: #94a3b8;
}

.empty-text {
  font-size: 0.9rem;
  color: #94a3b8;
}

/* Loading Overlay */
.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(4px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.spinner {
  width: 44px;
  height: 44px;
  border: 3px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 0.9rem;
  color: #64748b;
}

/* Error Message */
.error-message {
  position: absolute;
  bottom: 1.5rem;
  left: 1.5rem;
  right: calc(1.5rem + 160px);
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid #ef4444;
  border-radius: 8px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.error-icon {
  width: 18px;
  height: 18px;
  fill: #ef4444;
}

.error-text {
  font-size: 0.85rem;
  color: #ef4444;
}

/* Viewport Controls */
.viewport-controls {
  position: absolute;
  bottom: 1.5rem;
  right: 1.5rem;
  display: flex;
  gap: 0.5rem;
}

.control-btn {
  width: 42px;
  height: 42px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.control-btn:hover {
  background: #f1f5f9;
  border-color: #2563eb;
}

.control-btn svg {
  width: 18px;
  height: 18px;
  fill: #64748b;
}

/* Responsive */
@media (max-width: 900px) {
  .viewer-container {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }

  .sidebar {
    border-right: none;
    border-bottom: 1px solid #e2e8f0;
    max-height: 40vh;
  }

  .viewport {
    min-height: 50vh;
  }
}
</style>
