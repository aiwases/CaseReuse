<template>
  <div class="file-upload-container">
    <h3>{{ title || '文件上传' }}</h3>
    <div class="upload-area">
      <input 
        type="file" 
        ref="fileInput"
        :accept="accept"
        class="file-input" 
        @change="handleFileChange"
      >
      <div class="upload-content" @click="triggerFileInput">
        <div class="upload-icon">📁</div>
        <p>点击或拖拽文件到此处上传</p>
        <p class="upload-hint">{{ hint || '支持 PDF、TXT格式' }}</p>
      </div>
    </div>
    <div v-if="selectedFile" class="file-info">
      <span>{{ selectedFile.name }}</span>
      <button class="remove-btn" @click="removeFile">移除</button>
    </div>
    <div v-if="progress > 0 && progress < 100" class="progress-container">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>
      <span class="progress-text">{{ progress }}%</span>
    </div>
    <button 
      class="upload-btn" 
      :disabled="!selectedFile || isUploading"
      @click="uploadFile"
    >
      {{ isUploading ? '上传中...' : '上传文件' }}
    </button>
    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import service from '@/api/index'

// Props
const props = defineProps<{
  title?: string
  accept?: string
  hint?: string
  uploadUrl?: string
  projectId?: string | number
  customUpload?: (file: File) => Promise<any>
}>()

// Emits
const emit = defineEmits<{
  (e: 'upload-success', response: any): void
  (e: 'upload-error', error: string): void
  (e: 'progress', progress: number): void
}>()

// State
const fileInput = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)
const isUploading = ref(false)
const progress = ref(0)
const error = ref('')

// Methods
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
    error.value = ''
  }
}

const removeFile = () => {
  selectedFile.value = null
  progress.value = 0
  error.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const uploadFile = async () => {
  if (!selectedFile.value) return

  isUploading.value = true
  progress.value = 0
  error.value = ''

  try {
    if (props.customUpload) {
      // 使用自定义上传函数
      const response = await props.customUpload(selectedFile.value)
      emit('upload-success', response)
      removeFile()
    } else if (props.uploadUrl) {
      // 使用传统上传方式
      const formData = new FormData()
      formData.append('file', selectedFile.value)

      const response = await service.post(props.uploadUrl, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const uploadProgress = Math.round((progressEvent.loaded / progressEvent.total) * 100)
            progress.value = uploadProgress
            emit('progress', uploadProgress)
          }
        },
        validateStatus: () => true
      })

      if (response.status >= 200 && response.status < 300) {
        emit('upload-success', response.data)
        removeFile()
      } else {
        throw new Error(`上传失败: ${response.data?.message || '未知错误'}`)
      }
    } else {
      throw new Error('请提供上传URL或自定义上传函数')
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '上传失败'
    emit('upload-error', error.value)
  } finally {
    isUploading.value = false
    progress.value = 0
  }
}
</script>

<style scoped>
.file-upload-container {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 20px;
  background-color: #ffffff;
}

.file-upload-container:hover {
  border-color: #dcdfe6;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 15px;
  font-weight: 500;
  color: #303133;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f2f5;
}

.upload-area {
  position: relative;
  border: 2px dashed #dcdfe6;
  border-radius: 6px;
  padding: 40px 20px;
  text-align: center;
  background-color: #fafafa;
  cursor: pointer;
}

.upload-area:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.upload-icon {
  font-size: 56px;
}

.upload-content p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.upload-hint {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.file-info {
  margin-top: 14px;
  padding: 10px 14px;
  background-color: #ecf5ff;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-info span {
  font-size: 13px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  margin-right: 10px;
}

.remove-btn {
  background-color: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 12px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
}

.remove-btn:hover {
  background-color: #f78989;
}

.progress-container {
  margin-top: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background-color: #ecf5ff;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #409eff;
}

.progress-text {
  font-size: 12px;
  font-weight: 500;
  color: #409eff;
  min-width: 40px;
  text-align: right;
}

.upload-btn {
  margin-top: 20px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  width: 100%;
}

.upload-btn:hover:not(:disabled) {
  background-color: #66b1ff;
}

.upload-btn:disabled {
  background-color: #c0c4cc;
  cursor: not-allowed;
}

.error-message {
  margin-top: 10px;
  color: #f56c6c;
  font-size: 12px;
  padding: 8px 12px;
  background-color: #fef0f0;
  border-radius: 4px;
  border-left: 3px solid #f56c6c;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .file-upload-container {
    padding: 16px;
    border-radius: 4px;
  }
  
  h3 {
    margin-bottom: 16px;
    font-size: 14px;
  }
  
  .upload-area {
    padding: 32px 16px;
  }
  
  .upload-icon {
    font-size: 48px;
  }
  
  .upload-content p {
    font-size: 13px;
  }
  
  .file-info {
    padding: 8px 12px;
  }
  
  .upload-btn {
    margin-top: 16px;
    padding: 8px 16px;
  }
}

@media (max-width: 480px) {
  .file-upload-container {
    padding: 12px;
  }
  
  h3 {
    margin-bottom: 14px;
    font-size: 13px;
  }
  
  .upload-area {
    padding: 24px 12px;
  }
  
  .upload-icon {
    font-size: 40px;
  }
  
  .upload-content p {
    font-size: 12px;
  }
  
  .upload-hint {
    font-size: 11px;
  }
  
  .file-info {
    padding: 6px 10px;
  }
  
  .file-info span {
    font-size: 12px;
  }
  
  .remove-btn {
    padding: 3px 10px;
    font-size: 11px;
  }
  
  .upload-btn {
    margin-top: 14px;
    padding: 6px 14px;
    font-size: 13px;
  }
}
</style>