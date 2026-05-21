<template>
  <div>
    <!-- 删除按钮 -->
    <el-button
      type="danger"
      size="small"
      @click="openDeleteModal(fileId, fileName)"
      :disabled="!fileId"
    >
      删除文件
    </el-button>

    <!-- 删除文件确认弹窗 -->
    <el-dialog
      v-model="showDeleteModal"
      title="确认删除文件"
      width="60%"
      :close-on-click-modal="false"
    >
      <div>
        <p class="mb-3">{{ deleteMessage }}</p>

        <el-table
          v-if="deleteProjects.length > 0"
          :data="deleteProjects"
          border
          size="small"
        >
          <el-table-column prop="name" label="项目名称" />
          <el-table-column label="状态">
            <template #default="{ row }">
              <el-tag :type="getTagType(row.status)">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180" />
          <el-table-column prop="updated_at" label="更新时间" width="180" />
        </el-table>

        <div v-else class="text-center text-gray-500 my-3">
          该文件没有关联的项目
        </div>

        <p
          v-if="deleteProjects.length > 0"
          class="text-red-600 mt-3 flex items-center"
        >
          <el-icon color="#dc2626" class="mr-1">
            <WarningFilled />
          </el-icon>
          删除文件将同步删除上表中所有项目！
        </p>
      </div>

      <template #footer>
        <div class="flex justify-end gap-2">
          <el-button @click="closeDeleteModal">取消</el-button>
          <el-button type="danger" @click="confirmDelete">删除</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useFileStore } from '@/store/fileStore'
import { ElMessage } from 'element-plus'
import { WarningFilled } from '@element-plus/icons-vue'

// Props：文件信息由父组件传入
defineProps<{
  fileId: number
  fileName: string
}>()

// Store
const fileStore = useFileStore()

// 控制对话框显示
const showDeleteModal = ref(false)

// 数据
const deleteMessage = computed(() => fileStore.deleteMessage)
const deleteProjects = computed(() => fileStore.deleteProjects)

// 状态样式
const getTagType = (status: string) => {
  const map: Record<string, string> = {
    completed: 'success',
    running: 'info',
    failed: 'danger',
    pending: 'warning'
  }
  return map[status] || 'default'
}

// 打开对话框
const openDeleteModal = async (fileId: number, fileName: string) => {
  try {
    await fileStore.showDeleteModal(fileId, fileName)
    showDeleteModal.value = true
  } catch (error) {
    console.error('获取删除预览失败:', error)
    ElMessage.error('获取文件关联项目失败，请重试')
  }
}

// 确认删除
const confirmDelete = async () => {
  try {
    const message = await fileStore.confirmDelete()
    showDeleteModal.value = false
    ElMessage.success(message)
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除过程中出现错误，请重试')
  }
}

// 关闭弹窗
const closeDeleteModal = () => {
  showDeleteModal.value = false
}
</script>
