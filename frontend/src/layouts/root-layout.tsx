import { Outlet } from 'react-router-dom'
import { AuthProvider } from '@/lib/auth/context'
import { ErrorBoundary } from '@/components/shared/error-boundary'
import { SystemSettingsProvider } from '@/lib/system-settings/context'
import { PageTitleSync } from '@/lib/system-settings/title-hook'

export function RootLayout() {
  return (
    <AuthProvider>
      <SystemSettingsProvider>
        <ErrorBoundary>
          <PageTitleSync />
          <Outlet />
        </ErrorBoundary>
      </SystemSettingsProvider>
    </AuthProvider>
  )
}
