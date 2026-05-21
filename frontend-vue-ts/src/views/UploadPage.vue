<template>
  <div class="container-fluid py-4">
    <div class="row justify-content-center">
      <div class="col-lg-8 col-xl-6">
        <!-- 文件上传组件 -->
        <FileUpload />

        <!-- 帮助信息 -->
        <div class="card mt-4">
          <div class="card-body">
            <h6 class="card-title">上传指南</h6>
            <ul class="list-unstyled small">
              <li><i class="bi bi-check-circle text-success me-2"></i>支持格式: PDF</li>
              <li><i class="bi bi-check-circle text-success me-2"></i>文件将自动以"用户名_时间戳_文件名"格式保存</li>
              <li><i class="bi bi-check-circle text-success me-2"></i>上传后系统可以自动生成项目</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import FileUpload from '@/layouts/upload/FileUpload.vue'
</script>

<style scoped>
@import url('@/assets/css/upload-page.css');
</style>
