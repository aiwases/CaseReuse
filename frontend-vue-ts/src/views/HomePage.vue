<template>
  <main class="main-content">
    <!-- 英雄区域 -->
    <section class="hero-section bg-gradient-primary">
      <div class="container py-5">
        <div class="row align-items-center min-vh-60">
          <div class="col-lg-6 hero-content">
            <h1 class="display-6 fw-bold text-white mb-4">基于证券规则的测试用例生成工具</h1>

            <!-- 用户登录状态 -->
            <div v-if="userStore.isLoggedIn" class="user-welcome animate-slide-in">
              <div class="d-flex align-items-center mb-4">
                <span class="badge bg-light text-primary me-3">已登录</span>
                <span class="text-light">欢迎，{{ userStore.username }}！</span>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="hero-actions">
              <div v-if="userStore.isLoggedIn">
                <router-link to="/create-project" class="btn btn-light btn-lg rounded-pill me-3 px-4">
                  <i class="fas fa-plus-circle me-2"></i>创建项目
                </router-link>
                <router-link to="/projects" class="btn btn-outline-light btn-lg rounded-pill px-4">
                  <i class="fas fa-list me-2"></i>项目列表
                </router-link>
              </div>
              <div v-else>
                <router-link to="/login" class="btn btn-light btn-lg rounded-pill me-3 px-4">
                  <i class="fas fa-sign-in-alt me-2"></i>登录系统
                </router-link>
                <router-link to="/register" class="btn btn-outline-light btn-lg rounded-pill px-4">
                  <i class="fas fa-user-plus me-2"></i>注册账号
                </router-link>
              </div>
            </div>
          </div>

          <div class="col-lg-6 hero-visual">
            <div class="hero-graphic">
              <div class="graphic-container">
                <div class="graphic-item graphic-item-1">
                  <i class="fas fa-file-alt fa-3x"></i>
                </div>
                <div class="graphic-item graphic-item-2">
                  <i class="fas fa-cog fa-3x"></i>
                </div>
                <div class="graphic-item graphic-item-3">
                  <i class="fas fa-chart-line fa-3x"></i>
                </div>
                <div class="graphic-animation"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

  </main>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserStore } from '@/store/userStore'

// 用户状态管理
const userStore = useUserStore()
</script>

<style scoped>
/* 主内容区域 */
.main-content {
  min-height: 100vh;
  overflow-x: hidden;
}

/* 英雄区域 */
.hero-section {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="%23ffffff" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="%23ffffff" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="%23ffffff" opacity="0.1"/><circle cx="90" cy="40" r="0.5" fill="%23ffffff" opacity="0.1"/><circle cx="10" cy="85" r="0.5" fill="%23ffffff" opacity="0.1"/></pattern></defs><rect width="100%" height="100%" fill="url(%23grain)"/></svg>');
  pointer-events: none;
}

.hero-content {
  animation: slideInLeft 1s ease-out;
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.user-welcome {
  animation: fadeInUp 0.8s ease-out 0.5s both;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-actions {
  animation: fadeInUp 0.8s ease-out 0.8s both;
}

/* 英雄视觉效果 */
.hero-visual {
  animation: slideInRight 1s ease-out;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.hero-graphic {
  position: relative;
}

.graphic-container {
  position: relative;
  width: 300px;
  height: 300px;
  margin: 0 auto;
}

.graphic-item {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.graphic-item-1 {
  width: 100px;
  height: 100px;
  top: 20px;
  left: 20px;
  animation: float 6s ease-in-out infinite;
}

.graphic-item-2 {
  width: 80px;
  height: 80px;
  top: 120px;
  right: 20px;
  animation: float 8s ease-in-out infinite reverse;
}

.graphic-item-3 {
  width: 90px;
  height: 90px;
  bottom: 20px;
  left: 90px;
  animation: float 10s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

.graphic-item:hover {
  transform: scale(1.1);
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}

.graphic-animation {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
  height: 200px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  from {
    transform: translate(-50%, -50%) rotate(0deg);
  }
  to {
    transform: translate(-50%, -50%) rotate(360deg);
  }
}

/* 特性部分 */
.features-section {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.feature-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border-radius: 16px;
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1) !important;
}

.feature-icon {
  color: #667eea;
  animation: pulse 3s ease-in-out infinite;
}

/* 功能展示部分 */
.functions-section {
  background: white;
  color: #1a202c;
}

.function-item {
  animation: slideUp 0.6s ease-out forwards;
  opacity: 0;
}

.function-item:nth-child(1) {
  animation-delay: 0.2s;
}

.function-item:nth-child(2) {
  animation-delay: 0.4s;
}

.function-item:nth-child(3) {
  animation-delay: 0.6s;
}

@keyframes slideUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
  from {
    opacity: 0;
    transform: translateY(20px);
  }
}

.function-icon {
  color: #667eea;
  padding: 12px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 12px;
  min-width: 60px;
  text-align: center;
}

/* 视觉展示 */
.visual-container {
  animation: fadeInScale 1s ease-out 0.8s both;
}

@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.visual-window {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.window-header {
  background: #f8fafc;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
}

.window-controls {
  display: flex;
  gap: 6px;
  margin-right: 12px;
}

.control {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: block;
}

.control-close {
  background: #ff5f56;
}

.control-minimize {
  background: #ffbd2e;
}

.control-maximize {
  background: #27ca3f;
}

.window-title {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.window-content {
  padding: 20px;
}

.content-line {
  height: 4px;
  background: linear-gradient(90deg, #f1f5f9 0%, #e2e8f0 50%, #f1f5f9 100%);
  border-radius: 2px;
  margin-bottom: 8px;
}

.content-table {
  margin-top: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.table-row {
  display: flex;
  border-bottom: 1px solid #f1f5f9;
}

.table-row:last-child {
  border-bottom: none;
}

.table-cell {
  flex: 1;
  height: 20px;
  background: linear-gradient(90deg, #f8fafc 0%, #e2e8f0 50%, #f8fafc 100%);
  border-right: 1px solid #f1f5f9;
}

.table-cell:last-child {
  border-right: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .min-vh-60 {
    min-height: 80vh;
  }

  .hero-section .display-6 {
    font-size: 2rem;
  }

  .hero-content .lead {
    font-size: 1.1rem;
  }

  .hero-actions .btn {
    font-size: 0.9rem;
    padding: 0.5rem 1.5rem;
  }

  .graphic-container {
    width: 250px;
    height: 250px;
  }

  .functions-section .row {
    text-align: center;
  }

  .function-item {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .function-icon {
    margin-bottom: 1rem;
    margin-right: 0;
  }
}

/* 工具类 */
.bg-gradient-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.min-vh-60 {
  min-height: 80vh;
}

.animate-slide-in {
  animation: slideInLeft 1s ease-out;
}

.w-50 {
  width: 50% !important;
}

.w-75 {
  width: 75% !important;
}
</style>
