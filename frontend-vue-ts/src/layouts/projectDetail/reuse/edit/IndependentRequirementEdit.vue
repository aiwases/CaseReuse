<template>
  <div class="independent-requirement-edit">
    <!-- 编辑规则对话框 -->
    <el-dialog
      v-model="ruleDialogVisible"
      :title="ruleDialogTitle"
      width="500px"
      destroy-on-close
    >
      <el-form :model="editingRule" label-width="80px">
        <el-form-item label="规则ID">
          <el-input v-model="editingRule.id" disabled />
        </el-form-item>
        <el-form-item label="规则内容">
          <el-input
            v-model="editingRule.text"
            type="textarea"
            :rows="4"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="ruleDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveRule">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑需求对话框 -->
    <el-dialog
      v-model="requirementDialogVisible"
      :title="requirementDialogTitle"
      width="600px"
      destroy-on-close
    >
      <el-form :model="editingRequirement" label-width="80px">
        <el-form-item label="需求ID">
          <el-input v-model="editingRequirement.id" disabled />
        </el-form-item>
        <el-form-item label="规则文本">
          <el-input
            v-model="editingRequirement.ruleText"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="规则块">
          <div v-for="(block, blockIndex) in editingRequirement.blocks" :key="blockIndex" class="block-edit">
            <el-divider content-position="left">规则块 {{ blockIndex + 1 }}</el-divider>
            <el-form-item label="名称">
              <el-input v-model="block.name" />
            </el-form-item>
            
            <!-- IF 部分 -->
            <el-form-item label="IF 条件">
              <div v-for="(condition, condIndex) in block.if" :key="`if-${condIndex}`" class="condition-edit">
                <el-row :gutter="10">
                  <el-col :span="8">
                    <el-input v-model="condition.field" placeholder="字段" />
                  </el-col>
                  <el-col :span="8">
                    <el-input v-model="condition.value" placeholder="值" />
                  </el-col>
                  <el-col :span="8" class="condition-actions">
                    <el-button type="danger" size="small" @click="removeCondition(block.if, condIndex)">
                      删除
                    </el-button>
                  </el-col>
                </el-row>
              </div>
              <el-button type="primary" plain size="small" @click="addCondition(block.if)">
                添加条件
              </el-button>
            </el-form-item>
            
            <!-- THEN 部分 -->
            <el-form-item label="THEN 结果">
              <div v-for="(condition, condIndex) in block.then" :key="`then-${condIndex}`" class="condition-edit">
                <el-row :gutter="10">
                  <el-col :span="8">
                    <el-input v-model="condition.field" placeholder="字段" />
                  </el-col>
                  <el-col :span="8">
                    <el-input v-model="condition.value" placeholder="值" />
                  </el-col>
                  <el-col :span="8" class="condition-actions">
                    <el-button type="danger" size="small" @click="removeCondition(block.then, condIndex)">
                      删除
                    </el-button>
                  </el-col>
                </el-row>
              </div>
              <el-button type="primary" plain size="small" @click="addCondition(block.then)">
                添加结果
              </el-button>
            </el-form-item>
          </div>
          <el-button type="success" plain size="small" @click="addBlock">
            添加规则块
          </el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="requirementDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveRequirement">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useReuseStore } from '@/store/reuseStore';
import { ElMessage } from 'element-plus';

// 使用store
const reuseStore = useReuseStore();

// 接收项目ID
const props = defineProps<{
  projectId: number | string;
}>();

// 编辑规则相关
const ruleDialogVisible = ref(false);
const ruleDialogTitle = ref('编辑规则');
const editingRule = reactive({
  id: '',
  text: ''
});

// 编辑需求相关
const requirementDialogVisible = ref(false);
const requirementDialogTitle = ref('编辑需求');
const editingRequirement = reactive({
  id: '',
  ruleText: '',
  blocks: []
});

// 打开规则编辑对话框
const openRuleEdit = (rule: any) => {
  editingRule.id = rule.id;
  editingRule.text = rule.text;
  ruleDialogTitle.value = `编辑规则 ${rule.id}`;
  ruleDialogVisible.value = true;
};

// 打开需求编辑对话框
const openRequirementEdit = (requirement: any) => {
  editingRequirement.id = requirement.id;
  editingRequirement.ruleText = requirement.ruleText;
  // 深拷贝blocks，避免直接修改原始数据
  editingRequirement.blocks = JSON.parse(JSON.stringify(requirement.blocks));
  requirementDialogTitle.value = `编辑需求 ${requirement.id}`;
  requirementDialogVisible.value = true;
};

// 保存规则
const saveRule = async () => {
  try {
    // 获取当前独立需求数据
    const independentRequirementsData = reuseStore.getIndependentRequirements;
    if (independentRequirementsData) {
      // 找到并更新规则
      const updatedRules = independentRequirementsData.rules.map(rule => {
        if (rule.id === editingRule.id) {
          return { ...rule, text: editingRule.text };
        }
        return rule;
      });
      
      // 调用store的更新方法
      await reuseStore.updateIndependentRequirements(props.projectId, {
        rules: updatedRules,
        requirements: independentRequirementsData.requirements
      });
      
      ElMessage.success('规则保存成功');
    }
  } catch (error) {
    ElMessage.error('规则保存失败');
    console.error('保存规则失败:', error);
  } finally {
    // 保存成功后关闭对话框
    ruleDialogVisible.value = false;
  }
};

// 保存需求
const saveRequirement = async () => {
  try {
    // 获取当前独立需求数据
    const independentRequirementsData = reuseStore.getIndependentRequirements;
    if (independentRequirementsData) {
      // 找到并更新需求
      const updatedRequirements = independentRequirementsData.requirements.map(requirement => {
        if (requirement.id === editingRequirement.id) {
          return {
            ...requirement,
            ruleText: editingRequirement.ruleText,
            blocks: editingRequirement.blocks
          };
        }
        return requirement;
      });
      
      // 调用store的更新方法
      await reuseStore.updateIndependentRequirements(props.projectId, {
        rules: independentRequirementsData.rules,
        requirements: updatedRequirements
      });
      
      ElMessage.success('需求保存成功');
    }
  } catch (error) {
    ElMessage.error('需求保存失败');
    console.error('保存需求失败:', error);
  } finally {
    // 保存成功后关闭对话框
    requirementDialogVisible.value = false;
  }
};

// 添加规则块
const addBlock = () => {
  editingRequirement.blocks.push({
    name: `Block ${editingRequirement.blocks.length + 1}`,
    if: [],
    then: []
  });
};

// 添加条件
const addCondition = (conditions: any[]) => {
  conditions.push({
    field: '',
    value: ''
  });
};

// 删除条件
const removeCondition = (conditions: any[], index: number) => {
  conditions.splice(index, 1);
};

// 导出方法
defineExpose({
  openRuleEdit,
  openRequirementEdit
});
</script>

<style scoped>
.independent-requirement-edit {
  width: 100%;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.condition-edit {
  margin-bottom: 10px;
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.condition-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.block-edit {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
}
</style>