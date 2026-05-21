<template>
  <div class="sidebar-container" :class="{ 'sidebar-folded': isFolded }" :style="{ width: !isFolded ? sidebarWidth + 'px' : '' }">
    <!-- 系统logo -->
    <div class="sidebar-logo">
      <div class="logo-box">
        <el-icon class="logo-icon"><component :is="ElementPlusIconsVue.Menu" /></el-icon>
        <span v-if="!isFolded" class="logo-text">基于证券规则的测试用例生成工具</span>
      </div>
      <!-- 折叠按钮 -->
      <div class="sidebar-toggle" @click="toggleSidebar">
        <el-icon :class="isFolded ? 'icon-unfold' : 'icon-fold'">
          <component :is="ElementPlusIconsVue.ArrowRight" v-if="isFolded" />
          <component :is="ElementPlusIconsVue.ArrowLeft" v-else />
        </el-icon>
      </div>
    </div>
    
    <!-- 侧边栏菜单 -->
    <div class="sidebar-menu">
      <div class="menu-list">
        <!-- 首页 -->
        <div class="menu-item" :class="{ 'menu-active': currentRoute === 'home' }">
          <router-link to="/" class="menu-link">
            <el-icon class="menu-icon"><component :is="ElementPlusIconsVue.House" /></el-icon>
            <span v-if="!isFolded" class="menu-text">首页</span>
          </router-link>
        </div>
        
        <!-- 文件管理 (隐藏) -->
        <div v-if="false" class="menu-item menu-group" :class="{ 'menu-open': sidebarStore.openMenus.includes('file') }">
          <div class="menu-link menu-group-title" @click="toggleMenu('file')">
            <el-icon class="menu-icon"><component :is="ElementPlusIconsVue.Document" /></el-icon>
            <span v-if="!isFolded" class="menu-text">文件管理</span>
            <el-icon class="menu-arrow" :class="{ 'arrow-open': sidebarStore.openMenus.includes('file') }">
                <component :is="ElementPlusIconsVue.CaretBottom" v-if="sidebarStore.openMenus.includes('file')" />
                <component :is="ElementPlusIconsVue.CaretRight" v-else />
              </el-icon>
          </div>
          <div class="submenu-list" v-if="sidebarStore.openMenus.includes('file')">
            <div class="submenu-item" :class="{ 'menu-active': currentRoute === 'upload' }">
              <router-link to="/upload" class="submenu-link">
                <el-icon class="submenu-icon"><component :is="ElementPlusIconsVue.Upload" /></el-icon>
                <span v-if="!isFolded" class="submenu-text">文件上传</span>
              </router-link>
            </div>
            <div class="submenu-item" :class="{ 'menu-active': currentRoute === 'file-manage' }">
              <router-link to="/file-manage" class="submenu-link">
                <el-icon class="submenu-icon"><component :is="ElementPlusIconsVue.FolderOpened" /></el-icon>
                <span v-if="!isFolded" class="submenu-text">文件管理</span>
              </router-link>
            </div>
          </div>
        </div>
        
        <!-- 项目管理 -->
        <div class="menu-item menu-group" :class="{ 'menu-open': sidebarStore.openMenus.includes('project') }">
          <div class="menu-link menu-group-title" @click="toggleMenu('project')">
            <el-icon class="menu-icon"><component :is="ElementPlusIconsVue.Folder" /></el-icon>
            <span v-if="!isFolded" class="menu-text">项目管理</span>
            <el-icon class="menu-arrow" :class="{ 'arrow-open': sidebarStore.openMenus.includes('project') }">
                <component :is="ElementPlusIconsVue.CaretBottom" v-if="sidebarStore.openMenus.includes('project')" />
                <component :is="ElementPlusIconsVue.CaretRight" v-else />
              </el-icon>
          </div>
          <div class="submenu-list" v-if="sidebarStore.openMenus.includes('project')">
            <div class="submenu-item" :class="{ 'menu-active': currentRoute === 'create-project' }">
              <router-link to="/create-project" class="submenu-link">
                <el-icon class="submenu-icon"><component :is="ElementPlusIconsVue.Plus" /></el-icon>
                <span v-if="!isFolded" class="submenu-text">创建项目</span>
              </router-link>
            </div>
            <div class="submenu-item" :class="{ 'menu-active': currentRoute === 'ProjectManage' }">
              <router-link to="/projects" class="submenu-link">
                <el-icon class="submenu-icon"><component :is="ElementPlusIconsVue.List" /></el-icon>
                <span v-if="!isFolded" class="submenu-text">项目列表</span>
              </router-link>
            </div>
          </div>
        </div>

        <!-- 动态项目菜单 -->
        <div v-for="project in sidebarStore.activeProjects" :key="project.id" 
             class="menu-item menu-group" 
             :class="{ 'menu-open': sidebarStore.openMenus.includes(`project-${project.id}`) }">
          <div class="menu-link menu-group-title">
            <div class="project-link" @click="toggleMenu(`project-${project.id}`)">
              <el-icon class="menu-icon"><component :is="ElementPlusIconsVue.FolderOpened" /></el-icon>
              <span v-if="!isFolded" class="menu-text">{{ project.name }}</span>
            </div>
            <div class="menu-actions">
              <div class="project-actions">
                <div 
                  class="delete-btn" 
                  title="删除项目" 
                  @click.stop="deleteProject(project.id)"
                >
                  <el-icon class="delete-icon"><component :is="ElementPlusIconsVue.Delete" /></el-icon>
                </div>
              </div>
              <el-icon class="menu-arrow" :class="{ 'arrow-open': sidebarStore.openMenus.includes(`project-${project.id}`) }">
                <component :is="ElementPlusIconsVue.CaretBottom" v-if="sidebarStore.openMenus.includes(`project-${project.id}`)" />
                <component :is="ElementPlusIconsVue.CaretRight" v-else />
              </el-icon>
            </div>
          </div>
          <div class="submenu-list" v-if="sidebarStore.openMenus.includes(`project-${project.id}`)">
            <div v-for="child in project.children" :key="child.name">
              <!-- 处理嵌套子菜单 -->
              <div v-if="child.children" 
                   class="submenu-item menu-group" 
                   :class="{ 'menu-open': sidebarStore.openMenus.includes(`${project.id}-${child.name}`) }">
                <div class="submenu-link menu-group-title" @click="toggleMenu(`${project.id}-${child.name}`)">
                  <el-icon class="submenu-icon"><component :is="getMenuIcon(child.name)" /></el-icon>
                  <span v-if="!isFolded" class="submenu-text">{{ child.label }}</span>
                  <el-icon class="menu-arrow" :class="{ 'arrow-open': sidebarStore.openMenus.includes(`${project.id}-${child.name}`) }">
                    <component :is="ElementPlusIconsVue.CaretBottom" v-if="sidebarStore.openMenus.includes(`${project.id}-${child.name}`)" />
                    <component :is="ElementPlusIconsVue.CaretRight" v-else />
                  </el-icon>
                </div>
                <div class="submenu-list" v-if="sidebarStore.openMenus.includes(`${project.id}-${child.name}`)">
                  <div v-for="grandchild in child.children" :key="grandchild.name"
                       class="submenu-item" 
                       :class="{ 'menu-active': route.path === grandchild.path }">
                    <router-link :to="grandchild.path" class="submenu-link">
                      <el-icon class="submenu-icon"><component :is="getMenuIcon(grandchild.name)" /></el-icon>
                      <span v-if="!isFolded" class="submenu-text">{{ grandchild.label }}</span>
                    </router-link>
                  </div>
                </div>
              </div>
              <!-- 处理普通子菜单 -->
              <div v-else 
                   class="submenu-item" 
                   :class="{ 'menu-active': route.path === child.path }">
                <router-link :to="child.path" class="submenu-link">
                  <el-icon class="submenu-icon"><component :is="getMenuIcon(child.name)" /></el-icon>
                  <span v-if="!isFolded" class="submenu-text">{{ child.label }}</span>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- 可调整大小的拖拽手柄 -->
    <div 
      v-if="!isFolded" 
      class="sidebar-resize-handle"
      @mousedown="startResize"
    ></div>
  </div>
