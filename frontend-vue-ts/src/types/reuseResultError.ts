export const isMissingResultFileError = (err: any): boolean => {
  const status = err?.response?.status
  const rawMessage =
    err?.response?.data?.error ||
    err?.response?.data?.msg ||
    err?.response?.data?.message ||
    err?.message ||
    ""
  const message = String(rawMessage).toLowerCase()

  return (
    status === 404 ||
    message.includes("file not found") ||
    message.includes("not found") ||
    message.includes("no such file") ||
    message.includes("文件不存在") ||
    message.includes("文件缺失") ||
    message.includes("文件为空") ||
    message.includes("empty")
  )
}

export const resolveReuseResultErrorMessage = (
  err: any,
  missingResultName: string,
  fallbackMessage: string
): string => {
  if (isMissingResultFileError(err)) {
    return `${missingResultName}文件缺失`
  }

  return (
    err?.response?.data?.error ||
    err?.response?.data?.msg ||
    err?.response?.data?.message ||
    fallbackMessage
  )
}
