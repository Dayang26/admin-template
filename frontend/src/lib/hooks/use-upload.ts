import { useMutation } from '@tanstack/react-query'
import { uploadFile } from '../api/uploads'

export function useUploadFile() {
  return useMutation({
    mutationFn: (formData: FormData) => uploadFile(formData),
  })
}
