<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import NavBar from '@/components/NavBar.vue'

const canvas = ref(null)
const selectedOrbital = ref('2p_z')
const particleCount = ref(50000)
const glowIntensity = ref(1.5)
const particleSize = ref(0.06)
const particleOpacity = ref(0.6)
const loading = ref(false)
const orbitalInfo = ref({})

let scene, camera, renderer, controls, particleSystem, animationId

// 完整的轨道列表（到 4f）
const orbitals = [
  // 1s
  { value: '1s', label: '1s', n: 1, l: 0, m: 0, color1: '#00ffff', color2: '#ff00ff' },

  // 2s, 2p
  { value: '2s', label: '2s', n: 2, l: 0, m: 0, color1: '#00ffff', color2: '#ff00ff' },
  { value: '2p_x', label: '2p_x', n: 2, l: 1, m: 1, type: 'x', color1: '#ff6b6b', color2: '#4ecdc4' },
  { value: '2p_y', label: '2p_y', n: 2, l: 1, m: 1, type: 'y', color1: '#ffe66d', color2: '#a8e6cf' },
  { value: '2p_z', label: '2p_z', n: 2, l: 1, m: 0, type: 'z', color1: '#ff6b9d', color2: '#c44569' },

  // 3s, 3p, 3d
  { value: '3s', label: '3s', n: 3, l: 0, m: 0, color1: '#00ffff', color2: '#ff00ff' },
  { value: '3p_x', label: '3p_x', n: 3, l: 1, m: 1, type: 'x', color1: '#ff6b6b', color2: '#4ecdc4' },
  { value: '3p_y', label: '3p_y', n: 3, l: 1, m: 1, type: 'y', color1: '#ffe66d', color2: '#a8e6cf' },
  { value: '3p_z', label: '3p_z', n: 3, l: 1, m: 0, type: 'z', color1: '#ff6b9d', color2: '#c44569' },
  { value: '3d_xy', label: '3d_xy', n: 3, l: 2, m: 2, type: 'xy', color1: '#ffa502', color2: '#ff6348' },
  { value: '3d_xz', label: '3d_xz', n: 3, l: 2, m: 1, type: 'xz', color1: '#1e90ff', color2: '#ff1493' },
  { value: '3d_yz', label: '3d_yz', n: 3, l: 2, m: 1, type: 'yz', color1: '#32cd32', color2: '#ff4500' },
  { value: '3d_x2-y2', label: '3d_x²-y²', n: 3, l: 2, m: 2, type: 'x2-y2', color1: '#9370db', color2: '#ffd700' },
  { value: '3d_z2', label: '3d_z²', n: 3, l: 2, m: 0, type: 'z2', color1: '#00ced1', color2: '#ff69b4' },

  // 4s, 4p, 4d, 4f
  { value: '4s', label: '4s', n: 4, l: 0, m: 0, color1: '#00ffff', color2: '#ff00ff' },
  { value: '4p_x', label: '4p_x', n: 4, l: 1, m: 1, type: 'x', color1: '#ff6b6b', color2: '#4ecdc4' },
  { value: '4p_y', label: '4p_y', n: 4, l: 1, m: 1, type: 'y', color1: '#ffe66d', color2: '#a8e6cf' },
  { value: '4p_z', label: '4p_z', n: 4, l: 1, m: 0, type: 'z', color1: '#ff6b9d', color2: '#c44569' },
  { value: '4d_xy', label: '4d_xy', n: 4, l: 2, m: 2, type: 'xy', color1: '#ffa502', color2: '#ff6348' },
  { value: '4d_xz', label: '4d_xz', n: 4, l: 2, m: 1, type: 'xz', color1: '#1e90ff', color2: '#ff1493' },
  { value: '4d_yz', label: '4d_yz', n: 4, l: 2, m: 1, type: 'yz', color1: '#32cd32', color2: '#ff4500' },
  { value: '4d_x2-y2', label: '4d_x²-y²', n: 4, l: 2, m: 2, type: 'x2-y2', color1: '#9370db', color2: '#ffd700' },
  { value: '4d_z2', label: '4d_z²', n: 4, l: 2, m: 0, type: 'z2', color1: '#00ced1', color2: '#ff69b4' },
  { value: '4f_z3', label: '4f_z³', n: 4, l: 3, m: 0, type: 'z3', color1: '#ff1493', color2: '#00ced1' },
  { value: '4f_xz2', label: '4f_xz²', n: 4, l: 3, m: 1, type: 'xz2', color1: '#ff6347', color2: '#4169e1' },
  { value: '4f_yz2', label: '4f_yz²', n: 4, l: 3, m: 1, type: 'yz2', color1: '#ffa500', color2: '#9370db' },
  { value: '4f_xyz', label: '4f_xyz', n: 4, l: 3, m: 1, type: 'xyz', color1: '#32cd32', color2: '#ff4500' },
  { value: '4f_z(x2-y2)', label: '4f_z(x²-y²)', n: 4, l: 3, m: 2, type: 'z(x2-y2)', color1: '#1e90ff', color2: '#ff1493' },
  { value: '4f_x(x2-3y2)', label: '4f_x(x²-3y²)', n: 4, l: 3, m: 3, type: 'x(x2-3y2)', color1: '#ff00ff', color2: '#00ffff' },
  { value: '4f_y(3x2-y2)', label: '4f_y(3x²-y²)', n: 4, l: 3, m: 3, type: 'y(3x2-y2)', color1: '#ffff00', color2: '#0000ff' },

  // 5s, 5p, 5d, 5f
  { value: '5s', label: '5s', n: 5, l: 0, m: 0, color1: '#00ffff', color2: '#ff00ff' },
  { value: '5p_x', label: '5p_x', n: 5, l: 1, m: 1, type: 'x', color1: '#ff6b6b', color2: '#4ecdc4' },
  { value: '5p_y', label: '5p_y', n: 5, l: 1, m: 1, type: 'y', color1: '#ffe66d', color2: '#a8e6cf' },
  { value: '5p_z', label: '5p_z', n: 5, l: 1, m: 0, type: 'z', color1: '#ff6b9d', color2: '#c44569' },
  { value: '5d_xy', label: '5d_xy', n: 5, l: 2, m: 2, type: 'xy', color1: '#ffa502', color2: '#ff6348' },
  { value: '5d_xz', label: '5d_xz', n: 5, l: 2, m: 1, type: 'xz', color1: '#1e90ff', color2: '#ff1493' },
  { value: '5d_yz', label: '5d_yz', n: 5, l: 2, m: 1, type: 'yz', color1: '#32cd32', color2: '#ff4500' },
  { value: '5d_x2-y2', label: '5d_x²-y²', n: 5, l: 2, m: 2, type: 'x2-y2', color1: '#9370db', color2: '#ffd700' },
  { value: '5d_z2', label: '5d_z²', n: 5, l: 2, m: 0, type: 'z2', color1: '#00ced1', color2: '#ff69b4' },
  { value: '5f_z3', label: '5f_z³', n: 5, l: 3, m: 0, type: 'z3', color1: '#ff1493', color2: '#00ced1' },
  { value: '5f_xz2', label: '5f_xz²', n: 5, l: 3, m: 1, type: 'xz2', color1: '#ff6347', color2: '#4169e1' },
  { value: '5f_yz2', label: '5f_yz²', n: 5, l: 3, m: 1, type: 'yz2', color1: '#ffa500', color2: '#9370db' },
  { value: '5f_xyz', label: '5f_xyz', n: 5, l: 3, m: 1, type: 'xyz', color1: '#32cd32', color2: '#ff4500' },
  { value: '5f_z(x2-y2)', label: '5f_z(x²-y²)', n: 5, l: 3, m: 2, type: 'z(x2-y2)', color1: '#1e90ff', color2: '#ff1493' },
  { value: '5f_x(x2-3y2)', label: '5f_x(x²-3y²)', n: 5, l: 3, m: 3, type: 'x(x2-3y2)', color1: '#ff00ff', color2: '#00ffff' },
  { value: '5f_y(3x2-y2)', label: '5f_y(3x²-y²)', n: 5, l: 3, m: 3, type: 'y(3x2-y2)', color1: '#ffff00', color2: '#0000ff' },

  // 6s, 6p, 6d
  { value: '6s', label: '6s', n: 6, l: 0, m: 0, color1: '#00ffff', color2: '#ff00ff' },
  { value: '6p_x', label: '6p_x', n: 6, l: 1, m: 1, type: 'x', color1: '#ff6b6b', color2: '#4ecdc4' },
  { value: '6p_y', label: '6p_y', n: 6, l: 1, m: 1, type: 'y', color1: '#ffe66d', color2: '#a8e6cf' },
  { value: '6p_z', label: '6p_z', n: 6, l: 1, m: 0, type: 'z', color1: '#ff6b9d', color2: '#c44569' },
  { value: '6d_xy', label: '6d_xy', n: 6, l: 2, m: 2, type: 'xy', color1: '#ffa502', color2: '#ff6348' },
  { value: '6d_xz', label: '6d_xz', n: 6, l: 2, m: 1, type: 'xz', color1: '#1e90ff', color2: '#ff1493' },
  { value: '6d_yz', label: '6d_yz', n: 6, l: 2, m: 1, type: 'yz', color1: '#32cd32', color2: '#ff4500' },
  { value: '6d_x2-y2', label: '6d_x²-y²', n: 6, l: 2, m: 2, type: 'x2-y2', color1: '#9370db', color2: '#ffd700' },
  { value: '6d_z2', label: '6d_z²', n: 6, l: 2, m: 0, type: 'z2', color1: '#00ced1', color2: '#ff69b4' },

  // 7s, 7p
  { value: '7s', label: '7s', n: 7, l: 0, m: 0, color1: '#00ffff', color2: '#ff00ff' },
  { value: '7p_x', label: '7p_x', n: 7, l: 1, m: 1, type: 'x', color1: '#ff6b6b', color2: '#4ecdc4' },
  { value: '7p_y', label: '7p_y', n: 7, l: 1, m: 1, type: 'y', color1: '#ffe66d', color2: '#a8e6cf' },
  { value: '7p_z', label: '7p_z', n: 7, l: 1, m: 0, type: 'z', color1: '#ff6b9d', color2: '#c44569' }
]

