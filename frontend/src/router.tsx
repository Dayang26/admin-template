import { lazy, Suspense } from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { RequireAuth } from '@/lib/auth/guard'
import { RootLayout } from '@/layouts/root-layout'
import { AuthLayout } from '@/layouts/auth-layout'
import { AdminLayout } from '@/layouts/admin-layout'
import { UserLayout } from '@/layouts/user-layout'
import { RouteErrorPage } from '@/pages/route-error'

// 懒加载页面
const LoginPage = lazy(() =>
  import('@/pages/login').then((m) => ({ default: m.LoginPage })),
)
const ProfilePage = lazy(() =>
  import('@/pages/profile').then((m) => ({ default: m.ProfilePage })),
)
const DashboardPage = lazy(() =>
  import('@/pages/admin/dashboard').then((m) => ({ default: m.DashboardPage })),
)
const UserListPage = lazy(() =>
  import('@/pages/admin/users/list').then((m) => ({ default: m.UserListPage })),
)
const UserCreatePage = lazy(() =>
  import('@/pages/admin/users/create').then((m) => ({ default: m.UserCreatePage })),
)
const UserDetailPage = lazy(() =>
  import('@/pages/admin/users/detail').then((m) => ({ default: m.UserDetailPage })),
)
const AuditLogsPage = lazy(() =>
  import('@/pages/admin/audit-logs').then((m) => ({ default: m.AuditLogsPage })),
)
const RolesPage = lazy(() =>
  import('@/pages/admin/roles').then((m) => ({ default: m.RolesPage })),
)
const NotFoundPage = lazy(() =>
  import('@/pages/not-found').then((m) => ({ default: m.NotFoundPage })),
)

function PageLoader() {
  return (
    <div className="flex min-h-[50vh] items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
    </div>
  )
}

function SuspenseWrapper({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<PageLoader />}>{children}</Suspense>
}

export const router = createBrowserRouter([
  {
    element: <RootLayout />,
    errorElement: <RouteErrorPage />,
    children: [
      // 认证路由
      {
        element: <AuthLayout />,
        children: [
          {
            path: '/login',
            element: (
              <SuspenseWrapper>
                <LoginPage />
              </SuspenseWrapper>
            ),
          },
        ],
      },

      // 当前用户资料
      {
        element: (
          <RequireAuth>
            <UserLayout />
          </RequireAuth>
        ),
        children: [
          {
            path: '/',
            element: <Navigate to="/profile" replace />,
          },
          {
            path: '/profile',
            element: (
              <SuspenseWrapper>
                <ProfilePage />
              </SuspenseWrapper>
            ),
          },
        ],
      },

      // 管理端路由
      {
        element: (
          <RequireAuth>
            <AdminLayout />
          </RequireAuth>
        ),
        children: [
          {
            path: '/admin',
            element: (
              <RequireAuth permissions={['dashboard:read']}>
                <SuspenseWrapper>
                  <DashboardPage />
                </SuspenseWrapper>
              </RequireAuth>
            ),
          },
          {
            path: '/admin/users',
            element: (
              <RequireAuth permissions={['user:read']}>
                <SuspenseWrapper>
                  <UserListPage />
                </SuspenseWrapper>
              </RequireAuth>
            ),
          },
          {
            path: '/admin/users/create',
            element: (
              <RequireAuth permissions={['user:create']}>
                <SuspenseWrapper>
                  <UserCreatePage />
                </SuspenseWrapper>
              </RequireAuth>
            ),
          },
          {
            path: '/admin/users/:id',
            element: (
              <RequireAuth permissions={['user:read']}>
                <SuspenseWrapper>
                  <UserDetailPage />
                </SuspenseWrapper>
              </RequireAuth>
            ),
          },
          {
            path: '/admin/audit-logs',
            element: (
              <RequireAuth permissions={['audit_log:read']}>
                <SuspenseWrapper>
                  <AuditLogsPage />
                </SuspenseWrapper>
              </RequireAuth>
            ),
          },
          {
            path: '/admin/roles',
            element: (
              <RequireAuth permissions={['role:read']}>
                <SuspenseWrapper>
                  <RolesPage />
                </SuspenseWrapper>
              </RequireAuth>
            ),
          },
        ],
      },

      // 404
      {
        path: '*',
        element: (
          <SuspenseWrapper>
            <NotFoundPage />
          </SuspenseWrapper>
        ),
      },
    ],
  },
])
