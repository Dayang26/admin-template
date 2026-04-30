import { useLocation } from 'react-router-dom'
import { Separator } from '@/components/ui/separator'
import { SidebarTrigger } from '@/components/ui/sidebar'
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'
import { ThemeToggle } from './theme-toggle'

const breadcrumbMap: Record<string, string> = {
  '/admin': '仪表盘',
  '/admin/users': '用户管理',
  '/admin/users/create': '创建用户',
  '/admin/audit-logs': '日志审计',
  '/admin/roles': '权限管理',
  '/admin/system-settings': '系统设置',
}

function getBreadcrumbs(pathname: string) {
  // 处理动态路由，如 /admin/users/:id
  const segments = pathname.split('/').filter(Boolean)
  const crumbs: { label: string; href?: string }[] = []

  if (segments.length >= 2 && segments[0] === 'admin') {
    // 始终添加管理后台根面包屑
    crumbs.push({ label: '管理后台', href: '/admin' })

    if (segments.length === 1) {
      // /admin
      return crumbs
    }

    const section = segments[1]
    const sectionPath = `/admin/${section}`
    const sectionLabel = breadcrumbMap[sectionPath]

    if (segments.length === 2) {
      // /admin/users
      if (sectionLabel) {
        crumbs.push({ label: sectionLabel })
      }
    } else if (segments.length === 3) {
      // /admin/users/create 或 /admin/users/:id
      if (sectionLabel) {
        crumbs.push({ label: sectionLabel, href: sectionPath })
      }

      const subPath = `/admin/${section}/${segments[2]}`
      const subLabel = breadcrumbMap[subPath]
      if (subLabel) {
        crumbs.push({ label: subLabel })
      } else {
        crumbs.push({ label: '详情' })
      }
    }
  }

  return crumbs
}

export function AdminTopbar() {
  const location = useLocation()
  const crumbs = getBreadcrumbs(location.pathname)

  return (
    <header className="flex h-14 shrink-0 items-center gap-2 border-b px-4">
      <SidebarTrigger className="-ml-1" />
      <Separator orientation="vertical" className="mr-2 h-4" />

      <Breadcrumb className="flex-1">
        <BreadcrumbList>
          {crumbs.map((crumb, index) => {
            const isLast = index === crumbs.length - 1
            return (
              <BreadcrumbItem key={crumb.label}>
                {index > 0 && <BreadcrumbSeparator />}
                {isLast ? (
                  <BreadcrumbPage>{crumb.label}</BreadcrumbPage>
                ) : (
                  <BreadcrumbLink href={crumb.href}>
                    {crumb.label}
                  </BreadcrumbLink>
                )}
              </BreadcrumbItem>
            )
          })}
        </BreadcrumbList>
      </Breadcrumb>

      <ThemeToggle />
    </header>
  )
}
