<template>
  <div class="card shadow-sm upload-card">
    <div class="card-header bg-light py-3">
      <h5 class="card-title mb-0">上传文件</h5>
    </div>
    <div class="card-body p-5">
      <!-- 上传表单 -->
      <form @submit.prevent="handleSubmit" class="needs-validation" novalidate>
        <!-- 文件拖拽区域 -->
        <div
          class="drop-zone mb-4 p-6 border-2 border-dashed rounded-3 text-center"
          :class="{ 'drag-over': uploadStore.isDragOver }"
          @click="triggerFileSelect"
          @dragover.prevent="handleDragOver"
          @dragleave="handleDragLeave"
          @drop.prevent="handleDrop"
        >
          <div class="drop-zone-content">
            <i class="bi bi-cloud-arrow-up display-1 text-muted d-block mb-3"></i>
            <p class="mb-1">拖放文件到此处或点击此区域选择文件</p>
            <p class="small mb-0">支持 PDF 格式</p>
          </div>
          <input
            ref="fileInputRef"
            type="file"
            class="d-none"
            @change="handleFileSelect"
            accept=".pdf"
          >
        </div>

        <!-- 文件信息预览 -->
        <div v-if="uploadStore.selectedFile" class="file-info mb-4">
          <div class="d-flex align-items-center p-3 bg-light rounded-3">
            <div class="flex-shrink-0 me-3">
              <i class="bi bi-file-earmark-text display-6 text-primary"></i>
            </div>
            <div class="flex-grow-1">
              <h6 class="mb-1 filename-display">{{ uploadStore.selectedFile.name }}</h6>
              <p class="mb-0 small text-muted file-size-display">
                大小: {{ (uploadStore.selectedFile.size / 1024 / 1024).toFixed(2) }} MB
              </p>
            </div>
            <div class="flex-shrink-0">
              <button type="button" class="btn-close" @click="removeFile" aria-label="移除文件"></button>
            </div>
          </div>
        </div>

        <!-- 进度条 -->
        <div v-if="uploadStore.showProgress" class="progress mb-3">
          <div
            class="progress-bar progress-bar-striped progress-bar-animated"
            :style="{ width: uploadStore.progress + '%' }"
            role="progressbar"
            :aria-valuenow="uploadStore.progress"
            aria-valuemin="0"
            aria-valuemax="100"
          >
            <span class="progress-text">{{ uploadStore.progress }}%</span>
          </div>
        </div>

        <!-- 状态消息 -->
        <div v-if="uploadStore.statusMessage" class="alert" :class="'alert-' + uploadStore.statusType" role="alert">
          <div class="d-flex align-items-center">
            <div v-if="uploadStore.isUploading" class="spinner-border spinner-border-sm me-2" role="status"></div>
            <span>{{ uploadStore.statusMessage }}</span>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="d-flex justify-content-end gap-2">
          <router-link to="/file" class="btn btn-outline-secondary">取消</router-link>
          <button
            class="btn btn-primary"
            :disabled="!uploadStore.selectedFile || uploadStore.isUploading"
          >
            <i class="bi bi-cloud-arrow-up"></i> 开始上传
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useUploadStore } from '@/store/uploadStore'

// 使用 Pinia store
const uploadStore = useUploadStore()

// 从store中解构响应式变量
const {
  selectedFile,
  isDragOver,
  progress,
  showProgress,
  statusMessage,
  statusType,
  isUploading
} = uploadStore

// 引用
const fileInputRef = ref(null)

// 计算属性
const isUploadDisabled = computed(() => !uploadStore.selectedFile || uploadStore.isUploading)

// 方法
const triggerFileSelect = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = (event) => {
  const files = event.target.files
  console.log('handleFileSelect', files[0])
  if (files && files.length > 0) {
    uploadStore.setSelectedFile(files[0])
  }
}

const handleDragOver = () => {
  uploadStore.setDragOver(true)
}

