// src/api/reuse.ts
import axios from "@/api";

// 定义项目状态类型（匹配后端模型）
export type ProjectStatus = 'Ready' | 'Step1_old_ready' | 'Step1_all_ready' | 'Step2_Done' | 'Step3_Done' | 'Step4_Done' | 'Process' | 'Merge_Ready' | 'Step5_Done' | 'Completed' | 'failed';

// 项目进度接口（重用类型）
export interface ProjectProgress {
  id: number | string;
  branch_a_status: ProjectStatus;
  branch_b_status: ProjectStatus;
  reuse_status: ProjectStatus;
  is_running: boolean;
}

// 获取项目进度
export const fetchProjectProgressApi = (projectId: number | string) => {
  return axios.get<ProjectProgress>(`/reuse/${projectId}/progress`);
};

// 规则接口
export interface Rule {
  id: string;
  text: string;
}

// 条件接口
export interface Condition {
  field: string;
  value: string;
}

// 规则块接口
export interface RuleBlock {
  name: string;
  if: Condition[];
  then: Condition[];
}

// 需求接口
export interface Requirement {
  id: string;
  ruleText: string;
  blocks: RuleBlock[];
}

// 场景接口（测试场景合成专用）
export interface Scenario {
  id: string;
  rule: string;
  sourceId: string;
  text: string;
  blocks: RuleBlock[];
}

// 市场品种接口
export interface MarketVariety {
  market: string;
  variety: string;
}

// 独立需求生成结果响应接口
export interface IndependentRequirementResponse {
  project_id: number;
  intermediate_path1: string;
  market_variety: MarketVariety;
  requirements: Requirement[];
  rules: Rule[];
  sco: any[];
}

// 测试场景合成结果响应接口
export interface TestScenarioSynthesisResponse {
  project_id: number;
  intermediate_path2: string;
  scenarios: Scenario[];
}

// 节点接口
export interface Node {
  id: string;
  name: string;
  category: string;
}

// 链接接口
export interface Link {
  source: string;
  target: string;
}

// 场景-测试用例对齐结果响应接口
export interface ScenarioCaseAlignmentResponse {
  project_id: number;
  intermediate_path3: string;
  nodes: Node[];
  links: Link[];
}

// 监管变更识别规则接口
export interface RegulatoryChangeRule {
  id: string;
  text: string;
}

// 监管变更识别结果响应接口
export interface RegulatoryChangeIdentificationResponse {
  project_id: number;
  intermediate_path4: string;
  delete_rules: RegulatoryChangeRule[];
  add_rules: RegulatoryChangeRule[];
}

// 测试用例接口
export interface TestCase {
  id: string;
  [key: string]: string;
}

// 级联影响范围分析结果响应接口
export interface CascadingImpactScopeAnalysisResponse {
  project_id: number;
  intermediate_path5: string;
  to_delete_scenarios: string[];
  to_delete_testcases: string[];
}

// 测试用例项接口（测试套件重用与更新专用）
export interface TestCaseItem {
  rule: string;
  testid: string;
  [key: string]: any; // 支持动态字段
}

// 测试套件重用与更新结果响应接口
export interface TestSuiteReuseUpdateResponse {
  project_id: number;
  result_path: string;
  testcases: TestCaseItem[][];
}

// 获取独立需求生成结果（对应intermediate1 - 旧结果）
export const fetchIndependentRequirementApi = (projectId: number | string) => {
  return axios.get<IndependentRequirementResponse>(`/reuse/${projectId}/intermediate1`);
};

// 获取独立需求生成结果（对应intermediate2 - 新结果）
export const fetchNewIndependentRequirementApi = (projectId: number | string) => {
  return axios.get<IndependentRequirementResponse>(`/reuse/${projectId}/intermediate2`);
};

// 获取测试场景合成结果（对应intermediate3）
export const fetchTestScenarioSynthesisApi = (projectId: number | string) => {
  return axios.get<TestScenarioSynthesisResponse>(`/reuse/${projectId}/intermediate3`);
};

// 获取新文档测试场景合成结果（对应new_test_scenarios）
export const fetchNewTestScenarioSynthesisApi = (projectId: number | string) => {
  return axios.get<TestScenarioSynthesisResponse>(`/reuse/${projectId}/new_test_scenarios`);
};

// 获取场景-测试用例对齐结果（对应intermediate4）
export const fetchScenarioCaseAlignmentApi = (projectId: number | string) => {
  return axios.get<ScenarioCaseAlignmentResponse>(`/reuse/${projectId}/intermediate4`);
};

// 获取监管变更识别结果（对应intermediate5）
export const fetchRegulatoryChangeIdentificationApi = (projectId: number | string) => {
  return axios.get<RegulatoryChangeIdentificationResponse>(`/reuse/${projectId}/intermediate5`);
};

// 获取级联影响范围分析结果（对应intermediate6）
export const fetchCascadingImpactScopeAnalysisApi = (projectId: number | string) => {
  return axios.get<CascadingImpactScopeAnalysisResponse>(`/reuse/${projectId}/intermediate6`);
};

// 获取测试套件重用与更新结果（对应result）
export const fetchTestSuiteReuseUpdateApi = (projectId: number | string) => {
  return axios.get<TestSuiteReuseUpdateResponse>(`/reuse/${projectId}/result`);
};

export interface StartReuseProjectPayload {
  stage?: number;
  pageType?: 'dependency-modeling' | 'effect-aware-reuse';
  task?: number;
  documentType?: 'old' | 'new';
  runAll?: boolean;
}

// 启动项目
export const startReuseProjectApi = (
  projectId: number | string,
  payload: StartReuseProjectPayload = {},
) => {
  return axios.post(`/reuse/start/${projectId}`, payload);
};

// 获取上传文件
export const fetchReuseUploadFileApi = (projectId: number | string) => {
  return axios.get(`/reuse/${projectId}/upload_file`, {
    responseType: 'blob' // 设置响应类型为blob，支持二进制文件
  });
};

// 获取测试用例文件（对应test_case_file）
export const fetchTestCasesFileApi = (projectId: number | string) => {
  return axios.get<any>(`/reuse/${projectId}/test_case_file`);
};