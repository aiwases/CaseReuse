import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  downloadUpload,
  downloadNewDocument,
  downloadOldTestCase,
  downloadIntermediate,
  downloadResult
} from '@/api/result'

export const useResultStore = defineStore('result', () => {
  // 状态
  const isDownloading = ref(false)
  const downloadError = ref<string | null>(null)

  // 下载上传文件
  const handleDownloadUpload = async (projectId: number) => {
    try {
      isDownloading.value = true
      downloadError.value = null
      await downloadUpload(projectId)
      return true
    } catch (error) {
      downloadError.value = '下载上传文件失败'
      console.error('下载上传文件失败:', error)
      throw error
    } finally {
      isDownloading.value = false
    }
  }

  // 下载新文档
  const handleDownloadNewDocument = async (projectId: number) => {
    try {
      isDownloading.value = true
      downloadError.value = null
      await downloadNewDocument(projectId)
      return true
    } catch (error) {
      downloadError.value = '下载新文档失败'
      console.error('下载新文档失败:', error)
      throw error
    } finally {
      isDownloading.value = false
    }
  }

  // 下载旧测试用例
  const handleDownloadOldTestCase = async (projectId: number) => {
    try {
      isDownloading.value = true
      downloadError.value = null
      await downloadOldTestCase(projectId)
      return true
    } catch (error) {
      downloadError.value = '下载旧测试用例失败'
      console.error('下载旧测试用例失败:', error)
      throw error
    } finally {
      isDownloading.value = false
    }
  }

  // 下载中间结果
  const handleDownloadIntermediate = async (projectId: number, index: number) => {
    try {
      isDownloading.value = true
      downloadError.value = null
      await downloadIntermediate(projectId, index)
      return true
    } catch (error) {
      downloadError.value = '下载中间结果失败'
      console.error('下载中间结果失败:', error)
      throw error
    } finally {
      isDownloading.value = false
    }
  }

  // 下载最终结果
  const handleDownloadResult = async (projectId: number) => {
    try {
      isDownloading.value = true
      downloadError.value = null
      await downloadResult(projectId)
      return true
    } catch (error) {
      downloadError.value = '下载最终结果失败'
      console.error('下载最终结果失败:', error)
      throw error
    } finally {
      isDownloading.value = false
    }
  }

  // 清除错误
  const clearError = () => {
    downloadError.value = null
  }

  return {
    // 状态
    isDownloading,
    downloadError,

    // Actions
    handleDownloadUpload,
    handleDownloadNewDocument,
    handleDownloadOldTestCase,
    handleDownloadIntermediate,
    handleDownloadResult,
    clearError
  }
})
