<template>
  <div class="original-document">
    <div class="document-header">
      <p class="document-title" v-if="reuseStore.getOriginalFile.fileType">
        文件类型：{{ reuseStore.getOriginalFile.fileType.toUpperCase() }}
      </p>
    </div>
    <div class="document-content" v-loading="localLoading">
      <div v-if="localError" class="error-message">
        <el-alert type="error" :title="localError" show-icon />
      </div>
      <div v-else-if="!reuseStore.getOriginalFile.fileType" class="empty-message">
        <el-empty description="暂无文件内容" />
      </div>
      <div v-else-if="reuseStore.getOriginalFile.fileType === 'txt'" class="txt-content">
        <pre>{{ reuseStore.getOriginalFile.content }}</pre>
      </div>
      <div v-else-if="reuseStore.getOriginalFile.fileType === 'pdf'" class="pdf-content">
        <iframe 
          :src="reuseStore.getOriginalFile.pdfUrl" 
          frameborder="0" 
          width="100%" 
          height="100%"
        ></iframe>
      </div>
      <div v-else class="unsupported-content">
        <el-alert 
          type="warning" 
          title="不支持的文件类型" 
          show-icon 
        >
          当前不支持显示{{ reuseStore.getOriginalFile.fileType }}类型的文件
        </el-alert>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useReuseStore } from '@/store/reuseStore';

// 获取路由参数
const route = useRoute();
const projectId = route.params.id as string;

// 使用store
const reuseStore = useReuseStore();
const localLoading = ref(false);
const localError = ref('');

// 组件挂载时获取数据
onMounted(async () => {
  if (projectId) {
    try {
      localLoading.value = true;
      localError.value = '';
      // 这里暂时使用fetchUploadFile，稍后会修改为fetchOriginalFile
      await reuseStore.fetchUploadFile(projectId);
    } catch (error) {
      console.error('获取上传文件失败:', error);
      localError.value = '获取上传文件失败';
    } finally {
      localLoading.value = false;
    }
  }
});

// 组件卸载时清理资源
onUnmounted(() => {
  // 清理PDF URL，防止内存泄漏
  if (reuseStore.getOriginalFile.pdfUrl) {
    URL.revokeObjectURL(reuseStore.getOriginalFile.pdfUrl);
    // 重置store中的PDF URL
    reuseStore.resetUploadFiles();
  }
});
</script>

<style scoped>
.original-document {
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e4e7ed;
  background-color: #ffffff;
}

.document-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.document-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.document-title {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

.document-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #ffffff;
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
}

/* 自定义滚动条样式 */
.document-content::-webkit-scrollbar {
  width: 6px;
}

.document-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.document-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.document-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 文本内容样式 */
.txt-content {
  width: 100%;
  height: 100%;
}

.txt-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
}

/* PDF内容样式 */
.pdf-content {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.pdf-content iframe {
  border: none;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* 错误和空数据样式 */
.error-message,
.empty-message,
.unsupported-content {
  padding: 20px;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .document-header {
    padding: 8px 12px;
  }
  
  .document-header h3 {
    font-size: 14px;
  }
  
  .document-content {
    padding: 12px;
  }
  
  .txt-content pre {
    font-size: 13px;
  }
}
</style>