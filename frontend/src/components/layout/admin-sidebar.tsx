import { LayoutDashboard, Users, School, BookOpen, ClipboardList, ShieldCheck } from 'lucide-react'
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
  roles: string[]
}

const navItems: NavItem[] = [
  {
    title: '仪表盘',
    url: '/admin',
    icon: LayoutDashboard,
    roles: ['superuser'],
  },
  {
    title: '用户管理',
    url: '/admin/users',
    icon: Users,
    roles: ['superuser'],
  },
  {
    title: '班级管理',
    url: '/admin/classes',
    icon: School,
    roles: ['superuser'],
  },
  {
    title: '我的班级',
    url: '/admin/my-classes',
    icon: BookOpen,
    roles: ['teacher'],
  },
  {
    title: '操作日志',
    url: '/admin/audit-logs',
    icon: ClipboardList,
    roles: ['superuser'],
  },
  {
    title: '角色管理',
    url: '/admin/roles',
    icon: ShieldCheck,
    roles: ['superuser'],
  },
]

export function AdminSidebar() {
  const { user } = useAuth()
  const location = useLocation()

  const filteredItems = navItems.filter((item) =>
    item.roles.some((role) => user?.roles.includes(role)),
  )

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link to="/admin">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                  <School className="size-4" />
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
