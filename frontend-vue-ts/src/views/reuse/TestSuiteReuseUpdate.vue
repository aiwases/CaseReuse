<template>
  <div class="project-detail-page">
    <!-- 页面顶部操作栏 -->
    <div class="page-header">
      <h2>测试套件重用与更新</h2>
      <div class="page-actions">
        <StartRunButton :project-id="projectId" :stage="6" page-type="effect-aware-reuse" />
      </div>
    </div>
    
    <!-- 进度条组件 -->
    <ReuseProgressBar :project-id="projectId" />
    
    <!-- 左右分栏布局 -->
    <div class="document-detail-layout">
      <!-- 左侧上一步结果区域 -->
      <div class="left-panel">
        <CascadingImpactScopeAnalysisResult />
      </div>
      
      <!-- 右侧结果区域 -->
      <div class="right-panel">
        <TestSuiteReuseUpdateResult />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import ReuseProgressBar from '@/components/ReuseProgressBar.vue'
import CascadingImpactScopeAnalysisResult from '@/layouts/projectDetail/reuse/IntermediateResult/CascadingImpactScopeAnalysisResult.vue'
import TestSuiteReuseUpdateResult from '@/layouts/projectDetail/reuse/IntermediateResult/TestSuiteReuseUpdateResult.vue'
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

/* 左右分栏布局 */
.document-detail-layout {
  display: flex;
  gap: 20px;
  margin-top: 20px;
  height: calc(100vh - 200px);
}

/* 左侧原文面板 */
.left-panel {
  flex: 1;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 右侧结果面板 */
.right-panel {
  flex: 1;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .document-detail-layout {
    flex-direction: column;
    height: auto;
  }
  
  .right-panel {
    width: 100%;
    margin-top: 20px;
  }
}
</style>