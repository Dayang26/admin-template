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
import { useCreateUser } from '@/lib/hooks/use-users'
import { useRoles } from '@/lib/hooks/use-roles'
import { getRoleLabel } from '@/lib/utils/role-labels'

const createUserSchema = z.object({
  email: z.string().min(1, '请输入邮箱').email('请输入有效的邮箱地址'),
  password: z.string().min(8, '密码至少 8 位'),
  full_name: z.string().optional(),
  roles: z.array(z.string()).min(1, '请至少选择一个角色'),
})

type CreateUserForm = z.infer<typeof createUserSchema>

export function UserCreatePage() {
  const navigate = useNavigate()
  const createMutation = useCreateUser()
  const { data: roles } = useRoles()
  const [submitting, setSubmitting] = useState(false)

  // 过滤掉 superuser，不允许通过创建页面分配
  const assignableRoles = (roles ?? []).filter((r) => r.name !== 'superuser')

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<CreateUserForm>({
    resolver: zodResolver(createUserSchema),
    defaultValues: {
      email: '',
      password: '',
      full_name: '',
      roles: [],
    },
  })

  const selectedRoles = watch('roles')

  function toggleRole(role: string) {
    const current = selectedRoles || []
    if (current.includes(role)) {
      setValue('roles', current.filter((r) => r !== role), { shouldValidate: true })
    } else {
      setValue('roles', [...current, role], { shouldValidate: true })
    }
  }

  async function onSubmit(data: CreateUserForm) {
    setSubmitting(true)
    createMutation.mutate(
      {
        email: data.email,
        password: data.password,
        full_name: data.full_name || undefined,
        roles: data.roles,
      },
      {
        onSuccess: () => {
          toast.success('用户创建成功')
          navigate('/admin/users')
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
      <PageHeader title="创建用户" description="创建新用户并分配角色" />

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>用户信息</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">邮箱 *</Label>
            <Input id="email" type="email" placeholder="name@example.com" {...register('email')} />
            {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">密码 *</Label>
            <Input id="password" type="password" placeholder="至少 8 位" {...register('password')} />
            {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="full_name">姓名</Label>
            <Input id="full_name" placeholder="可选" {...register('full_name')} />
          </div>

          <div className="space-y-2">
            <Label>角色 *</Label>
            <div className="flex flex-wrap gap-2">
              {assignableRoles.map((role) => (
                <Button
                  key={role.name}
                  type="button"
                  variant={selectedRoles?.includes(role.name) ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => toggleRole(role.name)}
                >
                  {getRoleLabel(role.name)}
                </Button>
              ))}
            </div>
            {errors.roles && <p className="text-xs text-destructive">{errors.roles.message}</p>}
          </div>

          <div className="flex gap-2 pt-4">
            <Button
              type="button"
              disabled={submitting}
              onClick={() => handleSubmit(onSubmit)()}
            >
              {submitting ? '创建中...' : '创建'}
            </Button>
            <Button type="button" variant="outline" onClick={() => navigate('/admin/users')}>
              取消
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
