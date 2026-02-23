<template>
  <div class="answer-panel">
    <div class="answer-header">
      <div class="answer-avatar">🤖</div>
      <span class="answer-title">AI 助教</span>
    </div>

    <div class="answer-content">
      <p class="answer-text">
        氨气（NH₃）是极性分子，原因如下：
      </p>

      <ol class="answer-steps">
        <li>
          <strong>N-H 键是极性键</strong>：氮原子的电负性（3.0）大于氢原子（2.1），电子云偏向氮原子。
        </li>
        <li>
          <strong>分子构型不对称</strong>：氨分子呈三角锥形，氮原子上有一对孤对电子。
        </li>
        <li>
          <strong>偶极矩不能抵消</strong>：三个 N-H 键的极性不能相互抵消，整个分子表现出极性。
        </li>
      </ol>

      <!-- 对比示例 -->
      <div class="comparison-box">
        <h4>对比：四氯化碳（CCl₄）</h4>
        <p>CCl₄ 虽然有极性键，但分子呈正四面体构型，高度对称，键的极性相互抵消，因此是非极性分子。</p>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="answer-actions">
      <button class="action-btn primary">追问</button>
      <button class="action-btn">收藏</button>
      <button class="action-btn">出题练习</button>
    </div>

    <!-- 相关知识点 -->
    <div class="related-topics">
      <span class="topics-label">相关知识点：</span>
      <div class="topic-tags">
        <span class="topic-tag">分子极性</span>
        <span class="topic-tag">VSEPR理论</span>
        <span class="topic-tag">杂化轨道</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.answer-panel {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.answer-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.answer-avatar {
  font-size: 1.5rem;
}

.answer-title {
  font-weight: 600;
  color: #1e293b;
}

.answer-content {
  margin-bottom: 1.5rem;
}

.answer-text {
  color: #1e293b;
  line-height: 1.75;
  margin-bottom: 1rem;
}

.answer-steps {
  padding-left: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.answer-steps li {
  color: #1e293b;
  line-height: 1.75;
}

.comparison-box {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-left: 3px solid #2563eb;
  border-radius: 0 8px 8px 0;
}

.comparison-box h4 {
  font-size: 0.875rem;
  color: #2563eb;
  margin-bottom: 0.5rem;
}

.comparison-box p {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.6;
}

.answer-actions {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  background: white;
  color: #64748b;
  border-radius: 8px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  border-color: #2563eb;
  color: #2563eb;
}

.action-btn.primary {
  background: #2563eb;
  color: white;
  border-color: #2563eb;
}

.action-btn.primary:hover {
  background: #1d4ed8;
}

.related-topics {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.topics-label {
  font-size: 0.875rem;
  color: #64748b;
}

.topic-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.topic-tag {
  padding: 0.25rem 0.75rem;
  background: #f1f5f9;
  color: #2563eb;
  border-radius: 100px;
  font-size: 0.75rem;
}
</style>
