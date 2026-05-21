<template>
  <div class="scenario-case-alignment-graph">
    <div class="graph-header">
      <h3>场景-测试用例对齐关系图</h3>
    </div>
    <div class="graph-content" v-loading="loading">
      <div v-if="error" class="error-message">
        <el-alert type="error" :title="error" show-icon />
      </div>
      <div v-else-if="!alignmentData" class="empty-message">
        <el-empty description="暂无对齐数据" />
      </div>
      <div v-else class="chart-with-legend">
        <div class="chart-container">
          <div ref="chartRef" class="echarts-chart" :style="{ height: chartHeight + 'px' }"></div>
        </div>
        <div class="fixed-legend">
          <h4>图例</h4>
          <ul>
            <li>
              <span class="legend-color rule"></span>
              <span>规则</span>
            </li>
            <li>
              <span class="legend-color requirement"></span>
              <span>需求</span>
            </li>
            <li>
              <span class="legend-color scenario"></span>
              <span>场景</span>
            </li>
            <li>
              <span class="legend-color test-case"></span>
              <span>测试用例</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useReuseStore } from '@/store/reuseStore'
import { resolveReuseResultErrorMessage } from '@/types/reuseResultError'
import * as echarts from 'echarts'

const route = useRoute()
const projectId = computed(() => route.params.id as string)
const reuseStore = useReuseStore()
const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null
const chartHeight = ref<number>(700) // 画布高度，默认700px

// 计算属性：加载状态
const loading = ref(false)

// 计算属性：错误信息
const error = ref<string | null>(null)

// 计算属性：对齐数据
const alignmentData = computed(() => {
  return reuseStore.getScenarioCaseAlignments
})

const isMissingResultError = (err: any): boolean => {
  const status = err?.response?.status
  const rawMessage = err?.response?.data?.error || err?.response?.data?.msg || err?.response?.data?.message || err?.message || ''
  const message = String(rawMessage).toLowerCase()
  return (
    status === 404 ||
    message.includes('file not found') ||
    message.includes('not found') ||
    message.includes('no such file') ||
    message.includes('文件不存在') ||
    message.includes('文件缺失')
  )
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return
  
  // 确保容器有正确的尺寸
  const container = chartRef.value
  if (!container || container.offsetWidth === 0 || container.offsetHeight === 0) {
    // 延迟初始化，确保容器已渲染
    setTimeout(initChart, 100)
    return
  }
  
  // 销毁已存在的图表实例
  if (chart) {
    chart.dispose()
  }
  
  // 初始化图表
  chart = echarts.init(container)
  
  // 强制同步尺寸，解决只有一小块区域能拖拽/缩放的问题
  chart.resize()
  
  // 输出图表和容器尺寸信息
  console.log('=== 图表尺寸信息 ===')
  console.log('chart.getWidth():', chart.getWidth())
  console.log('chart.getHeight():', chart.getHeight())
  
  const chartElement = document.querySelector('.echarts-chart')
  if (chartElement) {
    console.log('echarts-chart clientWidth:', chartElement.clientWidth)
    console.log('echarts-chart clientHeight:', chartElement.clientHeight)
  }
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
  
  // 添加ResizeObserver监听容器尺寸变化
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
  
  resizeObserver = new ResizeObserver(() => {
    chart?.resize()
  })
  
  resizeObserver.observe(container)
  
  // 更新图表数据
  updateChart()
}

// 更新图表数据
const updateChart = () => {
  if (!chart || !alignmentData.value) return
  
  try {
    const { nodes = [], links = [] } = alignmentData.value
    
    if (nodes.length === 0) {
      chart.setOption({ series: [] })
      return
    }
    
    // 处理节点数据
    const processedNodes = nodes.map(node => {
      if (!node) return null
      
      return {
        id: node.id || Math.random().toString(36).substr(2, 9),
        name: node.name || '未命名',
        category: node.category || (node.id?.includes('_') ? 'testcase' : 'rule'),
        // 关键：给大坐标范围，让 viewport 变成一个很大的区域
        x: (Math.random() - 0.5) * 10000,
        y: (Math.random() - 0.5) * 10000,
        symbolSize: 5,
        itemStyle: {
          color: node.id?.includes('_') ? '#f56c6c' : '#409eff'
        }
      }
    }).filter(Boolean) as any[]
    
    // 处理链接数据
    const processedLinks = links.map(link => {
      if (!link) return null
      return {
        source: link.source,
        target: link.target
      }
    }).filter(Boolean) as any[]
    
    // 图表配置
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          if (params.dataType === 'node') {
            const category = params.data.category || 'unknown'
            return `${params.data.name}<br/>类型: ${getCategoryName(category)}`
          } else {
            const sourceNode = processedNodes.find(node => node.id === params.data.source)
            const targetNode = processedNodes.find(node => node.id === params.data.target)
            const sourceName = sourceNode?.name || params.data.source
            const targetName = targetNode?.name || params.data.target
            return `关系: ${sourceName} → ${targetName}`
          }
        }
      },
      series: [
        {
          type: 'graph',
          layout: 'force',
          // 无限画布配置
          roam: true,
          draggable: true,
          focusNodeAdjacency: false,
          // 优化拖拽性能
          animation: true,
          animationDurationUpdate: 200,
          animationEasingUpdate: 'quinticInOut',
          data: processedNodes,
          links: processedLinks,
          label: {
            show: true,
            position: 'right',
            fontSize: 12
          },
          lineStyle: {
            color: '#409eff',
            curveness: 0.3,
            width: 2
          },
          edgeSymbol: ['none', 'arrow'],
          edgeSymbolSize: [4, 8],
          force: {
            repulsion: 2000,
            edgeLength: 150,
            gravity: 0.05,
            layoutAnimation: true
          }
        }
      ]
    }
    
    chart.setOption(option)
  } catch (error) {
    console.error('更新图表时出错:', error)
    chart.setOption({ series: [] })
  }
}

