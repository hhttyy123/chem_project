<template>
  <div class="favorites-page">
    <NavBar />

    <main class="main-content">
      <div class="header">
        <h1>我的收藏</h1>
        <p>收藏的知识点和问题</p>
      </div>

      <!-- 收藏列表 -->
      <div class="favorites-list">
        <div class="favorite-item" v-for="i in 4" :key="i">
          <div class="item-icon">⭐</div>
          <div class="item-content">
            <h3>为什么氨气是极性分子？</h3>
            <p class="item-topic">分子结构 · 分子极性</p>
            <p class="item-date">收藏于 2024-01-30</p>
          </div>
          <div class="item-actions">
            <button class="btn-view">查看</button>
            <button class="btn-remove">取消收藏</button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div class="empty-state" v-if="false">
        <p>暂无收藏内容</p>
        <p class="hint">开始提问并收藏感兴趣的知识点吧</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import NavBar from '@/components/NavBar.vue'
</script>

<style scoped>
.favorites-page {
  min-height: 100vh;
  background: #f8fafc;
}

.main-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 2rem;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.header p {
  color: #64748b;
}

.favorites-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.favorite-item {
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  display: flex;
  gap: 1rem;
}

.item-icon {
  font-size: 1.5rem;
}

.item-content {
  flex: 1;
}

.item-content h3 {
  font-size: 1rem;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.item-topic {
  font-size: 0.875rem;
  color: #2563eb;
  margin-bottom: 0.25rem;
}

.item-date {
  font-size: 0.75rem;
  color: #94a3b8;
}

.item-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  justify-content: center;
}

.btn-view,
.btn-remove {
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-view {
  background: #2563eb;
  color: white;
  border: none;
}

.btn-view:hover {
  background: #1d4ed8;
}

.btn-remove {
  background: transparent;
  color: #ef4444;
  border: 1px solid #fecaca;
}

.btn-remove:hover {
  background: #fef2f2;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #64748b;
}

.hint {
  font-size: 0.875rem !important;
  color: #94a3b8 !important;
  margin-top: 0.5rem;
}
</style>
