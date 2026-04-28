export interface AuditLog {
  id: string
  created_at: string
  user_id: string | null
  user_email: string
  method: string
  path: string
  action: string
  detail: string | null
  status_code: number
  ip_address: string | null
  user_agent: string | null
}
