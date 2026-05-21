<template>
  <div class="test-scenario-synthesis-result">
    <div class="result-header">
      <h3>测试场景合成结果</h3>
      <span class="result-type">{{ isNewResult ? '（新文档）' : '（旧文档）' }}</span>
    </div>
    <div class="result-content" v-loading="localLoading">
      <div v-if="localError" class="error-message">
        <el-alert type="error" :title="localError" show-icon />
      </div>
      <div v-else-if="!testScenariosData" class="empty-message">
        <el-empty description="暂无数据" />
      </div>
      <div v-else>
        <!-- 场景块列表 -->
        <div class="scenarios-section">
          <h4 class="section-title">场景块列表</h4>
          <div class="scenarios-list">
            <div 
              v-for="(block, index) in testScenariosData.scenarios" 
              :key="block.id"
              class="scenario-item"
              @click="openScenarioEdit(block, index)"
            >
                  <div class="scenario-header">
                    <span class="scenario-id">{{ block.id }}</span>
                    <span class="scenario-rule">{{ block.rule }}</span>
                  </div>
                  <div class="blocks-list" v-if="block.blocks">
                    <template v-for="(ruleBlock, index) in block.blocks" :key="index">
                      <div class="block-item" v-if="ruleBlock && (ruleBlock.if?.length > 0 || ruleBlock.then?.length > 0)">
                        <div class="block-header">
                          <span class="block-name">{{ ruleBlock.name || `规则 ${index + 1}` }}</span>
                        </div>
                        <div class="block-body">
                          <!-- IF 部分 -->
                          <div class="condition-section">
                            <div class="condition-title">IF</div>
                            <div class="conditions-container">
                              <div 
                                v-for="(condition, condIndex) in ruleBlock.if" 
                                :key="`if-${condIndex}`"
                                class="condition-item"
                              >
                                <span class="condition-field">{{ condition.field }}</span>
                                <span class="condition-operator">is</span>
                                <span class="condition-value">{{ condition.value }}</span>
                              </div>
                              <div v-if="!ruleBlock.if || ruleBlock.if.length === 0" class="empty-condition">
                                无条件
                              </div>
                            </div>
                          </div>
                          
                          <!-- THEN 部分 -->
                          <div class="condition-section">
                            <div class="condition-title">THEN</div>
                            <div class="conditions-container">
                              <div 
                                v-for="(condition, condIndex) in ruleBlock.then" 
                                :key="`then-${condIndex}`"
                                class="condition-item"
                              >
                                <span class="condition-field">{{ condition.field }}</span>
                                <span class="condition-operator">is</span>
                                <span class="condition-value">{{ condition.value }}</span>
                              </div>
                              <div v-if="!ruleBlock.then || ruleBlock.then.length === 0" class="empty-condition">
                                无结果
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </template>
                  </div>
                </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 编辑组件 -->
    <TestScenarioSynthesisEdit 
      ref="editComponentRef"
      @update:block="handleBlockUpdate"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useReuseStore } from '@/store/reuseStore'
import { updateTestScenarioSynthesisApi, updateNewTestScenarioSynthesisApi } from '@/api/reuseEdit'
import { resolveReuseResultErrorMessage } from '@/types/reuseResultError'
import TestScenarioSynthesisEdit from '@/layouts/projectDetail/reuse/edit/TestScenarioSynthesisEdit.vue'

// 接收isNewResult作为prop
const props = defineProps<{
  isNewResult?: boolean
}>()

const route = useRoute()
const projectId = computed(() => route.params.id as string)
const reuseStore = useReuseStore()
const localLoading = ref(false)
const localError = ref('')

// 编辑组件引用
const editComponentRef = ref<any>(null)

// 计算属性：测试场景数据
const testScenariosData = computed(() => {
  return isNewResult.value ? reuseStore.getNewTestScenarios : reuseStore.getTestScenarios
})

// 计算属性：是否为新文档结果
const isNewResult = computed(() => {
  return props.isNewResult || false
})

// 打开场景编辑对话框
const openScenarioEdit = (block: any, index: number) => {
  if (editComponentRef.value) {
    editComponentRef.value.openEdit(block, index)
  }
}

