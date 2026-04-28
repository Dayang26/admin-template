import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { PageHeader } from '@/components/shared/page-header'
import { useUserDetail, useUpdateUser } from '@/lib/hooks/use-users'
import { useRoles } from '@/lib/hooks/use-roles'
import { getRoleLabel } from '@/lib/utils/role-labels'

const updateUserSchema = z.object({
  full_name: z.string().optional(),
  password: z.string().min(8, '密码至少 8 位').optional().or(z.literal('')),
  is_active: z.boolean(),
  roles: z.array(z.string()).min(1, '请至少选择一个角色'),
})

type UpdateUserForm = z.infer<typeof updateUserSchema>

export function UserDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: user, isLoading } = useUserDetail(id!)
  const { data: roles } = useRoles()
  const updateMutation = useUpdateUser()
  const [submitting, setSubmitting] = useState(false)

  // 过滤掉 superuser
  const assignableRoles = (roles ?? []).filter((r) => r.name !== 'superuser')

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors, isDirty },
  } = useForm<UpdateUserForm>({
    resolver: zodResolver(updateUserSchema),
    values: user
      ? {
          full_name: user.full_name ?? '',
          password: '',
          is_active: user.is_active,
          roles: user.roles.filter((r) => r !== 'superuser'),
        }
      : undefined,
  })

  const selectedRoles = watch('roles')
  const isActive = watch('is_active')

  function toggleRole(role: string) {
    const current = selectedRoles || []
    if (current.includes(role)) {
      setValue('roles', current.filter((r) => r !== role), { shouldValidate: true, shouldDirty: true })
    } else {
      setValue('roles', [...current, role], { shouldValidate: true, shouldDirty: true })
    }
  }

  async function onSubmit(data: UpdateUserForm) {
    if (!id) return
    setSubmitting(true)
    updateMutation.mutate(
      {
        userId: id,
        data: {
          full_name: data.full_name || null,
          password: data.password || null,
          is_active: data.is_active,
          roles: data.roles,
        },
      },
      {
        onSuccess: () => {
          toast.success('用户信息已更新')
          reset(data)
          setSubmitting(false)
        },
        onError: (err) => {
          toast.error(err instanceof Error ? err.message : '更新失败')
          setSubmitting(false)
        },
      },
    )
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <Card className="max-w-2xl">
          <CardContent className="space-y-4 pt-6">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="text-center text-muted-foreground py-12">
        用户不存在
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="用户详情"
        description={user.email}
        actions={
          <Button variant="outline" onClick={() => navigate('/admin/users')}>
            返回列表
          </Button>
        }
      />

      {/* 用户信息卡片 */}
      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            编辑用户
            {user.roles.includes('superuser') && (
              <Badge variant="destructive">超级管理员</Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>邮箱</Label>
            <Input value={user.email} disabled />
          </div>

          <div className="space-y-2">
            <Label htmlFor="full_name">姓名</Label>
            <Input id="full_name" placeholder="可选" {...register('full_name')} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">新密码</Label>
            <Input id="password" type="password" placeholder="留空则不修改" {...register('password')} />
            {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
          </div>

          <div className="space-y-2">
            <Label>状态</Label>
            <div className="flex gap-2">
              <Button
                type="button"
                variant={isActive ? 'default' : 'outline'}
                size="sm"
                onClick={() => setValue('is_active', true, { shouldDirty: true })}
              >
                活跃
              </Button>
              <Button
                type="button"
                variant={!isActive ? 'destructive' : 'outline'}
                size="sm"
                onClick={() => setValue('is_active', false, { shouldDirty: true })}
              >
                禁用
              </Button>
            </div>
          </div>

          {!user.roles.includes('superuser') && (
            <div className="space-y-2">
              <Label>角色</Label>
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
          )}

          <div className="flex gap-2 pt-4">
            <Button
              type="button"
              disabled={submitting || !isDirty}
              onClick={() => handleSubmit(onSubmit)()}
            >
              {submitting ? '保存中...' : '保存'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 班级成员身份 */}
      {user.class_memberships.length > 0 && (
        <Card className="max-w-2xl">
          <CardHeader>
            <CardTitle>班级成员身份</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {user.class_memberships.map((cm) => (
                <div key={cm.class_id} className="flex items-center justify-between rounded-md border p-3">
                  <span>{cm.class_name}</span>
                  <Badge variant="secondary">{cm.role}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
