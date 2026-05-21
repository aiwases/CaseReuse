<template>
  <div class="delete-scenarios-edit">
    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑删除的场景"
      width="800px"
      destroy-on-close
    >
      <div class="edit-container">
        <div class="edit-section">
          <div class="section-header">
            <h4>删除的场景列表</h4>
            <span class="item-count">共 {{ editingScenarios.length }} 个场景</span>
          </div>
          <div class="section-content">
            <div v-if="editingScenarios.length > 0" class="scenario-list">
              <div 
                v-for="(scenarioId, index) in editingScenarios" 
                :key="index"
                class="scenario-item"
              >
                <div class="scenario-info">
                  <span class="scenario-id">场景 {{ scenarioId }}</span>
                </div>
                <div class="scenario-actions">
                  <el-button
                    size="small"
                    type="danger"
                    @click="removeScenario(index)"
                  >
                    移除
                  </el-button>
                </div>
              </div>
            </div>
            <div v-else class="empty-message">
              <el-empty description="暂无删除的场景" />
            </div>
          </div>
        </div>
        
        <!-- 场景选择对话框 -->
        <el-dialog
          v-model="scenarioSelectionDialogVisible"
          title="选择要添加的场景"
          width="700px"
          destroy-on-close
        >
          <div class="selection-container">
            <div class="search-section">
              <el-input
                v-model="scenarioSearchQuery"
                placeholder="搜索场景ID"
                clearable
                prefix-icon="Search"
              />
            </div>
            
            <el-table 
              :data="filteredScenarios" 
              style="width: 100%"
              max-height="360"
              @selection-change="selectedScenarios = $event"
            >
              <el-table-column type="selection" width="55" />
              <el-table-column prop="id" label="场景ID" width="120" />
              <el-table-column prop="text" label="原始文本">
                <template #default="scope">
                  <div class="scenario-text">
                    {{ scope.row.text }}
                  </div>
                </template>
              </el-table-column>
            </el-table>
            
            <div class="selection-info">
              已选择 {{ selectedScenarios.length }} 个场景
            </div>
          </div>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="scenarioSelectionDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="confirmScenarioSelection" :disabled="selectedScenarios.length === 0">
                确认添加
              </el-button>
            </span>
          </template>
        </el-dialog>
      </div>
      
      <!-- 添加按钮固定在对话框底部 -->
      <div class="add-section">
        <el-button type="primary" size="small" @click="openScenarioSelectionDialog">
          <el-icon><Plus /></el-icon> 添加场景
        </el-button>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveChanges">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useReuseStore } from '@/store/reuseStore';
import { ElMessage } from 'element-plus';
import { updateCascadingImpactScopeAnalysisApi } from '@/api/reuseEdit';
import { Plus } from '@element-plus/icons-vue';

// 获取路由参数
const route = useRoute();
const projectId = route.params.id as string;

// 使用store
const reuseStore = useReuseStore();

// 对话框状态
const dialogVisible = ref(false);

// 场景选择对话框状态
const scenarioSelectionDialogVisible = ref(false);
const selectedScenarios = ref<any[]>([]);
const scenarioSearchQuery = ref('');

// 编辑中的数据（字符串数组）
const editingScenarios = ref<string[]>([]);

// 可用场景列表（从测试场景合成结果中获取）
const availableScenarios = computed(() => {
  const testScenarios = reuseStore.getTestScenarios;
  if (!testScenarios || !testScenarios.scenarios) {
    return [];
  }

  return testScenarios.scenarios
    .map((scenario: any) => ({
      id: scenario.id || scenario.rule || '',
      text: scenario.text || ''
    }))
    .filter((scenario: any) => !!scenario.id);
});

// 过滤后的场景列表
const filteredScenarios = computed(() => {
  if (!scenarioSearchQuery.value) {
    return availableScenarios.value;
  }
  
  const query = scenarioSearchQuery.value.toLowerCase();
  return availableScenarios.value.filter(scenario => 
    String(scenario.id).toLowerCase().includes(query)
  );
});

