<template>
  <div class="delete-test-cases-edit">
    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑删除的测试用例"
      width="800px"
      destroy-on-close
    >
      <div class="edit-container">
        <div class="edit-section">
          <div class="section-header">
            <h4>删除的测试用例列表</h4>
            <span class="item-count">共 {{ editingTestCases.length }} 个测试用例</span>
          </div>
          <div class="section-content">
            <div v-if="editingTestCases.length > 0" class="test-case-list">
              <div 
                v-for="(testCaseId, index) in editingTestCases" 
                :key="index"
                class="test-case-item"
              >
                <div class="test-case-info">
                  <span class="test-case-id">测试用例 {{ testCaseId }}</span>
                </div>
                <div class="test-case-actions">
                  <el-button
                    size="small"
                    type="danger"
                    @click="removeTestCase(index)"
                  >
                    移除
                  </el-button>
                </div>
              </div>
            </div>
            <div v-else class="empty-message">
              <el-empty description="暂无删除的测试用例" />
            </div>
          </div>
        </div>
        
        <!-- 测试用例选择对话框 -->
        <el-dialog
          v-model="testCaseSelectionDialogVisible"
          title="选择要添加的测试用例"
          width="800px"
          destroy-on-close
        >
          <div class="selection-container">
            <div class="search-section">
              <el-input
                v-model="testCaseSearchQuery"
                placeholder="搜索测试用例ID"
                clearable
                prefix-icon="Search"
              />
            </div>
            
            <el-table 
              class="selection-table"
              :data="filteredTestCases" 
              :max-height="360"
              style="width: 100%"
              @selection-change="selectedTestCases = $event"
            >
              <el-table-column type="selection" width="55" />
              <el-table-column prop="testid" label="测试用例ID" width="120" />
              <el-table-column prop="rule" label="规则" width="120" />
              <el-table-column prop="title" label="标题">
                <template #default="scope">
                  <div class="test-case-title">
                    {{ scope.row.title || '无标题' }}
                  </div>
                </template>
              </el-table-column>
            </el-table>
            
            <div class="selection-info">
              已选择 {{ selectedTestCases.length }} 个测试用例
            </div>
          </div>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="testCaseSelectionDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="confirmTestCaseSelection" :disabled="selectedTestCases.length === 0">
                确认添加
              </el-button>
            </span>
          </template>
        </el-dialog>
      </div>
      
      <!-- 添加按钮固定在对话框底部 -->
      <div class="add-section">
        <el-button type="primary" size="small" @click="openTestCaseSelectionDialog">
          <el-icon><Plus /></el-icon> 添加测试用例
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

// 测试用例选择对话框状态
const testCaseSelectionDialogVisible = ref(false);
const selectedTestCases = ref<any[]>([]);
const testCaseSearchQuery = ref('');

// 编辑中的数据（字符串数组）
const editingTestCases = ref<string[]>([]);

// 可用测试用例列表（从测试用例文件中获取）
const availableTestCases = computed(() => {
  const testCasesFile = reuseStore.getTestCasesFile;
  if (!testCasesFile) {
    return [];
  }

  const flattenRecords = (records: any): any[] => {
    if (!Array.isArray(records)) {
      return [];
    }

    return records.flatMap((item: any) => {
      if (Array.isArray(item)) {
        return item.filter((sub: any) => typeof sub === 'object' && sub !== null);
      }
      return typeof item === 'object' && item !== null ? [item] : [];
    });
  };

  if (Array.isArray(testCasesFile)) {
    return flattenRecords(testCasesFile);
  }

  if (typeof testCasesFile === 'object') {
    const candidates = [
      flattenRecords((testCasesFile as any).old_test_cases),
      flattenRecords((testCasesFile as any).test_cases),
      flattenRecords((testCasesFile as any).testcases),
      flattenRecords((testCasesFile as any).old_testcases),
      flattenRecords((testCasesFile as any).data?.old_test_cases),
      flattenRecords((testCasesFile as any).data?.testcases),
      flattenRecords((testCasesFile as any).data?.old_testcases)
    ];

    return candidates.find((items) => items.length > 0) || [];
  }

  return [];
});