const handleDragLeave = () => {
  uploadStore.setDragOver(false)
}

const handleDrop = (event) => {
  uploadStore.setDragOver(false)
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    uploadStore.setSelectedFile(files[0])
    // 更新 file input
    const dt = new DataTransfer()
    dt.items.add(files[0])
    if (fileInputRef.value) {
      fileInputRef.value.files = dt.files
    }
  }
}

const removeFile = () => {
  uploadStore.resetUpload()
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

const handleSubmit = async () => {
  await uploadStore.performUpload()
}
</script>

<style scoped>
.upload-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  border: 1px solid #e5e7eb;
  width: 100%;
}

.card-header {
  padding: 1.5rem;
  background: linear-gradient(to right, #f8fafc, #f1f5f9);
  border-bottom: 1px solid #e5e7eb;
}

.card-title {
  font-size: 1.25rem;
  font-weight: bold;
  color: #1f2937;
  margin: 0;
}

.drop-zone {
  background: linear-gradient(135deg, #f8fafc, #f0f4f8);
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  height: 350px;
}

.drop-zone::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(67, 97, 238, 0.05);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.drop-zone:hover {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #f0f4f8, #e8f0ff);
}

.drop-zone:hover::before {
  opacity: 1;
}

.drop-zone.drag-over {
  border-color: #2563eb;
  background: linear-gradient(135deg, #e8f0ff, #dbeafe);
}

.drop-zone.drag-over::before {
  opacity: 1;
  background: rgba(37, 99, 235, 0.1);
}

.drop-zone-content {
  position: relative;
  z-index: 1;
}

.drop-zone i {
  font-size: 6rem;
  color: #9ca3af;
  margin-bottom: 1rem;
  transition: all 0.3s ease;
}

.drop-zone:hover i {
  color: #3b82f6;
  transform: scale(1.1);
}

.drop-zone p {
  font-weight: 600;
  color: #374151;
  margin: 0.5rem 0;
  font-size: 1.1rem;
}

.drop-zone .text-muted {
  color: #6b7280;
  font-size: 9rem;
}

.file-info {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  padding: 1rem;
  margin: 1.5rem 0;
  display: flex;
  align-items: center;
  gap: 1rem;
  animation: fadeIn 0.5s ease;
}

.file-info i {
  font-size: 2rem;
  color: #3b82f6;
}

.file-info .filename-display {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.file-info .file-size-display {
  color: #6b7280;
  font-size: 0.875rem;
}

.progress {
  height: 8px;
  background-color: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
  margin: 1rem 0;
  position: relative;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(to right, #3b82f6, #1d4ed8);
  border-radius: 4px;
  transition: width 0.6s ease;
}

.progress-bar::animation {
  background-image: linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);
  background-size: 1rem 1rem;
  animation: progress-bar-stripes 1s linear infinite;
}

.alert {
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
  border-left: 4px solid;
  animation: fadeIn 0.5s ease;
}

.alert-info {
  background: #eff6ff;
  border-color: #3b82f6;
  color: #1e40af;
}

.alert-success {
  background: #f0fdf4;
  border-color: #10b981;
  color: #065f46;
}

.alert-danger {
  background: #fef2f2;
  border-color: #ef4444;
  color: #991b1b;
}

.btn-group-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
}

.btn-outline-secondary {
  background: white;
  color: #6b7280;
  border-color: #d1d5db;
}

.btn-outline-secondary:hover {
  background: #f9fafb;
  border-color: #9ca3af;
  color: #374151;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
  border-color: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.btn-primary:disabled {
  background: #e5e7eb;
  color: #9ca3af;
  border-color: #e5e7eb;
  cursor: not-allowed;
  transform: none;
  opacity: 0.7;
}

.btn-primary i {
  font-size: 1.2rem;
  margin-right: 0.5rem;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes progress-bar-stripes {
  0% {
    background-position: 1rem 0;
  }
}
</style>