const ensureScenarioSourceLoaded = async () => {
  if (reuseStore.getTestScenarios?.scenarios?.length) {
    return;
  }

  try {
    await reuseStore.fetchTestScenarios(projectId);
  } catch (error) {
    console.error('获取可选场景失败:', error);
    ElMessage.error('获取可选场景失败，请稍后重试');
  }
};

onMounted(async () => {
  await ensureScenarioSourceLoaded();
});

// 打开场景选择对话框
const openScenarioSelectionDialog = async () => {
  await ensureScenarioSourceLoaded();
  selectedScenarios.value = [];
  scenarioSearchQuery.value = '';
  scenarioSelectionDialogVisible.value = true;
};

// 确认场景选择
const confirmScenarioSelection = () => {
  if (selectedScenarios.value.length > 0) {
    // 将选中的场景ID添加到编辑列表中
    selectedScenarios.value.forEach(scenario => {
      if (!editingScenarios.value.includes(scenario.id)) {
        editingScenarios.value.push(scenario.id);
      }
    });
    
    // 关闭场景选择对话框
    scenarioSelectionDialogVisible.value = false;
  }
};

// 打开编辑对话框
const openEdit = async () => {
  await ensureScenarioSourceLoaded();

  // 从store获取当前数据
  const cascadingImpacts = reuseStore.getCascadingImpacts;
  if (cascadingImpacts && cascadingImpacts.to_delete_scenarios) {
    // 深拷贝数据
    editingScenarios.value = [...cascadingImpacts.to_delete_scenarios];
  } else {
    // 确保editingScenarios始终是数组
    editingScenarios.value = [];
  }
  
  dialogVisible.value = true;
};

// 移除场景
const removeScenario = (index: number) => {
  editingScenarios.value.splice(index, 1);
};

// 保存更改
const saveChanges = async () => {
  try {
    const cascadingImpacts = reuseStore.getCascadingImpacts || { to_delete_scenarios: [], to_delete_testcases: [] };
    const payload = {
      to_delete_scenarios: editingScenarios.value,
      to_delete_testcases: cascadingImpacts.to_delete_testcases || []
    };

    if (typeof (reuseStore as any).updateCascadingImpacts === 'function') {
      await reuseStore.updateCascadingImpacts(projectId, payload);
    } else {
      console.warn('reuseStore.updateCascadingImpacts is unavailable, fallback to direct API save. Please refresh page to load latest store actions.');
      await updateCascadingImpactScopeAnalysisApi(projectId, payload);
      await reuseStore.fetchCascadingImpacts(projectId);
    }
    ElMessage.success('删除场景已保存');
    dialogVisible.value = false;
  } catch (error) {
    console.error('保存删除场景失败:', error);
    ElMessage.error(reuseStore.error || '保存失败');
  }
};

// 暴露方法
defineExpose({
  openEdit
});
</script>

<style scoped>
.edit-container {
  width: 100%;
  max-height: 500px;
  overflow-y: auto;
  padding-right: 8px;
}

.edit-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.section-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.item-count {
  font-size: 13px;
  color: #909399;
  background-color: #f5f7fa;
  padding: 4px 12px;
  border-radius: 12px;
}

.section-content {
  min-height: 200px;
}

.scenario-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.scenario-item {
  background-color: #ffffff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.scenario-info {
  flex: 1;
}

.scenario-id {
  font-size: 14px;
  font-weight: 600;
  color: #f56c6c;
  background-color: rgba(245, 108, 108, 0.1);
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid #ffccc7;
}

.scenario-actions {
  display: flex;
  gap: 8px;
}

.empty-message {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  border: 1px dashed #ebeef5;
  border-radius: 8px;
}

.add-section {
  display: flex;
  justify-content: flex-start;
  padding: 16px;
  border-top: 1px solid #e4e7ed;
  background-color: #fafafa;
  margin-top: 16px;
}

.selection-container {
  width: 100%;
}

.search-section {
  margin-bottom: 16px;
}

.scenario-text {
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
  max-height: 40px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.selection-info {
  margin-top: 12px;
  font-size: 13px;
  color: #909399;
  text-align: right;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 自定义滚动条样式 */
.edit-container::-webkit-scrollbar {
  width: 6px;
}

.edit-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.edit-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.edit-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}</style>