// 处理窗口大小变化
const handleResize = () => {
  chart?.resize()
}

// 获取分类名称
const getCategoryName = (category: string): string => {
  const normalizedCategory = category.toLowerCase().trim()
  
  const categoryMap: Record<string, string> = {
    'rule': '规则',
    'rules': '规则',
    'requirement': '需求',
    'requirements': '需求',
    'scenario': '场景',
    'scenarios': '场景',
    'test case': '测试用例',
    'test cases': '测试用例',
    'testcase': '测试用例',
    'testcases': '测试用例'
  }
  
  return categoryMap[normalizedCategory] || '未知'
}

// 组件挂载时初始化
onMounted(async () => {
  // 获取数据
  if (projectId.value) {
    loading.value = true
    error.value = null
    try {
      await reuseStore.fetchScenarioCaseAlignments(projectId.value)
    } catch (err: any) {
      console.error('获取对齐数据失败:', err)
      if (isMissingResultError(err)) {
        reuseStore.resetScenarioCaseAlignments()
        error.value = '场景-测试用例对齐关系图结果文件缺失'
      } else {
        error.value = resolveReuseResultErrorMessage(err, '场景-测试用例对齐关系图结果', '获取对齐数据失败')
      }
    } finally {
      loading.value = false
    }
  }
  
  // 初始化图表
  nextTick(() => {
    initChart()
  })
})

// 监听数据变化
watch(alignmentData, () => {
  updateChart()
}, { deep: true })

// 组件卸载时清理
onUnmounted(() => {
  // 清理事件监听器
  window.removeEventListener('resize', handleResize)
  
  // 清理ResizeObserver
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  
  // 清理图表实例
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.scenario-case-alignment-graph {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.graph-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  background-color: #f5f7fa;
}

.graph-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.graph-content {
  flex: 1;
  padding: 16px;
  overflow: hidden;
  background-color: #ffffff;
  min-height: 700px;
}

.error-message,
.empty-message {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-with-legend {
  display: flex;
  width: 100%;
  height: 100%;
  min-height: 600px;
  gap: 20px;
  overflow: hidden;
}

.chart-container {
  flex: 1;
  height: 100%;
  min-height: 700px;
  position: relative;
  overflow: hidden;
}

.echarts-chart {
  width: 100%;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background-color: #fafafa;
  position: relative;
  box-sizing: border-box;
}

.fixed-legend {
  width: 120px;
  padding: 16px;
  background-color: #f5f7fa;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  align-self: flex-start;
}

.fixed-legend h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.fixed-legend ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.fixed-legend li {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  color: #606266;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 8px;
}

.legend-color.rule {
  background-color: #409eff; /* 蓝色 - 规则 */
}

.legend-color.requirement {
  background-color: #67c23a; /* 绿色 - 需求 */
}

.legend-color.scenario {
  background-color: #e6a23c; /* 橙色 - 场景 */
}

.legend-color.test-case {
  background-color: #f56c6c; /* 红色 - 测试用例 */
}

/* 响应式设计 */
@media (max-width: 768px) {
  .graph-content {
    padding: 12px;
  }
  
  .chart-with-legend {
    flex-direction: column;
  }
  
  .fixed-legend {
    width: 100%;
    margin-top: 12px;
  }
  
  .fixed-legend ul {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .fixed-legend li {
    margin-bottom: 0;
  }
  
  .chart-container {
    min-height: 600px;
  }
  
  .graph-header h3 {
    font-size: 14px;
  }
}
</style>
