<template>
  <div class="independent-requirement-result">
    <div class="result-header">
      <h3>独立需求生成结果</h3>
      <span class="result-type">{{ isNewResult ? '（新文档）' : '（旧文档）' }}</span>
    </div>
    <div class="result-content" v-loading="localLoading">
      <div v-if="localError" class="error-message">
        <el-alert type="error" :title="localError" show-icon />
      </div>
      <div v-else-if="!independentRequirementsData" class="empty-message">
        <el-empty description="暂无数据" />
      </div>
      <div v-else>
        <!-- 规则部分 -->
        <div class="rules-section">
          <h4 class="section-title">规则</h4>
          <div class="rules-list">
            <div 
              v-for="rule in independentRequirementsData.rules" 
              :key="rule.id" 
              class="rule-item"
              @click="openRuleEdit(rule)"
            >
              <span class="rule-id">{{ rule.id }}</span>
              <span class="rule-text">{{ rule.text }}</span>
            </div>
          </div>
        </div>
        
        <!-- 需求部分 -->
        <div class="requirements-section">
          <h4 class="section-title">需求</h4>
          <div class="requirements-list">
            <div 
              v-for="requirement in independentRequirementsData.requirements" 
              :key="requirement.id" 
              class="requirement-item"
              @click="openRequirementEdit(requirement)"
            >
              <div class="requirement-header">
                <span class="requirement-id">{{ requirement.id }}</span>
                <span class="requirement-rule">{{ requirement.ruleText }}</span>
              </div>
              <div class="blocks-list">
                <div 
                  v-for="block in requirement.blocks" 
                  :key="block.name" 
                  class="block-item"
                >
                  <div class="block-header">
                    <span class="block-name">{{ block.name }}</span>
                  </div>
                  <div class="block-body">
                    <!-- IF 部分 -->
                    <div class="condition-section">
                      <div class="condition-title">IF</div>
                      <div class="conditions-container">
                        <div 
                          v-for="(condition, condIndex) in block.if" 
                          :key="`if-${condIndex}`"
                          class="condition-item"
                        >
                          <span class="condition-field">{{ condition.field }}</span>
                          <span class="condition-operator">is</span>
                          <span class="condition-value">{{ condition.value }}</span>
                        </div>
                        <div v-if="block.if.length === 0" class="empty-condition">
                          无条件
                        </div>
                      </div>
                    </div>
                    
                    <!-- THEN 部分 -->
                    <div class="condition-section">
                      <div class="condition-title">THEN</div>
                      <div class="conditions-container">
                        <div 
                          v-for="(condition, condIndex) in block.then" 
                          :key="`then-${condIndex}`"
                          class="condition-item"
                        >
                          <span class="condition-field">{{ condition.field }}</span>
                          <span class="condition-operator">is</span>
                          <span class="condition-value">{{ condition.value }}</span>
                        </div>
                        <div v-if="block.then.length === 0" class="empty-condition">
                          无结果
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 编辑组件 -->
    <IndependentRequirementEdit ref="editComponentRef" :project-id="projectId" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useReuseStore } from '@/store/reuseStore';
import { resolveReuseResultErrorMessage } from '@/types/reuseResultError';
import IndependentRequirementEdit from '@/layouts/projectDetail/reuse/edit/IndependentRequirementEdit.vue';

// 接收isNewResult作为prop
const props = defineProps<{
  isNewResult?: boolean
}>();

// 获取路由参数
const route = useRoute();
const projectId = route.params.id as string;

// 使用store
const reuseStore = useReuseStore();
const localLoading = ref(false);
const localError = ref('');

// 编辑组件引用
const editComponentRef = ref<any>(null);

// 计算属性：获取独立需求数据
const independentRequirementsData = computed(() => {
  return reuseStore.getIndependentRequirements || null;
});

// 计算属性：是否为新文档结果
const isNewResult = computed(() => {
  return props.isNewResult || false;
});

// 打开规则编辑对话框
const openRuleEdit = (rule: any) => {
  if (editComponentRef.value) {
    editComponentRef.value.openRuleEdit(rule);
  }
};

// 打开需求编辑对话框
const openRequirementEdit = (requirement: any) => {
  if (editComponentRef.value) {
    editComponentRef.value.openRequirementEdit(requirement);
  }
};

// 加载数据
const loadData = async () => {
  if (projectId) {
    try {
      localLoading.value = true;
      localError.value = '';
      if (isNewResult.value) {
        await reuseStore.fetchNewIndependentRequirements(projectId);
      } else {
        await reuseStore.fetchIndependentRequirements(projectId);
      }
    } catch (error) {
      console.error('获取独立需求生成结果失败:', error);
      localError.value = resolveReuseResultErrorMessage(
        error,
        isNewResult.value ? '独立需求生成结果（新文档）' : '独立需求生成结果（旧文档）',
        '获取独立需求生成结果失败'
      );
    } finally {
      localLoading.value = false;
    }
  }
};

// 监听isNewResult变化，重新加载数据
watch(() => props.isNewResult, () => {
  loadData();
});

// 组件挂载时获取数据
onMounted(async () => {
  await loadData();
});
</script>

<style scoped>
.independent-requirement-result {
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

/* 规则部分样式 */
.rules-section {
  margin-bottom: 24px;
}

.requirements-section {
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

/* 规则列表样式 */
.rules-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rule-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background-color: #fafafa;
  cursor: pointer;
  transition: all 0.3s ease;
}

.rule-item:hover {
  background-color: #f0f9ff;
  border-color: #91d5ff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.rule-id {
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
  background-color: rgba(64, 158, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  min-width: 30px;
  text-align: center;
}

.rule-text {
  flex: 1;
  font-size: 14px;
  line-height: 1.5;
  color: #303133;
}

/* 需求列表样式 */
.requirements-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
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
  
  .rule-item,
  .requirement-item {
    padding: 12px;
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
