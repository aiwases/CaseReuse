<template>
  <div class="project-detail-page">
    <!-- 页面顶部操作栏 -->
    <div class="page-header">
      <h2>文档详情</h2>
      <div class="page-actions">
        <StartRunButton :project-id="projectId" workflow="reuse" />
      </div>
    </div>
    
    <!-- 进度条组件 -->
    <ReuseProgressBar :project-id="projectId" />
    
    <!-- 左右分栏布局 -->
    <div class="document-detail-layout">
      <!-- 左侧文件上传区域 -->
      <div class="left-panel">
        <FileUpload :projectId="projectId" />
      </div>
      
      <!-- 右侧结果展示区域 -->
      <div class="right-panel">
        <TestSuiteReuseUpdateResult />
      </div>
    </div>
    
    <!-- 重用追溯图区域 -->
    <div class="reuse-trace-graph-section">
      <ReuseTraceGraph :projectId="projectId" />
    </div>
    
    <!-- 文件下载区域 -->
    <div class="file-download-section">
      <FileDownload 
        :projectId="projectId"
        :showFixedFiles="true"
        :showIntermediateFiles="true"
        :showResultFile="true"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import ReuseProgressBar from '@/components/ReuseProgressBar.vue'
import FileUpload from '@/layouts/projectDetail/reuse/detail/FileUpload.vue'
import TestSuiteReuseUpdateResult from '@/layouts/projectDetail/reuse/IntermediateResult/TestSuiteReuseUpdateResult.vue'
import ReuseTraceGraph from '@/layouts/projectDetail/reuse/graph/ReuseTraceGraph.vue'
import FileDownload from '@/layouts/projectDetail/reuse/detail/FileDownload.vue'
import StartRunButton from '@/layouts/projectDetail/StartRunButton.vue'

const route = useRoute()
const projectId = Number(route.params.id)
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
  min-height: 600px;
}

/* 左侧面板 */
.left-panel {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  border-radius: 4px;
  overflow: hidden;
}

/* 右侧面板 */
.right-panel {
  flex: 1;
  height: 100%;
  border-radius: 4px;
  overflow: hidden;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

/* 重用追溯图区域 */
.reuse-trace-graph-section {
  margin-top: 20px;
  border-radius: 4px;
  overflow: hidden;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: calc(90vh);
}

/* 文件下载区域 */
.file-download-section {
  margin-top: 20px;
  border-radius: 4px;
  overflow: hidden;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .document-detail-layout {
    flex-direction: column;
    height: auto;
    min-height: auto;
  }
  
  .right-panel {
    width: 100%;
    margin-top: 20px;
  }
  
  .reuse-trace-graph-section {
    width: 100%;
    margin-top: 20px;
    height: auto;
    min-height: 400px;
  }
  
  .file-download-section {
    margin-top: 20px;
  }
}
</style>
