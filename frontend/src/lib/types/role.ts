export interface PermissionItem {
  id: string
  resource: string
  action: string
}

export interface RoleItem {
  id: string
  name: string
  description: string | null
  is_builtin: boolean
  permissions: PermissionItem[]
}
