import { defineStore } from "pinia";
import { fetchProjectProgressApi, type ProjectProgress } from "@/api/reuse";
import {
  fetchIndependentRequirementApi,
  fetchNewIndependentRequirementApi,
  fetchTestScenarioSynthesisApi,
  fetchNewTestScenarioSynthesisApi,
  fetchScenarioCaseAlignmentApi,
  fetchRegulatoryChangeIdentificationApi,
  fetchCascadingImpactScopeAnalysisApi,
  fetchTestSuiteReuseUpdateApi,
  fetchTestCasesFileApi,
  startReuseProjectApi,
  fetchReuseUploadFileApi,
} from "@/api/reuse";

import {
  updateIndependentRequirementApi,
  updateTestScenarioSynthesisApi,
  updateNewTestScenarioSynthesisApi,
  updateRegulatoryChangeIdentificationApi,
  updateCascadingImpactScopeAnalysisApi,
  updateTestSuiteReuseUpdateApi,
} from "@/api/reuseEdit";

// 规则接口
interface Rule {
  id: string;
  text: string;
}

// 条件接口
interface Condition {
  field: string;
  value: string;
}

// 规则块接口
interface RuleBlock {
  name: string;
  if: Condition[];
  then: Condition[];
}

// 需求接口
interface Requirement {
  id: string;
  ruleText: string;
  blocks: RuleBlock[];
}

// 场景接口（测试场景合成专用）
interface Scenario {
  id: string;
  rule: string;
  sourceId: string;
  text: string;
  blocks: RuleBlock[];
}

// 节点接口
interface Node {
  id: string;
  name: string;
  category: string;
}

// 链接接口
interface Link {
  source: string;
  target: string;
}

// 独立需求数据接口
interface IndependentRequirementData {
  rules: Rule[];
  requirements: Requirement[];
}

// 测试场景数据接口
interface TestScenariosData {
  scenarios: Scenario[];
}

// 场景-测试用例对齐数据接口
interface ScenarioCaseAlignmentData {
  nodes: Node[];
  links: Link[];
}

// 监管变更规则接口
interface RegulatoryChangeRule {
  id: string;
  text: string;
}

// 监管变更识别数据接口
interface RegulatoryChangeData {
  delete_rules: RegulatoryChangeRule[];
  add_rules: RegulatoryChangeRule[];
}



// 级联影响范围分析数据接口
interface CascadingImpactData {
  to_delete_scenarios: string[];
  to_delete_testcases: string[];
}

// 测试用例项接口（测试套件重用与更新专用）
interface TestCaseItem {
  rule: string;
  testid: string;
  [key: string]: any; // 支持动态字段
}

// 测试套件重用与更新数据接口
interface TestSuiteReuseData {
  testcases: TestCaseItem[][];
}

// 重用类型项目状态接口
interface ReuseState {
  // 项目进度
  progress: ProjectProgress | null;
  
  // 独立需求生成结果
  independentRequirements: IndependentRequirementData | null;
  
  // 测试场景合成结果（旧文档）
  testScenarios: TestScenariosData | null;
  
  // 测试场景合成结果（新文档）
  newTestScenarios: TestScenariosData | null;
  
  // 场景-测试用例对齐结果
  scenarioCaseAlignments: ScenarioCaseAlignmentData | null;
  
  // 监管变更识别结果
  regulatoryChanges: RegulatoryChangeData | null;
  
  // 级联影响范围分析结果
  cascadingImpacts: CascadingImpactData | null;
  
  // 测试套件重用与更新结果
  testSuiteReuse: TestSuiteReuseData | null;
  
  // 测试用例文件
  testCasesFile: any | null;
  
  // 上传文件信息
  uploadFiles: {
    original: {
      fileType: string;
      content: string | Blob;
      pdfUrl: string | null;
      uploaded: boolean;
    };
    rules: {
      fileType: string;
      content: string | Blob;
      uploaded: boolean;
    };
    testcases: {
      fileType: string;
      content: string | Blob;
      uploaded: boolean;
    };
  };
  
  // 通用状态
  loading: boolean;
  error: string | null;
}

