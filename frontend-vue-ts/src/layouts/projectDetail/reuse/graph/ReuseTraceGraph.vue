<template>
  <div class="reuse-trace-graph-container">
    <div class="reuse-trace-graph-header">
      <h3>重用追溯图</h3>
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
import type { TraceNode } from '@/api/trace';

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
  
  try {
    await traceStore.fetchReuseTraceRule(props.projectId, ruleId);
  } catch (error) {
    console.error('获取追溯数据失败:', error);
  }
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

interface TraceNodeWithChange extends TraceNode {
  change_type?: 'add' | 'delete';
}

interface TreeNode {
  id: string;
  name: string;
  value?: string;
  children?: TreeNode[];
  itemStyle?: {
    color: string;
    borderColor: string;
    borderWidth: number;
  };
  label?: {
    show: boolean;
    formatter: string;
    fontSize: number;
    color: string;
    fontWeight: 'bold';
  };
  text?: string;
  symbolSize?: number; // 节点大小
}

const TRACE_TYPE_LIST = [
  'old_rule',
  'new_rule',
  'rule',
  'old_requirement',
  'new_requirement',
  'old_scenario',
  'new_scenario',
  'old_testcase',
  'new_testcase'
];

const resolveLinkedNodeId = (rawId: string, aliasMap: Map<string, string>): string | undefined => {
  const direct = aliasMap.get(rawId);
  if (direct) {
    return direct;
  }

  // 兼容 source/target 可能包含计数后缀的情况
  const withoutCounter = rawId.replace(/_\d+$/, '');
  const noCounterMatch = aliasMap.get(withoutCounter);
  if (noCounterMatch) {
    return noCounterMatch;
  }

  // 回退：从后向前识别类型后缀（例如 old_requirement）
  const parts = withoutCounter.split('_');
  for (let i = parts.length - 1; i >= 0; i--) {
    const typeSuffix = parts.slice(i).join('_');
    if (!TRACE_TYPE_LIST.includes(typeSuffix)) {
      continue;
    }

    const originalId = parts.slice(0, i).join('_');
    const typed = aliasMap.get(`${originalId}_${typeSuffix}`);
    if (typed) {
      return typed;
    }

    const bare = aliasMap.get(originalId);
    if (bare) {
      return bare;
    }
  }

  return undefined;
};

