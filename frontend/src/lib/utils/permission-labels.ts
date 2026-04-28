import type { PermissionItem } from '@/lib/types/role'

/** 资源的中文化映射 */
export const RESOURCE_LABELS: Record<string, string> = {
  user: '用户管理',
  class: '班级管理',
}

/** 操作的中文化映射 */
export const ACTION_LABELS: Record<string, string> = {
  create: '创建',
  read: '查看',
  update: '编辑',
  delete: '删除',
}

/** 所有的可能操作集合，用于判断是否拥有“全部权限” */
const ALL_ACTIONS = ['create', 'read', 'update', 'delete']

/** 获取资源中文名 */
export function getResourceLabel(resource: string): string {
  return RESOURCE_LABELS[resource] ?? resource
}

/** 获取操作中文名 */
export function getActionLabel(action: string): string {
  return ACTION_LABELS[action] ?? action
}

/** 将平铺的权限列表按资源分组 */
export function groupPermissionsByResource(permissions: PermissionItem[]) {
  const groups: Record<string, PermissionItem[]> = {}
  permissions.forEach((perm) => {
    if (!groups[perm.resource]) {
      groups[perm.resource] = []
    }
    groups[perm.resource].push(perm)
  })
  return groups
}

/**
 * 聚合格式化权限列表，用于在角色卡片上展示。
 * 规则：
 * - 拥有一项资源的所有动作（create, read, update, delete）则聚合为 "XX管理：全部权限"
 * - 否则展示为 "XX管理：查看、编辑"
 */
export function formatAggregatedPermissions(permissions: PermissionItem[]): string[] {
  if (!permissions || permissions.length === 0) return []

  const groups = groupPermissionsByResource(permissions)
  const result: string[] = []

  for (const [resource, perms] of Object.entries(groups)) {
    const resourceLabel = getResourceLabel(resource)
    const actions = perms.map((p) => p.action)

    // 检查是否包含所有基础的 CRUD 权限
    const hasAll = ALL_ACTIONS.every((a) => actions.includes(a))

    if (hasAll && actions.length >= ALL_ACTIONS.length) {
      result.push(`${resourceLabel}：全部权限`)
    } else {
      // 对动作进行排序，避免顺序错乱（可选）
      const sortedActions = [...actions].sort((a, b) => {
        return ALL_ACTIONS.indexOf(a) - ALL_ACTIONS.indexOf(b)
      })
      const actionLabels = sortedActions.map(getActionLabel).join('、')
      result.push(`${resourceLabel}：${actionLabels}`)
    }
  }

  return result
}
