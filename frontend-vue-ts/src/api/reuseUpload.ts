import axios from "@/api";

export interface UploadResponse {
  code: number;
  msg: string;
  data: {
    file_path: string;
    filename: string;
    type?: string;
  };
}

export interface UploadStringRequest {
  content: string;
}

// 上传旧文档（支持文件或字符串）
export const uploadOldDocument = (
  projectId: number | string,
  data: FormData | UploadStringRequest
) => {
  const config = data instanceof FormData ? {} : { headers: { 'Content-Type': 'application/json' } };
  return axios.post<UploadResponse>(`/reuse/upload/old-document/${projectId}`, data, config);
};

// 上传新文档（支持文件或字符串）
export const uploadNewDocument = (
  projectId: number | string,
  data: FormData | UploadStringRequest
) => {
  const config = data instanceof FormData ? {} : { headers: { 'Content-Type': 'application/json' } };
  return axios.post<UploadResponse>(`/reuse/upload/new-document/${projectId}`, data, config);
};

// 上传旧测试用例文件（仅支持JSON文件）
export const uploadOldTestcase = (projectId: number | string, data: FormData) => {
  return axios.post<UploadResponse>(`/reuse/upload/old-testcase/${projectId}`, data);
};