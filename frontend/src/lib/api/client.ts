export class ApiError extends Error {
  code: number

  constructor(code: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.code = code
  }
}

export async function apiClient<T>(
  url: string,
  options?: RequestInit,
): Promise<T> {
  const token = localStorage.getItem('token')

  const headers: Record<string, string> = {
    ...(options?.headers as Record<string, string>),
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // 默认设置 Content-Type 为 JSON，除非已设置或 body 不是 JSON 或 FormData
  const isFormData = options?.body instanceof FormData
  if (!headers['Content-Type'] && !isFormData && !(options?.body instanceof URLSearchParams)) {
    headers['Content-Type'] = 'application/json'
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  // 处理非 JSON 响应
  const contentType = response.headers.get('content-type')
  if (!contentType?.includes('application/json')) {
    if (!response.ok) {
      throw new ApiError(response.status, `请求失败: ${response.statusText}`)
    }
    return undefined as T
  }

  const json = await response.json()

  // 处理 401 - 清除 token 并跳转到登录页
  if (response.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    throw new ApiError(401, json.message ?? '未授权，请重新登录')
  }

  // 处理统一响应结构：{ code, message, data }
  if ('code' in json && 'data' in json) {
    if (json.code >= 200 && json.code < 300) {
      return json.data as T
    }
    throw new ApiError(json.code, json.message ?? '请求失败')
  }

  // 处理非包装响应（如登录 token 响应）
  if (!response.ok) {
    throw new ApiError(
      response.status,
      json.message ?? json.detail ?? '请求失败',
    )
  }

  return json as T
}
