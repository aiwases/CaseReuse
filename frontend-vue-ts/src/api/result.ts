import service from './index'

// 下载上传文件
export const downloadUpload = async (projectId: number) => {
  try {
    const response = await service.get(`/result/download/upload/${projectId}`, {
      responseType: 'blob'
    });

    const url = window.URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `upload_${projectId}.pdf`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('下载上传文件失败:', error);
    throw error;
  }
};

// 下载新文档
export const downloadNewDocument = async (projectId: number) => {
  try {
    const response = await service.get(`/result/download/new-document/${projectId}`, {
      responseType: 'blob'
    });

    const url = window.URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `new_document_${projectId}.pdf`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('下载新文档失败:', error);
    throw error;
  }
};

// 下载旧测试用例
export const downloadOldTestCase = async (projectId: number) => {
  try {
    const response = await service.get(`/result/download/old-test-case/${projectId}`, {
      responseType: 'blob'
    });

    const url = window.URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `old_test_case_${projectId}.pdf`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('下载旧测试用例失败:', error);
    throw error;
  }
};

// 下载中间结果
export const downloadIntermediate = async (projectId: number, index: number) => {
  if (index < 1 || index > 6) {
    throw new Error('index 必须在 1~6 之间');
  }

  try {
    const response = await service.get(`/result/download/intermediate/${projectId}/${index}`, {
      responseType: 'blob'
    });

    const url = window.URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `intermediate_${projectId}_${index}.pdf`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('下载中间结果失败:', error);
    throw error;
  }
};

// 下载最终结果
export const downloadResult = async (projectId: number) => {
  try {
    const response = await service.get(`/result/download/result/${projectId}`, {
      responseType: 'blob'
    });

    const url = window.URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `result_${projectId}.pdf`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('下载最终结果失败:', error);
    throw error;
  }
};
