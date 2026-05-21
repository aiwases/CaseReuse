<template>
  <div class="app-container">
    <!-- 左侧侧边栏 -->
    <Sidebar 
      :isFolded="isSidebarFolded" 
      @toggleSidebar="toggleSidebar"
    />
    
    <!-- 主内容区域 -->
    <div class="main-container">
      <!-- 顶部导航栏 -->
      <Topbar />
      
      <!-- 内容区域 -->
      <div class="content-container">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/store/userStore';
import Sidebar from '@/components/Sidebar.vue';
import Topbar from '@/components/Topbar.vue';

const userStore = useUserStore();

// 侧边栏折叠状态
const isSidebarFolded = ref(false);

// 切换侧边栏折叠状态
const toggleSidebar = () => {
  isSidebarFolded.value = !isSidebarFolded.value;
};

onMounted(() => {
  // 初始化时可以从store获取用户信息
});
</script>

<style scoped>
/* 应用容器 */
.app-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* 主内容容器 */
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* 内容区域 */
.content-container {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background-color: #f0f2f5;
}
</style>