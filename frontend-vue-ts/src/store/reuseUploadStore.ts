import { defineStore } from "pinia";
import {
  uploadOldDocument,
  uploadNewDocument,
  uploadOldTestcase,
  type UploadResponse,
  type UploadStringRequest
} from "@/api/reuseUpload";

interface ReuseUploadState {
  oldDocumentLoading: boolean;
  newDocumentLoading: boolean;
  oldTestcaseLoading: boolean;
  error: string | null;
  oldDocumentInfo: UploadResponse['data'] | null;
  newDocumentInfo: UploadResponse['data'] | null;
  oldTestcaseInfo: UploadResponse['data'] | null;
}

export const useReuseUploadStore = defineStore("reuseUpload", {
  state: (): ReuseUploadState => ({
    oldDocumentLoading: false,
    newDocumentLoading: false,
    oldTestcaseLoading: false,
    error: null,
    oldDocumentInfo: null,
    newDocumentInfo: null,
    oldTestcaseInfo: null,
  }),

  getters: {
    isOldDocumentLoading: (state) => state.oldDocumentLoading,
    isNewDocumentLoading: (state) => state.newDocumentLoading,
    isOldTestcaseLoading: (state) => state.oldTestcaseLoading,
    getError: (state) => state.error,
    getOldDocumentInfo: (state) => state.oldDocumentInfo,
    getNewDocumentInfo: (state) => state.newDocumentInfo,
    getOldTestcaseInfo: (state) => state.oldTestcaseInfo,
  },

  actions: {
    async uploadOldDocumentAction(projectId: number | string, data: FormData | UploadStringRequest) {
      this.oldDocumentLoading = true;
      this.error = null;

      try {
        const response = await uploadOldDocument(projectId, data);
        this.oldDocumentInfo = response.data.data;
        return response.data;
      } catch (err: any) {
        console.error("上传旧文档失败:", err);
        this.error = err.response?.data?.msg || "上传旧文档失败";
        throw err;
      } finally {
        this.oldDocumentLoading = false;
      }
    },

    async uploadNewDocumentAction(projectId: number | string, data: FormData | UploadStringRequest) {
      this.newDocumentLoading = true;
      this.error = null;

      try {
        const response = await uploadNewDocument(projectId, data);
        this.newDocumentInfo = response.data.data;
        return response.data;
      } catch (err: any) {
        console.error("上传新文档失败:", err);
        this.error = err.response?.data?.msg || "上传新文档失败";
        throw err;
      } finally {
        this.newDocumentLoading = false;
      }
    },

    async uploadOldTestcaseAction(projectId: number | string, data: FormData) {
      this.oldTestcaseLoading = true;
      this.error = null;

      try {
        const response = await uploadOldTestcase(projectId, data);
        this.oldTestcaseInfo = response.data.data;
        return response.data;
      } catch (err: any) {
        console.error("上传旧测试用例失败:", err);
        this.error = err.response?.data?.msg || "上传旧测试用例失败";
        throw err;
      } finally {
        this.oldTestcaseLoading = false;
      }
    },

    clearError() {
      this.error = null;
    },

    resetUploadInfo() {
      this.oldDocumentInfo = null;
      this.newDocumentInfo = null;
      this.oldTestcaseInfo = null;
      this.error = null;
    },
  },
});