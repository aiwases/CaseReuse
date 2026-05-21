<template>
  <div class="form-actions-section">
    <el-form-item>
      <div class="form-actions">
        <el-button
          type="primary"
          :loading="store.isSubmitting"
          @click="handleSubmit"
          class="ruoyi-btn"
        >
          <el-icon v-if="!store.isSubmitting"><Check /></el-icon>
          <span v-if="store.isSubmitting">创建中...</span>
          <span v-else>创建项目</span>
        </el-button>
        <router-link to="/projects">
          <el-button class="ruoyi-btn">
            <el-icon><Close /></el-icon>
            取消
          </el-button>
        </router-link>
      </div>
    </el-form-item>
  </div>
</template>

<script setup lang="ts">
import { useCreatProjectStore } from '@/store/creatProjectStore';
import { RouterLink } from 'vue-router';
import { Check, Close } from '@element-plus/icons-vue';

// 获取store实例
const store = useCreatProjectStore();

// 处理表单提交
const handleSubmit = async () => {
  await store.submitProject();
};
</script>

<style scoped>
.form-actions-section {
  width: 100%;
}

.form-actions {
  margin-top: 30px;
  display: flex;
  gap: 10px;
  justify-content: center;
  width: 100%;
}

.ruoyi-btn {
  min-width: 80px;
  border-radius: 4px;
  font-size: 14px;
  padding: 8px 16px;
  margin-right: 10px;
}

@media (max-width: 768px) {
  .form-actions {
    flex-direction: column;
    align-items: center;
  }

  .form-actions .ruoyi-btn {
    width: 100%;
  }
}
</style>