<template>
  <div class="card shadow-sm mb-4">
    <div class="card-body">
      <h5 class="card-title">项目详情</h5>
      <p class="text-muted">{{ project.description || '暂无描述' }}</p>

      <div class="row mt-3">
        <div class="col-md-3 mb-2">
          <strong>当前状态：</strong>
          <span :class="getStatusBadgeClass(project.status)">
            {{ project.status }}
          </span>
        </div>
        <div class="col-md-3 mb-2">
          <strong>创建时间：</strong>
          {{ formatDate(project.created_at) }}
        </div>
        <div class="col-md-3 mb-2">
          <strong>更新时间：</strong>
          {{ formatDate(project.updated_at) }}
        </div>
        <div v-if="project.completed_at" class="col-md-3 mb-2">
          <strong>完成时间：</strong>
          {{ formatDate(project.completed_at) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

// Props
const props = defineProps({
  project: {
    type: Object,
    required: true
  }
})

// Methods
const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusBadgeClass = (status: string) => {
  const classes: Record<string, string> = {
    completed: 'badge bg-success',
    stage1: 'badge bg-info',
    stage2: 'badge bg-info',
    stage3: 'badge bg-info',
    ready: 'badge bg-primary',
    failed: 'badge bg-danger'
  }
  return classes[status] || 'badge bg-danger'
}
</script>

<style scoped>

</style>
