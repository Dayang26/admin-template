import type { UserDetail } from '@/lib/types/user'

const ADMIN_ROUTE_BY_PERMISSION: Array<[string, string]> = [
  ['dashboard:read', '/admin'],
  ['user:read', '/admin/users'],
  ['role:read', '/admin/roles'],
  ['audit_log:read', '/admin/audit-logs'],
  ['system_setting:read', '/admin/system-settings'],
]

export function getDefaultRoute(
  user: UserDetail | null | undefined,
  defaultHomePath?: string
): string {
  if (!user) return '/login'
  
  const isSuperuser = user.roles.includes('superuser')
  const permissions = user.permissions ?? []

  // 如果系统设置了 defaultHomePath，优先尝试该路径
  if (defaultHomePath) {
    if (isSuperuser || defaultHomePath === '/profile') return defaultHomePath
    
    // 检查该路径是否属于受控管理端路由
    const routeConfig = [...ADMIN_ROUTE_BY_PERMISSION]
      .sort((a, b) => b[1].length - a[1].length)
      .find(([, path]) => defaultHomePath.startsWith(path))
      
    // 如果不在受控列表内，或者用户拥有对应的权限，则允许跳转
    if (!routeConfig || permissions.includes(routeConfig[0])) {
      return defaultHomePath
    }
  }

  // 兜底逻辑：无 defaultHomePath 或无权限时的默认跳转
  if (isSuperuser) return '/admin'

  const matched = ADMIN_ROUTE_BY_PERMISSION.find(([permission]) =>
    permissions.includes(permission),
  )

  return matched?.[1] ?? '/profile'
}
