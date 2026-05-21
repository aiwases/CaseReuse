<template>
  <div class="app-container">
    <!-- 创建项目表单 -->
    <el-card class="ruoyi-card" shadow="never">
      <template #header>
        <div class="card-header">
          <h3 class="card-title">
            <el-icon><Plus /></el-icon>
            创建新项目
          </h3>
        </div>
      </template>

      <el-form @submit.prevent="handleSubmit" label-width="100px" class="ruoyi-form">
        <!-- 项目信息部分 -->
        <ProjectInfoSection />
        
        <!-- 文件上传部分 -->
        <FileUploadSection />
        
        <!-- 表单操作部分 -->
        <FormActions />
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useCreatProjectStore } from "@/store/creatProjectStore";
import { Plus } from "@element-plus/icons-vue";
import ProjectInfoSection from '@/layouts/creatProject/ProjectInfoSection.vue';
import FileUploadSection from '@/layouts/creatProject/FileUploadSection.vue';
import FormActions from '@/layouts/creatProject/FormActions.vue';

const route = useRoute();
const store = useCreatProjectStore();

// ------------------- 检查是否从文件库跳转 -------------------
onMounted(() => {
  const fileIdFromQuery = route.query.file_id as string;
  if (fileIdFromQuery) {
    console.log("从文件库跳转创建项目，file_id =", fileIdFromQuery);
    store.loadFileRecord(fileIdFromQuery);
  }
});

// ------------------- 表单提交 -------------------
const handleSubmit = async () => {
  await store.submitProject();
};
</script>


<style scoped>
/* RuoYi 风格样式 */
.app-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

/* 容器和卡片 */
.breadcrumb-container,
.ruoyi-card {
  width: 100%;
}

.breadcrumb-container {
  margin-bottom: 20px;
}

.ruoyi-card {
  background-color: #fff;
  border-radius: 4px;
  border: 1px solid #ebeef5;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 500;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 表单样式 */
.ruoyi-form {
  padding: 20px 40px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  width: 100%;
  min-width: 0;
}

/* 响应式样式 */
@media (max-width: 768px) {
  .app-container {
    padding: 10px;
  }
  
  .ruoyi-form {
    padding: 20px;
  }
}
</style>
