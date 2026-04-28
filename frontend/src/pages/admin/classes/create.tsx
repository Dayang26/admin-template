import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { PageHeader } from '@/components/shared/page-header'
import { useCreateClass } from '@/lib/hooks/use-classes'

const createClassSchema = z.object({
  name: z.string().min(1, '请输入班级名称').max(100, '名称最多 100 个字符'),
  description: z.string().max(500, '描述最多 500 个字符').optional(),
})

type CreateClassForm = z.infer<typeof createClassSchema>

export function ClassCreatePage() {
  const navigate = useNavigate()
  const createMutation = useCreateClass()
  const [submitting, setSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateClassForm>({
    resolver: zodResolver(createClassSchema),
    defaultValues: { name: '', description: '' },
  })

  async function onSubmit(data: CreateClassForm) {
    setSubmitting(true)
    createMutation.mutate(
      { name: data.name, description: data.description || undefined },
      {
        onSuccess: () => {
          toast.success('班级创建成功')
          navigate('/admin/classes')
        },
        onError: (err) => {
          toast.error(err instanceof Error ? err.message : '创建失败')
          setSubmitting(false)
        },
      },
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader title="创建班级" description="创建新的班级" />

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>班级信息</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">班级名称 *</Label>
            <Input id="name" placeholder="例如：2026级1班" {...register('name')} />
            {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">描述</Label>
            <Input id="description" placeholder="可选" {...register('description')} />
            {errors.description && <p className="text-xs text-destructive">{errors.description.message}</p>}
          </div>

          <div className="flex gap-2 pt-4">
            <Button type="button" disabled={submitting} onClick={() => handleSubmit(onSubmit)()}>
              {submitting ? '创建中...' : '创建'}
            </Button>
            <Button type="button" variant="outline" onClick={() => navigate('/admin/classes')}>
              取消
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
