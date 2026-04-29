import { Outlet } from 'react-router-dom'
import { SidebarProvider } from '@/components/ui/sidebar'
import { AdminSidebar } from '@/components/layout/admin-sidebar'
import { AdminTopbar } from '@/components/layout/admin-topbar'
import { useSystemSettingsContext } from '@/lib/system-settings/context'
import { cn } from '@/lib/utils'

export function AdminLayout() {
  const { settings } = useSystemSettingsContext()
  
  const isHeaderFixed = settings?.fixed_header ?? true
  const isSidebarFixed = settings?.fixed_sidebar ?? true
  const isPageAnimationEnabled = settings?.page_animation_enabled ?? true
  const isMenuCollapsedDefault = settings?.menu_collapsed_default ?? false

  return (
    <SidebarProvider defaultOpen={!isMenuCollapsedDefault}>
      <AdminSidebar className={!isSidebarFixed ? 'absolute h-full' : ''} />
      <div className="flex min-h-svh flex-1 flex-col">
        {isHeaderFixed ? (
          <div className="sticky top-0 z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <AdminTopbar />
          </div>
        ) : (
          <AdminTopbar />
        )}
        <main className={cn('flex-1 overflow-auto p-6', isPageAnimationEnabled ? 'animate-in fade-in duration-500' : '')}>
          <Outlet />
        </main>
      </div>
    </SidebarProvider>
  )
}
