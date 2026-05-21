<template>
  <div class="file-download-container">
    <h3>文件下载</h3>
    
    <!-- 固定文件 -->
    <div v-if="showFixedFiles" class="file-section">
      <h4>上传文件</h4>
      <div class="file-list">
        <div class="file-item" v-for="file in fixedFiles" :key="file.id">
          <div class="file-info">
            <div class="file-icon">{{ getFileIcon(file.type) }}</div>
            <div class="file-details">
              <div class="file-name">{{ file.name }}</div>
              <div class="file-meta">
                <span>{{ file.description }}</span>
              </div>
            </div>
          </div>
          <button 
            class="download-btn" 
            @click="downloadFixedFile(file.id)"
            :disabled="isDownloading"
          >
            {{ isDownloading ? '下载中...' : '下载' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 中间结果 -->
    <div v-if="showIntermediateFiles" class="file-section">
      <h4>中间结果</h4>
      <div class="file-list">
        <div class="file-item" v-for="file in intermediateFiles" :key="file.id">
          <div class="file-info">
            <div class="file-icon">{{ getFileIcon(file.type) }}</div>
            <div class="file-details">
              <div class="file-name">{{ file.name }}</div>
              <div class="file-meta">
                <span>{{ file.description }}</span>
              </div>
            </div>
          </div>
          <button 
            class="download-btn" 
            @click="downloadIntermediateFile(file.id)"
            :disabled="isDownloading"
          >
            {{ isDownloading ? '下载中...' : '下载' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 最终结果 -->
    <div v-if="showResultFile" class="file-section">
      <h4>最终结果</h4>
      <div class="file-list">
        <div class="file-item">
          <div class="file-info">
            <div class="file-icon">{{ getFileIcon('pdf') }}</div>
            <div class="file-details">
              <div class="file-name">最终处理结果</div>
              <div class="file-meta">
                <span>完整的处理结果报告</span>
              </div>
            </div>
          </div>
          <button 
            class="download-btn" 
            @click="downloadResultFile"
            :disabled="isDownloading"
          >
            {{ isDownloading ? '下载中...' : '下载' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="downloadError" class="error-message">
      <div class="error-icon">⚠️</div>
      <p>{{ downloadError }}</p>
      <button class="error-close" @click="clearError">×</button>
    </div>
    

  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useResultStore } from '@/store/resultStore'

// Props
const props = defineProps<{
  projectId: number
  showFixedFiles?: boolean
  showIntermediateFiles?: boolean
  showResultFile?: boolean
}>()

// Store
const resultStore = useResultStore()

// 状态
const isDownloading = computed(() => resultStore.isDownloading)
const downloadError = computed(() => resultStore.downloadError)

// 文件定义
interface FileItem {
  id: string
  name: string
  type: string
  description: string
}

const fixedFiles: FileItem[] = [
  { id: 'upload', name: '旧文档', type: 'pdf', description: '用户上传的旧文档' },
  { id: 'new-document', name: '新文档', type: 'pdf', description: '用户上传的新文档' },
  { id: 'old-test-case', name: '旧测试用例', type: 'pdf', description: '用户上传的旧测试用例' }
]

const intermediateFiles: FileItem[] = [
  { id: '1', name: '独立需求生成结果', type: 'pdf', description: '独立需求生成后的结果文件' },
  { id: '2', name: '测试场景合成结果', type: 'pdf', description: '测试场景合成后的结果文件' },
  { id: '3', name: '场景-测试用例对齐结果', type: 'pdf', description: '场景与测试用例对齐后的结果文件' },
  { id: '4', name: '监管变更识别结果', type: 'pdf', description: '监管变更识别后的结果文件' },
  { id: '5', name: '级联影响范围分析结果', type: 'pdf', description: '级联影响范围分析后的结果文件' },
  { id: '6', name: '测试套件重用与更新结果', type: 'pdf', description: '测试套件重用与更新后的结果文件' }
]

// 计算属性
const showFixedFiles = computed(() => props.showFixedFiles !== false)
const showIntermediateFiles = computed(() => props.showIntermediateFiles !== false)
const showResultFile = computed(() => props.showResultFile !== false)

// 方法
const getFileIcon = (type: string): string => {
  const iconMap: Record<string, string> = {
    pdf: '📄',
    excel: '📊',
    word: '📝',
    csv: '📋',
    zip: '📦'
  }
  return iconMap[type] || '📄'
}

// 下载固定文件
const downloadFixedFile = async (fileId: string) => {
  try {
    switch (fileId) {
      case 'upload':
        await resultStore.handleDownloadUpload(props.projectId)
        break
      case 'new-document':
        await resultStore.handleDownloadNewDocument(props.projectId)
        break
      case 'old-test-case':
        await resultStore.handleDownloadOldTestCase(props.projectId)
        break
    }
  } catch (error) {
    console.error('下载文件失败:', error)
  }
}

// 下载中间结果
const downloadIntermediateFile = async (fileId: string) => {
  try {
    const index = parseInt(fileId)
    await resultStore.handleDownloadIntermediate(props.projectId, index)
  } catch (error) {
    console.error('下载中间结果失败:', error)
  }
}

// 下载最终结果
const downloadResultFile = async () => {
  try {
    await resultStore.handleDownloadResult(props.projectId)
  } catch (error) {
    console.error('下载最终结果失败:', error)
  }
}

// 清除错误
const clearError = () => {
  resultStore.clearError()
}
</script>

<style scoped>
.file-download-container {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 20px;
  background-color: #f9f9f9;
  margin-top: 20px;
}

h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 16px;
  color: #303133;
}

h4 {
  margin-top: 20px;
  margin-bottom: 15px;
  font-size: 14px;
  color: #606266;
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 8px;
}

.file-section {
  margin-bottom: 20px;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background-color: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  transition: all 0.3s;
}

.file-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 15px;
  flex: 1;
}

.file-icon {
  font-size: 24px;
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 5px;
}

.file-meta {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #909399;
}

.download-btn {
  background-color: #67c23a;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.download-btn:hover:not(:disabled) {
  background-color: #85ce61;
}

.download-btn:disabled {
  background-color: #c0c4cc;
  cursor: not-allowed;
}

.error-message {
  margin-top: 15px;
  padding: 12px;
  background-color: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 4px;
  color: #f56c6c;
  display: flex;
  align-items: center;
  gap: 10px;
  animation: fadeIn 0.3s ease;
}

.error-icon {
  font-size: 16px;
}

.error-message p {
  margin: 0;
  flex: 1;
}

.error-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #909399;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-close:hover {
  color: #606266;
}



@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>