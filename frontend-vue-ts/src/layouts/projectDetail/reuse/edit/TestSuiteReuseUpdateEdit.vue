<template>
  <div class="test-suite-reuse-update-edit">
    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑测试套件重用与更新结果"
      width="80%"
      destroy-on-close
    >
      <div class="edit-container">
        <!-- 测试用例编辑区域 -->
        <div class="edit-section">
          <h4>测试用例管理</h4>
          <div class="test-case-list">
            <div
              v-for="(testCaseGroup, groupIndex) in editingTestCases"
              :key="groupIndex"
              class="test-case-group"
            >
              <div
                v-for="(testCase, testCaseIndex) in testCaseGroup"
                :key="testCase.testid"
                class="test-case-item"
              >
                <el-form :model="testCase" label-width="80px">
                  <el-form-item label="测试用例ID">
                    <el-input v-model="testCase.testid" placeholder="测试用例ID" />
                  </el-form-item>
                  
                  <el-form-item label="规则">
                    <el-input v-model="testCase.rule" placeholder="规则" />
                  </el-form-item>
                  
                  <!-- 属性编辑区域 -->
                  <el-form-item label="属性列表">
                    <div class="property-list">
                      <div
                        v-for="(_, key) in testCase"
                        :key="String(key)"
                        v-if="key !== 'testid' && key !== 'rule'"
                        class="property-item"
                      >
                        <el-form :model="testCase" label-width="60px">
                          <el-form-item :label="String(key)">
                            <el-input v-model="testCase[key]" :placeholder="String(key)" />
                          </el-form-item>
                          <el-button
                            type="danger"
                            size="small"
                            @click="removeProperty(groupIndex, testCaseIndex, String(key))"
                          >
                            删除属性
                          </el-button>
                        </el-form>
                      </div>
                      
                      <!-- 添加属性区域 -->
                      <div class="add-property-section">
                        <el-input
                          v-model="newPropertyKey"
                          placeholder="属性名称"
                          style="width: 150px; margin-right: 8px;"
                        />
                        <el-input
                          v-model="newPropertyValue"
                          placeholder="属性值"
                          style="width: 200px; margin-right: 8px;"
                        />
                        <el-button
                          type="primary"
                          size="small"
                          @click="addProperty(groupIndex, testCaseIndex)"
                        >
                          添加属性
                        </el-button>
                      </div>
                    </div>
                  </el-form-item>
                  
                  <el-button
                    type="danger"
                    size="small"
                    @click="removeTestCase(groupIndex, testCaseIndex)"
                  >
                    删除测试用例
                  </el-button>
                </el-form>
              </div>
            </div>
          </div>
          <el-button type="primary" size="small" @click="addTestCase">
            添加测试用例
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
import { ref } from 'vue'
import { useReuseStore } from '@/store/reuseStore'

const reuseStore = useReuseStore()

// 对话框状态
const dialogVisible = ref(false)

// 编辑中的数据 - 嵌套数组结构
const editingTestCases = ref<any[][]>([])

// 新增属性的临时变量
const newPropertyKey = ref('')
const newPropertyValue = ref('')

// 打开编辑对话框
const openEdit = () => {
  const testSuiteReuseData = reuseStore.getTestSuiteReuse
  if (testSuiteReuseData) {
    // 深拷贝数据
    editingTestCases.value = JSON.parse(JSON.stringify(testSuiteReuseData.testcases || []))
  } else {
    // 使用默认数据结构
    editingTestCases.value = []
  }
  
  dialogVisible.value = true
}

// 添加测试用例
const addTestCase = () => {
  // 如果没有组，创建一个新组
  if (editingTestCases.value.length === 0) {
    editingTestCases.value.push([])
  }
  editingTestCases.value[0].push({
    testid: '',
    rule: '',
    '交易品种': '',
    '交易市场': '',
    '交易方向': '',
    '操作主体': '',
    '状态': '',
    '结果': '',
    '结果操作': '',
    '结果操作部分': '',
    '结果状态': ''
  })
}

// 删除测试用例
const removeTestCase = (groupIndex: number, testCaseIndex: number) => {
  editingTestCases.value[groupIndex].splice(testCaseIndex, 1)
  // 如果组为空，删除该组
  if (editingTestCases.value[groupIndex].length === 0) {
    editingTestCases.value.splice(groupIndex, 1)
  }
}

// 添加属性
const addProperty = (groupIndex: number, testCaseIndex: number) => {
  if (newPropertyKey.value && newPropertyValue.value) {
    editingTestCases.value[groupIndex][testCaseIndex][newPropertyKey.value] = newPropertyValue.value
    // 清空临时变量
    newPropertyKey.value = ''
    newPropertyValue.value = ''
  }
}

// 删除属性
const removeProperty = (groupIndex: number, testCaseIndex: number, key: string) => {
  delete editingTestCases.value[groupIndex][testCaseIndex][key]
}

// 保存更改
const saveChanges = () => {
  const testSuiteReuseData = {
    testcases: editingTestCases.value
  }
  
  // 更新store中的数据
  reuseStore.testSuiteReuse = testSuiteReuseData
  dialogVisible.value = false
}

// 暴露方法给父组件
defineExpose({
  openEdit
})
</script>

<style scoped>
.test-suite-reuse-update-edit {
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

.test-case-list,
.property-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.test-case-item,
.property-item {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  background-color: #ffffff;
}

.add-property-section {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background-color: #f9f9f9;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

@media (max-width: 768px) {
  .add-property-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .add-property-section .el-input {
    width: 100% !important;
    margin-right: 0 !important;
    margin-bottom: 8px;
  }
}
</style>