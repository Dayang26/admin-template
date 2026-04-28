import { apiClient } from './client'
import type { UserPublic, UserDetail } from '../types/user'
import type { PaginatedData } from '../types/api'

export interface UserSearchParams {
  page?: number
  size?: number
  q?: string
  email?: string
  full_name?: string
  role?: string
  class_id?: string
}

export interface UserCreateByAdminData {
  email: string
  password: string
  full_name?: string
  is_active?: boolean
  roles: string[]
}

export interface UserUpdateData {
  full_name?: string | null
  password?: string | null
  is_active?: boolean | null
  roles?: string[] | null
}

export async function getUsers(params: UserSearchParams = {}): Promise<PaginatedData<UserPublic>> {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.size) searchParams.set('size', String(params.size))
  if (params.q) searchParams.set('q', params.q)
  if (params.email) searchParams.set('email', params.email)
  if (params.full_name) searchParams.set('full_name', params.full_name)
  if (params.role) searchParams.set('role', params.role)
  if (params.class_id) searchParams.set('class_id', params.class_id)

  const query = searchParams.toString()
  return apiClient<PaginatedData<UserPublic>>(`/api/v1/admin/users/${query ? `?${query}` : ''}`)
}

export async function getUserDetail(userId: string): Promise<UserDetail> {
  return apiClient<UserDetail>(`/api/v1/admin/users/${userId}`)
}

export async function createUserByAdmin(data: UserCreateByAdminData): Promise<UserPublic> {
  return apiClient<UserPublic>('/api/v1/admin/users/', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateUser(userId: string, data: UserUpdateData): Promise<UserPublic> {
  return apiClient<UserPublic>(`/api/v1/admin/users/${userId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

export async function deleteUser(userId: string): Promise<void> {
  await apiClient<null>(`/api/v1/admin/users/${userId}`, {
    method: 'DELETE',
  })
}
