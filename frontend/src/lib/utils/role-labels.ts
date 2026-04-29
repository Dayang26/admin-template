/** 角色名到中文标签的映射 */
export const ROLE_LABELS: Record<string, string> = {
  superuser: '超级管理员',
}

/** 获取角色的中文显示名称 */
export function getRoleLabel(roleName: string): string {
  return ROLE_LABELS[roleName] ?? roleName
}
