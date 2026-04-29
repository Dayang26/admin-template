import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '@/lib/auth/context'
import { getDefaultRoute } from '@/lib/auth/routes'

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
    return <Navigate to={getDefaultRoute(user)} replace />
  }

  return <Outlet />
}
