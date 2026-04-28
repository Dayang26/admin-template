import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '@/lib/auth/context'

export function AuthLayout() {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-muted/50">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  // 已登录 — 根据权限重定向
  if (user) {
    if (user.roles.includes('superuser')) {
      return <Navigate to="/admin" replace />
    }
    if (user.roles.includes('teacher') || user.roles.includes('superuser')) {
      // 有 dashboard 权限去仪表盘，否则去我的班级
      const perms = user.permissions ?? []
      if (perms.includes('dashboard:read')) {
        return <Navigate to="/admin" replace />
      }
      if (perms.includes('class:read')) {
        return <Navigate to="/admin/my-classes" replace />
      }
      return <Navigate to="/admin" replace />
    }
    return <Navigate to="/" replace />
  }

  return <Outlet />
}
