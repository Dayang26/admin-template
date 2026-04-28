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

  // Already logged in - redirect based on role
  if (user) {
    if (user.roles.includes('superuser') || user.roles.includes('teacher')) {
      return <Navigate to="/admin" replace />
    }
    return <Navigate to="/" replace />
  }

  return <Outlet />
}