export const useReuseStore = defineStore("reuse", {
  state: (): ReuseState => ({
    progress: null,
    independentRequirements: null,
    testScenarios: null,
    newTestScenarios: null,
    scenarioCaseAlignments: null,
    regulatoryChanges: null,
    cascadingImpacts: null,
    testSuiteReuse: null,
    testCasesFile: null,
    uploadFiles: {
      original: {
        fileType: "",
        content: "",
        pdfUrl: null,
        uploaded: false,
      },
      rules: {
        fileType: "",
        content: "",
        uploaded: false,
      },
      testcases: {
        fileType: "",
        content: "",
        uploaded: false,
      },
    },
    loading: false,
    error: null,
  }),

  getters: {
    // 项目进度
    projectProgress: (state) => state.progress,
    isRunning: (state) => state.progress?.is_running || false,
    currentStatus: (state) => state.progress?.reuse_status || "Ready",
    
    // 结果数据 - 添加get前缀避免与state属性冲突
    getIndependentRequirements: (state) => state.independentRequirements,
    getTestScenarios: (state) => state.testScenarios,
    getNewTestScenarios: (state) => state.newTestScenarios,
    getScenarioCaseAlignments: (state) => state.scenarioCaseAlignments,
    getRegulatoryChanges: (state) => state.regulatoryChanges,
    getCascadingImpacts: (state) => state.cascadingImpacts,
    getTestSuiteReuse: (state) => state.testSuiteReuse,
    getTestCasesFile: (state) => state.testCasesFile,
    
    // 上传文件 - 确保返回安全的默认值
    getUploadFiles: (state) => state.uploadFiles || {
      original: { fileType: '', content: '', pdfUrl: null, uploaded: false },
      rules: { fileType: '', content: '', uploaded: false },
      testcases: { fileType: '', content: '', uploaded: false },
    },
    
    // 单个文件上传状态
    getOriginalFile: (state) => state.uploadFiles.original,
    getRulesFile: (state) => state.uploadFiles.rules,
    getUploadedTestCasesFile: (state) => state.uploadFiles.testcases,
    
    // 状态
    isLoading: (state) => state.loading,
    hasError: (state) => state.error !== null,
    errorMessage: (state) => state.error,
  },

  actions: {
    // 获取项目进度
    async fetchProgress(projectId: number | string) {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetchProjectProgressApi(projectId);
        this.progress = response.data;
        return response.data;
      } catch (err: any) {
        console.error("获取项目进度失败:", err);
        this.error = err.response?.data?.message || "获取项目进度失败";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 获取独立需求生成结果（旧结果 - 对应intermediate1_）
    async fetchIndependentRequirements(projectId: number | string) {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetchIndependentRequirementApi(projectId);
        const data = response.data;
        this.independentRequirements = {
          rules: data.rules || [],
          requirements: (data.requirements || []).map((req: any) => ({
            id: req.rule || req.id,
            ruleText: req.rule || req.ruleText,
            blocks: req.blocks || []
          }))
        };
        return this.independentRequirements;
      } catch (err: any) {
        console.error("获取独立需求生成结果失败:", err);
        this.error = err.response?.data?.error || err.response?.data?.msg || "获取独立需求生成结果失败";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 获取独立需求生成结果（新结果 - 对应intermediate2_）
    async fetchNewIndependentRequirements(projectId: number | string) {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetchNewIndependentRequirementApi(projectId);
        const data = response.data;
        this.independentRequirements = {
          rules: data.rules || [],
          requirements: (data.requirements || []).map((req: any) => ({
            id: req.rule || req.id,
            ruleText: req.rule || req.ruleText,
            blocks: req.blocks || []
          }))
        };
        return this.independentRequirements;
      } catch (err: any) {
        console.error("获取新独立需求生成结果失败:", err);
        this.error = err.response?.data?.error || err.response?.data?.msg || "获取新独立需求生成结果失败";
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
        // 调用编辑接口
        await updateIndependentRequirementApi(projectId, data);
        
        // 编辑接口不返回内容，重新获取数据
        await this.fetchIndependentRequirements(projectId);
        
        return this.independentRequirements;
      } catch (err: any) {
        console.error("更新独立需求生成结果失败:", err);
        this.error = err.response?.data?.error || err.response?.data?.msg || "更新独立需求生成结果失败";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 获取测试场景合成结果（旧文档）
    async fetchTestScenarios(projectId: number | string) {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetchTestScenarioSynthesisApi(projectId);
        const data = response.data;
        this.testScenarios = {
          scenarios: data.scenarios || []
        };
        return this.testScenarios;
      } catch (err: any) {
        console.error("获取测试场景合成结果失败:", err);
        this.error = err.response?.data?.error || err.response?.data?.msg || "获取测试场景合成结果失败";
        throw err;
      } finally {
        this.loading = false;
      }
    },
    
    // 获取新文档测试场景合成结果
    async fetchNewTestScenarios(projectId: number | string) {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetchNewTestScenarioSynthesisApi(projectId);
        const data = response.data;
        this.newTestScenarios = {
          scenarios: data.scenarios || []
        };
        return this.newTestScenarios;
      } catch (err: any) {
        console.error("获取新文档测试场景合成结果失败:", err);
        this.error = err.response?.data?.error || err.response?.data?.msg || "获取新文档测试场景合成结果失败";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 更新测试场景合成结果（旧文档）
    async updateTestScenarios(projectId: number | string, data: { scenarios: Scenario[] }) {
      this.loading = true;
      this.error = null;
      try {
        await updateTestScenarioSynthesisApi(projectId, data);
        await this.fetchTestScenarios(projectId);
        return this.testScenarios;
      } catch (err: any) {
        console.error("更新测试场景合成结果失败:", err);
        this.error = err.response?.data?.error || err.response?.data?.msg || "更新测试场景合成结果失败";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 更新测试场景合成结果（新文档）
    async updateNewTestScenarios(projectId: number | string, data: { scenarios: Scenario[] }) {
      this.loading = true;
      this.error = null;
      try {
        await updateNewTestScenarioSynthesisApi(projectId, data);
        await this.fetchNewTestScenarios(projectId);
        return this.newTestScenarios;
      } catch (err: any) {
        console.error("更新新文档测试场景合成结果失败:", err);
        this.error = err.response?.data?.error || err.response?.data?.msg || "更新新文档测试场景合成结果失败";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 获取场景-测试用例对齐结果
    async fetchScenarioCaseAlignments(projectId: number | string) {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetchScenarioCaseAlignmentApi(projectId);
        const data = response.data;
        this.scenarioCaseAlignments = {
          nodes: data.nodes || [],
          links: data.links || []
        };
        return this.scenarioCaseAlignments;
      } catch (err: any) {
        console.error("获取场景-测试用例对齐结果失败:", err);
        this.error = err.response?.data?.error || err.response?.data?.msg || "获取场景-测试用例对齐结果失败";
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
          add_rules: response.data.add_rules || []
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

    // 更新监管变更识别结果
    async updateRegulatoryChanges(projectId: number | string, data: { delete_rules?: RegulatoryChangeRule[], add_rules?: RegulatoryChangeRule[] }) {
      this.loading = true;
      this.error = null;
      try {
        await updateRegulatoryChangeIdentificationApi(projectId, data);
        await this.fetchRegulatoryChanges(projectId);
        return this.regulatoryChanges;
      } catch (err: any) {
        console.error("更新监管变更识别结果失败:", err);
        this.error = err.response?.data?.error || err.response?.data?.msg || "更新监管变更识别结果失败";
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
          to_delete_scenarios: response.data.to_delete_scenarios || [],
          to_delete_testcases: response.data.to_delete_testcases || []
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

    // 更新级联影响范围分析结果
    async updateCascadingImpacts(projectId: number | string, data: { to_delete_scenarios?: string[], to_delete_testcases?: string[] }) {
      this.loading = true;
      this.error = null;
      try {
        await updateCascadingImpactScopeAnalysisApi(projectId, data);
        await this.fetchCascadingImpacts(projectId);
        return this.cascadingImpacts;
      } catch (err: any) {
        console.error("更新级联影响范围分析结果失败:", err);
        this.error = err.response?.data?.error || err.response?.data?.msg || "更新级联影响范围分析结果失败";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 获取测试套件重用与更新结果
    async fetchTestSuiteReuse(projectId: number | string) {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetchTestSuiteReuseUpdateApi(projectId);
        this.testSuiteReuse = {
          testcases: response.data.testcases || []
        };
        return this.testSuiteReuse;
      } catch (err: any) {
        console.error("获取测试套件重用与更新结果失败:", err);
        this.error = err.response?.data?.error || "获取测试套件重用与更新结果失败";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 更新测试套件重用与更新结果
    async updateTestSuiteReuse(projectId: number | string, data: { testcases?: any[] }) {
      this.loading = true;
      this.error = null;
      try {
        await updateTestSuiteReuseUpdateApi(projectId, data);
        await this.fetchTestSuiteReuse(projectId);
        return this.testSuiteReuse;
      } catch (err: any) {
        console.error("更新测试套件重用与更新结果失败:", err);
        this.error = err.response?.data?.error || err.response?.data?.msg || "更新测试套件重用与更新结果失败";
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
        // Fail-safe fallback for edit dialog: keep UI usable even if backend returns 500.
        this.testCasesFile = {
          project_id: projectId,
          source_type: 'old_test_case',
          old_test_cases: [],
          test_cases: [],
          warning: this.error
        };
        return this.testCasesFile;
      } finally {
        this.loading = false;
      }
    },

    // 设置级联影响范围分析结果
    setCascadingImpacts(impacts: CascadingImpactData) {
      this.cascadingImpacts = impacts;
      this.error = null;
    },

    // 启动项目
    async startProject(projectId: number | string) {
      this.loading = true;
      this.error = null;
      try {
        const response = await startReuseProjectApi(projectId);
        return response.data;
      } catch (err: any) {
        console.error("启动项目失败:", err);
        this.error = err.response?.data?.message || "启动项目失败";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 获取上传文件
    async fetchUploadFile(projectId: number | string) {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetchReuseUploadFileApi(projectId);
        const blob = response.data;
        const contentType = response.headers['content-type'] || '';
        console.log('获取上传文件响应:', { contentType, blob });

        if (contentType.includes('application/pdf')) {
          const pdfUrl = URL.createObjectURL(blob);
          this.uploadFiles.original = {
            fileType: 'pdf',
            content: blob,
            pdfUrl: pdfUrl,
            uploaded: true,
          };
        } else if (contentType.includes('application/json')) {
          const text = await blob.text();
          const data = JSON.parse(text);

          if (data.error) {
            throw new Error(data.error);
          }

          this.uploadFiles.original = {
            fileType: data.file_type || 'txt',
            content: data.content,
            pdfUrl: null,
            uploaded: true,
          };
        } else if (contentType.includes('text/')) {
          // 处理纯文本文件
          const text = await blob.text();
          this.uploadFiles.original = {
            fileType: 'txt',
            content: text,
            pdfUrl: null,
            uploaded: true,
          };
        } else {
          // 尝试将未知类型转换为文本
          try {
            const text = await blob.text();
            this.uploadFiles.original = {
              fileType: 'txt',
              content: text,
              pdfUrl: null,
              uploaded: true,
            };
          } catch (e) {
            throw new Error(`不支持的文件类型: ${contentType}`);
          }
        }

        return this.uploadFiles.original;
      } catch (err: any) {
        console.error("获取上传文件失败:", err);
        this.error = err.message || "获取上传文件失败";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 重置项目进度
    resetProgress() {
      this.progress = null;
      this.error = null;
    },

    // 重置独立需求生成结果
    resetIndependentRequirements() {
      this.independentRequirements = null;
      this.error = null;
    },

    // 重置测试场景合成结果
    resetTestScenarios() {
      this.testScenarios = null;
      this.newTestScenarios = null;
      this.error = null;
    },

    // 重置场景-测试用例对齐结果
    resetScenarioCaseAlignments() {
      this.scenarioCaseAlignments = null;
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

    // 重置测试套件重用与更新结果
    resetTestSuiteReuse() {
      this.testSuiteReuse = null;
      this.error = null;
    },

    // 设置原始文档上传状态
    setOriginalFile(fileInfo: any) {
      this.uploadFiles.original = {
        fileType: fileInfo.fileType || "",
        content: fileInfo.content || "",
        pdfUrl: fileInfo.pdfUrl || null,
        uploaded: true,
      };
      this.error = null;
    },

    // 设置规则文件上传状态
    setRulesFile(fileInfo: any) {
      this.uploadFiles.rules = {
        fileType: fileInfo.fileType || "",
        content: fileInfo.content || "",
        uploaded: true,
      };
      this.error = null;
    },

    // 设置测试用例文件上传状态
    setTestCasesFile(fileInfo: any) {
      this.uploadFiles.testcases = {
        fileType: fileInfo.fileType || "",
        content: fileInfo.content || "",
        uploaded: true,
      };
      this.error = null;
    },

    // 重置上传文件信息
    resetUploadFiles() {
      this.uploadFiles = {
        original: {
          fileType: "",
          content: "",
          pdfUrl: null,
          uploaded: false,
        },
        rules: {
          fileType: "",
          content: "",
          uploaded: false,
        },
        testcases: {
          fileType: "",
          content: "",
          uploaded: false,
        },
      };
      this.error = null;
    },

    // 重置所有状态
    resetAll() {
      this.progress = null;
      this.independentRequirements = null;
      this.testScenarios = null;
      this.newTestScenarios = null;
      this.scenarioCaseAlignments = null;
      this.regulatoryChanges = null;
      this.cascadingImpacts = null;
      this.testSuiteReuse = null;
      this.uploadFiles = {
        original: {
          fileType: "",
          content: "",
          pdfUrl: null,
          uploaded: false,
        },
        rules: {
          fileType: "",
          content: "",
          uploaded: false,
        },
        testcases: {
          fileType: "",
          content: "",
          uploaded: false,
        },
      };
      this.loading = false;
      this.error = null;
    },
  },
});