import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './context'
import type { ReactNode } from 'react'

interface RequireAuthProps {
  children: ReactNode
  roles?: string[]
}

export function RequireAuth({ children, roles }: RequireAuthProps) {
  const { user, isLoading, token } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (!token || !user) {
    return (
      <Navigate
        to={`/login?returnUrl=${encodeURIComponent(location.pathname)}`}
        replace
      />
    )
  }

  if (roles && roles.length > 0) {
    const hasRole = roles.some((role) => user.roles.includes(role))
    if (!hasRole) {
      // 根据用户实际角色重定向
      if (user.roles.includes('student')) {
        return <Navigate to="/" replace />
      }
      return <Navigate to="/admin" replace />
    }
  }

  return children
}
