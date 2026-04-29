import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './context'
import { getDefaultRoute } from './routes'
import type { ReactNode } from 'react'

interface RequireAuthProps {
  children: ReactNode
  roles?: string[]
  permissions?: string[]
}

export function RequireAuth({ children, roles, permissions }: RequireAuthProps) {
  const { user, isLoading, token, hasPermission } = useAuth()
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
      return <Navigate to={getDefaultRoute(user)} replace />
    }
  }

  if (permissions && permissions.length > 0) {
    const allowed = permissions.some((permission) => hasPermission(permission))
    if (!allowed) {
      return <Navigate to={getDefaultRoute(user)} replace />
    }
  }

  return children
}