// 处理块更新
const handleBlockUpdate = async (updatedBlock: any, index: number) => {
  const sourceData = isNewResult.value
    ? reuseStore.getNewTestScenarios
    : reuseStore.getTestScenarios

  if (!sourceData?.scenarios) {
    ElMessage.error('当前无可保存的场景数据')
    return
  }

  const scenarios = [...sourceData.scenarios]
  scenarios[index] = updatedBlock

  try {
    const hasStoreUpdateActions =
      typeof (reuseStore as any).updateTestScenarios === 'function' &&
      typeof (reuseStore as any).updateNewTestScenarios === 'function'

    if (hasStoreUpdateActions) {
      if (isNewResult.value) {
        await reuseStore.updateNewTestScenarios(projectId.value, { scenarios })
      } else {
        await reuseStore.updateTestScenarios(projectId.value, { scenarios })
      }
    } else {
      console.warn('reuseStore update actions are unavailable, fallback to direct API save. Please refresh page to load latest store actions.')
      if (isNewResult.value) {
        await updateNewTestScenarioSynthesisApi(projectId.value, { scenarios })
        await reuseStore.fetchNewTestScenarios(projectId.value)
      } else {
        await updateTestScenarioSynthesisApi(projectId.value, { scenarios })
        await reuseStore.fetchTestScenarios(projectId.value)
      }
    }
    ElMessage.success('测试场景合成结果已保存')
  } catch (error) {
    console.error('保存测试场景合成结果失败:', error)
    ElMessage.error(reuseStore.error || '保存失败')
  }
}

// 加载数据
const loadData = async () => {
  if (projectId.value) {
    try {
      localLoading.value = true
      localError.value = ''
      if (isNewResult.value) {
        await reuseStore.fetchNewTestScenarios(projectId.value)
      } else {
        await reuseStore.fetchTestScenarios(projectId.value)
      }
    } catch (error) {
      console.error('获取测试场景合成结果失败:', error)
      localError.value = resolveReuseResultErrorMessage(
        error,
        isNewResult.value ? '测试场景合成结果（新文档）' : '测试场景合成结果（旧文档）',
        '获取测试场景合成结果失败'
      )
    } finally {
      localLoading.value = false
    }
  }
}

// 监听isNewResult变化，重新加载数据
watch(() => props.isNewResult, () => {
  loadData()
})

// 组件挂载时获取数据
onMounted(async () => {
  await loadData()
})
</script>

<style scoped>
.test-scenario-synthesis-result {
  min-height: 200px;
  display: flex;
  flex-direction: column;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
  background-color: #ffffff;
}

.result-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  background-color: #f5f7fa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-type {
  font-size: 14px;
  font-weight: 400;
  color: #606266;
  background-color: #ecf5ff;
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid #d9ecff;
}

.result-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #ffffff;
  max-height: calc(100vh - 200px);
}

/* 自定义滚动条样式 */
.result-content::-webkit-scrollbar {
  width: 8px;
}

.result-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.result-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.result-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 场景部分样式 */
.scenarios-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #409eff;
}

/* 场景列表样式 */
.scenarios-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.scenario-item {
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background-color: #fafafa;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.3s ease;
}

.scenario-item:hover {
  background-color: #f0f9ff;
  border-color: #91d5ff;
  box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.scenario-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.scenario-id {
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
  background-color: rgba(64, 158, 255, 0.1);
  padding: 4px 10px;
  border-radius: 4px;
  margin-right: 12px;
}

.scenario-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  line-height: 1.5;
}

/* 需求列表样式 */
.scenario-requirements {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.requirement-item {
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background-color: #fafafa;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.3s ease;
}

.requirement-item:hover {
  background-color: #f6ffed;
  border-color: #b7eb8f;
  box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.requirement-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.requirement-id {
  font-size: 14px;
  font-weight: 600;
  color: #67c23a;
  background-color: rgba(103, 194, 58, 0.1);
  padding: 4px 10px;
  border-radius: 4px;
  margin-right: 12px;
}

.requirement-rule {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  line-height: 1.5;
}

/* 区块列表样式 */
.blocks-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.block-item {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background-color: #ffffff;
}

.block-header {
  margin-bottom: 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid #e4e7ed;
}

.block-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

/* 条件部分样式 */
.condition-section {
  margin-bottom: 12px;
}

.condition-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid #e4e7ed;
}

.conditions-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 条件项样式 */
.condition-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.condition-field {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  background-color: #e6f7ff;
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid #91d5ff;
}

.condition-operator {
  font-size: 13px;
  font-weight: 500;
  color: #909399;
  font-style: italic;
}

.condition-value {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  background-color: #f6ffed;
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid #b7eb8f;
  flex: 1;
}

/* 空条件样式 */
.empty-condition {
  font-size: 13px;
  color: #909399;
  font-style: italic;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border: 1px dashed #ebeef5;
  border-radius: 4px;
  text-align: center;
}

/* 错误和空数据样式 */
.error-message,
.empty-message {
  padding: 20px;
  text-align: center;
}

/* 自定义滚动条样式 */
.result-content::-webkit-scrollbar {
  width: 6px;
}

.result-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.result-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.result-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .result-content {
    padding: 12px;
  }
  
  .scenario-item,
  .requirement-item {
    padding: 12px;
  }
  
  .scenario-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .requirement-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .condition-item {
    padding: 6px 10px;
  }
  
  .condition-field,
  .condition-value {
    font-size: 12px;
  }
}
</style>
