export interface DashboardStats {
  total_users: number
  active_users: number
  total_classes: number
  role_distribution: Record<string, number>
}
