<template>
  <div class="trace-graph-container">
    <div class="trace-graph-header">
      <h3>规则追溯图</h3>
      <div class="trace-controls">
        <el-input
          v-model="ruleIdInput"
          placeholder="输入规则ID (如: 2.2.1)"
          size="small"
          style="width: 200px"
          @keyup.enter="handleTrace"
        />
        <el-button
          type="primary"
          size="small"
          :loading="traceStore.loading"
          @click="handleTrace"
        >
          追溯
        </el-button>
      </div>
    </div>
    
    <div v-if="traceStore.loading && !traceStore.graphData.nodes.length" class="loading-container">
      <el-empty description="加载中..." />
    </div>
    
    <div v-else-if="traceStore.error" class="error-container">
      <el-alert :title="traceStore.error" type="error" show-icon />
    </div>
    
    <div v-else-if="!traceStore.graphData.nodes.length" class="empty-container">
      <el-empty description="请输入规则ID进行追溯" />
    </div>
    
    <div v-else class="graph-wrapper">
      <div class="graph-stats">
        <el-tag size="small" type="primary">节点: {{ traceStore.nodeCount }}</el-tag>
        <el-tag size="small" type="success">边: {{ traceStore.linkCount }}</el-tag>
        <el-tag size="small" v-if="traceStore.currentRuleId">当前规则: {{ traceStore.currentRuleId }}</el-tag>
      </div>
      <div class="graph-container" ref="graphContainerRef"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import * as echarts from 'echarts';
import { useTraceStore } from '@/store/traceStore';

interface Props {
  projectId: number | string;
}

const props = defineProps<Props>();

const traceStore = useTraceStore();

const ruleIdInput = ref('');
const graphContainerRef = ref<HTMLDivElement>();
let chartInstance: echarts.ECharts | null = null;

const handleTrace = async () => {
  const ruleId = ruleIdInput.value.trim();
  if (!ruleId) {
    traceStore.clearError();
    traceStore.error = '请输入规则ID';
    return;
  }
  
  await traceStore.fetchTraceRule(props.projectId, ruleId);
};

const initChart = () => {
  if (!graphContainerRef.value) return false;
  
  if (chartInstance) {
    chartInstance.dispose();
  }
  
  try {
    chartInstance = echarts.init(graphContainerRef.value);
    return true;
  } catch (error) {
    console.error('初始化图表失败:', error);
    return false;
  }
};

const renderChart = () => {
  if (!traceStore.graphData.nodes.length) return;
  
  if (!chartInstance) {
    const success = initChart();
    if (!success || !chartInstance) return;
  }
  
  if (!graphContainerRef.value) return;
  
  const container = graphContainerRef.value;
  if (container.clientWidth === 0 || container.clientHeight === 0) {
    requestAnimationFrame(() => renderChart());
    return;
  }
  
  const nodes = traceStore.graphData.nodes.map(node => ({
    id: node.id,
    name: node.label,
    symbolSize: 45,
    itemStyle: {
      color: node.id === traceStore.currentRuleId ? '#f56c6c' : '#409EFF',
      borderColor: '#fff',
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: node.label,
      fontSize: 11,
      color: '#fff',
      fontWeight: 'bold'
    }
  }));
  
  const links = traceStore.graphData.links.map(link => ({
    source: link.source,
    target: link.target,
    lineStyle: {
      color: '#999',
      width: 2
    },
    symbol: ['none', 'arrow']
  }));
  
  const option: echarts.EChartsOption = {
    backgroundColor: '#ffffff',
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove',
      enterable: true,
      confine: true,
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          const node = traceStore.graphData.nodes.find(n => n.id === params.name);
          if (node?.text) {
            const text = node.text.replace(/\n/g, '<br/>');
            return `<div style="max-width: 300px; white-space: normal; word-break: break-word;">
              <div style="font-weight: bold; margin-bottom: 8px;">${params.name}</div>
              <div>${text}</div>
            </div>`;
          }
          return params.name;
        }
        return '';
      }
    },
    animationDurationUpdate: 1500,
    series: [{
      type: 'graph',
      layout: 'force',
      data: nodes,
      links: links,
      roam: true,
      focusNodeAdjacency: true,
      lineStyle: {
        color: '#999',
        curveness: 0.3,
        width: 2
      },
      edgeSymbol: ['none', 'arrow'],
      edgeSymbolSize: [4, 10],
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 4
        }
      },
      force: {
        repulsion: 1200,
        edgeLength: [80, 150],
        gravity: 0.1
      }
    }]
  };
  
  chartInstance.setOption(option, true);
};

const handleResize = () => {
  chartInstance?.resize();
};

watch(
  () => traceStore.graphData,
  () => {
    if (traceStore.graphData.nodes.length > 0) {
      nextTick(() => {
        renderChart();
      });
    }
  },
  { deep: true }
);

onMounted(() => {
  nextTick(() => {
    initChart();
  });
  
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
  
  traceStore.resetTraceGraph();
});
</script>

<style scoped>
.trace-graph-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.trace-graph-header {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.trace-graph-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.trace-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.loading-container,
.error-container,
.empty-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fff;
}

.graph-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  margin: 16px;
  min-height: 0;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.graph-stats {
  flex-shrink: 0;
  display: flex;
  gap: 10px;
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
}

.graph-container {
  flex: 1;
  width: 100%;
  min-height: 560px;
}
</style>
