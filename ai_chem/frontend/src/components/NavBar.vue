<template>
  <nav class="navbar">
    <div class="nav-container">
      <!-- Logo -->
      <div class="logo">
        <span class="logo-icon">🧪</span>
        <span class="logo-text">ChemTutor</span>
      </div>

      <!-- 导航链接 -->
      <div class="nav-links">
        <router-link to="/" class="nav-link">问答</router-link>
        <router-link to="/viewer" class="nav-link">分子</router-link>
        <router-link to="/practice" class="nav-link">练习</router-link>
      </div>

      <!-- 右侧操作 -->
      <div class="nav-actions">
        <button class="mode-toggle">
          <span>{{ isQuickMode ? '速通' : '深度' }}</span>
        </button>
        <router-link to="/favorites" class="icon-btn">⭐</router-link>
        <router-link to="/profile" class="icon-btn">👤</router-link>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const isQuickMode = ref(true)
</script>

<style scoped>
.navbar {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.logo-icon {
  font-size: 1.5rem;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2563eb;
}

.nav-links {
  display: flex;
  gap: 0.5rem;
}

.nav-link {
  padding: 0.5rem 1rem;
  color: #64748b;
  text-decoration: none;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.nav-link:hover {
  color: #2563eb;
  background: #f1f5f9;
}

.nav-link:active {
  transform: scale(0.95);
  background: #e0e7ff;
}

.nav-link.active,
.nav-link.router-link-active {
  color: #2563eb;
  background: #dbeafe;
}

.nav-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.mode-toggle {
  padding: 0.375rem 0.75rem;
  background: #f1f5f9;
  border: none;
  border-radius: 6px;
  font-size: 0.75rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-toggle:hover {
  background: #e2e8f0;
}

.mode-toggle:active {
  transform: scale(0.95);
  background: #cbd5e1;
}

.icon-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
  color: #64748b;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: #f1f5f9;
  color: #2563eb;
}

.icon-btn:active {
  transform: scale(0.9);
  background: #e0e7ff;
  color: #1d4ed8;
}
</style>
