<template>
  <div class="delete-rules-edit">
    <!-- 删除的规则编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑删除的规则"
      width="80%"
      destroy-on-close
    >
      <div class="edit-container">
        <!-- 规则列表编辑区域 -->
        <div class="rules-section">
          <div class="section-header">
            <h4>删除规则列表</h4>
            <span class="item-count">{{ editingRules.length }} 项</span>
          </div>
          
          <div class="rules-list">
            <div
              v-for="(rule, index) in editingRules"
              :key="rule.id || index"
              class="rule-item"
            >
              <el-form :model="rule" label-width="60px">
                <el-form-item label="规则ID">
                  <el-input v-model="rule.id" placeholder="规则ID" disabled />
                </el-form-item>
                
                <el-form-item label="规则内容">
                  <el-input
                    v-model="rule.text"
                    type="textarea"
                    :rows="4"
                    placeholder="请输入规则内容"
                  />
                </el-form-item>
                
                <div class="rule-actions">
                  <el-button
                    type="danger"
                    size="small"
                    @click="removeRule(index)"
                  >
                    删除规则
                  </el-button>
                </div>
              </el-form>
            </div>
            
            <div v-if="editingRules.length === 0" class="empty-state">
              <el-empty description="暂无删除规则" />
            </div>
          </div>
        </div>
        
        <!-- 添加规则区域 -->
        <div class="add-section">
          <div class="section-header">
            <h4>添加规则</h4>
          </div>
          
          <div class="add-actions">
            <el-button
              type="primary"
              size="small"
              @click="openRuleSelectionDialog"
              :disabled="availableRules.length === 0"
            >
              <el-icon><Plus /></el-icon>
              从所有规则中选择添加
            </el-button>
            
            <el-button
              type="success"
              size="small"
              @click="addNewRule"
            >
              <el-icon><Plus /></el-icon>
              手动添加新规则
            </el-button>
          </div>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveChanges">保存</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 规则选择对话框 -->
    <el-dialog
      v-model="ruleSelectionDialogVisible"
      title="选择要删除的规则"
      width="80%"
      destroy-on-close
    >
      <div class="selection-container">
        <div class="search-box">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索规则内容..."
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
        
        <el-table
          :data="filteredRules"
          style="width: 100%"
          @selection-change="handleSelectionChange"
          max-height="400"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="id" label="规则ID" width="80" />
          <el-table-column prop="text" label="规则内容">
            <template #default="scope">
              <div class="rule-text-preview">{{ scope.row.text }}</div>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="selection-info">
          已选择 {{ selectedRules.length }} 项
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="ruleSelectionDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            @click="confirmRuleSelection"
            :disabled="selectedRules.length === 0"
          >
            确认选择 ({{ selectedRules.length }})
          </el-button>
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
import { Plus, Search } from '@element-plus/icons-vue';

// 获取路由参数
const route = useRoute();
const projectId = route.params.id as string;

// 使用store
const reuseStore = useReuseStore();

// 对话框状态
const dialogVisible = ref(false);
const ruleSelectionDialogVisible = ref(false);

// 搜索关键字
const searchKeyword = ref('');

// 选择的规则
const selectedRules = ref<any[]>([]);

// 编辑中的数据
const editingRules = ref<any[]>([]);

// 所有规则列表（从store获取）
const allRules = computed(() => {
  const independentRequirements = reuseStore.getIndependentRequirements;
  return independentRequirements?.rules || [];
});

// 可用规则列表（不在编辑列表中的规则）
const availableRules = computed(() => {
  const usedRuleIds = new Set(editingRules.value.map((rule: any) => rule.id));
  return allRules.value.filter(rule => !usedRuleIds.has(rule.id));
});

// 过滤后的规则列表
const filteredRules = computed(() => {
  if (!searchKeyword.value) {
    return availableRules.value;
  }
  const keyword = searchKeyword.value.toLowerCase();
  return availableRules.value.filter(rule => 
    rule.text.toLowerCase().includes(keyword) || 
    rule.id.toLowerCase().includes(keyword)
  );
});

