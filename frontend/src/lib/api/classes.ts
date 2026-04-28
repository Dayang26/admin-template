import { apiClient } from './client'
import type { ClassPublic, ClassMember } from '../types/class'
import type { PaginatedData } from '../types/api'

export interface ClassSearchParams {
  page?: number
  size?: number
  name?: string
}

export interface ClassCreateData {
  name: string
  description?: string
}

export interface ClassUpdateData {
  name?: string | null
  description?: string | null
}

export interface ClassMemberAddData {
  user_id: string
  role: string
}

export async function getClasses(params: ClassSearchParams = {}): Promise<PaginatedData<ClassPublic>> {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.size) searchParams.set('size', String(params.size))
  if (params.name) searchParams.set('name', params.name)

  const query = searchParams.toString()
  return apiClient<PaginatedData<ClassPublic>>(`/api/v1/admin/classes/${query ? `?${query}` : ''}`)
}

export async function getClassDetail(classId: string): Promise<ClassPublic> {
  return apiClient<ClassPublic>(`/api/v1/admin/classes/${classId}`)
}

export async function createClass(data: ClassCreateData): Promise<ClassPublic> {
  return apiClient<ClassPublic>('/api/v1/admin/classes/', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateClass(classId: string, data: ClassUpdateData): Promise<ClassPublic> {
  return apiClient<ClassPublic>(`/api/v1/admin/classes/${classId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

export async function deleteClass(classId: string): Promise<void> {
  await apiClient<null>(`/api/v1/admin/classes/${classId}`, {
    method: 'DELETE',
  })
}

export async function getClassMembers(classId: string, params: { page?: number; size?: number } = {}): Promise<PaginatedData<ClassMember>> {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.size) searchParams.set('size', String(params.size))

  const query = searchParams.toString()
  return apiClient<PaginatedData<ClassMember>>(`/api/v1/admin/classes/${classId}/members${query ? `?${query}` : ''}`)
}

export async function addClassMember(classId: string, data: ClassMemberAddData): Promise<void> {
  await apiClient<null>(`/api/v1/admin/classes/${classId}/members`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function removeClassMember(classId: string, userId: string): Promise<void> {
  await apiClient<null>(`/api/v1/admin/classes/${classId}/members/${userId}`, {
    method: 'DELETE',
  })
}
