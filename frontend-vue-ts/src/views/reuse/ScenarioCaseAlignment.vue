<template>
  <div class="project-detail-page">
    <!-- 页面顶部操作栏 -->
    <div class="page-header">
      <h2>测试场景-测试用例对齐</h2>
      <div class="page-actions">
        <StartRunButton :project-id="projectId" :stage="2" page-type="dependency-modeling" />
      </div>
    </div>
    
    <!-- 进度条组件 -->
    <ReuseProgressBar :project-id="projectId" />
    
    <!-- 单栏布局 -->
    <div class="single-panel-layout">
      <!-- 结果区域 -->
      <div class="result-panel">
        <ScenarioCaseAlignmentGraph />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import ReuseProgressBar from '@/components/ReuseProgressBar.vue'
import ScenarioCaseAlignmentGraph from '@/layouts/projectDetail/reuse/IntermediateResult/ScenarioCaseAlignmentGraph.vue'
import StartRunButton from '@/layouts/projectDetail/StartRunButton.vue'

const route = useRoute()
const projectId = route.params.id as string
</script>

<style scoped>
.project-detail-page {
  padding: 20px;
  min-height: calc(100vh - 64px);
  background-color: #f5f7fa;
}

/* 页面顶部样式 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.page-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.page-actions {
  display: flex;
  gap: 10px;
}

/* 单栏布局 */
.single-panel-layout {
  margin-top: 20px;
  height: calc(100vh - 200px);
}

/* 结果面板 */
.result-panel {
  width: 100%;
  height: 100%;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .single-panel-layout {
    height: auto;
  }
}
</style>