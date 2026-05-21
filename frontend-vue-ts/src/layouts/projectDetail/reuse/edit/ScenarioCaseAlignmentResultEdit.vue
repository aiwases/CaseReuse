<template>
  <div class="scenario-case-alignment-result-edit">
    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑场景-测试用例对齐结果"
      width="80%"
      destroy-on-close
    >
      <div class="edit-container">
        <!-- 对齐关系编辑区域 -->
        <div class="edit-section">
          <h4>对齐关系管理</h4>
          <div class="alignment-list">
            <div
              v-for="(alignment, index) in editingAlignments"
              :key="index"
              class="alignment-item"
            >
              <el-form :model="alignment" label-width="100px">
                <el-form-item label="场景ID">
                  <el-input v-model="alignment.scenarioId" placeholder="场景ID" />
                </el-form-item>
                <el-form-item label="场景名称">
                  <el-input v-model="alignment.scenarioName" placeholder="场景名称" />
                </el-form-item>
                <el-form-item label="测试用例ID">
                  <el-input v-model="alignment.testCaseId" placeholder="测试用例ID" />
                </el-form-item>
                <el-form-item label="测试用例名称">
                  <el-input v-model="alignment.testCaseName" placeholder="测试用例名称" />
                </el-form-item>
                <el-form-item label="对齐状态">
                  <el-select v-model="alignment.status" placeholder="选择对齐状态">
                    <el-option label="已对齐" value="aligned" />
                    <el-option label="未对齐" value="not_aligned" />
                    <el-option label="部分对齐" value="partially_aligned" />
                  </el-select>
                </el-form-item>
                <el-button
                  type="danger"
                  size="small"
                  @click="removeAlignment(index)"
                >
                  删除对齐关系
                </el-button>
              </el-form>
            </div>
          </div>
          <el-button type="primary" size="small" @click="addAlignment">
            添加对齐关系
          </el-button>
        </div>
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
import { ref, reactive } from 'vue'
import { useReuseStore } from '@/store/reuseStore'

const reuseStore = useReuseStore()

// 对话框状态
const dialogVisible = ref(false)

// 编辑中的数据
const editingAlignments = ref<any[]>([])

// 打开编辑对话框
const openEdit = () => {
  // 从store获取数据，如果没有则使用默认数据
  const alignmentData = reuseStore.getScenarioCaseAlignments || {
    alignments: []
  }
  
  // 深拷贝数据
  editingAlignments.value = JSON.parse(JSON.stringify(alignmentData.alignments || []))
  
  dialogVisible.value = true
}

// 添加对齐关系
const addAlignment = () => {
  editingAlignments.value.push({
    scenarioId: '',
    scenarioName: '新场景',
    testCaseId: '',
    testCaseName: '新测试用例',
    status: 'aligned'
  })
}

// 删除对齐关系
const removeAlignment = (index: number) => {
  editingAlignments.value.splice(index, 1)
}

// 保存更改
const saveChanges = () => {
  const alignmentData = {
    alignments: editingAlignments.value
  }
  
  // 更新store中的数据
  reuseStore.updateScenarioCaseAlignments(alignmentData)
  dialogVisible.value = false
}

// 暴露方法给父组件
defineExpose({
  openEdit
})
</script>

<style scoped>
.scenario-case-alignment-result-edit {
  width: 100%;
}

.edit-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.edit-section {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  background-color: #fafafa;
}

.edit-section h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.alignment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.alignment-item {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  background-color: #ffffff;
}

.alignment-item .el-form {
  margin-bottom: 0;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>