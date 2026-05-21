// src/api/reuseEdit.ts
import axios from "@/api";

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

// 独立需求生成结果响应接口
export interface IndependentRequirementResponse {
  project_id: number;
  intermediate_path1: string;
  rules: Rule[];
  requirements: Requirement[];
}

// 监管变更规则接口
export interface RegulatoryChangeRule {
  id: string;
  text: string;
}

// 监管变更需求接口
export interface RegulatoryChangeRequirement {
  id: string;
  text: string;
  requirement: string;
}

// 监管变更识别结果响应接口
export interface RegulatoryChangeIdentificationResponse {
  project_id: number;
  intermediate_path4: string;
  delete_rules: RegulatoryChangeRule[];
  add_rules: RegulatoryChangeRule[];
  delete_requirements: RegulatoryChangeRequirement[];
  add_requirements: RegulatoryChangeRequirement[];
}

// 需求接口（级联影响范围分析专用）
export interface ImpactRequirement {
  id: string;
  text: string;
  requirement: string;
}

// 场景接口（级联影响范围分析专用）
export interface ImpactScenario {
  id: string;
  requirements: ImpactRequirement[];
}

// 测试用例接口
export interface TestCase {
  id: string;
  [key: string]: string;
}

// 场景接口（测试场景合成专用）
export interface Scenario {
  id: string;
  rule: string;
  sourceId: string;
  text: string;
  blocks: RuleBlock[];
}

// 测试场景合成结果响应接口
export interface TestScenarioSynthesisResponse {
  project_id: number;
  intermediate_path3: string;
  scenarios: Scenario[];
}

// 级联影响范围分析结果响应接口
export interface CascadingImpactScopeAnalysisResponse {
  project_id: number;
  intermediate_path5: string;
  delete_scenarios: ImpactScenario[];
  add_scenarios: ImpactScenario[];
  delete_test_cases: TestCase[];
}

// 更新独立需求生成结果（对应后端路由：/reuse/first-stage/edit/<project_id>/intermediate1）
export const updateIndependentRequirementApi = (projectId: number | string, data: { rules?: Rule[], requirements?: Requirement[] }) => {
  return axios.put<IndependentRequirementResponse>(`/reuse/first-stage/edit/${projectId}/intermediate1`, data);
};

// 更新测试场景合成结果（旧文档，对应 intermediate3）
export const updateTestScenarioSynthesisApi = (
  projectId: number | string,
  data: { scenarios: Scenario[] }
) => {
  return axios.put(`/reuse/first-stage/edit/${projectId}/intermediate3`, data);
};

// 更新测试场景合成结果（新文档，对应 new_test_scenarios）
export const updateNewTestScenarioSynthesisApi = (
  projectId: number | string,
  data: { scenarios: Scenario[] }
) => {
  return axios.put(`/reuse/first-stage/edit/${projectId}/new_test_scenarios`, data);
};

// 更新监管变更识别结果（对应 intermediate5）
export const updateRegulatoryChangeIdentificationApi = (
  projectId: number | string,
  data: {
    delete_rules?: RegulatoryChangeRule[];
    add_rules?: RegulatoryChangeRule[];
  }
) => {
  return axios.put(`/reuse/${projectId}/intermediate5`, data);
};

// 更新级联影响范围分析结果（对应 intermediate6）
export const updateCascadingImpactScopeAnalysisApi = (
  projectId: number | string,
  data: {
    to_delete_scenarios?: string[];
    to_delete_testcases?: string[];
  }
) => {
  return axios.put(`/reuse/${projectId}/intermediate6`, data);
};

// 更新测试套件重用与更新结果（对应 result）
export const updateTestSuiteReuseUpdateApi = (
  projectId: number | string,
  data: {
    testcases?: any[];
  }
) => {
  return axios.put(`/reuse/${projectId}/result`, data);
};
