import { LayoutDashboard, Users, Shield, ClipboardList, ShieldCheck } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '@/lib/auth/context'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from '@/components/ui/sidebar'
import { UserMenu } from './user-menu'

interface NavItem {
  title: string
  url: string
  icon: React.ComponentType<{ className?: string }>
  /** 需要的权限，满足任一即可显示 */
  permissions: string[]
}

const navItems: NavItem[] = [
  {
    title: '仪表盘',
    url: '/admin',
    icon: LayoutDashboard,
    permissions: ['dashboard:read'],
  },
  {
    title: '用户管理',
    url: '/admin/users',
    icon: Users,
    permissions: ['user:read'],
  },
  {
    title: '操作日志',
    url: '/admin/audit-logs',
    icon: ClipboardList,
    permissions: ['audit_log:read'],
  },
  {
    title: '角色管理',
    url: '/admin/roles',
    icon: ShieldCheck,
    permissions: ['role:read'],
  },
]

export function AdminSidebar() {
  const { hasPermission } = useAuth()
  const location = useLocation()

  const filteredItems = navItems.filter((item) =>
    item.permissions.some((perm) => hasPermission(perm)),
  )

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link to="/admin">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                  <Shield className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">Carrier Agent</span>
                  <span className="truncate text-xs text-muted-foreground">
                    管理后台
                  </span>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>导航菜单</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {filteredItems.map((item) => {
                const isActive =
                  item.url === '/admin'
                    ? location.pathname === '/admin'
                    : location.pathname.startsWith(item.url)

                return (
                  <SidebarMenuItem key={item.url}>
                    <SidebarMenuButton
                      asChild
                      isActive={isActive}
                      tooltip={item.title}
                    >
                      <Link to={item.url}>
                        <item.icon className="size-4" />
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                )
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <UserMenu />
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  )
}