// 处理选择变更
const handleSelectionChange = (selection: any[]) => {
  selectedRules.value = selection;
};

// 组件挂载时获取数据
onMounted(async () => {
  if (projectId) {
    try {
      // 先获取独立需求数据（包含所有规则）
      if (!reuseStore.getIndependentRequirements) {
        await reuseStore.fetchNewIndependentRequirements(projectId);
      }
    } catch (error) {
      console.error('获取数据失败:', error);
    }
  }
});

// 打开编辑对话框
const openEdit = async () => {
  // 确保独立需求数据已加载（删除规则使用新结果接口）
  if (projectId && !reuseStore.getIndependentRequirements) {
    try {
      await reuseStore.fetchNewIndependentRequirements(projectId);
    } catch (error) {
      console.error('获取独立需求数据失败:', error);
    }
  }
  
  // 从store获取当前数据
  const regulatoryChanges = reuseStore.getRegulatoryChanges;
  if (regulatoryChanges && regulatoryChanges.delete_rules) {
    // 深拷贝数据
    editingRules.value = JSON.parse(JSON.stringify(regulatoryChanges.delete_rules));
  } else {
    // 确保editingRules始终是数组
    editingRules.value = [];
  }
  
  dialogVisible.value = true;
};

// 打开规则选择对话框
const openRuleSelectionDialog = () => {
  selectedRules.value = [];
  searchKeyword.value = '';
  ruleSelectionDialogVisible.value = true;
};

// 确认规则选择
const confirmRuleSelection = () => {
  if (selectedRules.value.length > 0) {
    selectedRules.value.forEach(rule => {
      editingRules.value.push({ ...rule });
    });
  }
  ruleSelectionDialogVisible.value = false;
};

// 添加新规则
const addNewRule = () => {
  editingRules.value.push({
    id: `new_${Date.now()}`,
    text: ''
  });
};

// 移除规则
const removeRule = (index: number) => {
  editingRules.value.splice(index, 1);
};

// 保存变更
const saveChanges = async () => {
  try {
    const regulatoryChanges = reuseStore.getRegulatoryChanges || { delete_rules: [], add_rules: [] };
    await reuseStore.updateRegulatoryChanges(projectId, {
      delete_rules: editingRules.value,
      add_rules: regulatoryChanges.add_rules || []
    });
    ElMessage.success('删除规则已保存');
    dialogVisible.value = false;
  } catch (error) {
    console.error('保存删除规则失败:', error);
    ElMessage.error(reuseStore.error || '保存失败');
  }
};

// 导出方法
defineExpose({
  openEdit
});
</script>

<style scoped>
.delete-rules-edit {
  width: 100%;
}

.edit-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
}

/* 规则列表区域 */
.rules-section {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  background-color: #fafafa;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.section-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.item-count {
  font-size: 12px;
  color: #909399;
  background-color: #ecf5ff;
  padding: 2px 8px;
  border-radius: 10px;
  border: 1px solid #d9ecff;
}

.rules-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.rule-item {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 16px;
  background-color: #ffffff;
}

.rule-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

/* 添加规则区域 */
.add-section {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  background-color: #fafafa;
}

.add-actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

/* 规则选择对话框样式 */
.selection-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-box {
  width: 100%;
}

.rule-text-preview {
  font-size: 13px;
  line-height: 1.4;
  color: #606266;
  max-width: 100%;
  word-break: break-word;
}

.selection-info {
  font-size: 12px;
  color: #909399;
  text-align: right;
  padding: 8px 0;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 修复Element-UI表单样式 */
:deep(.el-form-item) {
  margin-bottom: 16px;
  width: 100%;
}

:deep(.el-form-item__label) {
  text-align: right;
  padding-right: 12px;
}

:deep(.el-form-item__content) {
  width: calc(100% - 60px);
}

:deep(.el-input__inner),
:deep(.el-textarea__inner) {
  width: 100%;
}
</style>
