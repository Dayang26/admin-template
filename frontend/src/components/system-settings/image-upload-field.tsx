import React, { useRef } from 'react'
import { useUploadFile } from '@/lib/hooks/use-upload'
import { Button } from '@/components/ui/button'
import { Upload, X, Loader2 } from 'lucide-react'
import { toast } from 'sonner'

interface ImageUploadFieldProps {
  label: string
  description?: string
  value: { file_id: string | null; url: string | null }
  onChange: (value: { file_id: string | null; url: string | null }) => void
  disabled?: boolean
}

export function ImageUploadField({ label, description, value, onChange, disabled }: ImageUploadFieldProps) {
  const { mutateAsync: uploadFile, isPending } = useUploadFile()
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)
    formData.append('file_type', 'image')
    formData.append('visibility', 'public')

    try {
      const result = await uploadFile(formData)
      onChange({ file_id: result.id, url: result.public_url })
      toast.success('上传成功')
    } catch (error) {
      const err = error as Error
      toast.error(err.message || '上传失败')
    } finally {
      if (inputRef.current) inputRef.current.value = ''
    }
  }

  const handleClear = () => {
    onChange({ file_id: null, url: null })
  }

  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-sm font-medium leading-none mb-1.5">{label}</h4>
        {description && <p className="text-sm text-muted-foreground">{description}</p>}
      </div>

      <div className="flex items-center gap-6">
        <div className="relative flex h-24 w-24 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-dashed bg-muted">
          {value.url ? (
            <>
              <img src={value.url} alt="Preview" className="h-full w-full object-contain p-1" />
            </>
          ) : (
            <div className="text-muted-foreground">
              <Upload className="size-6" />
            </div>
          )}
        </div>

        <div className="flex flex-col gap-2">
          <input
            type="file"
            accept="image/*"
            className="hidden"
            ref={inputRef}
            onChange={handleFileChange}
            disabled={disabled || isPending}
          />
          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={disabled || isPending}
              onClick={() => inputRef.current?.click()}
            >
              {isPending ? <Loader2 className="mr-2 size-4 animate-spin" /> : <Upload className="mr-2 size-4" />}
              {value.url ? '更换图片' : '上传图片'}
            </Button>
            {value.url && !disabled && (
              <Button type="button" variant="ghost" size="sm" onClick={handleClear} disabled={isPending}>
                <X className="mr-2 size-4" />
                清除
              </Button>
            )}
          </div>
          <p className="text-xs text-muted-foreground">支持 PNG, JPG, WEBP, ICO 等格式。建议大小不超过 2MB。</p>
        </div>
      </div>
    </div>
  )
}
