import { defineStore } from "pinia";
import {
  fetchTraceRuleApi,
  fetchReuseTraceRuleApi,
  type TraceGraphData,
  type TraceRuleRequest,
  INTERMEDIATE_PATHS
} from "@/api/trace";

interface TraceState {
  graphData: TraceGraphData;
  loading: boolean;
  error: string | null;
  currentRuleId: string | null;
}

export const useTraceStore = defineStore("trace", {
  state: (): TraceState => ({
    graphData: { nodes: [], links: [] },
    loading: false,
    error: null,
    currentRuleId: null,
  }),

  getters: {
    getGraphData: (state) => state.graphData,
    isLoading: (state) => state.loading,
    getError: (state) => state.error,
    getCurrentRuleId: (state) => state.currentRuleId,
    nodeCount: (state) => state.graphData.nodes.length,
    linkCount: (state) => state.graphData.links.length,
  },

  actions: {
    async fetchTraceRule(projectId: number | string, ruleId: string) {
      this.loading = true;
      this.error = null;
      this.currentRuleId = ruleId;

      try {
        const requestData: TraceRuleRequest = {
          rule_id: ruleId,
          paths: [...INTERMEDIATE_PATHS]
        };

        const response = await fetchTraceRuleApi(projectId, requestData);
        this.graphData = response.data.graph;

        if (this.graphData.nodes.length === 0) {
          this.error = `未找到规则 "${ruleId}" 的追溯关系`;
        }

        return this.graphData;
      } catch (err: any) {
        console.error("获取追溯图失败:", err);
        this.error = err.response?.data?.error || "获取追溯图失败";
        this.graphData = { nodes: [], links: [] };
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async fetchReuseTraceRule(projectId: number | string, ruleId: string) {
      this.loading = true;
      this.error = null;
      this.currentRuleId = ruleId;

      try {
        const requestData: TraceRuleRequest = {
          rule_id: ruleId,
          paths: [...INTERMEDIATE_PATHS]
        };

        const response = await fetchReuseTraceRuleApi(projectId, requestData);
        this.graphData = response.data.graph;

        if (this.graphData.nodes.length === 0) {
          this.error = `未找到规则 "${ruleId}" 的追溯关系`;
        }

        return this.graphData;
      } catch (err: any) {
        console.error("获取重用追溯图失败:", err);
        this.error = err.response?.data?.error || "获取重用追溯图失败";
        this.graphData = { nodes: [], links: [] };
        throw err;
      } finally {
        this.loading = false;
      }
    },

    resetTraceGraph() {
      this.graphData = { nodes: [], links: [] };
      this.error = null;
      this.currentRuleId = null;
    },

    clearError() {
      this.error = null;
    }
  },
});
