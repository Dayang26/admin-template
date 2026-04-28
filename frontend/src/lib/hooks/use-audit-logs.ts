import { useQuery } from '@tanstack/react-query'
import { getAuditLogs, type AuditLogSearchParams } from '../api/audit-logs'

export function useAuditLogs(params: AuditLogSearchParams = {}) {
  return useQuery({
    queryKey: ['audit-logs', params],
    queryFn: () => getAuditLogs(params),
    staleTime: 10 * 1000, // 10 秒后视为过期，自动重新获取
    refetchOnWindowFocus: true, // 切换回页面时自动刷新
  })
}
