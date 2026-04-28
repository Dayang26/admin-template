import { apiClient } from './client'
import type { ClassPublic, ClassMember } from '../types/class'
import type { PaginatedData } from '../types/api'

export async function getMyClasses(): Promise<ClassPublic[]> {
  return apiClient<ClassPublic[]>('/api/v1/teacher/classes')
}

export async function getMyClassMembers(
  classId: string,
  params: { page?: number; size?: number } = {},
): Promise<PaginatedData<ClassMember>> {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.size) searchParams.set('size', String(params.size))

  const query = searchParams.toString()
  return apiClient<PaginatedData<ClassMember>>(
    `/api/v1/teacher/classes/${classId}/members${query ? `?${query}` : ''}`,
  )
}
