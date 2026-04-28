import { apiClient } from './client'
import type { LoginResponse } from '../types/user'

export async function login(
  email: string,
  password: string,
): Promise<LoginResponse> {
  const formData = new URLSearchParams()
  formData.append('username', email) // OAuth2 协议要求使用 'username' 字段
  formData.append('password', password)

  return apiClient<LoginResponse>('/api/v1/login/access-token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData.toString(),
  })
}
