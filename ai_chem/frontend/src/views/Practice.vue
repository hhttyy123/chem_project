<template>
  <div class="practice-page">
    <NavBar />

    <main class="main-content">
      <div class="header">
        <h1>练习题</h1>
        <p>巩固化学知识</p>
      </div>

      <!-- 题目筛选 -->
      <div class="filter-bar">
        <select class="filter-select">
          <option>全部知识点</option>
          <option>分子结构</option>
          <option>化学平衡</option>
          <option>氧化还原</option>
        </select>
        <select class="filter-select">
          <option>全部难度</option>
          <option>简单</option>
          <option>中等</option>
          <option>困难</option>
        </select>
      </div>

      <!-- 题目列表 -->
      <div class="questions-list">
        <div class="question-card" v-for="i in 5" :key="i">
          <div class="question-header">
            <span class="question-type">选择题</span>
            <span class="question-difficulty">中等</span>
          </div>
          <div class="question-content">
            <p>下列物质中，属于极性分子的是：</p>
            <div class="options">
              <label class="option">
                <input type="radio" name="q1" />
                <span>A. CO₂</span>
              </label>
              <label class="option">
                <input type="radio" name="q1" />
                <span>B. CCl₄</span>
              </label>
              <label class="option">
                <input type="radio" name="q1" />
                <span>C. NH₃</span>
              </label>
              <label class="option">
                <input type="radio" name="q1" />
                <span>D. CH₄</span>
              </label>
            </div>
          </div>
          <div class="question-actions">
            <button class="btn-submit">提交答案</button>
            <button class="btn-view">查看解析</button>
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
.practice-page {
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

.filter-bar {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  font-size: 0.875rem;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.question-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.question-header {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.question-type {
  padding: 0.25rem 0.75rem;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 4px;
  font-size: 0.75rem;
}

.question-difficulty {
  padding: 0.25rem 0.75rem;
  background: #fef3c7;
  color: #92400e;
  border-radius: 4px;
  font-size: 0.75rem;
}

.question-content p {
  margin-bottom: 1rem;
  color: #1e293b;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.option:hover {
  border-color: #2563eb;
  background: #f8fafc;
}

.option input[type="radio"] {
  margin: 0;
}

.question-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.btn-submit,
.btn-view {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-submit {
  background: #2563eb;
  color: white;
  border: none;
}

.btn-submit:hover {
  background: #1d4ed8;
}

.btn-view {
  background: transparent;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.btn-view:hover {
  border-color: #64748b;
  color: #1e293b;
}
</style>
