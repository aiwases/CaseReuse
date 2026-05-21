<template>
  <div class="project-detail-page">
    <!-- 页面顶部操作栏 -->
    <div class="page-header">
      <h2>级联影响范围分析</h2>
      <div class="page-actions">
        <StartRunButton :project-id="projectId" :stage="5" page-type="effect-aware-reuse" />
      </div>
    </div>
    
    <!-- 进度条组件 -->
    <ReuseProgressBar :project-id="projectId" />
    
    <!-- 左右分栏布局 -->
    <div class="document-detail-layout">
      <!-- 左侧上下布局 -->
      <div class="left-panel">
        <!-- 左侧上部：场景-测试用例对齐关系图 -->
        <div class="left-top-panel">
          <ScenarioCaseAlignmentGraph />
        </div>
        <!-- 左侧下部：监管变更识别结果 -->
        <div class="left-bottom-panel">
          <RegulatoryChangeIdentificationResult />
        </div>
      </div>
      
      <!-- 右侧结果区域 -->
      <div class="right-panel">
        <CascadingImpactScopeAnalysisResult />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import ReuseProgressBar from '@/components/ReuseProgressBar.vue'
import ScenarioCaseAlignmentGraph from '@/layouts/projectDetail/reuse/IntermediateResult/ScenarioCaseAlignmentGraph.vue'
import RegulatoryChangeIdentificationResult from '@/layouts/projectDetail/reuse/IntermediateResult/RegulatoryChangeIdentificationResult.vue'
import CascadingImpactScopeAnalysisResult from '@/layouts/projectDetail/reuse/IntermediateResult/CascadingImpactScopeAnalysisResult.vue'
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

/* 左侧面板（上下布局） */
.left-panel {
  flex: 1;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
}

/* 左侧上部面板 */
.left-top-panel {
  flex: 1;
  background-color: #f9f9f9;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 左侧下部面板 */
.left-bottom-panel {
  flex: 1;
  background-color: #f9f9f9;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
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