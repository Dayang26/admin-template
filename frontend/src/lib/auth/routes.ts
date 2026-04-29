import type { UserDetail } from '@/lib/types/user'

const ADMIN_ROUTE_BY_PERMISSION: Array<[string, string]> = [
  ['dashboard:read', '/admin'],
  ['user:read', '/admin/users'],
  ['role:read', '/admin/roles'],
  ['audit_log:read', '/admin/audit-logs'],
  ['system_setting:read', '/admin/system-settings'],
]

export function getDefaultRoute(user: UserDetail | null | undefined): string {
  if (!user) return '/login'

  const isSuperuser = user.roles.includes('superuser')
  const permissions = user.permissions ?? []

  if (isSuperuser) return '/admin'

  const matched = ADMIN_ROUTE_BY_PERMISSION.find(([permission]) =>
    permissions.includes(permission),
  )

  return matched?.[1] ?? '/profile'
}
