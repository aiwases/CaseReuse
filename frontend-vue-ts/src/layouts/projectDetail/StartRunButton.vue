<template>
  <el-button 
    type="primary" 
    :loading="isRunning" 
    @click="startProject"
  >
    <el-icon><CirclePlus /></el-icon>
    开始运行
  </el-button>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { CirclePlus } from '@element-plus/icons-vue'
import { startReuseProjectApi } from '@/api/reuse'
import { startProjectApi } from '@/api/detail'

type ReusePageType = 'dependency-modeling' | 'effect-aware-reuse'
type DocumentType = 'old' | 'new'
type WorkflowType = 'generation' | 'reuse'

// 接收 projectId，以及两种启动方式：
// 1) 传 stage + pageType（兼容现有页面）
// 2) 直接传 task + documentType
const props = defineProps<{
  projectId: string | number
  workflow?: WorkflowType
  stage?: number
  pageType?: ReusePageType
  task?: number
  documentType?: DocumentType
}>()

const isRunning = ref(false)

const isReuseWorkflow = computed(() => {
  if (props.workflow) {
    return props.workflow === 'reuse'
  }

  // 传入重用流程参数时按重用模式处理，否则默认按生成流程处理
  return (
    typeof props.stage === 'number' ||
    !!props.pageType ||
    typeof props.task === 'number' ||
    !!props.documentType
  )
})

const getTaskFromStage = (
  stage: number | undefined,
  pageType: ReusePageType | undefined,
): { task?: number; documentType?: DocumentType } => {
  if (typeof stage !== 'number' || !pageType) {
    return {}
  }

  if (pageType === 'dependency-modeling') {
    if (stage === 0) return { task: 1, documentType: 'old' }
    if (stage === 1) return { task: 2, documentType: 'old' }
    if (stage === 2) return { task: 3 }
    return {}
  }

  if (stage === 0) return { task: 1, documentType: 'old' }
  if (stage === 1) return { task: 1, documentType: 'new' }
  if (stage === 2) return { task: 2, documentType: 'old' }
  if (stage === 3) return { task: 2, documentType: 'new' }
  if (stage === 4) return { task: 4 }
  if (stage === 5) return { task: 5 }
  if (stage === 6) return { task: 6 }
  return {}
}

// 开始运行项目
const startProject = async () => {
  isRunning.value = true
  try {
    let response

    if (isReuseWorkflow.value) {
      const mapped = getTaskFromStage(props.stage, props.pageType)
      const runAll = typeof props.stage !== 'number' || !props.pageType
      response = await startReuseProjectApi(props.projectId, {
        stage: props.stage,
        pageType: props.pageType,
        task: props.task ?? mapped.task,
        documentType: props.documentType ?? mapped.documentType,
        runAll,
      })
    } else {
      response = await startProjectApi(props.projectId)
    }

    ElMessage.success(response.data.message || '任务已启动，后台处理中...')
  } catch (error: any) {
    const errorMessage = error.response?.data?.message || '启动任务失败，请稍后重试'
    ElMessage.error(errorMessage)
  } finally {
    isRunning.value = false
  }
}
</script>

<style scoped>
/* 可以添加组件特定的样式 */
</style>