// 过滤后的测试用例列表
const filteredTestCases = computed(() => {
  if (!testCaseSearchQuery.value) {
    return availableTestCases.value;
  }
  
  const query = testCaseSearchQuery.value.toLowerCase();
  return availableTestCases.value.filter(testCase => 
    testCase.testid && testCase.testid.toLowerCase().includes(query)
  );
});

const ensureTestCaseSourceLoaded = async () => {
  const current = reuseStore.getTestCasesFile as any;
  const sameProject = String(current?.project_id ?? '') === String(projectId);
  const isOldSource = !current || current?.source_type === 'old_test_case';

  if (current && sameProject && isOldSource) {
    return;
  }

  try {
    const loaded = await reuseStore.fetchTestCasesFile(projectId) as any;
    const records = Array.isArray(loaded?.old_test_cases)
      ? loaded.old_test_cases
      : Array.isArray(loaded?.test_cases)
        ? loaded.test_cases
        : [];

    if (records.length === 0 && loaded?.warning) {
      ElMessage.warning(`旧测试用例为空或不可用: ${loaded.warning}`);
    }
  } catch (error) {
    console.error('获取测试用例文件失败:', error);
    ElMessage.error('获取测试用例文件失败，请稍后重试');
  }
};

onMounted(async () => {
  await ensureTestCaseSourceLoaded();
});

// 打开测试用例选择对话框
const openTestCaseSelectionDialog = async () => {
  await ensureTestCaseSourceLoaded();
  selectedTestCases.value = [];
  testCaseSearchQuery.value = '';
  testCaseSelectionDialogVisible.value = true;
};

// 确认测试用例选择
const confirmTestCaseSelection = () => {
  if (selectedTestCases.value.length > 0) {
    // 将选中的测试用例ID添加到编辑列表中
    selectedTestCases.value.forEach(testCase => {
      if (testCase.testid && !editingTestCases.value.includes(testCase.testid)) {
        editingTestCases.value.push(testCase.testid);
      }
    });
    
    // 关闭测试用例选择对话框
    testCaseSelectionDialogVisible.value = false;
  }
};

// 打开编辑对话框
const openEdit = () => {
  // 从store获取当前数据
  const cascadingImpacts = reuseStore.getCascadingImpacts;
  if (cascadingImpacts && cascadingImpacts.to_delete_testcases) {
    // 深拷贝数据
    editingTestCases.value = [...cascadingImpacts.to_delete_testcases];
  } else {
    // 确保editingTestCases始终是数组
    editingTestCases.value = [];
  }
  
  dialogVisible.value = true;
};

// 移除测试用例
const removeTestCase = (index: number) => {
  editingTestCases.value.splice(index, 1);
};

// 保存更改
const saveChanges = async () => {
  try {
    const cascadingImpacts = reuseStore.getCascadingImpacts || { to_delete_scenarios: [], to_delete_testcases: [] };
    const payload = {
      to_delete_scenarios: cascadingImpacts.to_delete_scenarios || [],
      to_delete_testcases: editingTestCases.value
    };

    if (typeof (reuseStore as any).updateCascadingImpacts === 'function') {
      await reuseStore.updateCascadingImpacts(projectId, payload);
    } else {
      console.warn('reuseStore.updateCascadingImpacts is unavailable, fallback to direct API save. Please refresh page to load latest store actions.');
      await updateCascadingImpactScopeAnalysisApi(projectId, payload);
      await reuseStore.fetchCascadingImpacts(projectId);
    }
    ElMessage.success('删除测试用例已保存');
    dialogVisible.value = false;
  } catch (error) {
    console.error('保存删除测试用例失败:', error);
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

.test-case-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.test-case-item {
  background-color: #ffffff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.test-case-info {
  flex: 1;
}

.test-case-id {
  font-size: 14px;
  font-weight: 600;
  color: #f56c6c;
  background-color: rgba(245, 108, 108, 0.1);
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid #ffccc7;
}

.test-case-actions {
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

.test-case-title {
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

.selection-table :deep(.el-scrollbar__bar.is-vertical) {
  width: 8px;
}

.selection-table :deep(.el-scrollbar__thumb) {
  background-color: #c1c7d0;
  border-radius: 8px;
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
