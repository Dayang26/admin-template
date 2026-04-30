import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { useSystemSettingsContext } from './context'
import { formatPageTitle } from './title'

const PAGE_NAMES: Record<string, string> = {
  '/login': '登录',
  '/profile': '个人资料',
  '/admin': '仪表盘',
  '/admin/users': '用户管理',
  '/admin/users/create': '创建用户',
  '/admin/audit-logs': '日志审计',
  '/admin/roles': '权限管理',
  '/admin/system-settings': '系统设置',
}

export function usePageTitleSync() {
  const location = useLocation()
  const { settings } = useSystemSettingsContext()

  useEffect(() => {
    const pageName = PAGE_NAMES[location.pathname] || '页面'
    
    if (settings) {
      document.title = formatPageTitle(
        pageName,
        settings.page_title_template,
        settings.system_name
      )
    } else {
      document.title = `${pageName} - Carrier Agent`
    }
  }, [location.pathname, settings])
}

export function PageTitleSync() {
  usePageTitleSync()
  return null
}
