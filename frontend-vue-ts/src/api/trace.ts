import axios from "@/api";

export interface TraceNode {
  id: string;
  label: string;
  text?: string;
  type?: string;
}

export interface TraceLink {
  source: string;
  target: string;
}

export interface TraceGraphData {
  nodes: TraceNode[];
  links: TraceLink[];
}

export interface TraceRuleResponse {
  project_id: number;
  rule_id: string;
  graph: TraceGraphData;
}

export interface TraceRuleRequest {
  rule_id: string;
  paths: string[];
}

// 测试用例生成页面使用的追溯API
export const fetchTraceRuleApi = (projectId: number | string, data: TraceRuleRequest) => {
  return axios.post<TraceRuleResponse>(`/project/${projectId}/trace-rule`, data);
};

// 重用功能使用的追溯API
export const fetchReuseTraceRuleApi = (projectId: number | string, data: TraceRuleRequest) => {
  return axios.post<TraceRuleResponse>(`/reuse/${projectId}/trace-rule`, data);
};

export const INTERMEDIATE_PATHS = [
  'intermediate_path3',
  'intermediate_path4',
  'intermediate_path5',
  'intermediate_path6'
] as const;
