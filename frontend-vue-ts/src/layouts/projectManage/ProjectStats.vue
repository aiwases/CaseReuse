<template>
  <div class="ruoyi-stats-container">
    <el-row :gutter="16">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="ruoyi-stat-card total">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">总项目数</div>
              <div class="stat-value">{{ stats.total || 0 }}</div>
            </div>
            <div class="stat-icon">
              <el-icon><Folder /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="ruoyi-stat-card completed">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">已完成</div>
              <div class="stat-value">{{ stats.completed || 0 }}</div>
            </div>
            <div class="stat-icon">
              <el-icon><CircleCheck /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="ruoyi-stat-card running">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">运行中</div>
              <div class="stat-value">{{ stats.running || 0 }}</div>
            </div>
            <div class="stat-icon">
              <el-icon><VideoPlay /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="ruoyi-stat-card ready">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">待启动</div>
              <div class="stat-value">{{ stats.ready || 0 }}</div>
            </div>
            <div class="stat-icon">
              <el-icon><Document /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { Folder, CircleCheck, VideoPlay, Document } from '@element-plus/icons-vue'

// Props
const props = defineProps<{
  stats: {
    total: number
    completed: number
    running: number
    ready: number
  }
}>()
</script>

<style scoped>
/* 统计卡片样式 */
.ruoyi-stats-container {
  width: 100%;
  box-sizing: border-box;
}

.ruoyi-stat-card {
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border-left: 4px solid #409eff;
}

.ruoyi-stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.ruoyi-stat-card.total {
  border-left-color: #409eff;
}

.ruoyi-stat-card.completed {
  border-left-color: #67c23a;
}

.ruoyi-stat-card.running {
  border-left-color: #e6a23c;
}

.ruoyi-stat-card.ready {
  border-left-color: #f56c6c;
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.stat-icon {
  font-size: 32px;
  color: #409eff;
}

.ruoyi-stat-card.completed .stat-icon {
  color: #67c23a;
}

.ruoyi-stat-card.running .stat-icon {
  color: #e6a23c;
}

.ruoyi-stat-card.ready .stat-icon {
  color: #f56c6c;
}

/* 响应式样式 */
@media (max-width: 768px) {
  .ruoyi-stats-container .el-col {
    margin-bottom: 15px;
  }
}
</style>