import { defineStore } from "pinia";
import {
  updateIndependentRequirementApi,
  type IndependentRequirementResponse,
} from "@/api/reuseEdit";

import {
  fetchIndependentRequirementApi,
  fetchNewIndependentRequirementApi,
  fetchRegulatoryChangeIdentificationApi,
  fetchCascadingImpactScopeAnalysisApi,
  fetchTestScenarioSynthesisApi,
  fetchTestCasesFileApi,
  type RegulatoryChangeIdentificationResponse,
  type CascadingImpactScopeAnalysisResponse,
  type TestScenarioSynthesisResponse,
} from "@/api/reuse";

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

// 独立需求数据接口
export interface IndependentRequirementData {
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

// 监管变更识别数据接口
export interface RegulatoryChangeData {
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

// 级联影响范围分析数据接口
export interface CascadingImpactData {
  delete_scenarios: ImpactScenario[];
  add_scenarios: ImpactScenario[];
  delete_test_cases: TestCase[];
}

// 测试场景数据接口
export interface TestScenariosData {
  scenarios: any[];
}

// 重用编辑状态接口
interface ReuseEditState {
  // 独立需求生成结果
  independentRequirements: IndependentRequirementData | null;
  
  // 监管变更识别结果
  regulatoryChanges: RegulatoryChangeData | null;
  
  // 测试场景合成结果
  testScenarios: TestScenariosData | null;
  
  // 级联影响范围分析结果
  cascadingImpacts: CascadingImpactData | null;
  
  // 测试用例文件
  testCasesFile: any | null;
  
  // 通用状态
  loading: boolean;
  error: string | null;
}

export const useReuseEditStore = defineStore("reuseEdit", {
  state: (): ReuseEditState => ({
    independentRequirements: null,
    regulatoryChanges: null,
    testScenarios: null,
    cascadingImpacts: null,
    testCasesFile: null,
    loading: false,
    error: null,
  }),

  getters: {
    // 独立需求生成结果
    getIndependentRequirements: (state) => state.independentRequirements,
    
    // 监管变更识别结果
    getRegulatoryChanges: (state) => state.regulatoryChanges,
    
    // 测试场景合成结果
    getTestScenarios: (state) => state.testScenarios,
    
    // 级联影响范围分析结果
    getCascadingImpacts: (state) => state.cascadingImpacts,
    
    // 测试用例文件
    getTestCasesFile: (state) => state.testCasesFile,
    
    // 状态
    isLoading: (state) => state.loading,
    hasError: (state) => state.error !== null,
    errorMessage: (state) => state.error,
  },

  actions: {
    // 获取独立需求生成结果（旧结果 - 对应intermediate1_，用于新增规则/需求）
    async fetchIndependentRequirements(projectId: number | string) {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetchIndependentRequirementApi(projectId);
        this.independentRequirements = {
          rules: response.data.rules,
          requirements: response.data.requirements
        };
        return this.independentRequirements;
      } catch (err: any) {
        console.error("获取独立需求生成结果失败:", err);
        this.error = err.response?.data?.error || "获取独立需求生成结果失败";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 更新独立需求生成结果
    async updateIndependentRequirements(projectId: number | string, data: { rules?: Rule[], requirements?: Requirement[] }) {
      this.loading = true;
      this.error = null;
      try {
        const response = await updateIndependentRequirementApi(projectId, data);
        const result = response.data;
        this.independentRequirements = {
          rules: result.rules || [],
          requirements: (result.requirements || []).map((req: any) => ({
            id: req.rule || req.id,
            ruleText: req.rule || req.ruleText,
            blocks: req.blocks || []
          }))
        };
        return this.independentRequirements;
      } catch (err: any) {
        console.error("更新独立需求生成结果失败:", err);
        this.error = err.response?.data?.error || err.response?.data?.msg || "更新独立需求生成结果失败";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 获取独立需求生成结果（新结果 - 对应intermediate2_，用于删除规则/需求）
    async fetchNewIndependentRequirements(projectId: number | string) {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetchNewIndependentRequirementApi(projectId);
        this.independentRequirements = {
          rules: response.data.rules,
          requirements: response.data.requirements
        };
        return this.independentRequirements;
      } catch (err: any) {
        console.error("获取新独立需求生成结果失败:", err);
        this.error = err.response?.data?.error || "获取新独立需求生成结果失败";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 获取监管变更识别结果
    async fetchRegulatoryChanges(projectId: number | string) {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetchRegulatoryChangeIdentificationApi(projectId);
        this.regulatoryChanges = {
          delete_rules: response.data.delete_rules || [],
          add_rules: response.data.add_rules || [],
          delete_requirements: response.data.delete_requirements || [],
          add_requirements: response.data.add_requirements || []
        };
        return this.regulatoryChanges;
      } catch (err: any) {
        console.error("获取监管变更识别结果失败:", err);
        this.error = err.response?.data?.error || "获取监管变更识别结果失败";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 设置监管变更识别结果
    setRegulatoryChanges(changes: RegulatoryChangeData) {
      this.regulatoryChanges = changes;
      this.error = null;
    },

    // 获取测试场景合成结果
    async fetchTestScenarios(projectId: number | string) {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetchTestScenarioSynthesisApi(projectId);
        this.testScenarios = {
          scenarios: response.data.scenarios
        };
        return this.testScenarios;
      } catch (err: any) {
        console.error("获取测试场景合成结果失败:", err);
        this.error = err.response?.data?.error || "获取测试场景合成结果失败";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 获取测试用例文件
    async fetchTestCasesFile(projectId: number | string) {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetchTestCasesFileApi(projectId);
        this.testCasesFile = response.data;
        return this.testCasesFile;
      } catch (err: any) {
        console.error("获取测试用例文件失败:", err);
        this.error = err.response?.data?.error || "获取测试用例文件失败";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 获取级联影响范围分析结果
    async fetchCascadingImpacts(projectId: number | string) {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetchCascadingImpactScopeAnalysisApi(projectId);
        this.cascadingImpacts = {
          delete_scenarios: response.data.delete_scenarios || [],
          add_scenarios: response.data.add_scenarios || [],
          delete_test_cases: response.data.delete_test_cases || []
        };
        return this.cascadingImpacts;
      } catch (err: any) {
        console.error("获取级联影响范围分析结果失败:", err);
        this.error = err.response?.data?.error || "获取级联影响范围分析结果失败";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 设置级联影响范围分析结果
    setCascadingImpacts(impacts: CascadingImpactData) {
      this.cascadingImpacts = impacts;
      this.error = null;
    },

    // 重置独立需求生成结果
    resetIndependentRequirements() {
      this.independentRequirements = null;
      this.error = null;
    },

    // 重置监管变更识别结果
    resetRegulatoryChanges() {
      this.regulatoryChanges = null;
      this.error = null;
    },

    // 重置级联影响范围分析结果
    resetCascadingImpacts() {
      this.cascadingImpacts = null;
      this.error = null;
    },

    // 重置所有状态
    resetAll() {
      this.independentRequirements = null;
      this.regulatoryChanges = null;
      this.testScenarios = null;
      this.cascadingImpacts = null;
      this.testCasesFile = null;
      this.loading = false;
      this.error = null;
    },
  },
});
