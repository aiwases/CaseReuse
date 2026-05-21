<template>
  <div class="app-container">
    <!-- 搜索和筛选栏 -->
    <ProjectSearchFilter 
      v-model:queryParams="queryParams"
      @query="handleQuery"
    />

    <!-- 统计卡片 -->
    <ProjectStats :stats="stats" />

    <!-- 项目表格 -->
    <ProjectTable 
      :loading="loading"
      :projects="projects"
      :total="total"
      v-model:queryParams="queryParams"
      @view="handleView"
      @edit="handleEdit"
      @delete="handleDelete"
      @selection-change="handleSelectionChange"
      @refresh="handleQuery"
    />

    <!-- 编辑项目信息模态框组件 -->
    <EditProjectModal 
      v-model:visible="editModalVisible" 
      :project-id="currentEditProject?.id" 
      :project-info="currentEditProject" 
      @success="handleEditSuccess" 
      @error="handleEditError" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useProjectStore } from '@/store/projectStore'
import { useSidebarStore } from '@/store/sidebarStore'
import { ElMessage } from 'element-plus'
import EditProjectModal from '@/components/EditProjectModal.vue'
import ProjectSearchFilter from '@/layouts/projectManage/ProjectSearchFilter.vue'
import ProjectStats from '@/layouts/projectManage/ProjectStats.vue'
import ProjectTable from '@/layouts/projectManage/ProjectTable.vue'

const router = useRouter()
const projectStore = useProjectStore()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const total = ref(0)
const selectedRows = ref([])
const fileId = ref<string | null>(null)

// 编辑项目相关
const editModalVisible = ref(false)
const currentEditProject = ref(null)

// 查询参数
const queryParams = ref({
  pageNum: 1,
  pageSize: 10,
  projectName: '',
  fileName: '',
  status: ''
})

// 计算属性
const projects = ref([])
const stats = ref({
  total: 0,
  completed: 0,
  running: 0,
  ready: 0
})

// 监听路由参数变化
watch(() => route.query.file_id, (newVal) => {
  if (newVal) {
    fileId.value = newVal as string
  } else {
    fileId.value = null
  }
  queryParams.value.pageNum = 1
  getProjectList()
})

// 获取项目列表
const getProjectList = async () => {
  loading.value = true
  try {
    // 构建搜索参数
    const searchKeyword = queryParams.value.projectName || queryParams.value.fileName
    const searchType = queryParams.value.projectName ? 'project' : queryParams.value.fileName ? 'file' : ''
    
    await projectStore.fetchProjects({
      page: queryParams.value.pageNum,
      perPage: queryParams.value.pageSize,
      sort: 'updated_desc',
      keyword: searchKeyword,
      searchType: searchType,
      status: queryParams.value.status,
      file_id: fileId.value
    })
    
    projects.value = projectStore.projects
    stats.value = projectStore.stats
    total.value = projectStore.pagination?.total || 0
  } catch (error) {
    console.error('获取项目列表失败', error)
  } finally {
    loading.value = false
  }
}

// 查询按钮操作
const handleQuery = () => {
  queryParams.value.pageNum = 1
  getProjectList()
}

// 选择项变化
const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

// 跳转到项目详情
  const handleView = (projectId) => {
    // 查找当前项目信息
    const project = projectStore.projects.find(item => item.id === projectId)
    const processType = String(project?.process_type || '').toLowerCase()
    const isReuseProject = processType === 'reuse' || processType.includes('重用')

    if (project) {
      // 添加项目到侧边栏
      const sidebarStore = useSidebarStore()
      sidebarStore.addProjectToSidebar({
        id: project.id,
        name: project.name,
        process_type: project.process_type
      })
    }
    
    router.push({
      name: isReuseProject ? 'ReuseDocumentDetail' : 'DocumentDetail',
      params: { id: projectId }
    })
  }

// 打开项目编辑模态框
const handleEdit = (projectId) => {
  // 查找当前项目信息
  const project = projectStore.projects.find(item => item.id === projectId)
  if (project) {
    currentEditProject.value = project
    editModalVisible.value = true
  }
}

// 编辑成功回调
const handleEditSuccess = () => {
  editModalVisible.value = false
  getProjectList()
}

// 编辑失败回调
const handleEditError = (error) => {
  console.error('编辑项目失败:', error)
}

// 删除项目
const handleDelete = async (projectId) => {
  try {
    await projectStore.deleteProject(projectId)
    ElMessage.success('删除成功')
    handleQuery()
  } catch (error) {
    ElMessage.error('删除失败')
    console.error('删除项目失败:', error)
  }
}

// 组件挂载时获取数据
onMounted(() => {
  if (route.query.file_id) {
    fileId.value = route.query.file_id as string
  }
  getProjectList()
})
</script>

<style scoped>
/* RuoYi 风格样式 */
.app-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 响应式样式 */
@media (max-width: 768px) {
  .app-container {
    padding: 10px;
  }
}
</style>
