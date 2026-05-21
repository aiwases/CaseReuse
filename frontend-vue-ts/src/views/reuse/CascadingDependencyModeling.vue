<template>
  <div class="project-detail-page">
    <!-- 页面顶部操作栏 -->
    <div class="page-header">
      <h2>级联依赖建模</h2>
      <div class="page-actions">
        <StartRunButton :project-id="projectId" :stage="currentStage" page-type="dependency-modeling" />
        <el-dropdown>
          <el-button type="primary" plain :loading="isDownloading">
            下载文件
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleDownloadUpload">
                下载上传文件
              </el-dropdown-item>
              <el-dropdown-item @click="handleDownloadIntermediate(1)">
                下载独立需求生成结果
              </el-dropdown-item>
              <el-dropdown-item @click="handleDownloadIntermediate(2)">
                下载测试场景合成结果
              </el-dropdown-item>
              <el-dropdown-item @click="handleDownloadIntermediate(3)">
                下载场景-测试用例对齐结果
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <!-- 进度条组件 -->
    <ReuseProgressBar :project-id="projectId" />
    
    <!-- 导航按钮 -->
    <div class="navigation-buttons">
      <button 
        class="nav-btn prev-btn" 
        @click="prevStage"
        :disabled="currentStage === 0"
      >
        上一步
      </button>
      <div class="stage-indicator">
        <span 
          v-for="(stage, index) in stages" 
          :key="index"
          class="stage-dot"
          :class="{ active: index === currentStage }"
          @click="goToStage(index)"
        ></span>
      </div>
      <button 
        class="nav-btn next-btn" 
        @click="nextStage"
        :disabled="currentStage === stages.length - 1"
      >
        下一步
      </button>
    </div>
    
    <!-- 根据当前选择的阶段显示不同的组件 -->
    <div v-if="currentStage === 0" class="document-detail-layout">
      <!-- 左侧原文区域 -->
      <div class="left-panel">
        <OriginalDocument />
      </div>
      
      <!-- 右侧结果区域 -->
      <div class="right-panel">
        <IndependentRequirementResult />
      </div>
    </div>
    
    <div v-else-if="currentStage === 1" class="document-detail-layout">
      <!-- 左侧上一步结果区域 -->
      <div class="left-panel">
        <IndependentRequirementResult />
      </div>
      
      <!-- 右侧结果区域 -->
      <div class="right-panel">
        <TestScenarioSynthesisResult />
      </div>
    </div>
    
    <div v-else-if="currentStage === 2" class="single-panel-layout">
      <!-- 结果区域 -->
      <div class="result-panel">
        <ScenarioCaseAlignmentGraph />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowDown } from '@element-plus/icons-vue'
import ReuseProgressBar from '@/components/ReuseProgressBar.vue'
import OriginalDocument from '@/layouts/projectDetail/reuse/IntermediateResult/OriginalDocument.vue'
import IndependentRequirementResult from '@/layouts/projectDetail/reuse/IntermediateResult/IndependentRequirementResult.vue'
import TestScenarioSynthesisResult from '@/layouts/projectDetail/reuse/IntermediateResult/TestScenarioSynthesisResult.vue'
import ScenarioCaseAlignmentGraph from '@/layouts/projectDetail/reuse/IntermediateResult/ScenarioCaseAlignmentGraph.vue'
import StartRunButton from '@/layouts/projectDetail/StartRunButton.vue'
import { useResultStore } from '@/store/resultStore'

const route = useRoute()
const projectId = route.params.id as string
const projectIdNumber = computed(() => Number(projectId))
const resultStore = useResultStore()

// 阶段配置
const stages = [
  { id: 'independent-requirement', name: '独立需求生成' },
  { id: 'test-scenario', name: '测试场景合成' },
  { id: 'scenario-case-alignment', name: '场景-测试用例对齐' }
]

// 当前阶段索引
const currentStage = ref(0)

// 上一步
const prevStage = () => {
  if (currentStage.value > 0) {
    currentStage.value--
  }
}