onMounted(() => {
  initScene()
  generateOrbital()
  animate()
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  if (renderer) renderer.dispose()
})

const initScene = () => {
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x0a0a0a)
  scene.fog = new THREE.Fog(0x0a0a0a, 10, 50)

  camera = new THREE.PerspectiveCamera(
    75,
    canvas.value.clientWidth / canvas.value.clientHeight,
    0.1,
    1000
  )
  camera.position.set(0, 0, 15)

  renderer = new THREE.WebGLRenderer({
    canvas: canvas.value,
    antialias: true,
    alpha: true
  })
  renderer.setSize(canvas.value.clientWidth, canvas.value.clientHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.autoRotate = false

  const ambientLight = new THREE.AmbientLight(0xffffff, 0.3)
  scene.add(ambientLight)

  const pointLight = new THREE.PointLight(0xffffff, 1, 100)
  pointLight.position.set(5, 5, 5)
  scene.add(pointLight)

  const atomGeometry = new THREE.SphereGeometry(0.3, 32, 32)
  const atomMaterial = new THREE.MeshPhongMaterial({
    color: 0xffffff,
    emissive: 0x444444,
    shininess: 100
  })
  const atom = new THREE.Mesh(atomGeometry, atomMaterial)
  scene.add(atom)

  // 添加更大的坐标轴
  const axisLength = 10
  const axisRadius = 0.01

  // X 轴 (红色)
  const xAxisGeometry = new THREE.CylinderGeometry(axisRadius, axisRadius, axisLength, 8)
  const xAxisMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 })
  const xAxis = new THREE.Mesh(xAxisGeometry, xAxisMaterial)
  xAxis.rotation.z = Math.PI / 2
  scene.add(xAxis)

  // Y 轴 (绿色)
  const yAxisGeometry = new THREE.CylinderGeometry(axisRadius, axisRadius, axisLength, 8)
  const yAxisMaterial = new THREE.MeshBasicMaterial({ color: 0x00ff00 })
  const yAxis = new THREE.Mesh(yAxisGeometry, yAxisMaterial)
  scene.add(yAxis)

  // Z 轴 (蓝色)
  const zAxisGeometry = new THREE.CylinderGeometry(axisRadius, axisRadius, axisLength, 8)
  const zAxisMaterial = new THREE.MeshBasicMaterial({ color: 0x0000ff })
  const zAxis = new THREE.Mesh(zAxisGeometry, zAxisMaterial)
  zAxis.rotation.x = Math.PI / 2
  scene.add(zAxis)

  // 添加坐标轴标签
  const createTextSprite = (text, color) => {
    const canvas2d = document.createElement('canvas')
    const context = canvas2d.getContext('2d')
    canvas2d.width = 128
    canvas2d.height = 128

    context.clearRect(0, 0, 128, 128)
    context.font = 'Bold 80px Arial'
    context.fillStyle = color
    context.textAlign = 'center'
    context.textBaseline = 'middle'
    context.fillText(text, 64, 64)

    const texture = new THREE.CanvasTexture(canvas2d)
    const spriteMaterial = new THREE.SpriteMaterial({ map: texture })
    const sprite = new THREE.Sprite(spriteMaterial)
    sprite.scale.set(1.5, 1.5, 1)
    return sprite
  }

  const xLabel = createTextSprite('X', '#ff0000')
  xLabel.position.set(axisLength / 2 + 1, 0, 0)
  scene.add(xLabel)

  const yLabel = createTextSprite('Y', '#00ff00')
  yLabel.position.set(0, axisLength / 2 + 1, 0)
  scene.add(yLabel)

  const zLabel = createTextSprite('Z', '#0000ff')
  zLabel.position.set(0, 0, axisLength / 2 + 1)
  scene.add(zLabel)

  window.addEventListener('resize', onWindowResize)
}

