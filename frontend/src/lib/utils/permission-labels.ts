import type { PermissionItem } from '../types/role'

/** 资源名到中文标签的映射 */
export const RESOURCE_LABELS: Record<string, string> = {
  user: '用户管理',
  role: '角色管理',
  audit_log: '审计日志',
  dashboard: '仪表盘',
}

/** 操作名到中文标签的映射 */
export const ACTION_LABELS: Record<string, string> = {
  create: '创建',
  read: '查看',
  update: '编辑',
  delete: '删除',
}

/** 获取资源的中文显示名称 */
export function getResourceLabel(resource: string): string {
  return RESOURCE_LABELS[resource] ?? resource
}

/** 获取操作的中文显示名称 */
export function getActionLabel(action: string): string {
  return ACTION_LABELS[action] ?? action
}

/** 获取权限的中文显示名称 */
export function getPermissionLabel(resource: string, action: string): string {
  return `${getResourceLabel(resource)}：${getActionLabel(action)}`
}

/** 按资源分组权限 */
export function groupPermissionsByResource(
  permissions: PermissionItem[],
): Record<string, PermissionItem[]> {
  const groups: Record<string, PermissionItem[]> = {}
  for (const perm of permissions) {
    if (!groups[perm.resource]) {
      groups[perm.resource] = []
    }
    groups[perm.resource].push(perm)
  }
  return groups
}

/** 格式化权限列表为聚合显示（返回数组，每项为一个资源的权限摘要） */
export function formatAggregatedPermissions(permissions: PermissionItem[]): string[] {
  const groups = groupPermissionsByResource(permissions)
  return Object.entries(groups).map(([resource, perms]) => {
    const actions = perms.map((p) => getActionLabel(p.action)).join('/')
    return `${getResourceLabel(resource)}(${actions})`
  })
}
