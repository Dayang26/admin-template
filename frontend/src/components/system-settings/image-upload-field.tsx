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
    <div className="group space-y-4 rounded-xl border bg-card p-4 transition-all hover:shadow-md">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <h4 className="text-sm font-semibold leading-none text-foreground">{label}</h4>
          {description && <p className="text-xs text-muted-foreground">{description}</p>}
        </div>
      </div>

      <div className="flex items-center gap-6">
        <div 
          className="relative flex h-24 w-24 shrink-0 items-center justify-center overflow-hidden rounded-lg border bg-muted ring-offset-background transition-all group-hover:ring-2 group-hover:ring-ring group-hover:ring-offset-2"
          style={{
            backgroundImage: 'linear-gradient(45deg, #e5e7eb 25%, transparent 25%), linear-gradient(-45deg, #e5e7eb 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #e5e7eb 75%), linear-gradient(-45deg, transparent 75%, #e5e7eb 75%)',
            backgroundSize: '12px 12px',
            backgroundPosition: '0 0, 0 6px, 6px 6px, 6px 0',
          }}
        >
          {value.url ? (
            <img src={value.url} alt="Preview" className="h-full w-full object-contain p-2" />
          ) : (
            <div className="text-muted-foreground/40">
              <Upload className="size-8" />
            </div>
          )}
        </div>

        <div className="flex flex-1 flex-col gap-3">
          <input
            type="file"
            accept="image/*"
            className="hidden"
            ref={inputRef}
            onChange={handleFileChange}
            disabled={disabled || isPending}
          />
          <div className="flex flex-wrap items-center gap-2">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              className="h-8"
              disabled={disabled || isPending}
              onClick={() => inputRef.current?.click()}
            >
              {isPending ? <Loader2 className="mr-1.5 size-3.5 animate-spin" /> : <Upload className="mr-1.5 size-3.5" />}
              {value.url ? '更换' : '上传图片'}
            </Button>
            {value.url && !disabled && (
              <Button 
                type="button" 
                variant="ghost" 
                size="sm" 
                className="h-8 text-destructive hover:text-destructive hover:bg-destructive/10" 
                onClick={handleClear} 
                disabled={isPending}
              >
                <X className="mr-1.5 size-3.5" />
                移除
              </Button>
            )}
          </div>
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground/60 font-medium">支持 PNG, JPG, WEBP, ICO (Max 2MB)</p>
        </div>
      </div>
    </div>
  )
}
