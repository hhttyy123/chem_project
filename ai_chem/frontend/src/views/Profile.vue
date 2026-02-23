<template>
  <div class="profile-page">
    <NavBar />

    <main class="main-content">
      <div class="header">
        <div class="avatar">👤</div>
        <h1>学习者</h1>
        <p>高二学生</p>
      </div>

      <!-- 学习统计 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">28</div>
          <div class="stat-label">已学知识点</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">156</div>
          <div class="stat-label">练习题数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">85%</div>
          <div class="stat-label">正确率</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">12</div>
          <div class="stat-label">收藏数</div>
        </div>
      </div>

      <!-- 掌握度热力图 -->
      <div class="mastery-section">
        <h2>知识点掌握度</h2>
        <div class="mastery-list">
          <div class="mastery-item" v-for="i in 5" :key="i">
            <div class="mastery-info">
              <span class="topic">分子结构</span>
              <span class="score">92%</span>
            </div>
            <div class="mastery-bar">
              <div class="mastery-fill" style="width: 92%"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 设置选项 -->
      <div class="settings-section">
        <h2>设置</h2>
        <div class="settings-list">
          <div class="setting-item">
            <span>学习模式</span>
            <select class="setting-select">
              <option>速通模式</option>
              <option>深度模式</option>
            </select>
          </div>
          <div class="setting-item">
            <span>复习提醒</span>
            <input type="checkbox" checked />
          </div>
          <div class="setting-item">
            <span>清除缓存</span>
            <button class="setting-btn">清除</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import NavBar from '@/components/NavBar.vue'
</script>

<style scoped>
.profile-page {
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

.avatar {
  width: 80px;
  height: 80px;
  margin: 0 auto 1rem;
  font-size: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 50%;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.header h1 {
  font-size: 1.5rem;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.header p {
  color: #64748b;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  text-align: center;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #2563eb;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: #64748b;
}

.mastery-section,
.settings-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  margin-bottom: 1.5rem;
}

.mastery-section h2,
.settings-section h2 {
  font-size: 1.125rem;
  margin-bottom: 1rem;
  color: #1e293b;
}

.mastery-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.mastery-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.mastery-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
}

.topic {
  color: #1e293b;
}

.score {
  color: #2563eb;
  font-weight: 600;
}

.mastery-bar {
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.mastery-fill {
  height: 100%;
  background: linear-gradient(90deg, #2563eb, #10b981);
  border-radius: 4px;
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-select {
  padding: 0.375rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.875rem;
}

.setting-btn {
  padding: 0.375rem 0.75rem;
  background: #fef2f2;
  color: #ef4444;
  border: 1px solid #fecaca;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
}
</style>