const convertToTreeData = (): TreeNode[] => {
  const { nodes, links } = traceStore.graphData;
  
  const nodeMap = new Map<string, TreeNode>();
  
  // 第一步：创建所有节点，处理相同ID但不同类型的节点
  const idCounter = new Map<string, number>();
  
  nodes.forEach(node => {
    let color = '#409EFF';
    
    // 根据change_type设置颜色
    if (node.change_type === 'delete') {
      color = '#f56c6c'; // 红色表示删除
    } else if (node.change_type === 'add') {
      color = '#67c23a'; // 绿色表示添加
    } else {
      color = '#409EFF'; // 蓝色表示其他
    }
    
    // 只输出测试用例节点的change_type和颜色
    if (node.type === 'old_testcase' || node.type === 'new_testcase') {
      console.log('Testcase node - original change_type:', node.change_type, 'color:', color, 'node.type:', node.type, 'node.id:', node.id);
    }
    
    // 为相同ID但不同类型的节点生成唯一ID
    const key = `${node.id}_${node.type}`;
    const counter = (idCounter.get(key) || 0) + 1;
    idCounter.set(key, counter);
    const uniqueId = `${node.id}_${node.type}_${counter}`;
    
    // 根据节点类型计算大小
    let symbolSize = 15; // 默认大小
    if (node.type === 'old_rule' || node.type === 'new_rule') {
      symbolSize = 28; // 规则节点最大
    } else if (node.type === 'old_requirement' || node.type === 'new_requirement') {
      symbolSize = 22; // 需求节点中等
    } else if (node.type === 'old_scenario' || node.type === 'new_scenario') {
      symbolSize = 18; // 场景节点较小
    } else if (node.type === 'old_testcase' || node.type === 'new_testcase') {
      symbolSize = 14; // 测试用例节点最小
    }
    
    // 为不同类型的节点设置不同的形状
    let symbol = 'circle'; // 默认圆形
    if (node.type === 'old_rule' || node.type === 'new_rule') {
      symbol = 'rect'; // 规则节点使用矩形
    } else if (node.type === 'old_requirement' || node.type === 'new_requirement') {
      symbol = 'triangle'; // 需求节点使用三角形
    } else if (node.type === 'old_scenario' || node.type === 'new_scenario') {
      symbol = 'diamond'; // 场景节点使用菱形
    } else if (node.type === 'old_testcase' || node.type === 'new_testcase') {
      symbol = 'circle'; // 测试用例节点使用圆形
    }
    
    const treeNode = {
      id: uniqueId,
      name: node.label,
      text: node.text,
      symbol: symbol,
      symbolSize: symbolSize, // 设置节点大小
      children: [],
      itemStyle: {
        color: color,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: true,
        formatter: node.label,
        fontSize: ['old_scenario', 'new_scenario', 'new_testcase', 'old_testcase'].includes(node.type) ? 9 : 11,
        color: '#fff',
        fontWeight: 'bold' as const
      }
    };
    
    nodeMap.set(uniqueId, treeNode);
  });
  
  // 第二步：建立链接关系，处理带类型后缀的source和target
  links.forEach(link => {
    // 从带类型后缀的ID中提取原始ID和类型
    const extractNode = (idWithType: string): TreeNode | undefined => {
      // 分割ID和类型
      const parts = idWithType.split('_');
      
      // 查找类型后缀（如 old_rule, new_requirement 等）
      let type = '';
      let originalId = '';
      
      // 从后往前查找类型后缀
      for (let i = parts.length - 1; i >= 0; i--) {
        const potentialType = parts.slice(i).join('_');
        // 检查是否是有效的类型后缀
        if (['old_rule', 'new_rule', 'old_requirement', 'new_requirement', 'old_scenario', 'new_scenario', 'old_testcase', 'new_testcase'].includes(potentialType)) {
          type = potentialType;
          originalId = parts.slice(0, i).join('_');
          break;
        }
      }
      
      if (!type) {
        // 没有找到类型后缀，使用整个ID作为原始ID
        originalId = idWithType;
        // 尝试查找任何类型的节点
        return Array.from(nodeMap.values()).find(node => {
          // 对于没有类型后缀的链接，查找所有可能的节点
          // 节点ID格式：原始ID_类型_计数器
          return node.id.startsWith(`${originalId}_`);
        });
      }
      
      // 查找匹配的节点（节点ID格式：原始ID_类型_计数器）
      return Array.from(nodeMap.values()).find(node => {
        // 节点ID格式：原始ID_类型_计数器
        // 其中类型可能包含下划线，如 old_rule
        return node.id.startsWith(`${originalId}_${type}_`);
      });
    };
    
    const sourceNode = extractNode(link.source);
    const targetNode = extractNode(link.target);
    
    if (sourceNode && targetNode) {
      // 避免循环引用（节点不能是自己的子节点）
      if (sourceNode.id !== targetNode.id) {
        if (!sourceNode.children) {
          sourceNode.children = [];
        }
        // 避免重复添加
        if (!sourceNode.children.includes(targetNode)) {
          sourceNode.children.push(targetNode);
        }
      }
    }
  });
  
  // 第三步：识别根节点（规则类型节点）
  const rootNodes: TreeNode[] = [];
  
  // 查找所有规则类型的节点作为根节点
  Array.from(nodeMap.values()).forEach(treeNode => {
    // 直接检查节点ID是否包含规则类型
    if (treeNode.id.includes('_old_rule_') || treeNode.id.includes('_new_rule_')) {
      rootNodes.push(treeNode);
    }
  });
  
  // 如果没有找到规则节点，使用当前规则ID查找
  if (rootNodes.length === 0 && traceStore.currentRuleId) {
    // 尝试查找当前规则节点
    let rootNode: TreeNode | undefined;
    
    // 根据当前规则ID查找匹配的规则节点
    for (const [key, node] of nodeMap.entries()) {
      if (key.startsWith(`${traceStore.currentRuleId}_`)) {
        rootNode = node;
        break;
      }
    }
    
    // 如果找到，添加到根节点列表
    if (rootNode) {
      rootNodes.push(rootNode);
    }
  }
  
  // 如果还是没有根节点，取第一个节点
  if (rootNodes.length === 0 && nodeMap.size > 0) {
    rootNodes.push(nodeMap.values().next().value);
  }
  
  // 清理循环引用，防止栈溢出
  const visited = new Set<string>();
  const cleanCircularReference = (node: TreeNode) => {
    if (visited.has(node.id)) {
      return;
    }
    visited.add(node.id);
    
    if (node.children) {
      // 过滤掉已访问过的子节点，避免循环引用
      node.children = node.children.filter(child => {
        if (visited.has(child.id)) {
          return false;
        }
        cleanCircularReference(child);
        return true;
      });
    }
  };
  
  rootNodes.forEach(node => {
    cleanCircularReference(node);
  });
  
  return rootNodes;
};

