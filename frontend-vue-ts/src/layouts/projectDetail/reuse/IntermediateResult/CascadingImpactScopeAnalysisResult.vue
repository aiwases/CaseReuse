<template>
  <div class="cascading-impact-scope-analysis-result">
    <div class="component-header">
      <h3>级联影响范围分析结果</h3>
    </div>
    
    <div v-loading="loading" class="component-content">
      <div v-if="error" class="error-message">
        <el-alert type="error" :title="error" show-icon />
      </div>
      <div v-else-if="!cascadingImpacts" class="empty-message">
        <el-empty description="暂无数据" />
      </div>
      <div v-else class="impact-container">
        <!-- 场景变更 -->
        <h4 class="change-title">场景变更</h4>
        <div class="impact-card delete-scenarios" @click="openDeleteScenariosEdit">
          <div class="card-header">
            <h5>删除的场景</h5>
            <el-button type="primary" size="small">编辑</el-button>
          </div>
          <div class="card-content">
            <div v-if="cascadingImpacts.to_delete_scenarios && cascadingImpacts.to_delete_scenarios.length > 0">
              <div v-for="(scenarioId, index) in cascadingImpacts.to_delete_scenarios" :key="index" class="scenario-item">
                <div class="scenario-header">
                  <span class="scenario-id">场景{{ scenarioId }}</span>
                </div>
              </div>
            </div>
            <p v-else class="no-data">无删除的场景</p>
          </div>
        </div>
        
        <!-- 测试用例变更 -->
        <h4 class="change-title">测试用例变更</h4>
        <div class="impact-card delete-test-cases" @click="openDeleteTestCasesEdit">
          <div class="card-header">
            <h5>删除的测试用例</h5>
            <el-button type="primary" size="small">编辑</el-button>
          </div>
          <div class="card-content">
            <div v-if="cascadingImpacts.to_delete_testcases && cascadingImpacts.to_delete_testcases.length > 0">
              <div v-for="(testCaseId, index) in cascadingImpacts.to_delete_testcases" :key="index" class="test-case-item">
                <div class="test-case-header">
                  <span class="test-case-id">测试用例{{ testCaseId }}</span>
                </div>
              </div>
            </div>
            <p v-else class="no-data">无删除的测试用例</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 编辑组件 -->
    <DeleteScenariosEdit ref="deleteScenariosEditRef" />
    <DeleteTestCasesEdit ref="deleteTestCasesEditRef" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useReuseStore } from '@/store/reuseStore'
import { resolveReuseResultErrorMessage } from '@/types/reuseResultError'
import DeleteScenariosEdit from '@/layouts/projectDetail/reuse/edit/cascadingImpact/DeleteScenariosEdit.vue'
import DeleteTestCasesEdit from '@/layouts/projectDetail/reuse/edit/cascadingImpact/DeleteTestCasesEdit.vue'

const route = useRoute()
const projectId = computed(() => route.params.id as string)
const reuseStore = useReuseStore()

// 编辑组件引用
const deleteScenariosEditRef = ref<any>(null)
const deleteTestCasesEditRef = ref<any>(null)

// 计算属性：加载状态
const loading = ref(false)

// 计算属性：错误信息
const error = ref<string | null>(null)

// 计算属性：级联影响范围分析结果数据
const cascadingImpacts = computed(() => {
  return reuseStore.getCascadingImpacts
})

const shouldTreatAsEmptyResult = (err: any): boolean => {
  const status = err?.response?.status
  const rawMessage = err?.response?.data?.error || err?.response?.data?.msg || err?.response?.data?.message || err?.message || ''
  const message = String(rawMessage).toLowerCase()
  return (
    status === 404 ||
    message.includes('empty') ||
    message.includes('not found') ||
    message.includes('no such file') ||
    message.includes('文件为空') ||
    message.includes('文件不存在')
  )
}

// 打开删除的场景编辑对话框
const openDeleteScenariosEdit = () => {
  if (deleteScenariosEditRef.value) {
    deleteScenariosEditRef.value.openEdit()
  }
}

// 打开删除的测试用例编辑对话框
const openDeleteTestCasesEdit = () => {
  if (deleteTestCasesEditRef.value) {
    deleteTestCasesEditRef.value.openEdit()
  }
}

// 组件挂载时获取数据
onMounted(async () => {
  if (projectId.value) {
    loading.value = true
    error.value = null
    try {
      await reuseStore.fetchCascadingImpacts(projectId.value)
    } catch (err: any) {
      console.error('获取级联影响范围分析结果失败:', err)
      if (shouldTreatAsEmptyResult(err)) {
        reuseStore.resetCascadingImpacts()
        error.value = '级联影响范围分析结果文件缺失'
      } else {
        error.value = resolveReuseResultErrorMessage(err, '级联影响范围分析结果', '获取级联影响范围分析结果失败')
      }
    } finally {
      loading.value = false
    }
  }
})
</script>

<style scoped>
.cascading-impact-scope-analysis-result {
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0; /* allow children to shrink for proper scrolling */
}

.component-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  background-color: #f5f7fa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.component-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.component-content {
  flex: 1;
  padding: 16px;
  background-color: #ffffff;
  min-height: 0; /* allow internal scroll */
  overflow-y: auto; /* overall scrollbar for the component */
}



.error-message,
.empty-message {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 影响容器 */
.impact-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 变更标题 */
.change-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  padding-bottom: 8px;
  border-bottom: 2px solid #409eff;
  display: inline-block;
}

/* 影响网格 */
.impact-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* 影响卡片 */
.impact-card {
  background-color: #ffffff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 220px;
  max-height: 420px;
}

/* 卡片标题 */
.card-header {
  padding: 12px 14px;
  border-bottom: 1px solid #f0f0f0;
  background-color: #f9f9f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h5 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

/* 卡片内容 */
.card-content {
  flex: 1;
  padding: 14px;
  overflow-y: auto;
  overflow-x: hidden;
  max-height: calc(100% - 48px);
}

/* 自定义滚动条样式 */
.card-content::-webkit-scrollbar {
  width: 6px;
}

.card-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.card-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.card-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.no-data {
  text-align: center;
  color: #909399;
  font-size: 14px;
  margin: 0;
  padding: 20px 0;
}

/* 场景样式 */
.scenario-item {
  margin-bottom: 20px;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background-color: #fafafa;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.scenario-item:last-child {
  margin-bottom: 0;
}

.scenario-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 12px;
}

.scenario-id {
  font-size: 14px;
  font-weight: 600;
  color: #f56c6c;
  background-color: rgba(245, 108, 108, 0.1);
  padding: 4px 10px;
  border-radius: 4px;
  border: 1px solid #ffccc7;
  min-width: 100px;
  text-align: center;
}

/* 测试用例样式 */
.test-case-item {
  margin-bottom: 20px;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background-color: #fafafa;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.test-case-item:last-child {
  margin-bottom: 0;
}

.test-case-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 12px;
}

.test-case-id {
  font-size: 14px;
  font-weight: 600;
  color: #f56c6c;
  background-color: rgba(245, 108, 108, 0.1);
  padding: 4px 10px;
  border-radius: 4px;
  border: 1px solid #ffccc7;
  min-width: 100px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .impact-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .impact-card {
    min-height: 120px;
  }
  
  .section-header {
    padding: 14px;
  }
  
  .section-content {
    padding: 12px;
  }
}
</style>
