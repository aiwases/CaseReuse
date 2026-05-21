<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="handleVisibleChange"
    title="编辑项目信息"
    width="500px"
    class="ruoyi-dialog"
    center
  >
    <el-form
      :model="localEditForm"
      :rules="rules"
      ref="editFormRef"
      label-width="80px"
      class="ruoyi-form"
    >
      <!-- 项目名称 -->
      <el-form-item label="项目名称" prop="name">
        <el-input
          v-model="localEditForm.name"
          placeholder="请输入项目名称"
          clearable
          class="ruoyi-input"
        />
      </el-form-item>

      <!-- 项目描述 -->
      <el-form-item label="项目描述" prop="description">
        <el-input
          v-model="localEditForm.description"
          type="textarea"
          rows="4"
          placeholder="请输入项目描述"
          class="ruoyi-textarea"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel" class="ruoyi-btn">取消</el-button>
        <el-button type="primary" @click="handleSubmit" class="ruoyi-btn">保存</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { useProjectStore } from '@/store/projectStore'
import { ElMessage, FormInstance } from 'element-plus'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  projectId: {
    type: Number,
    default: null
  },
  projectInfo: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['update:visible', 'success', 'error'])

// Store
const projectStore = useProjectStore()

// Local state
const localEditForm = reactive({
  name: '',
  description: ''
})

const editFormRef = ref<FormInstance | null>(null)

// 表单验证规则
const rules = reactive({
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 1, max: 50, message: '项目名称长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '项目描述长度不能超过 200 个字符', trigger: 'blur' }
  ]
})

// 监听项目信息变化，更新本地表单
watch(() => props.projectInfo, (newVal) => {
  if (newVal) {
    localEditForm.value = {
      name: newVal.name || '',
      description: newVal.description || ''
    }
  }
}, { deep: true })

// 监听visible变化，控制模态框显示/隐藏
watch(() => props.visible, (newVal) => {
  // Element Plus的el-dialog已经通过v-model处理了显示/隐藏
  // 这里可以添加额外的处理逻辑
})

// 表单提交处理
const handleSubmit = async () => {
  if (!editFormRef.value) return
  
  try {
    // 表单验证
    await editFormRef.value.validate()
    
    const name = localEditForm.name.trim()
    const desc = localEditForm.description.trim()

    await projectStore.updateProjectInfo(Number(props.projectId), name, desc)
    
    // 触发成功事件
    emit('success')
    
    // 关闭模态框
    emit('update:visible', false)
    
    ElMessage.success('项目信息更新成功')
  } catch (error: any) {
    console.error('更新项目信息失败:', error)
    
    // 如果是表单验证错误，Element Plus会自动处理
    if (error.name !== 'Error') return
    
    emit('error', error)
    
    if (error.response) {
      // 后端返回了错误信息
      const data = error.response.data
      ElMessage.error(data.message || '更新失败')
    } else {
      ElMessage.error('网络错误，请稍后重试')
    }
  }
}

// 取消操作
const handleCancel = () => {
  emit('update:visible', false)
}

// 处理对话框可见性变化
const handleVisibleChange = (visible: boolean) => {
  if (!visible) {
    // 当对话框关闭时，重置表单
    editFormRef.value?.resetFields()
  }
  emit('update:visible', visible)
}
</script>

<style scoped>
/* RuoYi 风格样式 */
.ruoyi-dialog {
  border-radius: 4px;
}

.ruoyi-form {
  margin-bottom: 0;
}

.ruoyi-input {
  border-radius: 4px;
}

.ruoyi-textarea {
  border-radius: 4px;
}

.ruoyi-btn {
  margin-right: 5px;
  border-radius: 4px;
}

.dialog-footer {
  text-align: right;
}
</style>