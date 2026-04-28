import { apiClient } from './client'
import type { UserDetail, UserPublic } from '../types/user'

export async function getMe(): Promise<UserDetail> {
  return apiClient<UserDetail>('/api/v1/users/me')
}

export async function updateMe(data: { full_name?: string | null }): Promise<UserPublic> {
  return apiClient<UserPublic>('/api/v1/users/me', {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

export async function changePassword(data: {
  current_password: string
  new_password: string
}): Promise<void> {
  await apiClient<null>('/api/v1/users/me/password', {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}
