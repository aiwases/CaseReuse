<template>
  <el-card class="ruoyi-card" shadow="never">
    <el-table
      v-loading="loading"
      :data="projects"
      border
      stripe
      style="width: 100%"
      @selection-change="handleSelectionChange"
      class="ruoyi-table"
    >
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column prop="name" label="项目名称" min-width="180" show-overflow-tooltip />
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip>
        <template #default="scope">
          {{ scope.row.description || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="user.name" label="创建人" width="120" align="center" />
      <el-table-column label="文件类型" width="120" align="center">
        <template #default="scope">
          <el-tag size="small" type="info">
            {{ scope.row.file_record ? scope.row.file_record.file_type.toUpperCase() : '未知' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="项目类型" width="140" align="center">
        <template #default="scope">
          <el-tag size="small" type="success">
            {{ getProjectTypeText(scope.row.process_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="120" align="center">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)" size="small">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" align="center">
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="updated_at" label="更新时间" width="180" align="center">
        <template #default="scope">
          {{ formatDate(scope.row.updated_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240" align="center" fixed="right">
        <template #default="scope">
          <div style="display: flex; justify-content: center; gap: 5px;">
            <el-button
              type="primary"
              size="small"
              @click="handleView(scope.row.id)"
              :icon="View"
              class="ruoyi-btn"
            >
              查看
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="handleEdit(scope.row.id)"
              :icon="Edit"
              class="ruoyi-btn"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(scope.row.id)"
              :icon="Delete"
              class="ruoyi-btn"
            >
              删除
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="ruoyi-pagination-container">
      <el-pagination
        v-show="total > 0"
        :total="total"
        :current-page="queryParams.pageNum"
        :page-size="queryParams.pageSize"
        :page-sizes="[10, 20, 30, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { View, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Props
const props = defineProps<{
  loading: boolean
  projects: any[]
  total: number
  queryParams: {
    pageNum: number
    pageSize: number
  }
}>()

// Emits
const emit = defineEmits<{
  (e: 'update:queryParams', value: any): void
  (e: 'view', projectId: number): void
  (e: 'edit', projectId: number): void
  (e: 'delete', projectId: number): void
  (e: 'selection-change', selection: any[]): void
  (e: 'refresh'): void
}>()

// 选择项变化
const handleSelectionChange = (selection: any[]) => {
  emit('selection-change', selection)
}

// 分页大小改变
const handleSizeChange = (val: number) => {
  const newParams = { ...props.queryParams, pageSize: val, pageNum: 1 }
  emit('update:queryParams', newParams)
}

// 当前页码改变
const handleCurrentChange = (val: number) => {
  const newParams = { ...props.queryParams, pageNum: val }
  emit('update:queryParams', newParams)
}

// 跳转到项目详情
const handleView = (projectId: number) => {
  emit('view', projectId)
}

// 打开项目编辑模态框
const handleEdit = (projectId: number) => {
  emit('edit', projectId)
}

// 删除项目
const handleDelete = (projectId: number) => {
  ElMessageBox.confirm(
    '此操作将永久删除该项目，是否继续？',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    emit('delete', projectId)
  }).catch(() => {
    // 取消删除操作
  })
}

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap = {
    'completed': 'success',
    'running': 'info',
    'stage1': 'info',
    'stage2': 'info',
    'stage3': 'info',
    'ready': 'primary',
    'failed': 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap = {
    'completed': '已完成',
    'running': '运行中',
    'stage1': '运行中',
    'stage2': '运行中',
    'stage3': '运行中',
    'ready': '就绪',
    'failed': '失败'
  }
  return textMap[status] || status
}

// 获取项目类型文本
const getProjectTypeText = (type: string) => {
  const textMap = {
    'generation': '测试用例生成',
    'reuse': '测试用例重用'
  }
  return textMap[type] || type
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
/* 表格样式 */
.ruoyi-table {
  border-radius: 4px;
}

.ruoyi-table th {
  background-color: #f5f7fa;
  font-weight: 500;
  color: #303133;
  border-bottom: 1px solid #e4e7ed;
}

.ruoyi-table td {
  border-bottom: 1px solid #ebeef5;
  color: #606266;
}

.ruoyi-table tr:hover {
  background-color: #f5f7fa;
}

/* 按钮样式 */
.ruoyi-btn {
  margin-right: 5px;
  border-radius: 4px;
}

/* 分页样式 */
.ruoyi-pagination-container {
  padding: 15px 0;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.ruoyi-pagination-container .el-pagination {
  margin: 0;
}

/* 响应式样式 */
@media (max-width: 768px) {
  .ruoyi-pagination-container {
    justify-content: center;
  }
}
</style>