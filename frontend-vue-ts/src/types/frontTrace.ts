// 文档节点类型
export interface DocumentNode {
  id: number;
  content: string;
  children: DocumentNode[];
  is_requirement?: boolean;
  reason?: string;
  requirement_type?: string[];
}

// 整合后的文档数据
export interface IntegratedDocument extends DocumentNode {
  llm?: string;
}

// API 响应类型
export interface ApiResponse<T = any> {
  data: T;
  status_code: number;
  message?: string;
}

// 思维导图节点数据
export interface MindMapNode {
  id: string;
  topic: string;
  data: {
    isRequirement: boolean;
    reason?: string;
    requirementTypes: string[];
    originalContent: string;
  };
  children?: MindMapNode[];
}

// 反向追溯节点数据
export interface BackTraceNode {
  id?: number[];  // 可选，只有叶子节点有id
  content: string;
  children: BackTraceNode[];
  back_level?: number; // 从叶子节点往上计算的深度，叶子节点为0
}
