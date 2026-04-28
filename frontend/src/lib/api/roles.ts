import { apiClient } from './client'
import type { RoleItem, PermissionItem } from '../types/role'

export async function getRoles(): Promise<RoleItem[]> {
  return apiClient<RoleItem[]>('/api/v1/admin/roles/')
}

export async function createRole(data: { name: string; description?: string }): Promise<RoleItem> {
  return apiClient<RoleItem>('/api/v1/admin/roles/', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateRole(roleId: string, data: { name?: string; description?: string }): Promise<RoleItem> {
  return apiClient<RoleItem>(`/api/v1/admin/roles/${roleId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

export async function deleteRole(roleId: string): Promise<void> {
  await apiClient<null>(`/api/v1/admin/roles/${roleId}`, {
    method: 'DELETE',
  })
}

export async function updateRolePermissions(roleId: string, permissionIds: string[]): Promise<RoleItem> {
  return apiClient<RoleItem>(`/api/v1/admin/roles/${roleId}/permissions`, {
    method: 'PUT',
    body: JSON.stringify({ permission_ids: permissionIds }),
  })
}

export async function getPermissions(): Promise<PermissionItem[]> {
  return apiClient<PermissionItem[]>('/api/v1/admin/roles/permissions')
}
