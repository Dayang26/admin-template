import { apiClient } from './client'
import type { DashboardStats } from '../types/dashboard'

export async function getDashboardStats(): Promise<DashboardStats> {
  return apiClient<DashboardStats>('/api/v1/admin/dashboard/stats')
}