const onWindowResize = () => {
  if (!canvas.value) return
  camera.aspect = canvas.value.clientWidth / canvas.value.clientHeight
  camera.updateProjectionMatrix()
  renderer.setSize(canvas.value.clientWidth, canvas.value.clientHeight)
}

const generateOrbital = async () => {
  loading.value = true

  try {
    const orbitalData = generateOrbitalData(
      selectedOrbital.value,
      particleCount.value
    )
    createParticleSystem(orbitalData)
  } catch (error) {
    console.error('生成轨道失败:', error)
  } finally {
    loading.value = false
  }
}

// 阶乘函数
const factorial = (n) => {
  if (n <= 1) return 1
  let result = 1
  for (let i = 2; i <= n; i++) result *= i
  return result
}

// 双阶乘函数
const doubleFactorial = (n) => {
  if (n <= 0) return 1
  let result = 1
  for (let i = n; i > 0; i -= 2) result *= i
  return result
}

// 关联拉盖尔多项式 L^alpha_n(x)
const associatedLaguerre = (n, alpha, x) => {
  if (n === 0) return 1
  if (n === 1) return 1 + alpha - x

  // 使用递推关系
  let L0 = 1
  let L1 = 1 + alpha - x
  let L2 = 0

  for (let k = 2; k <= n; k++) {
    L2 = ((2 * k - 1 + alpha - x) * L1 - (k - 1 + alpha) * L0) / k
    L0 = L1
    L1 = L2
  }

  return L2
}

