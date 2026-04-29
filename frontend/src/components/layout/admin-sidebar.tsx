import { LayoutDashboard, Users, Shield, ClipboardList, ShieldCheck, Settings } from 'lucide-react'
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
import { useSystemSettingsContext } from '@/lib/system-settings/context'

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
    title: '日志审计',
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
  {
    title: '系统设置',
    url: '/admin/system-settings',
    icon: Settings,
    permissions: ['system_setting:read'],
  },
]

export function AdminSidebar({ className }: { className?: string }) {
  const { hasPermission } = useAuth()
  const location = useLocation()
  const { settings } = useSystemSettingsContext()

  const filteredItems = navItems.filter((item) =>
    item.permissions.some((perm) => hasPermission(perm)),
  )

  return (
    <Sidebar collapsible="icon" className={className}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link to="/admin">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-primary/10 text-primary overflow-hidden">
                  {settings?.logo_light_url ? (
                    <>
                      <img src={settings.logo_light_url} className="h-full w-full object-contain p-1 dark:hidden" alt="Logo" />
                      {settings?.logo_dark_url ? (
                        <img src={settings.logo_dark_url} className="h-full w-full object-contain p-1 hidden dark:block" alt="Logo" />
                      ) : (
                        <img src={settings.logo_light_url} className="h-full w-full object-contain p-1 hidden dark:block" alt="Logo" />
                      )}
                    </>
                  ) : (
                    <Shield className="size-4" />
                  )}
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">{settings?.system_name || 'Carrier Agent'}</span>
                  <span className="truncate text-xs text-muted-foreground">
                    {settings?.tagline || '管理后台'}
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
