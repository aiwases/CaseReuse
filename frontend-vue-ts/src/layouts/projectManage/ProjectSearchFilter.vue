<template>
  <el-card class="ruoyi-card" shadow="never">
    <el-form :inline="true" :model="queryParams" class="ruoyi-search-form">
      <el-form-item label="项目名">
        <el-input
          v-model="queryParams.projectName"
          placeholder="请输入项目名"
          clearable
          @keyup.enter="handleQuery"
          class="ruoyi-input"
        />
      </el-form-item>
      <el-form-item label="文件名">
        <el-input
          v-model="queryParams.fileName"
          placeholder="请输入文件名"
          clearable
          @keyup.enter="handleQuery"
          class="ruoyi-input"
        />
      </el-form-item>
      <el-form-item label="状态">
        <el-select
          v-model="queryParams.status"
          placeholder="请选择状态"
          clearable
          class="ruoyi-select"
        >
          <el-option label="所有状态" value="" />
          <el-option label="就绪" value="ready" />
          <el-option label="运行中" value="running" />
          <el-option label="已完成" value="completed" />
          <el-option label="失败" value="failed" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleQuery" :icon="Search">
          查询
        </el-button>
        <el-button @click="resetQuery" :icon="RefreshRight">
          重置
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Search, RefreshRight } from '@element-plus/icons-vue'

// Props
const props = defineProps<{
  queryParams: {
    pageNum: number
    pageSize: number
    projectName: string
    fileName: string
    status: string
  }
}>()

// Emits
const emit = defineEmits<{
  (e: 'update:queryParams', value: any): void
  (e: 'query'): void
}>()

// 查询按钮操作
const handleQuery = () => {
  emit('query')
}

// 重置按钮操作
const resetQuery = () => {
  const newParams = {
    pageNum: 1,
    pageSize: props.queryParams.pageSize,
    projectName: '',
    fileName: '',
    status: ''
  }
  emit('update:queryParams', newParams)
  emit('query')
}
</script>

<style scoped>
/* 搜索表单样式 */
.ruoyi-search-form {
  padding: 15px;
  width: 100%;
  box-sizing: border-box;
}

.ruoyi-input, .ruoyi-select {
  width: 200px;
  margin-right: 15px;
}

.ruoyi-search-form .el-form-item {
  margin-bottom: 0;
}

/* 响应式样式 */
@media (max-width: 768px) {
  .ruoyi-search-form {
    display: flex;
    flex-direction: column;
  }

  .ruoyi-search-form .el-form-item {
    width: 100%;
    margin-right: 0;
  }

  .ruoyi-input, .ruoyi-select {
    width: 100%;
    margin-right: 0;
  }
}
</style>