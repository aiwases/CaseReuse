<template>
  <div class="test-suite-reuse-update-result">
    <div class="component-header">
      <h3>测试套件重用与更新结果</h3>
    </div>
    
    <div v-loading="localLoading" class="component-content">
      <div v-if="error" class="error-message">
        <el-alert type="error" :title="error" show-icon />
      </div>
      <div v-else-if="!testSuiteReuse" class="empty-message">
        <el-empty description="暂无测试套件重用与更新结果" />
      </div>
      <div v-else class="result-container">
        <!-- 更新的测试用例 -->
        <div v-if="testSuiteReuse.testcases && testSuiteReuse.testcases.length > 0">
          <div v-for="(testCaseGroup, groupIndex) in testSuiteReuse.testcases" :key="groupIndex" class="test-case-group">
            <div v-for="(testCase, testCaseIndex) in testCaseGroup" :key="testCase.testid" class="test-case-item" @click="openTestCaseEdit(testCase, groupIndex, testCaseIndex)">
              <div class="test-case-header">
                <span class="test-case-id">测试用例{{ testCase.testid }}</span>
                <span class="test-case-rule">规则: {{ testCase.rule }}</span>
              </div>
              <div class="test-case-details">
                <template v-for="(value, key) in testCase" :key="key">
                  <div 
                    v-if="key !== 'testid' && key !== 'rule'"
                    class="test-case-property"
                  >
                    <span class="property-key">{{ key }}:</span>
                    <span class="property-value">{{ value }}</span>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
        <p v-else class="no-data">无更新的测试用例</p>
      </div>
    </div>
    
    <!-- 编辑组件 -->
    <TestSuiteReuseUpdateBlockEdit 
      v-model:visible="editVisible"
      :test-case="currentTestCase"
      @update:block="handleBlockUpdate"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useReuseStore } from '@/store/reuseStore'
import TestSuiteReuseUpdateBlockEdit from '@/layouts/projectDetail/reuse/edit/TestSuiteReuseUpdateBlockEdit.vue'
import { updateTestSuiteReuseUpdateApi } from '@/api/reuseEdit'
import { ElMessage } from 'element-plus'
import { resolveReuseResultErrorMessage } from '@/types/reuseResultError'

const route = useRoute()
const projectId = computed(() => route.params.id as string)
const reuseStore = useReuseStore()

const localLoading = ref(false)
const error = ref<string | null>(null)

// 计算属性：测试套件重用与更新结果数据
const testSuiteReuse = computed(() => {
  return reuseStore.getTestSuiteReuse
})

// 编辑对话框状态
const editVisible = ref(false)
const currentTestCase = ref<any>(null)
const currentGroupIndex = ref<number>(-1)
const currentTestCaseIndex = ref<number>(-1)

// 打开编辑对话框
const openTestCaseEdit = (testCase: any, groupIndex: number, testCaseIndex: number) => {
  currentTestCase.value = testCase
  currentGroupIndex.value = groupIndex
  currentTestCaseIndex.value = testCaseIndex
  editVisible.value = true
}

// 处理块更新
const handleBlockUpdate = async (updatedTestCase: any) => {
  const testSuiteReuseData = reuseStore.getTestSuiteReuse
  if (testSuiteReuseData && currentGroupIndex.value >= 0 && currentTestCaseIndex.value >= 0) {
    // 更新store中的数据
    const updatedTestCases = [...testSuiteReuseData.testcases]
    updatedTestCases[currentGroupIndex.value][currentTestCaseIndex.value] = updatedTestCase

    const payload = {
      testcases: updatedTestCases
    }

    try {
      if (typeof (reuseStore as any).updateTestSuiteReuse === 'function') {
        await (reuseStore as any).updateTestSuiteReuse(projectId.value, payload)
      } else {
        console.warn('reuseStore.updateTestSuiteReuse is unavailable, fallback to direct API save. Please refresh page to load latest store actions.')
        await updateTestSuiteReuseUpdateApi(projectId.value, payload)
        await reuseStore.fetchTestSuiteReuse(projectId.value)
      }
      ElMessage.success('测试套件重用与更新结果已保存')
    } catch (error) {
      console.error('保存测试套件重用与更新结果失败:', error)
      ElMessage.error(reuseStore.error || '保存失败')
    }
  }
}

// 组件挂载时获取数据
onMounted(() => {
  if (projectId.value) {
    localLoading.value = true
    error.value = null
    reuseStore.fetchTestSuiteReuse(projectId.value).catch((err: any) => {
      console.error('获取测试套件复用与更新结果失败:', err)
      error.value = resolveReuseResultErrorMessage(err, '测试套件复用与更新结果', '获取测试套件复用与更新结果失败')
    }).finally(() => {
      localLoading.value = false
    })
  }
})
</script>

<style scoped>
.test-suite-reuse-update-result {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 防止组件影响页面滚动 */
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
  overflow-y: auto;
  background-color: #ffffff;
}

/* 自定义滚动条样式 */
.component-content::-webkit-scrollbar,
.test-case-group::-webkit-scrollbar {
  width: 6px;
}

.component-content::-webkit-scrollbar-track,
.test-case-group::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.component-content::-webkit-scrollbar-thumb,
.test-case-group::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.component-content::-webkit-scrollbar-thumb:hover,
.test-case-group::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.error-message,
.empty-message {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 结果容器 */
.result-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 测试用例组 */
.test-case-group {
  margin-bottom: 20px;
}

/* 部分标题 */
.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  padding-bottom: 8px;
  border-bottom: 2px solid #409eff;
  display: inline-block;
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
  color: #409eff;
  background-color: rgba(64, 158, 255, 0.1);
  padding: 4px 10px;
  border-radius: 4px;
  border: 1px solid #91d5ff;
  min-width: 100px;
  text-align: center;
}

.test-case-rule {
  font-size: 13px;
  color: #67c23a;
  background-color: rgba(103, 194, 58, 0.1);
  padding: 4px 10px;
  border-radius: 4px;
  border: 1px solid #a0d468;
}

.test-case-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
  margin-top: 8px;
}

.test-case-property {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.property-key {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.property-value {
  font-size: 13px;
  color: #606266;
  background-color: #ffffff;
  padding: 6px;
  border-radius: 3px;
  border: 1px solid #e4e7ed;
}

.no-data {
  text-align: center;
  color: #909399;
  font-size: 14px;
  margin: 0;
  padding: 20px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .test-case-details {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .component-header {
    padding: 14px;
  }
  
  .component-content {
    padding: 12px;
  }
  
  .test-case-item {
    padding: 12px;
  }
}
</style>