// 连带勒让德多项式 P^m_l(x)
const associatedLegendre = (l, m, x) => {
  const absM = Math.abs(m)

  if (absM > l) return 0

  // P^m_m(x)
  let pmm = 1.0
  if (absM > 0) {
    const somx2 = Math.sqrt((1 - x) * (1 + x))
    let fact = 1.0
    for (let i = 1; i <= absM; i++) {
      pmm *= -fact * somx2
      fact += 2.0
    }
  }

  if (l === absM) return pmm

  // P^m_{m+1}(x)
  let pmmp1 = x * (2 * absM + 1) * pmm

  if (l === absM + 1) return pmmp1

  // P^m_l(x) 递推
  let pll = 0
  for (let ll = absM + 2; ll <= l; ll++) {
    pll = ((2 * ll - 1) * x * pmmp1 - (ll + absM - 1) * pmm) / (ll - absM)
    pmm = pmmp1
    pmmp1 = pll
  }

  return pll
}

// 通用径向波函数 R_nl(r)
const getRadialWavefunction = (n, l, r, Z) => {
  const a0 = 1.0
  const rho = (2 * Z * r) / (n * a0)

  // 归一化系数
  const coeff1 = Math.sqrt(Math.pow(2 * Z / (n * a0), 3) * factorial(n - l - 1) / (2 * n * factorial(n + l)))

  // 径向部分: rho^l * exp(-rho/2) * L^(2l+1)_(n-l-1)(rho)
  const radialPart = Math.pow(rho, l) * Math.exp(-rho / 2) * associatedLaguerre(n - l - 1, 2 * l + 1, rho)

  return coeff1 * radialPart
}

