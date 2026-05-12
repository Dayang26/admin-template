export class ApiError extends Error {
  status: number
  code: number
  fieldErrors: Record<string, string>
  payload: unknown

  constructor({
    status,
    code,
    message,
    fieldErrors = {},
    payload,
  }: {
    status: number
    code?: number
    message: string
    fieldErrors?: Record<string, string>
    payload?: unknown
  }) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code ?? status
    this.fieldErrors = fieldErrors
    this.payload = payload
  }
}

function getMessageFromPayload(payload: unknown, fallback: string) {
  if (!payload || typeof payload !== 'object') return fallback

  const body = payload as Record<string, unknown>
  const message = body.message ?? body.detail
  if (typeof message === 'string' && message.trim()) {
    return message
  }

  return fallback
}

function getStatusMessage(status: number, fallback: string) {
  if (status === 401) return '登录状态已过期，请重新登录'
  if (status === 403) return '权限不足，无法执行该操作'
  if (status >= 500) return '服务器暂时不可用，请稍后重试'
  return fallback
}

function normalizeFieldPath(path: unknown) {
  if (Array.isArray(path)) {
    const parts = path.filter((part) => part !== 'body' && part !== 'query' && part !== 'path')
    return parts.join('.')
  }

  if (typeof path === 'string') {
    return path.replace(/^(body|query|path)\./, '')
  }

  return ''
}

function extractFieldErrors(payload: unknown): Record<string, string> {
  if (!payload || typeof payload !== 'object') return {}

  const body = payload as Record<string, unknown>
  const message = body.message ?? body.detail
  if (typeof message === 'string') {
    const match = message.match(/^([A-Za-z0-9_.]+):\s*(.+)$/)
    if (match) {
      return { [match[1]]: match[2] }
    }
  }

  const candidates = [body.errors, body.field_errors, body.data, body.detail]

  for (const candidate of candidates) {
    if (!candidate) continue

    if (Array.isArray(candidate)) {
      return candidate.reduce<Record<string, string>>((acc, item) => {
        if (!item || typeof item !== 'object') return acc
        const entry = item as Record<string, unknown>
        const field = normalizeFieldPath(entry.field ?? entry.loc ?? entry.name)
        const message = entry.message ?? entry.msg ?? entry.detail

        if (field && typeof message === 'string') {
          acc[field] = message
        }
        return acc
      }, {})
    }

    if (typeof candidate === 'object') {
      return Object.entries(candidate as Record<string, unknown>).reduce<Record<string, string>>(
        (acc, [field, value]) => {
          if (typeof value === 'string') {
            acc[field] = value
          } else if (Array.isArray(value) && typeof value[0] === 'string') {
            acc[field] = value[0]
          }
          return acc
        },
        {},
      )
    }
  }

  return {}
}

function redirectToLogin() {
  localStorage.removeItem('token')

  if (window.location.pathname === '/login') return

  const returnUrl = `${window.location.pathname}${window.location.search}`
  window.location.href = `/login?returnUrl=${encodeURIComponent(returnUrl)}`
}

function createApiError(status: number, payload: unknown, fallback: string) {
  const message = getStatusMessage(status, getMessageFromPayload(payload, fallback))
  const code =
    payload && typeof payload === 'object' && typeof (payload as Record<string, unknown>).code === 'number'
      ? ((payload as Record<string, unknown>).code as number)
      : status

  return new ApiError({
    status,
    code,
    message,
    fieldErrors: extractFieldErrors(payload),
    payload,
  })
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
      if (response.status === 401) redirectToLogin()
      throw createApiError(response.status, null, response.statusText || '请求失败')
    }
    return undefined as T
  }

  const json = await response.json()

  // 处理 401 - 清除 token 并带回当前地址，交给登录页恢复跳转
  if (response.status === 401) {
    redirectToLogin()
    throw createApiError(401, json, '登录状态已过期，请重新登录')
  }

  // 处理统一响应结构：{ code, message, data }
  if ('code' in json && 'data' in json) {
    if (json.code >= 200 && json.code < 300) {
      return json.data as T
    }

    if (json.code === 401) redirectToLogin()
    throw createApiError(response.ok ? json.code : response.status, json, '请求失败')
  }

  // 处理非包装响应（如登录 token 响应）
  if (!response.ok) {
    throw createApiError(response.status, json, '请求失败')
  }

  return json as T
}
