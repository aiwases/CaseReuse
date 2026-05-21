<template>
  <div class="topbar-container">
    <div class="topbar-left">
      <div class="breadcrumb-container">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item>{{ currentBreadcrumb }}</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
    </div>
    <div class="topbar-right">
      <div class="topbar-item user-info">
        <span class="user-name">{{ userName }}</span>
        <el-dropdown>
          <span class="dropdown-trigger">▼</span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>个人中心</el-dropdown-item>
              <el-dropdown-item>系统设置</el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/userStore'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 当前面包屑
const currentBreadcrumb = computed(() => {
    const routeName = route.name || ''
    const breadcrumbMap = {
      'home': '首页',
      'upload': '文件上传',
      'file-manage': '文件管理',
      'create-project': '创建项目',
      'ProjectManage': '项目列表',
      'ProjectDetail': '项目详情',
      'ProjectEditor': '项目编辑器',
      'ReuseDocumentDetail': '文档详情',
      'IndependentRequirementGeneration': 'Independent Requirement Generation',
      'TestScenarioSynthesis': 'Test Scenario Synthesis',
      'ScenarioCaseAlignment': 'Scenario-Test Case Alignment',
      'RegulatoryChangeIdentification': 'Regulatory Change Identification',
      'CascadingImpactScopeAnalysis': 'Cascading Impact Scope Analysis',
      'TestSuiteReuseUpdate': 'Test Suite Reuse and Update',
      'CascadingDependencyModeling': 'Cascading Dependency Modeling'
    }
    return breadcrumbMap[routeName] || routeName
  })

// 用户信息
const userName = ref('管理员')

// 退出登录
const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
/* 顶部导航栏 */
.topbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  padding: 0 24px;
  background-color: #fff;
  border-bottom: 1px solid #e8e8e8;
}

/* 顶部左侧 */
.topbar-left {
  flex: 1;
}

/* 面包屑 */
.breadcrumb-container {
  display: flex;
  align-items: center;
}

/* 顶部右侧 */
.topbar-right {
  display: flex;
  align-items: center;
}

.topbar-item {
  display: flex;
  align-items: center;
  margin-left: 32px;
  cursor: pointer;
  transition: color 0.3s ease;
}

.topbar-item:hover {
  color: #1890ff;
}

/* 用户信息 */
.user-info {
  display: flex;
  align-items: center;
}

.user-name {
  margin-left: 8px;
  font-size: 14px;
}

.dropdown-trigger {
  margin-left: 4px;
  font-size: 12px;
}
</style>