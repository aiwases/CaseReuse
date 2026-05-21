import service from "@/api/index";

// 文件上传接口
export const uploadFileApi = (formData: FormData, onUploadProgress?: (progressEvent: any) => void) => {
  return service.post("/upload_file", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress
  });
};

// 获取文件记录接口
export const getFileRecordApi = (fileId: string) => {
  return service.get(`/file_record/${fileId}`);
};

// 创建项目接口
export const createProjectApi = (data: {
  name: string;
  description?: string;
  process_type: string;
  file_id?: string;
}) => {
  return service.post("/create_project", data, {
    validateStatus: () => true
  });
};

// 检查项目名称是否可用
export const checkProjectNameApi = (name: string) => {
  return service.get("/check_name", { params: { name } });
};
