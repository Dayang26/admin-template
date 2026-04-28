import { apiClient } from './client'
import type { AuditLog } from '../types/audit-log'
import type { PaginatedData } from '../types/api'

export interface AuditLogSearchParams {
  page?: number
  size?: number
  user_email?: string
  action?: string
  start_date?: string
  end_date?: string
}

export async function getAuditLogs(params: AuditLogSearchParams = {}): Promise<PaginatedData<AuditLog>> {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.size) searchParams.set('size', String(params.size))
  if (params.user_email) searchParams.set('user_email', params.user_email)
  if (params.action) searchParams.set('action', params.action)
  if (params.start_date) searchParams.set('start_date', params.start_date)
  if (params.end_date) searchParams.set('end_date', params.end_date)

  const query = searchParams.toString()
  return apiClient<PaginatedData<AuditLog>>(`/api/v1/admin/audit-logs/${query ? `?${query}` : ''}`)
}
