<template>
  <div class="regulatory-change-identification-result">
    <div class="component-header">
      <h3>监管变更识别结果</h3>
    </div>
    
    <div v-loading="loading" class="component-content">
      <div v-if="error" class="error-message">
        <el-alert type="error" :title="error" show-icon />
      </div>
      <div v-else-if="!regulatoryChanges" class="empty-message">
        <el-empty description="暂无监管变更识别结果" />
      </div>
      <div v-else class="change-container">
        <!-- 规则变更 -->
        <h4 class="change-title">规则变更</h4>
        <div class="change-grid">
          <!-- 上左：删除的规则 -->
          <div class="change-card delete-rules" @click="openDeleteRulesEdit">
            <div class="card-header">
              <h5>删除的规则</h5>
            </div>
            <div class="card-content">
              <ul v-if="regulatoryChanges.delete_rules && regulatoryChanges.delete_rules.length > 0">
                <li v-for="rule in regulatoryChanges.delete_rules" :key="rule.id">
                  <div class="rule-id">规则{{ rule.id }}</div>
                  <div class="rule-text">{{ rule.text }}</div>
                </li>
              </ul>
              <p v-else class="no-data">无删除的规则</p>
            </div>
          </div>
          
          <!-- 上右：新增的规则 -->
          <div class="change-card add-rules" @click="openAddRulesEdit">
            <div class="card-header">
              <h5>新增的规则</h5>
            </div>
            <div class="card-content">
              <ul v-if="regulatoryChanges.add_rules && regulatoryChanges.add_rules.length > 0">
                <li v-for="rule in regulatoryChanges.add_rules" :key="rule.id">
                  <div class="rule-id">规则{{ rule.id }}</div>
                  <div class="rule-text">{{ rule.text }}</div>
                </li>
              </ul>
              <p v-else class="no-data">无新增的规则</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 编辑组件 -->
    <DeleteRulesEdit ref="deleteRulesEditRef" />
    <AddRulesEdit ref="addRulesEditRef" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useReuseStore } from '@/store/reuseStore'
import { isMissingResultFileError, resolveReuseResultErrorMessage } from '@/types/reuseResultError'
import DeleteRulesEdit from '@/layouts/projectDetail/reuse/edit/regulatoryChange/DeleteRulesEdit.vue'
import AddRulesEdit from '@/layouts/projectDetail/reuse/edit/regulatoryChange/AddRulesEdit.vue'

const route = useRoute()
const projectId = computed(() => route.params.id as string)
const reuseStore = useReuseStore()

// 编辑组件引用
const deleteRulesEditRef = ref<any>(null)
const addRulesEditRef = ref<any>(null)

// 计算属性：加载状态
const loading = ref(false)

// 计算属性：错误信息
const error = ref<string | null>(null)

// 计算属性：监管变更识别结果数据
const regulatoryChanges = computed(() => {
  return reuseStore.getRegulatoryChanges
})

// 打开删除的规则编辑对话框
const openDeleteRulesEdit = () => {
  if (deleteRulesEditRef.value) {
    deleteRulesEditRef.value.openEdit()
  }
}

// 打开新增的规则编辑对话框
const openAddRulesEdit = () => {
  if (addRulesEditRef.value) {
    addRulesEditRef.value.openEdit()
  }
}

// 组件挂载时获取数据
onMounted(async () => {
  if (projectId.value) {
    loading.value = true
    error.value = null
    try {
      await reuseStore.fetchRegulatoryChanges(projectId.value)
    } catch (err: any) {
      console.error('获取监管变更识别结果失败:', err)
      if (isMissingResultFileError(err)) {
        reuseStore.resetRegulatoryChanges()
        error.value = '监管变更识别结果文件缺失'
      } else {
        error.value = resolveReuseResultErrorMessage(err, '监管变更识别结果', '获取监管变更识别结果失败')
      }
    } finally {
      loading.value = false
    }
  }
})
</script>

<style scoped>
.regulatory-change-identification-result {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.component-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  background-color: #f5f7fa;
}

.component-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.component-content {
  flex: 1;
  padding: 16px;
  overflow: auto;
}

.error-message,
.empty-message {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 变更容器 */
.change-container {
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

/* 变更网格 */
.change-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* 变更卡片 */
.change-card {
  background-color: #ffffff;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
  cursor: pointer;
  transition: all 0.3s ease;
}

.change-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

/* 卡片标题 */
.card-header {
  padding: 12px 14px;
  border-bottom: 1px solid #f0f0f0;
  background-color: #f9f9f9;
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

.card-content ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.card-content li {
  padding: 10px 12px;
  margin-bottom: 8px;
  background-color: #f9f9f9;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
  border-left: 3px solid #d9d9d9;
}

/* 不同类型的边框颜色 */
.delete-rules li {
  border-left-color: #f56c6c;
}

.add-rules li {
  border-left-color: #67c23a;
}

/* 规则ID样式 */
.rule-id {
  font-size: 13px;
  font-weight: 600;
  color: #409eff;
  background-color: rgba(64, 158, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid #91d5ff;
  margin-right: 8px;
  margin-bottom: 8px;
  display: inline-block;
}

.rule-text {
  line-height: 1.4;
  margin-bottom: 8px;
}

/* 无数据样式 */
.no-data {
  text-align: center;
  color: #909399;
  font-size: 14px;
  margin: 0;
  padding: 20px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .change-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .change-card {
    height: 100%;
  }
  
  .section-header {
    padding: 14px;
  }
  
  .section-content {
    padding: 12px;
  }
}
</style>
