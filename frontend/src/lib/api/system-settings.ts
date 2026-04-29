import { apiClient } from './client'
import type {
  SystemSettingAdmin,
  SystemSettingPublic,
  SystemSettingUpdatePayload,
} from '../types/system-setting'

export const getPublicSystemSettings = () => {
  return apiClient<SystemSettingPublic>('/api/v1/system-settings/public')
}

export const getAdminSystemSettings = () => {
  return apiClient<SystemSettingAdmin>('/api/v1/admin/system-settings')
}

export const updateAdminSystemSettings = (payload: SystemSettingUpdatePayload) => {
  return apiClient<SystemSettingAdmin>('/api/v1/admin/system-settings', {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}