// 通用球谐函数 Y^m_l(theta, phi)
const getSphericalHarmonic = (l, m, type, theta, phi) => {
  const cosTheta = Math.cos(theta)
  const sinTheta = Math.sin(theta)

  // 对于实轨道，需要线性组合
  if (type) {
    // 处理实轨道（线性组合）
    if (l === 0) {
      // s 轨道
      return 1 / Math.sqrt(4 * Math.PI)
    } else if (l === 1) {
      // p 轨道
      if (type === 'x') {
        return Math.sqrt(3 / (4 * Math.PI)) * sinTheta * Math.cos(phi)
      } else if (type === 'y') {
        return Math.sqrt(3 / (4 * Math.PI)) * sinTheta * Math.sin(phi)
      } else if (type === 'z') {
        return Math.sqrt(3 / (4 * Math.PI)) * cosTheta
      }
    } else if (l === 2) {
      // d 轨道
      if (type === 'z2') {
        return Math.sqrt(5 / (16 * Math.PI)) * (3 * cosTheta * cosTheta - 1)
      } else if (type === 'xz') {
        return Math.sqrt(15 / (4 * Math.PI)) * sinTheta * cosTheta * Math.cos(phi)
      } else if (type === 'yz') {
        return Math.sqrt(15 / (4 * Math.PI)) * sinTheta * cosTheta * Math.sin(phi)
      } else if (type === 'xy') {
        return Math.sqrt(15 / (4 * Math.PI)) * sinTheta * sinTheta * Math.sin(phi) * Math.cos(phi)
      } else if (type === 'x2-y2') {
        return Math.sqrt(15 / (16 * Math.PI)) * sinTheta * sinTheta * Math.cos(2 * phi)
      }
    } else if (l === 3) {
      // f 轨道
      const sin2Theta = sinTheta * sinTheta
      const cos2Theta = cosTheta * cosTheta

      if (type === 'z3') {
        return Math.sqrt(7 / (16 * Math.PI)) * (5 * cos2Theta * cosTheta - 3 * cosTheta)
      } else if (type === 'xz2') {
        return Math.sqrt(21 / (32 * Math.PI)) * (5 * cos2Theta - 1) * sinTheta * Math.cos(phi)
      } else if (type === 'yz2') {
        return Math.sqrt(21 / (32 * Math.PI)) * (5 * cos2Theta - 1) * sinTheta * Math.sin(phi)
      } else if (type === 'xyz') {
        return Math.sqrt(105 / (4 * Math.PI)) * sinTheta * sinTheta * cosTheta * Math.sin(phi) * Math.cos(phi)
      } else if (type === 'z(x2-y2)') {
        return Math.sqrt(105 / (16 * Math.PI)) * sin2Theta * cosTheta * Math.cos(2 * phi)
      } else if (type === 'x(x2-3y2)') {
        return Math.sqrt(35 / (32 * Math.PI)) * sin2Theta * sinTheta * (Math.cos(phi) * Math.cos(2 * phi) - Math.sin(phi) * Math.sin(2 * phi))
      } else if (type === 'y(3x2-y2)') {
        return Math.sqrt(35 / (32 * Math.PI)) * sin2Theta * sinTheta * (Math.sin(phi) * Math.cos(2 * phi) + Math.cos(phi) * Math.sin(2 * phi))
      }
    }
  }

  // 标准复球谐函数（如果没有指定 type）
  const absM = Math.abs(m)
  const Plm = associatedLegendre(l, absM, cosTheta)

  const normalization = Math.sqrt((2 * l + 1) / (4 * Math.PI) * factorial(l - absM) / factorial(l + absM))

  if (m === 0) {
    return normalization * Plm
  } else if (m > 0) {
    return normalization * Plm * Math.cos(m * phi) * Math.sqrt(2)
  } else {
    return normalization * Plm * Math.sin(absM * phi) * Math.sqrt(2)
  }
}

