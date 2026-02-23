<template>
  <div class="question-input">
    <div class="input-wrapper">
      <input
        type="text"
        placeholder="请输入你的化学问题... 例如：为什么氨气是极性分子？"
        class="input-field"
      />
      <button class="submit-btn">
        <span v-if="!loading">提问</span>
        <span v-else>...</span>
      </button>
    </div>

    <!-- 示例问题 -->
    <div class="example-questions">
      <span class="example-label">试试问：</span>
      <button class="example-btn">为什么氨气是极性分子？</button>
      <button class="example-btn">展示甲烷的分子结构</button>
      <button class="example-btn">水的电子式是什么？</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const loading = ref(false)
</script>

<style scoped>
.question-input {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.input-wrapper {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.input-field {
  flex: 1;
  padding: 0.875rem 1.25rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 1rem;
  outline: none;
  transition: all 0.2s;
}

.input-field:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.submit-btn {
  padding: 0.875rem 2rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn:hover {
  background: #1d4ed8;
}

.example-questions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.example-label {
  font-size: 0.875rem;
  color: #64748b;
}

.example-btn {
  padding: 0.375rem 0.75rem;
  background: #f1f5f9;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.example-btn:hover {
  background: #e2e8f0;
  color: #2563eb;
}
</style>
