import { defineStore } from "pinia";
import { ref, computed, reactive } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import {
  uploadFileApi,
  getFileRecordApi,
  createProjectApi,
  checkProjectNameApi
} from "@/api/creatProject";

interface FileRecord {
  id: string;
  filename: string;
  filepath?: string;
  [key: string]: any;
}

export const useCreatProjectStore = defineStore("creatProject", () => {
  // 表单数据
  const formData = reactive({
    name: "",
    description: "",
    process_type: ""
  });

  // 文件上传相关
  const selectedFile = ref<File | null>(null);
  const uploadProgress = ref(0);
  const isUploading = ref(false);
  const uploadStatus = ref("");
  const fileRecord = ref<FileRecord | null>(null);

  // 项目名称唯一性
  const nameAvailable = ref(true);

  // 提交状态
  const isSubmitting = ref(false);

  // 文件拖拽状态
  const isDragOver = ref(false);

  // Router实例
  const router = useRouter();

  // 计算属性
  const hasFile = computed(() => selectedFile.value || fileRecord.value);

  // 文件操作方法
  const triggerFileInput = (fileInputRef: HTMLInputElement | null) => {
    fileInputRef?.click();
  };

  const handleDragOver = () => {
    isDragOver.value = true;
  };

  const handleDragLeave = () => {
    isDragOver.value = false;
  };

  const handleDrop = (event: DragEvent) => {
    isDragOver.value = false;
    if (!event.dataTransfer) return;
    const files = event.dataTransfer.files;
    if (files.length > 0) handleFile(files[0]);
  };

  const handleFileSelect = (event: Event) => {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      handleFile(input.files[0]);
    }
  };

  const handleFile = (file: File) => {
    if (file.type !== "application/pdf") {
      alert("仅支持 PDF 文件");
      return;
    }
    selectedFile.value = file;
  };

  const removeFile = () => {
    selectedFile.value = null;
    uploadProgress.value = 0;
  };

  // 工具函数
  const formatFileSize = (size: number | undefined) => {
    if (!size) return "";
    if (size < 1024) return size + " B";
    if (size < 1024 * 1024) return (size / 1024).toFixed(1) + " KB";
    return (size / 1024 / 1024).toFixed(1) + " MB";
  };

  // 文件上传
  const uploadFile = async (): Promise<string | null> => {
    if (!selectedFile.value) return null;

    const form = new FormData();
    form.append("file", selectedFile.value);

    isUploading.value = true;
    uploadProgress.value = 0;
    uploadStatus.value = "上传中...";

    try {
      const response = await uploadFileApi(form, (progressEvent: any) => {
        if (progressEvent.total) {
          uploadProgress.value = Math.round(
            (progressEvent.loaded / progressEvent.total) * 100
          );
        }
      });

      if (response.data.success) {
        uploadStatus.value = "上传成功";
        fileRecord.value = response.data.file;
        return response.data.file.id;
      } else {
        uploadStatus.value = "上传失败: " + response.data.message;
        return null;
      }
    } catch (error: any) {
      console.error(error);
      uploadStatus.value = "上传出错，请重试";
      return null;
    } finally {
      isUploading.value = false;
    }
  };

  // 加载文件记录（从文件库跳转时）
  const loadFileRecord = async (fileId: string) => {
    try {
      const resp = await getFileRecordApi(fileId);
      if (resp.data.success) {
        fileRecord.value = resp.data.file;
      } else {
        alert("无法加载文件信息：" + resp.data.message);
      }
    } catch (err) {
      console.error("加载文件失败", err);
    }
  };

  // 检查项目名称
  const checkProjectName = async (name: string) => {
    try {
      const response = await checkProjectNameApi(name);
      nameAvailable.value = !response.data.exists; // 假设API返回exists字段
    } catch (error) {
      console.error("检查项目名称失败", error);
    }
  };

  // 表单提交
  const submitProject = async () => {
    isSubmitting.value = true;

    const projectName = (formData.name || "").trim();

    // 验证项目名称
    if (!projectName) {
      ElMessage.error("项目名称不能为空");
      isSubmitting.value = false;
      return;
    }

    // 验证项目类型
    if (!formData.process_type) {
      ElMessage.error("请选择项目类型");
      isSubmitting.value = false;
      return;
    }

    // 提交前再做一次项目名查重
    await checkProjectName(projectName);
    if (!nameAvailable.value) {
      ElMessage.error("该项目名称已存在，请更换名称");
      isSubmitting.value = false;
      return;
    }

    // 文件来源处理
    let fileId: string | null = null;
    const isGenerationProject = formData.process_type === "generation";

    // 测试用例生成：必须有文件
    if (isGenerationProject) {
      // 情况1：文件管理页跳转过来的（fileRecord 已有）
      if (fileRecord.value) {
        fileId = fileRecord.value.id;
      }
      // 情况2：用户本地手动上传
      else if (selectedFile.value) {
        fileId = await uploadFile();
        if (!fileId) {
          isSubmitting.value = false;
          return;
        }
      }
      // 情况3：都没有
      else {
        ElMessage.error("测试用例生成项目必须上传文档");
        isSubmitting.value = false;
        return;
      }
    }

    // 测试用例重用：允许不上传文件（fileId 为空）

    // 调用后端创建项目接口
    try {
      const response = await createProjectApi({
        name: projectName,
        description: formData.description,
        process_type: formData.process_type,
        file_id: fileId || undefined
      });

      if (response.data.success) {
        ElMessage.success("项目创建成功！");
        resetForm();  // 清空表单状态
        router.push("/projects");
      } else {
        ElMessage.error("创建失败: " + response.data.message);
        if (response.status === 409) {
          nameAvailable.value = false;
        }
      }
    } catch (error: any) {
      console.error(error);
      ElMessage.error("网络错误，请稍后重试");
    } finally {
      isSubmitting.value = false;
    }
  };

  // 重置表单
  const resetForm = () => {
    formData.name = "";
    formData.description = "";
    formData.process_type = "";
    selectedFile.value = null;
    uploadProgress.value = 0;
    fileRecord.value = null;
    nameAvailable.value = true;
    isSubmitting.value = false;
    isDragOver.value = false;
  };

  return {
    // 状态
    formData,
    selectedFile,
    uploadProgress,
    isUploading,
    uploadStatus,
    fileRecord,
    nameAvailable,
    isSubmitting,
    isDragOver,
    hasFile,

    // 方法
    triggerFileInput,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleFileSelect,
    handleFile,
    removeFile,
    formatFileSize,
    uploadFile,
    loadFileRecord,
    checkProjectName,
    submitProject,
    resetForm
  };
});