const generateOrbitalData = (orbitalType, count) => {
  const positions = []
  const colors = []
  const sizes = []

  // 从轨道列表中获取量子数
  const orbital = orbitals.find(o => o.value === orbitalType)
  if (!orbital) return { positions, colors, sizes }

  const { n, l, m, type, color1: c1, color2: c2 } = orbital
  const color1 = new THREE.Color(c1)
  const color2 = new THREE.Color(c2)

  // 有效核电荷数（固定为氢原子）
  const Z = 1

  // 玻尔半径
  const a0 = 1.0

  // 固定搜索范围，让所有轨道视觉大小一致
  const searchRadius = 8  // 固定大小

  // 但在计算波函数时使用正确的缩放
  const scaleFactor = 1.0 / n  // n 越大，波函数越分散，需要缩放

  // 计算径向节点数和角节点数
  const radialNodes = n - l - 1
  const angularNodes = l

  // 更新轨道信息
  orbitalInfo.value = {
    n: n,
    l: l,
    m: m,
    name: orbital.label,
    radialNodes: radialNodes,
    angularNodes: angularNodes,
    totalNodes: radialNodes + angularNodes,
    shellName: ['K', 'L', 'M', 'N', 'O', 'P', 'Q'][n - 1] || `n=${n}`,
    subshellName: ['s', 'p', 'd', 'f', 'g', 'h'][l] || `l=${l}`
  }

  let generated = 0
  let attempts = 0
  const maxAttempts = count * 1000

  // 预计算最大概率（用于归一化）
  let maxProb = 0
  for (let i = 0; i < 2000; i++) {
    const testR = Math.random() * searchRadius
    const testTheta = Math.acos(2 * Math.random() - 1)
    const testPhi = Math.random() * 2 * Math.PI

    const physicalTestR = testR / scaleFactor

    const R = getRadialWavefunction(n, l, physicalTestR, Z)
    const Y = getSphericalHarmonic(l, m, type, testTheta, testPhi)
    const prob = R * R * Y * Y * testR * testR

    if (prob > maxProb) maxProb = prob
  }

  while (generated < count && attempts < maxAttempts) {
    attempts++

    // 均匀球体采样
    const r = Math.random() * searchRadius
    const cosTheta = 2 * Math.random() - 1
    const theta = Math.acos(cosTheta)
    const phi = Math.random() * 2 * Math.PI

    // 应用缩放：将采样半径映射到物理半径
    const physicalR = r / scaleFactor

    // 计算波函数
    const R = getRadialWavefunction(n, l, physicalR, Z)
    const Y = getSphericalHarmonic(l, m, type, theta, phi)

    const psi = R * Y
    const prob = psi * psi * r * r  // 包含径向体积元 r²

    // 拒绝采样
    if (Math.random() * maxProb < prob) {
      // 转换为笛卡尔坐标
      const x = r * Math.sin(theta) * Math.cos(phi)
      const y = r * Math.sin(theta) * Math.sin(phi)
      const z = r * Math.cos(theta)

      positions.push(x, y, z)

      // 根据波函数符号着色
      let color
      if (psi > 0) {
        color = color1
      } else {
        color = color2
      }
      colors.push(color.r, color.g, color.b)

      sizes.push(0.05)
      generated++
    }
  }

  console.log(`生成 ${orbital.label}: ${generated} 个粒子，尝试 ${attempts} 次，径向节点=${radialNodes}，角节点=${angularNodes}`)

  return { positions, colors, sizes }
}

const createParticleSystem = (data) => {
  if (particleSystem) {
    scene.remove(particleSystem)
    particleSystem.geometry.dispose()
    particleSystem.material.dispose()
  }

  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(data.positions, 3))
  geometry.setAttribute('color', new THREE.Float32BufferAttribute(data.colors, 3))
  geometry.setAttribute('size', new THREE.Float32BufferAttribute(data.sizes, 1))

  const material = new THREE.PointsMaterial({
    size: particleSize.value,
    vertexColors: true,
    transparent: true,
    opacity: particleOpacity.value,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    sizeAttenuation: true,
    map: createGlowTexture()
  })

  particleSystem = new THREE.Points(geometry, material)
  scene.add(particleSystem)
}

// 创建发光纹理
const createGlowTexture = () => {
  const canvas = document.createElement('canvas')
  canvas.width = 64
  canvas.height = 64
  const ctx = canvas.getContext('2d')

  // 创建径向渐变，边缘更清晰
  const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32)
  gradient.addColorStop(0, 'rgba(255, 255, 255, 1)')
  gradient.addColorStop(0.4, 'rgba(255, 255, 255, 0.9)')
  gradient.addColorStop(0.7, 'rgba(255, 255, 255, 0.4)')
  gradient.addColorStop(0.9, 'rgba(255, 255, 255, 0.1)')
  gradient.addColorStop(1, 'rgba(255, 255, 255, 0)')

  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, 64, 64)

  const texture = new THREE.CanvasTexture(canvas)
  return texture
}

const animate = () => {
  animationId = requestAnimationFrame(animate)

  if (controls) controls.update()

  if (renderer && scene && camera) {
    renderer.render(scene, camera)
  }
}