const renderChart = () => {
  if (!traceStore.graphData.nodes.length) {
    return;
  }
  
  if (!chartInstance) {
    const success = initChart();
    if (!success || !chartInstance) {
      return;
    }
  }
  
  if (!graphContainerRef.value) {
    return;
  }
  
  const container = graphContainerRef.value;
  
  if (container.clientWidth === 0 || container.clientHeight === 0) {
    requestAnimationFrame(() => renderChart());
    return;
  }
  
  // 转换为关系图数据格式
  const nodes: echarts.GraphNode[] = [];
  const links: echarts.GraphLink[] = [];
  const linkAliasToNodeId = new Map<string, string>();
  
  // 为相同ID但不同类型的节点生成唯一ID
  const idCounter = new Map<string, number>();
  
  // 遍历所有节点，创建关系图节点
  const visitedNodes = new Set<string>();
  // 记录每层节点数量，用于均匀分布
  const layerNodeCount = {
    rule: 0,
    requirement: 0,
    scenario: 0,
    testcase: 0
  };
  // 记录每层节点索引
  const layerNodeIndex = {
    rule: 0,
    requirement: 0,
    scenario: 0,
    testcase: 0
  };
  
  // 直接从原始数据创建所有节点
  traceStore.graphData.nodes.forEach(node => {
    let color = '#409EFF';
    
    // 根据change_type设置颜色
    if (node.change_type === 'delete') {
      color = '#f56c6c'; // 红色表示删除
    } else if (node.change_type === 'add') {
      color = '#67c23a'; // 绿色表示添加
    } else {
      color = '#409EFF'; // 蓝色表示其他
    }
    
    // 只输出测试用例节点的change_type和颜色
    if (node.type === 'old_testcase' || node.type === 'new_testcase') {
      console.log('Testcase node - original change_type:', node.change_type, 'color:', color, 'node.type:', node.type, 'node.id:', node.id);
    }
    
    // 为相同ID但不同类型的节点生成唯一ID
    const key = `${node.id}_${node.type}`;
    const counter = (idCounter.get(key) || 0) + 1;
    idCounter.set(key, counter);
    const uniqueId = `${node.id}_${node.type}_${counter}`;
    const normalizedType = (node.type || '').replace(/^(old|new)_/, '');

    // 建立后端 link source/target 到图节点 ID 的映射
    if (node.type) {
      linkAliasToNodeId.set(`${node.id}_${node.type}`, uniqueId);
    }
    if (!linkAliasToNodeId.has(node.id)) {
      linkAliasToNodeId.set(node.id, uniqueId);
    }
    if (normalizedType) {
      linkAliasToNodeId.set(`${node.id}_${normalizedType}`, uniqueId);
    }
    // 后端会为兜底规则使用 other_rule 键
    if (node.id === 'other' && normalizedType === 'rule') {
      linkAliasToNodeId.set('other_rule', uniqueId);
    }
    
    // 根据节点类型计算大小
    let symbolSize = 15; // 默认大小
    if (node.type === 'old_rule' || node.type === 'new_rule') {
      symbolSize = 38; // 规则节点最大
    } else if (node.type === 'old_requirement' || node.type === 'new_requirement') {
      symbolSize = 30; // 需求节点中等
    } else if (node.type === 'old_scenario' || node.type === 'new_scenario') {
      symbolSize = 28; // 场景节点较小
    } else if (node.type === 'old_testcase' || node.type === 'new_testcase') {
      symbolSize = 18; // 测试用例节点最小
    }
    
    // delete类型的节点增大尺寸，使其更明显
    if (node.change_type === 'delete') {
      symbolSize += 5; // 增大5个单位
    }
    
    // 根据节点类型确定层级位置
    let x = 0;
    let layer = 'rule';
    
    // 根据节点类型设置位置和颜色
    if (node.type === 'old_rule' || node.type === 'new_rule') {
      x = 150; // 规则层（输入层）- 左侧，增加水平间距
      if (node.change_type !== 'delete') {
        color = '#409EFF'; // 蓝色，与规则层标题颜色一致
      }
      layer = 'rule';
      layerNodeCount[layer]++;
    } else if (node.type === 'old_requirement' || node.type === 'new_requirement') {
      x = 400; // 需求层（隐藏层1）- 左中，增加水平间距
      if (node.change_type !== 'delete') {
        color = '#909399'; // 灰色
      }
      layer = 'requirement';
      layerNodeCount[layer]++;
    } else if (node.type === 'old_scenario' || node.type === 'new_scenario') {
      x = 650; // 场景层（隐藏层2）- 右中，增加水平间距
      if (node.change_type !== 'delete') {
        color = '#67c23a'; // 绿色
      }
      layer = 'scenario';
      layerNodeCount[layer]++;
    } else if (node.type === 'old_testcase' || node.type === 'new_testcase') {
      x = 900; // 测试用例层（输出层）- 右侧，增加水平间距
      if (node.change_type !== 'delete') {
        color = '#e6a23c'; // 橙色
      }
      layer = 'testcase';
      layerNodeCount[layer]++;
    }
    
    // 为不同类型的节点设置不同的形状
    let symbol = 'circle'; // 默认圆形
    if (node.type === 'old_rule' || node.type === 'new_rule') {
      symbol = 'rect'; // 规则节点使用矩形
    } else if (node.type === 'old_requirement' || node.type === 'new_requirement') {
      symbol = 'triangle'; // 需求节点使用三角形
    } else if (node.type === 'old_scenario' || node.type === 'new_scenario') {
      symbol = 'diamond'; // 场景节点使用菱形
    } else if (node.type === 'old_testcase' || node.type === 'new_testcase') {
      symbol = 'circle'; // 测试用例节点使用圆形
    }
    
    // 为不同类型的节点添加特殊样式
    const itemStyle = {
      color: color,
      borderColor: '#fff',
      borderWidth: 2
    };
    
    if (node.change_type === 'delete') {
      itemStyle.color = '#f56c6c'; // 红色表示删除
      itemStyle.borderColor = '#ff0000'; // 红色边框
      itemStyle.borderWidth = 3; // 加粗边框
      itemStyle.shadowBlur = 10; // 阴影效果
      itemStyle.shadowColor = 'rgba(255, 0, 0, 0.5)'; // 红色阴影
    }
    // else if (node.change_type === 'add') {
    //   // add类型的节点使用根据节点类型设置的颜色
    //   itemStyle.borderColor = color; // 使用与节点颜色一致的边框
    //   itemStyle.borderWidth = 3; // 加粗边框
    //   itemStyle.shadowBlur = 10; // 阴影效果
    //   itemStyle.shadowColor = `${color}80`; // 使用与节点颜色一致的阴影（添加透明度）
    // }
    
    const chartNode = {
      id: uniqueId,
      name: node.label,
      symbol: symbol,
      symbolSize: symbolSize,
      itemStyle: itemStyle,
      label: {
        show: true,
        formatter: node.label,
        fontSize: ['old_scenario', 'new_scenario', 'new_testcase', 'old_testcase'].includes(node.type) ? 9 : 11,
        color: '#fff',
        fontWeight: 'bold' as const
      },
      x: x,
      y: 0, // 暂时设为0，后面统一计算
      layer: layer
    };
    
    // 只输出测试用例节点的最终对象
    if (node.type === 'old_testcase' || node.type === 'new_testcase') {
      console.log('Final testcase node:', chartNode);
    }
    
    nodes.push(chartNode);
  });
  
  // 计算每层节点的Y坐标，确保均匀分布
  nodes.forEach(node => {
    const layer = node.layer;
    if (layer && layerNodeCount[layer] > 0) {
      // 计算均匀分布的Y坐标
      const spacing = 600 / (layerNodeCount[layer] + 1); // 600为垂直空间高度
      const index = layerNodeIndex[layer]++;
      node.y = spacing * (index + 1);
    }
  });
  
  // 直接使用原始的links数据创建边
  traceStore.graphData.links.forEach(link => {
    const sourceId = resolveLinkedNodeId(link.source, linkAliasToNodeId);
    const targetId = resolveLinkedNodeId(link.target, linkAliasToNodeId);
    
    if (sourceId && targetId) {
      links.push({
        source: sourceId,
        target: targetId
      });
    }
  });
  
  // 创建关系图系列
  const series = [{
    type: 'graph' as const,
    layout: 'none' as const, // 使用自定义布局，按照x、y坐标排列
    data: nodes,
    links: links,
    roam: true,
    label: {
      show: true,
      position: 'inside' as const,
      formatter: '{b}',
      fontSize: 9,
      color: '#fff',
      fontWeight: 'bold'
    },
    labelLayout: {
      hideOverlap: true
    },
    scaleLimit: {
      min: 0.3,
      max: 3
    },
    lineStyle: {
      color: '#666',
      width: 1.5,
      curveness: 0.2,
      opacity: 0.6
    },
    emphasis: {
      focus: 'adjacency' as const,
      lineStyle: {
        width: 3,
        opacity: 1
      },
      itemStyle: {
        shadowBlur: 10,
        shadowColor: 'rgba(0, 0, 0, 0.5)'
      }
    }
  }];
  
  const option: echarts.EChartsOption = {
    backgroundColor: '#ffffff',
    graphic: [
      // 规则层标题
      {
        type: 'text',
        left: '15%',
        top: '1%',
        style: {
          text: '规则',
          fontSize: 16,
          fontWeight: 'bold',
          fill: '#409EFF'
        }
      },
      // 需求层标题
      {
        type: 'text',
        left: '38%',
        top: '1%',
        style: {
          text: '需求',
          fontSize: 16,
          fontWeight: 'bold',
          fill: '#909399'
        }
      },
      // 场景层标题
      {
        type: 'text',
        left: '60%',
        top: '1%',
        style: {
          text: '场景',
          fontSize: 16,
          fontWeight: 'bold',
          fill: '#67c23a'
        }
      },
      // 测试用例层标题
      {
        type: 'text',
        left: '85%',
        top: '1%',
        style: {
          text: '测试用例',
          fontSize: 16,
          fontWeight: 'bold',
          fill: '#e6a23c'
        }
      },
      // 删除节点图例
      {
        type: 'text',
        left: '1%',
        top: '1%',
        style: {
          text: '红色表示节点被删除',
          fontSize: 12,
          fontWeight: 'bold',
          fill: '#f56c6c'
        }
      }
    ],
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove',
      enterable: true,
      confine: true,
      formatter: (params: any) => {
        let originalNode = null;
        
        // 尝试直接匹配节点ID和类型（对于测试用例节点）
        const testcaseMatch = params.data.id.match(/^(.+?)_(new_testcase|old_testcase)_\d+$/);
        if (testcaseMatch) {
          const testcaseId = testcaseMatch[1];
          const testcaseType = testcaseMatch[2];
          originalNode = traceStore.graphData.nodes.find(n => n.id === testcaseId && n.type === testcaseType);
        }
        
        // 如果没有找到，尝试其他节点类型的匹配
        if (!originalNode) {
          const nodeParts = params.data.id.split('_');
          if (nodeParts.length >= 3) {
            // 节点ID格式：原始ID_类型_计数器
            const counter = nodeParts[nodeParts.length - 1];
            const typeParts = nodeParts.slice(nodeParts.length - 2, nodeParts.length - 1);
            const nodeType = typeParts.join('_');
            const originalId = nodeParts.slice(0, nodeParts.length - 2).join('_');
            originalNode = traceStore.graphData.nodes.find(n => n.id === originalId && n.type === nodeType);
          }
        }
        
        // 如果还是没找到，尝试遍历所有节点查找匹配
        if (!originalNode) {
          for (const node of traceStore.graphData.nodes) {
            if (params.data.id.includes(node.id) && params.data.id.includes(node.type)) {
              originalNode = node;
              break;
            }
          }
        }
        
        // 显示测试用例详情
        if (originalNode && originalNode.testcase) {
          const testcase = originalNode.testcase;
          let testcaseHtml = '<div style="font-weight: bold; margin-bottom: 8px;">测试用例详情</div>';
          
          // 显示节点类型
          if (originalNode.type) {
            testcaseHtml += `<div><strong>节点类型:</strong> ${originalNode.type}</div>`;
          }
          
          // 如果有change_type，显示出来
          if (originalNode.change_type) {
            testcaseHtml += `<div><strong>变更类型:</strong> ${originalNode.change_type}</div>`;
          }
          
          Object.entries(testcase).forEach(([key, value]) => {
            testcaseHtml += `<div><strong>${key}:</strong> ${value}</div>`;
          });
          return `<div style="max-width: 400px; white-space: normal; word-break: break-word;">${testcaseHtml}</div>`;
        }
        
        // 显示节点文本内容
        if (originalNode && originalNode.text) {
          const text = originalNode.text.replace(/\n/g, '<br/>');
          let contentHtml = `<div style="font-weight: bold; margin-bottom: 8px;">${params.data.name}</div>`;
          
          // 显示节点类型
          if (originalNode.type) {
            contentHtml += `<div><strong>节点类型:</strong> ${originalNode.type}</div>`;
          }
          
          // 如果有change_type，显示出来
          if (originalNode.change_type) {
            contentHtml += `<div><strong>变更类型:</strong> ${originalNode.change_type}</div><br/>`;
          }
          
          contentHtml += `<div>${text}</div>`;
          return `<div style="max-width: 300px; white-space: normal; word-break: break-word;">${contentHtml}</div>`;
        }
        
        // 如果只有name但没有text，检查是否有change_type
        if (originalNode) {
          let contentHtml = `<div style="max-width: 300px; white-space: normal; word-break: break-word;">
            <div style="font-weight: bold; margin-bottom: 8px;">${params.data.name}</div>`;
            
          // 显示节点类型
          if (originalNode.type) {
            contentHtml += `<div><strong>节点类型:</strong> ${originalNode.type}</div>`;
          }
          
          // 如果有change_type，显示出来
          if (originalNode.change_type) {
            contentHtml += `<div><strong>变更类型:</strong> ${originalNode.change_type}</div>`;
          }
          
          contentHtml += '</div>';
          return contentHtml;
        }
        
        return params.data.name;
      }
    },
    animationDuration: 1500,
    animationDurationUpdate: 1500,
    series: series
  };
  
  chartInstance.setOption(option, true);
};

const handleResize = () => {
  chartInstance?.resize();
};

watch(
  () => traceStore.graphData.nodes.length,
  (newLength, oldLength) => {
    if (newLength > 0) {
      nextTick(() => {
        renderChart();
      });
    }
  }
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
.reuse-trace-graph-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.reuse-trace-graph-header {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.reuse-trace-graph-header h3 {
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
  min-height: 800px;
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
  min-height: 800px;
  overflow: auto;
}
</style>
