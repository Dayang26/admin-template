import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  getAdminSystemSettings,
  getPublicSystemSettings,
  updateAdminSystemSettings,
} from '../api/system-settings'
import type { SystemSettingUpdatePayload } from '../types/system-setting'

export const systemSettingsKeys = {
  all: ['system-settings'] as const,
  public: () => [...systemSettingsKeys.all, 'public'] as const,
  admin: () => [...systemSettingsKeys.all, 'admin'] as const,
}

export function usePublicSystemSettings() {
  return useQuery({
    queryKey: systemSettingsKeys.public(),
    queryFn: getPublicSystemSettings,
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: 2,
  })
}

export function useAdminSystemSettings() {
  return useQuery({
    queryKey: systemSettingsKeys.admin(),
    queryFn: getAdminSystemSettings,
  })
}

export function useUpdateSystemSettings() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: SystemSettingUpdatePayload) =>
      updateAdminSystemSettings(payload),
    onSuccess: () => {
      // 成功更新后刷新缓存
      queryClient.invalidateQueries({ queryKey: systemSettingsKeys.admin() })
      queryClient.invalidateQueries({ queryKey: systemSettingsKeys.public() })
    },
  })
}
