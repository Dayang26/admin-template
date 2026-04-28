import { lazy, Suspense } from 'react'
import { createBrowserRouter } from 'react-router-dom'
import { RequireAuth } from '@/lib/auth/guard'
import { RootLayout } from '@/layouts/root-layout'
import { AuthLayout } from '@/layouts/auth-layout'
import { AdminLayout } from '@/layouts/admin-layout'
import { StudentLayout } from '@/layouts/student-layout'
import { RouteErrorPage } from '@/pages/route-error'

// 懒加载页面
const LoginPage = lazy(() =>
  import('@/pages/login').then((m) => ({ default: m.LoginPage })),
)
const StudentHomePage = lazy(() =>
  import('@/pages/student/home').then((m) => ({ default: m.StudentHomePage })),
)
const ProfilePage = lazy(() =>
  import('@/pages/student/profile').then((m) => ({ default: m.ProfilePage })),
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
const ClassListPage = lazy(() =>
  import('@/pages/admin/classes/list').then((m) => ({ default: m.ClassListPage })),
)
const ClassCreatePage = lazy(() =>
  import('@/pages/admin/classes/create').then((m) => ({ default: m.ClassCreatePage })),
)
const ClassDetailPage = lazy(() =>
  import('@/pages/admin/classes/detail').then((m) => ({ default: m.ClassDetailPage })),
)
const MyClassListPage = lazy(() =>
  import('@/pages/admin/my-classes/list').then((m) => ({ default: m.MyClassListPage })),
)
const MyClassDetailPage = lazy(() =>
  import('@/pages/admin/my-classes/detail').then((m) => ({ default: m.MyClassDetailPage })),
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

      // 学生路由
      {
        element: (
          <RequireAuth roles={['student']}>
            <StudentLayout />
          </RequireAuth>
        ),
        children: [
          {
            path: '/',
            element: (
              <SuspenseWrapper>
                <StudentHomePage />
              </SuspenseWrapper>
            ),
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
          <RequireAuth roles={['teacher', 'superuser']}>
            <AdminLayout />
          </RequireAuth>
        ),
        children: [
          {
            path: '/admin',
            element: (
              <SuspenseWrapper>
                <DashboardPage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/admin/users',
            element: (
              <SuspenseWrapper>
                <UserListPage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/admin/users/create',
            element: (
              <SuspenseWrapper>
                <UserCreatePage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/admin/users/:id',
            element: (
              <SuspenseWrapper>
                <UserDetailPage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/admin/classes',
            element: (
              <SuspenseWrapper>
                <ClassListPage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/admin/classes/create',
            element: (
              <SuspenseWrapper>
                <ClassCreatePage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/admin/classes/:id',
            element: (
              <SuspenseWrapper>
                <ClassDetailPage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/admin/my-classes',
            element: (
              <SuspenseWrapper>
                <MyClassListPage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/admin/my-classes/:id',
            element: (
              <SuspenseWrapper>
                <MyClassDetailPage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/admin/audit-logs',
            element: (
              <SuspenseWrapper>
                <AuditLogsPage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/admin/roles',
            element: (
              <SuspenseWrapper>
                <RolesPage />
              </SuspenseWrapper>
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
