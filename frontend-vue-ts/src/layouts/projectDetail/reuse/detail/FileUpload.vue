<template>
  <div class="reuse-file-upload">
    <div class="component-header">
      <h3>文件上传</h3>
    </div>
    
    <div class="component-content">
      <!-- 旧文档上传 -->
      <FileUpload
        title="旧文档"
        accept=".pdf,.txt"
        hint="支持 PDF、TXT 文件"
        :projectId="projectId"
        :custom-upload="handleOldDocumentUpload"
        @upload-success="handleUploadSuccess"
        @upload-error="handleUploadError"
        @progress="handleProgress"
      />
      
      <!-- 新文档上传 -->
      <FileUpload
        title="新文档"
        accept=".pdf,.txt"
        hint="支持 PDF、TXT 文件"
        :projectId="projectId"
        :custom-upload="handleNewDocumentUpload"
        @upload-success="handleRulesUploadSuccess"
        @upload-error="handleUploadError"
        @progress="handleProgress"
      />
      
      <!-- 旧测试用例文件上传 -->
      <FileUpload
        title="旧测试用例文件"
        accept=".json"
        hint="支持 JSON 文件"
        :projectId="projectId"
        :custom-upload="handleOldTestcaseUpload"
        @upload-success="handleTestCasesUploadSuccess"
        @upload-error="handleUploadError"
        @progress="handleProgress"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useReuseUploadStore } from '@/store/reuseUploadStore'
import FileUpload from '@/components/FileUpload.vue'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps<{
  projectId: string | number
}>()

// 使用reuse upload store
const reuseUploadStore = useReuseUploadStore()

// 旧文档上传函数
const handleOldDocumentUpload = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return await reuseUploadStore.uploadOldDocumentAction(props.projectId, formData)
}

// 新文档上传函数
const handleNewDocumentUpload = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return await reuseUploadStore.uploadNewDocumentAction(props.projectId, formData)
}

// 旧测试用例上传函数
const handleOldTestcaseUpload = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return await reuseUploadStore.uploadOldTestcaseAction(props.projectId, formData)
}

// 处理上传成功
const handleUploadSuccess = (response: any) => {
  console.log('上传成功:', response)
  const msg = response?.msg || response?.message || '旧文档上传成功'
  ElMessage.success(msg)
}

// 处理规则文件上传成功
const handleRulesUploadSuccess = (response: any) => {
  console.log('规则文件上传成功:', response)
  const msg = response?.msg || response?.message || '新文档上传成功'
  ElMessage.success(msg)
}

// 处理测试用例文件上传成功
const handleTestCasesUploadSuccess = (response: any) => {
  console.log('测试用例文件上传成功:', response)
  const msg = response?.msg || response?.message || '旧测试用例文件上传成功'
  ElMessage.success(msg)
}

// 处理上传错误
const handleUploadError = (error: string) => {
  console.error('上传错误:', error)
  ElMessage.error(error || '上传失败，请稍后重试')
}

// 处理上传进度
const handleProgress = (progress: number) => {
  console.log('上传进度:', progress)
  // 可以更新store中的进度状态
}
</script>

<style scoped>
.reuse-file-upload {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  overflow: hidden;
}

.reuse-file-upload:hover {
  border-color: #dcdfe6;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.component-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  background-color: #f8f9fa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.component-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.component-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

/* 调整FileUpload组件间距 */
:deep(.file-upload-container) {
  margin-bottom: 16px;
  border-radius: 6px;
}

:deep(.file-upload-container):hover {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

/* 最后一个组件没有底部间距 */
:deep(.file-upload-container:last-child) {
  margin-bottom: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .component-header {
    padding: 10px 14px;
  }
  
  .component-content {
    padding: 12px;
  }
  
  :deep(.file-upload-container) {
    margin-bottom: 12px;
  }
}

@media (max-width: 480px) {
  .component-header {
    padding: 8px 12px;
  }
  
  .component-header h3 {
    font-size: 14px;
  }
  
  .component-content {
    padding: 10px;
  }
  
  :deep(.file-upload-container) {
    margin-bottom: 10px;
  }
}
</style>