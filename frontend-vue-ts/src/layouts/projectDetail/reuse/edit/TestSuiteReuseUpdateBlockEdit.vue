<template>
  <div class="test-suite-reuse-update-block-edit">
    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑测试用例"
      width="700px"
      destroy-on-close
    >
      <div class="edit-container">
        <el-form :model="editingTestCase" label-width="80px">
          <el-form-item label="测试用例ID">
            <el-input v-model="editingTestCase.testid" placeholder="测试用例ID" />
          </el-form-item>
          
          <el-form-item label="规则">
            <el-input v-model="editingTestCase.rule" placeholder="规则" />
          </el-form-item>
          
          <!-- 属性编辑区域 -->
          <el-form-item label="属性列表">
            <div class="property-list">
              <div
                v-for="(_, key) in editingTestCase"
                :key="String(key)"
                v-if="key !== 'testid' && key !== 'rule'"
                class="property-item"
              >
                <el-form :model="editingTestCase" label-width="60px">
                  <el-form-item :label="String(key)">
                    <el-input v-model="editingTestCase[key]" :placeholder="String(key)" />
                  </el-form-item>
                  <el-button
                    type="danger"
                    size="small"
                    @click="removeProperty(String(key))"
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
                  @click="addProperty"
                >
                  添加属性
                </el-button>
              </div>
            </div>
          </el-form-item>
        </el-form>
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
import { ref, reactive, watch } from 'vue'
import { useReuseStore } from '@/store/reuseStore'

// 使用store
const reuseStore = useReuseStore()

// 定义props
const props = defineProps({
  testCase: {
    type: Object,
    default: null
  },
  visible: {
    type: Boolean,
    default: false
  }
})

// 定义事件
const emit = defineEmits(['update:visible', 'update:block'])

// 对话框状态
const dialogVisible = ref(false)

// 编辑中的数据
const editingTestCase = reactive({})

// 新增属性的临时变量
const newPropertyKey = ref('')
const newPropertyValue = ref('')

// 监听visible变化
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal && props.testCase) {
    // 深拷贝数据
    Object.assign(editingTestCase, JSON.parse(JSON.stringify(props.testCase)))
  }
})

// 监听dialogVisible变化
watch(dialogVisible, (newVal) => {
  emit('update:visible', newVal)
})

// 添加属性
const addProperty = () => {
  if (newPropertyKey.value && newPropertyValue.value) {
    editingTestCase[newPropertyKey.value] = newPropertyValue.value
    // 清空临时变量
    newPropertyKey.value = ''
    newPropertyValue.value = ''
  }
}

// 删除属性
const removeProperty = (key: string) => {
  delete editingTestCase[key]
}

// 保存更改
const saveChanges = () => {
  // 发送更新事件
  emit('update:block', editingTestCase)
  dialogVisible.value = false
}
</script>

<style scoped>
.edit-container {
  width: 100%;
}

.property-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

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
