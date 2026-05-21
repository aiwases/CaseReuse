<template>
  <div class="file-upload-section">
    <el-form-item v-if="isGenerationProject && !store.fileRecord" label-position="top">
      <template #label>
        <div class="custom-label-container">
          <span class="label-text">选择源文件</span>
          <router-link to="/files" class="file-library-link">
            <el-icon><Folder /></el-icon>
            文件在文件库里？去文件库看看
          </router-link>
        </div>
      </template>

      <div class="upload-area">
        <!-- 拖拽上传区 -->
        <div
          class="drop-zone"
          :class="{ 'drag-over': isDragOver }"
          @click="triggerFileInput"
          @dragover.prevent="handleDragOver"
          @dragleave="handleDragLeave"
          @drop.prevent="handleDrop"
        >
          <div class="drop-zone-content">
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <p class="mb-1">拖放文件到此处或点击选择</p>
            <p class="text-muted small mb-0">仅支持 PDF 文件</p>
          </div>
          <input
            type="file"
            class="d-none"
            ref="fileInput"
            @change="handleFileSelect"
            accept=".pdf"
          />
        </div>

        <!-- 文件信息 -->
        <div v-if="store.selectedFile" class="file-info">
          <el-card shadow="never" class="file-info-card">
            <div class="file-info-content">
              <div class="file-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="file-details">
                <h6 class="mb-1 filename-display">{{ store.selectedFile?.name }}</h6>
                <p class="mb-0 small text-muted file-size-display">{{ formatFileSize(store.selectedFile?.size) }}</p>
              </div>
              <div class="file-actions">
                <el-button
                  type="danger"
                  size="small"
                  text
                  @click="removeFile"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 上传进度条 -->
        <div v-if="store.uploadProgress > 0" class="progress-container">
          <el-progress
            :percentage="store.uploadProgress"
            :format="percentage => `${percentage}%`"
            :color="['#67c23a', '#e6a23c', '#f56c6c']"
          />
        </div>

        <!-- 状态消息 -->
        <div v-if="store.isUploading" class="status-message">
          <el-alert
            title="上传中..."
            :description="store.uploadStatus"
            type="info"
            show-icon
            :closable="false"
          />
        </div>
      </div>
    </el-form-item>

    <!-- 自动选中的文件信息 -->
    <el-form-item v-else-if="isGenerationProject" label="已选择文件">
      <el-card shadow="never" class="file-info-card">
        <div class="file-info-content">
          <div class="file-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div class="file-details">
            <h6 class="mb-1 filename-display">{{ store.fileRecord.filename }}</h6>
            <p class="mb-0 small text-muted file-size-display">
              文件路径：{{ store.fileRecord.filepath || '已存储在系统中' }}
            </p>
          </div>
        </div>
      </el-card>
    </el-form-item>

    <!-- 重用项目提示 -->
    <el-form-item v-else label="源文件">
      <el-alert
        title="测试用例重用项目创建阶段无需上传文档"
        description="创建后可在项目文档详情页面上传旧文档、新文档和测试用例文件。"
        type="info"
        show-icon
        :closable="false"
      />
    </el-form-item>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { useCreatProjectStore } from '@/store/creatProjectStore';
import { Folder, UploadFilled, Document, Delete } from '@element-plus/icons-vue';

// 获取store实例
const store = useCreatProjectStore();
const isGenerationProject = computed(() => store.formData.process_type === 'generation');

// 文件拖拽状态
const isDragOver = ref(false);

// 文件输入引用
const fileInput = ref<HTMLInputElement | null>(null);

// 文件操作
const triggerFileInput = () => {
  store.triggerFileInput(fileInput.value);
};

const handleDragOver = () => {
  isDragOver.value = true;
  store.handleDragOver();
};

const handleDragLeave = () => {
  isDragOver.value = false;
  store.handleDragLeave();
};

const handleDrop = (event: DragEvent) => {
  isDragOver.value = false;
  store.handleDrop(event);
};

const handleFileSelect = (event: Event) => {
  store.handleFileSelect(event);
};

const removeFile = () => {
  store.removeFile();
};

// 格式化文件大小
const formatFileSize = (size: number | undefined) => {
  return store.formatFileSize(size);
};
</script>

<style scoped>
.file-upload-section {
  width: 100%;
  max-height: 360px;
  overflow-y: auto;
  padding-right: 4px;
}

/* 自定义标签容器 */
.custom-label-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.label-text {
  font-weight: 500;
  font-size: 14px;
  color: #303133;
}

.file-library-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #409eff;
  text-decoration: none;
}

.file-library-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

/* 文件上传区域 */
.upload-area, .drop-zone {
  width: 100%;
}

.drop-zone {
  border: 2px dashed #dcdfe6;
  border-radius: 4px;
  padding: 48px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background-color: #fafafa;
}

.drop-zone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  text-align: center;
}

.drop-zone:hover, .drop-zone.drag-over {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.upload-icon {
  font-size: 48px;
  color: #909399;
  margin-bottom: 16px;
}

/* 文件信息展示 */
.file-info {
  margin-top: 20px;
}

.file-info-card {
  border: 1px solid #ebeef5;
}

.file-info-content {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.file-icon {
  font-size: 32px;
  color: #409eff;
}

.file-details {
  flex: 1;
  min-width: 0;
}

.filename-display {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 进度和状态 */
.progress-container,
.status-message {
  margin-top: 20px;
  width: 100%;
}

/* 滚动条样式 */
.file-upload-section::-webkit-scrollbar {
  width: 6px;
}

.file-upload-section::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.file-upload-section::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.file-upload-section::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.drop-zone-content p {
  margin: 5px 0;
  text-align: center;
}
</style>