<template>
  <div>
    <!-- 预览按钮 -->
    <el-button
      type="info"
      size="small"
      @click="handlePreview"
      :disabled="!fileId"
    >
      <el-icon class="mr-1"><View /></el-icon>
      预览
    </el-button>

    <!-- 预览弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      title="文件预览"
      width="95%"
      :before-close="handleClose"
      class="preview-dialog"
    >
      <div v-if="loading" class="text-center my-5">
        <el-icon><Loading /></el-icon>
        <p>正在加载预览...</p>
      </div>

      <div class="preview-content" v-else>
        <iframe
          :src="previewUrl"
          width="100%"
          height="1000px"
          frameborder="0"
          style="border-radius: 8px;"
        ></iframe>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useFileStore } from '@/store/fileStore'
import { ElMessage, ElIcon } from 'element-plus'
import { View, Loading } from '@element-plus/icons-vue'

const props = defineProps<{ fileId?: number }>()

const fileStore = useFileStore()
const dialogVisible = ref(false)
const previewUrl = ref('')
const loading = ref(false)

const handleClose = () => {
  dialogVisible.value = false
}

const handlePreview = async () => {
  if (!props.fileId) return

  dialogVisible.value = true
  loading.value = true

  try {
    if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
    const blob = await fileStore.previewFile(props.fileId)
    previewUrl.value = URL.createObjectURL(blob.data)
  } catch (err) {
    console.error('预览失败', err)
    ElMessage.error('文件预览失败，请重试')
    dialogVisible.value = false
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.preview-dialog :deep(.el-dialog) {
  margin-top: 5vh !important;
  max-height: 90vh;
}

.preview-dialog :deep(.el-dialog__body) {
  padding: 20px;
  max-height: calc(90vh - 120px);
  overflow: hidden;
}

.preview-content {
  width: 100%;
  height: 100%;
}

.text-center {
  text-align: center;
}
</style>