// 下一步
const nextStage = () => {
  if (currentStage.value < stages.length - 1) {
    currentStage.value++
  }
}

// 跳转到指定阶段
const goToStage = (index: number) => {
  currentStage.value = index
}

// 下载相关
const isDownloading = computed(() => resultStore.isDownloading)

// 下载上传文件
const handleDownloadUpload = async () => {
  try {
    await resultStore.handleDownloadUpload(projectIdNumber.value)
  } catch (error) {
    console.error('下载上传文件失败:', error)
  }
}

// 下载中间结果
const handleDownloadIntermediate = async (index: number) => {
  try {
    await resultStore.handleDownloadIntermediate(projectIdNumber.value, index)
  } catch (error) {
    console.error('下载中间结果失败:', error)
  }
}


</script>

<style scoped>
.project-detail-page {
  padding: 24px;
  min-height: calc(100vh - 64px);
  background-color: #f8f9fa;
}

/* 页面顶部样式 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e9ecef;
}

.page-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #2c3e50;
  line-height: 1.3;
  letter-spacing: 0.5px;
}

.page-actions {
  display: flex;
  gap: 12px;
}

/* 左右分栏布局 */
.document-detail-layout {
  display: flex;
  gap: 24px;
  margin-top: 24px;
  min-height: 600px;
  height: calc(100vh - 200px);
}

/* 左侧面板 */
.left-panel {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* 右侧面板 */
.right-panel {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* 单栏布局 */
.single-panel-layout {
  margin-top: 24px;
  min-height: 600px;
  height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

/* 结果面板 */
.result-panel {
  width: 100%;
  height: 100%;
  min-height: 600px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
}

/* 导航按钮样式 */
.navigation-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 24px 0;
  gap: 24px;
}

.nav-btn {
  padding: 8px 20px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #ffffff;
  color: #606266;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.nav-btn:hover:not(:disabled) {
  color: #409eff;
  border-color: #c6e2ff;
  background-color: #ecf5ff;
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.prev-btn {
  order: 1;
}

.next-btn {
  order: 3;
}

.stage-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  order: 2;
}

.stage-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #dcdfe6;
  cursor: pointer;
  transition: all 0.3s ease;
}

.stage-dot:hover {
  transform: scale(1.1);
}

.stage-dot.active {
  background-color: #409eff;
  box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.1);
}

/* 空状态 */
.empty-state {
  margin-top: 24px;
  min-height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-content {
  text-align: center;
  padding: 48px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-content h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.empty-content p {
  margin: 0;
  font-size: 14px;
  color: #6c757d;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .project-detail-page {
    padding: 16px;
  }
  
  .page-header {
    margin-bottom: 20px;
    padding-bottom: 12px;
  }
  
  .page-header h2 {
    font-size: 18px;
  }
  
  .document-detail-layout {
    flex-direction: column;
    gap: 20px;
    margin-top: 20px;
    min-height: 500px;
    height: auto;
  }
  
  .right-panel {
    width: 100%;
    margin-top: 0;
  }
  
  .single-panel-layout {
    margin-top: 20px;
    min-height: 500px;
    height: auto;
  }
  
  .empty-state {
    margin-top: 20px;
    min-height: 500px;
  }
  
  .empty-content {
    padding: 32px;
  }
  
  .empty-icon {
    font-size: 48px;
  }
}

@media (max-width: 480px) {
  .project-detail-page {
    padding: 12px;
  }
  
  .page-header {
    margin-bottom: 16px;
    padding-bottom: 10px;
  }
  
  .page-header h2 {
    font-size: 16px;
  }
  
  .document-detail-layout {
    gap: 16px;
    margin-top: 16px;
    min-height: 400px;
  }
  
  .single-panel-layout {
    margin-top: 16px;
    min-height: 400px;
  }
  
  .empty-state {
    margin-top: 16px;
    min-height: 400px;
  }
  
  .empty-content {
    padding: 24px;
  }
  
  .empty-icon {
    font-size: 32px;
  }
  
  .empty-content h3 {
    font-size: 16px;
  }
  
  .empty-content p {
    font-size: 13px;
  }
}
</style>