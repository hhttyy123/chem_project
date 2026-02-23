<template>
  <div class="molecule-display">
    <!-- Loading -->
    <div class="loading-overlay" v-show="isLoading">
      <div class="spinner"></div>
      <div class="loading-text">正在生成分子结构...</div>
    </div>

    <!-- Empty State -->
    <div class="empty-state" v-show="!currentSmiles && !isLoading">
      <div class="empty-icon">🔬</div>
      <div class="empty-text">点击对话中的化学物质查看 3D 结构</div>
    </div>

    <!-- Error -->
    <div class="error-message" v-show="error">
      <div class="error-text">{{ error }}</div>
    </div>

    <!-- 3D Canvas -->
    <div class="molecule-canvas" v-show="currentSmiles && !isLoading">
      <div ref="molContainer" class="mol-container"></div>
    </div>

    <!-- Molecule Info -->
    <div class="molecule-info" v-show="currentSmiles && !isLoading && moleculeInfo">
      <div class="info-row">
        <span class="label">分子式</span>
        <span class="value">{{ moleculeInfo?.formula || '-' }}</span>
      </div>
      <div class="info-row">
        <span class="label">分子量</span>
        <span class="value">{{ moleculeInfo?.molecular_weight ? moleculeInfo.molecular_weight + ' Da' : '-' }}</span>
      </div>
      <div class="info-row">
        <span class="label">原子数</span>
        <span class="value">{{ moleculeInfo?.num_atoms || '-' }}</span>
      </div>
    </div>

    <!-- Style Controls -->
    <div class="style-controls" v-show="currentSmiles && !isLoading">
      <button
        class="style-btn"
        :class="{ active: currentStyle === 'stick' }"
        @click="setStyle('stick')"
        title="球棍模型"
      >
        ⚪ 球棍
      </button>
      <button
        class="style-btn"
        :class="{ active: currentStyle === 'sphere' }"
        @click="setStyle('sphere')"
        title="空间填充"
      >
        🔵 填充
      </button>
      <button class="style-btn" @click="resetView" title="重置视图">
        ↺ 重置
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'

// Props
interface Props {
  smiles?: string
  name?: string
}

const props = defineProps<Props>()

// API Configuration
const API_BASE = 'http://localhost:8001'

// Types
interface MoleculeInfo {
  num_atoms: number
  num_bonds: number
  molecular_weight: number
  formula: string
}

// Reactive state
const currentSmiles = ref('')
const currentStyle = ref<'stick' | 'sphere'>('stick')
const isLoading = ref(false)
const error = ref('')
const moleculeInfo = ref<MoleculeInfo | null>(null)

// DOM refs
const molContainer = ref<HTMLElement | null>(null)

// 3Dmol viewer
let viewer: any = null
let scriptLoaded = false

// Initialize 3Dmol viewer
function initViewer() {
  if (!molContainer.value || viewer) return

  try {
    // @ts-ignore - 3Dmol is loaded via CDN
    viewer = $3Dmol.createViewer(molContainer.value, {
      backgroundColor: '#f8fafc'
    })
    if (viewer) {
      viewer.setBackgroundColor('#f8fafc')
    }
  } catch (e) {
    console.warn('3Dmol not ready yet')
  }
}

// Load 3Dmol.js script
function load3DmolScript() {
  if (scriptLoaded) return

  return new Promise<void>((resolve) => {
    if (window.$3Dmol) {
      scriptLoaded = true
      resolve()
      return
    }

    const script = document.createElement('script')
    script.src = 'https://3dmol.org/build/3Dmol-min.js'
    script.onload = () => {
      scriptLoaded = true
      // @ts-ignore
      window.$3Dmol = $3Dmol
      initViewer()
      resolve()
    }
    document.head.appendChild(script)
  })
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
    const err = await response.json()
    throw new Error(err.detail || 'Failed to parse SMILES')
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
async function visualizeMolecule(smiles: string) {
  if (!smiles.trim() || !viewer) return

  isLoading.value = true
  error.value = ''

  try {
    const result = await parseSMILES(smiles)

    if (!result.success || !result.sdf) {
      throw new Error('无法生成 3D 结构')
    }

    viewer.clear()
    viewer.addModel(result.sdf, 'sdf')

    applyStyle()
    viewer.zoomTo()
    viewer.render()

    // Get molecule info
    const info = await getMoleculeInfo(smiles)
    if (info) {
      moleculeInfo.value = info
    }

    isLoading.value = false
  } catch (e: any) {
    console.error('Visualization error:', e)
    isLoading.value = false
    error.value = e.message || '无法显示该分子'
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

// Reset view
function resetView() {
  if (viewer) {
    viewer.zoomTo()
  }
}

// Watch for smiles changes
watch(() => props.smiles, async (newSmiles) => {
  if (newSmiles && newSmiles !== currentSmiles.value) {
    currentSmiles.value = newSmiles

    // Ensure script is loaded
    if (!scriptLoaded) {
      await load3DmolScript()
    }

    // Wait for DOM update
    await nextTick()

    // Initialize viewer if needed
    if (!viewer && molContainer.value) {
      initViewer()
    }

    // Visualize molecule
    if (viewer) {
      visualizeMolecule(newSmiles)
    }
  } else if (!newSmiles) {
    currentSmiles.value = ''
    moleculeInfo.value = null
    error.value = ''
    if (viewer) {
      viewer.clear()
    }
  }
})

// Lifecycle
onMounted(async () => {
  await load3DmolScript()
})

onUnmounted(() => {
  if (viewer) {
    viewer.clear()
  }
})
</script>

<style scoped>
.molecule-display {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
}

/* Loading */
.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 0.875rem;
  color: #64748b;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem 1rem;
  text-align: center;
}

.empty-icon {
  font-size: 3rem;
  opacity: 0.5;
}

.empty-text {
  font-size: 0.875rem;
  color: #94a3b8;
}

/* Error */
.error-message {
  padding: 0.75rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid #ef4444;
  border-radius: 8px;
}

.error-text {
  font-size: 0.875rem;
  color: #ef4444;
}

/* Canvas */
.molecule-canvas {
  position: relative;
  height: 250px;
  background: #f8fafc;
  border-radius: 12px;
  overflow: hidden;
}

.mol-container {
  width: 100%;
  height: 100%;
}

/* Info */
.molecule-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem;
  background: #f8fafc;
  border-radius: 6px;
}

.info-row .label {
  font-size: 0.75rem;
  color: #64748b;
}

.info-row .value {
  font-size: 0.875rem;
  color: #1e293b;
  font-weight: 500;
  font-family: monospace;
}

/* Style Controls */
.style-controls {
  display: flex;
  gap: 0.5rem;
}

.style-btn {
  flex: 1;
  padding: 0.5rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.75rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.style-btn:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.style-btn.active {
  background: #2563eb;
  border-color: #2563eb;
  color: white;
}
</style>
