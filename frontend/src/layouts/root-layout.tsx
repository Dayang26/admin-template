import { Outlet } from 'react-router-dom'
import { AuthProvider } from '@/lib/auth/context'
import { ErrorBoundary } from '@/components/shared/error-boundary'

export function RootLayout() {
  return (
    <AuthProvider>
      <ErrorBoundary>
        <Outlet />
      </ErrorBoundary>
    </AuthProvider>
  )
}
