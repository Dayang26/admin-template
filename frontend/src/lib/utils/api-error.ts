import type { FieldValues, Path, UseFormSetError } from 'react-hook-form'
import { toast } from 'sonner'
import { ApiError } from '@/lib/api/client'

function isNetworkError(error: unknown) {
  return error instanceof TypeError && error.message.toLowerCase().includes('fetch')
}

export function getApiErrorMessage(error: unknown, fallback: string) {
  if (error instanceof ApiError) {
    return error.message || fallback
  }

  if (isNetworkError(error)) {
    return '网络连接失败，请检查后重试'
  }

  if (error instanceof Error && error.message) {
    return error.message
  }

  return fallback
}

export function showApiError(error: unknown, fallback: string) {
  toast.error(getApiErrorMessage(error, fallback))
}

export function applyApiFieldErrors<TFieldValues extends FieldValues>(
  error: unknown,
  setError: UseFormSetError<TFieldValues>,
) {
  if (!(error instanceof ApiError)) return false

  const entries = Object.entries(error.fieldErrors)
  if (entries.length === 0) return false

  entries.forEach(([field, message]) => {
    setError(field as Path<TFieldValues>, {
      type: 'server',
      message,
    })
  })

  return true
}

export function showFormApiError<TFieldValues extends FieldValues>(
  error: unknown,
  setError: UseFormSetError<TFieldValues>,
  fallback: string,
) {
  const hasFieldErrors = applyApiFieldErrors(error, setError)
  toast.error(getApiErrorMessage(error, fallback), {
    description: hasFieldErrors ? '请检查表单中标记的字段。' : undefined,
  })
}