</template>

<script setup>
import { computed, defineProps, defineEmits, ref, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { useSidebarStore } from '@/store/sidebarStore';
import * as ElementPlusIconsVue from '@element-plus/icons-vue';

const route = useRoute();
const sidebarStore = useSidebarStore();

// Props
const props = defineProps({
  isFolded: Boolean
});

// Emits
const emit = defineEmits(['toggleSidebar', 'resize']);

// 侧边栏宽度
const sidebarWidth = ref(220);
const minWidth = 200;
const maxWidth = 400;

// 拖拽状态
const isResizing = ref(false);

// 当前路由
const currentRoute = computed(() => {
  return route.name || 'home';
});

// 当前项目ID
const currentProjectId = computed(() => {
  return route.params.id;
});

// 切换侧边栏折叠状态
const toggleSidebar = () => {
  emit('toggleSidebar');
};

// 切换菜单展开/收起
const toggleMenu = (menuName) => {
  sidebarStore.toggleMenu(menuName);
};

// 获取菜单图标
const getMenuIcon = (menuName) => {
  const iconMap = {
    'slice-filter': ElementPlusIconsVue.Filter,
    'annotation': ElementPlusIconsVue.Edit,
    'rule-synthesis': ElementPlusIconsVue.CodeBox,
    'case-generation': ElementPlusIconsVue.FileText,
    'document-detail': ElementPlusIconsVue.DocumentIcon,
    'independent-requirement-generation': ElementPlusIconsVue.Document,
    'test-scenario-synthesis': ElementPlusIconsVue.DataAnalysis,
    'scenario-case-alignment': ElementPlusIconsVue.Match, 
    'regulatory-change-identification': ElementPlusIconsVue.Notification, 
    'cascading-impact-scope-analysis': ElementPlusIconsVue.Tree,
    'test-suite-reuse-update': ElementPlusIconsVue.RefreshRight,
    'cascading-dependency-modeling': ElementPlusIconsVue.Link,
    'individual-steps': ElementPlusIconsVue.List,
  };
  return iconMap[menuName] || ElementPlusIconsVue.Folder;
};

// 删除项目
const deleteProject = (projectId) => {
  sidebarStore.removeProjectFromSidebar(projectId);
};

// 开始调整大小
const startResize = (e) => {
  isResizing.value = true;
  e.preventDefault();
  e.stopPropagation();
  
  // 添加全局事件监听
  document.addEventListener('mousemove', handleResize);
  document.addEventListener('mouseup', stopResize);
  
  // 添加body类名，优化用户体验
  document.body.classList.add('resize-active');
};

// 处理调整大小
const handleResize = (e) => {
  if (!isResizing.value || props.isFolded) return;
  
  // 计算新宽度
  const containerRect = document.querySelector('.app-container').getBoundingClientRect();
  const newWidth = e.clientX - containerRect.left;
  
  // 限制最小和最大宽度
  if (newWidth >= minWidth && newWidth <= maxWidth) {
    sidebarWidth.value = newWidth;
    emit('resize', newWidth);
  }
};

// 停止调整大小
const stopResize = () => {
  isResizing.value = false;
  
  // 移除全局事件监听
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
  
  // 移除body类名
  document.body.classList.remove('resize-active');
};

// 组件卸载时移除事件监听
onUnmounted(() => {
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
});
</script>

<style scoped>
/* 侧边栏容器 */
.sidebar-container {
  min-width: 70px;
  height: 100%;
  background-color: #001529;
  color: #fff;
  transition: width 0.3s ease;
  overflow: hidden;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  position: relative;
}

/* 侧边栏折叠状态 */
.sidebar-container.sidebar-folded {
  width: 8px;
}

/* 可调整大小的拖拽手柄 */
.sidebar-resize-handle {
  position: absolute;
  right: 0;
  top: 0;
  width: 4px;
  height: 100%;
  background-color: transparent;
  cursor: col-resize;
  transition: background-color 0.3s ease;
}

.sidebar-resize-handle:hover {
  background-color: #1890ff;
}

/* 调整大小时的光标样式 */
.sidebar-container .sidebar-resize-handle:active {
  cursor: col-resize;
}

/* 全局光标样式 */
body.resize-active {
  cursor: col-resize;
  user-select: none;
}

/* 侧边栏logo */
.sidebar-logo {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 12px;
  height: 64px;
  border-bottom: 1px solid #1f2d3d;
}

.logo-box {
  display: flex;
  align-items: center;
}

.logo-icon {
  font-size: 24px;
  color: #1890ff;
  margin-right: 8px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
}

/* 折叠按钮 */
.sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.sidebar-toggle:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar-toggle .el-icon {
  font-size: 18px;
  transition: transform 0.3s ease;
}

/* 侧边栏菜单 */
.sidebar-menu {
  height: calc(100% - 64px);
  overflow-y: auto;
}

.menu-list {
  padding: 8px 0;
}

/* 菜单项 */
.menu-item {
  margin-bottom: 4px;
}

.menu-link {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  color: #ffffff;
  cursor: pointer;
  transition: background-color 0.3s ease;
  text-decoration: none;
  justify-content: flex-start;
}

.menu-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.menu-item.menu-active .menu-link {
  background-color: rgba(24, 144, 255, 0.2);
  border-right: 3px solid #1890ff;
}

.menu-icon {
  font-size: 18px;
  margin-right: 8px;
  width: 20px;
  text-align: center;
}

.menu-text {
  font-size: 14px;
}

/* 菜单组 */
.menu-group-title {
  position: relative;
  width: 100%;
  display: flex;
  justify-content: flex-start;
}

.menu-arrow {
  position: relative;
  margin-left: auto;
  transition: transform 0.3s ease;
}

.menu-arrow.arrow-open {
  transform: rotate(180deg);
}

/* 菜单操作区域 */
.menu-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

/* 项目操作按钮 */
.project-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 删除按钮 */
.delete-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #f56c6c;
}

.delete-btn:hover {
  background-color: rgba(245, 108, 108, 0.1);
  color: #f78989;
}

.delete-icon {
  font-size: 14px;
}

.project-link {
  display: flex;
  align-items: center;
  flex: 1;
  text-decoration: none;
  color: inherit;
  justify-content: flex-start;
}

.project-link:hover {
  text-decoration: none;
  color: inherit;
}

/* 子菜单 */
.submenu-list {
  padding-left: 16px;
  background-color: rgba(255, 255, 255, 0.05);
}

.submenu-item {
  margin-bottom: 2px;
}

.submenu-link {
  display: flex;
  align-items: center;
  padding: 8px 16px 8px 32px;
  color: #ffffff;
  cursor: pointer;
  transition: background-color 0.3s ease;
  text-decoration: none;
  font-size: 13px;
}

.submenu-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.submenu-item.menu-active .submenu-link {
  background-color: rgba(24, 144, 255, 0.2);
}

.submenu-icon {
  font-size: 16px;
  margin-right: 8px;
  width: 18px;
  text-align: center;
}

.submenu-text {
  font-size: 13px;
}
</style>