const updateGlow = () => {
  if (particleSystem && particleSystem.material) {
    // 发光强度影响透明度
    particleSystem.material.opacity = particleOpacity.value * (glowIntensity.value / 1.5)
  }
}

const updateSize = () => {
  if (particleSystem && particleSystem.material) {
    particleSystem.material.size = particleSize.value
  }
}
</script>

<template>
  <div class="page-wrapper">
    <NavBar />
    <div class="orbital-viewer">
    <div class="controls">
      <h2>原子轨道可视化</h2>

      <div class="control-group">
        <label>轨道类型</label>
        <select v-model="selectedOrbital">
          <option v-for="orb in orbitals" :key="orb.value" :value="orb.value">
            {{ orb.label }}
          </option>
        </select>
      </div>

      <div class="control-group">
        <label>粒子数量: {{ particleCount }}</label>
        <input type="range" v-model.number="particleCount" min="10000" max="100000" step="5000">
      </div>

      <div class="control-group">
        <label>粒子大小: {{ parseFloat(particleSize).toFixed(2) }}</label>
        <input type="range" v-model.number="particleSize" min="0.01" max="0.2" step="0.01" @input="updateSize">
      </div>

      <div class="control-group">
        <label>粒子透明度: {{ parseFloat(particleOpacity).toFixed(2) }}</label>
        <input type="range" v-model.number="particleOpacity" min="0.1" max="1.0" step="0.05" @input="updateGlow">
      </div>

      <div class="control-group">
        <label>发光强度: {{ parseFloat(glowIntensity).toFixed(1) }}</label>
        <input type="range" v-model.number="glowIntensity" min="0.5" max="3" step="0.1" @input="updateGlow">
      </div>

      <button @click="generateOrbital" :disabled="loading" class="btn-generate">
        {{ loading ? '生成中...' : '重新生成' }}
      </button>

      <div class="info" v-if="orbitalInfo.name">
        <h3>轨道信息</h3>
        <p><strong>名称:</strong> {{ orbitalInfo.name }}</p>
        <p><strong>能层:</strong> {{ orbitalInfo.shellName }} (n={{ orbitalInfo.n }})</p>
        <p><strong>能级:</strong> {{ orbitalInfo.subshellName }} (l={{ orbitalInfo.l }})</p>
        <p><strong>磁量子数:</strong> m={{ orbitalInfo.m }}</p>
        <p><strong>径向节点:</strong> {{ orbitalInfo.radialNodes }}</p>
        <p><strong>角节点:</strong> {{ orbitalInfo.angularNodes }}</p>
        <p><strong>总节点数:</strong> {{ orbitalInfo.totalNodes }}</p>
      </div>

      <div class="info">
        <p>🖱️ 拖动旋转</p>
        <p>🔍 滚轮缩放</p>
      </div>
    </div>

    <div class="canvas-container">
      <canvas ref="canvas"></canvas>
      <div v-if="loading" class="loading">生成中...</div>
    </div>
  </div>
  </div>
</template>

<style scoped>
.page-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.orbital-viewer {
  display: flex;
  flex: 1;
  background: #0a0a0a;
  color: white;
}

.controls {
  width: 300px;
  background: rgba(20, 20, 20, 0.9);
  padding: 2rem;
  overflow-y: auto;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.controls h2 {
  margin: 0 0 2rem;
  font-size: 1.5rem;
  background: linear-gradient(135deg, #00ffff 0%, #ff00ff 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
}

.control-group {
  margin-bottom: 1.5rem;
}

.control-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #aaa;
}

.control-group select,
.control-group input[type="range"] {
  width: 100%;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: white;
  font-size: 0.9rem;
}

.control-group select option {
  background: #1a1a1a;
  color: white;
}

.control-group select {
  cursor: pointer;
}

.control-group select:focus {
  outline: none;
  border-color: #00ffff;
}

.btn-generate {
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(135deg, #00ffff 0%, #ff00ff 100%);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-generate:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn-generate:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.info {
  margin-top: 2rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  font-size: 0.85rem;
  color: #888;
}

.info h3 {
  margin: 0 0 0.75rem;
  font-size: 1rem;
  color: #00ffff;
}

.info p {
  margin: 0.5rem 0;
  line-height: 1.6;
}

.info p strong {
  color: #aaa;
}

.canvas-container {
  flex: 1;
  position: relative;
}

canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.5rem;
  color: #00ffff;
}
</style>
