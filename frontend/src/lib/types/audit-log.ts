export interface AuditLog {
  id: string
  created_at: string
  user_id: string | null
  user_email: string
  method: string
  path: string
  action: string
  detail: string | null
  resource_type: string | null
  resource_id: string | null
  changes: Record<string, unknown> | null
  status_code: number
  ip_address: string | null
  user_agent: string | null
}
