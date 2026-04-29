import { apiClient } from './client'
import type { UploadFileResponse } from '../types/upload'

export const uploadFile = (formData: FormData) => {
  return apiClient<UploadFileResponse>('/api/v1/uploads', {
    method: 'POST',
    body: formData,
  })
}
