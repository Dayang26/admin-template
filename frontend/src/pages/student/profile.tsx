import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { useMutation } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { useAuth } from '@/lib/auth/context'
import { updateMe, changePassword } from '@/lib/api/me'

const nameSchema = z.object({
  full_name: z.string().max(255, '姓名最多 255 个字符').optional(),
})

const passwordSchema = z
  .object({
    current_password: z.string().min(8, '密码至少 8 位'),
    new_password: z.string().min(8, '新密码至少 8 位'),
    confirm_password: z.string().min(1, '请确认新密码'),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: '两次输入的密码不一致',
    path: ['confirm_password'],
  })

type NameForm = z.infer<typeof nameSchema>
type PasswordForm = z.infer<typeof passwordSchema>

const ROLE_LABELS: Record<string, string> = {
  superuser: '超级管理员',
  teacher: '教师',
  student: '学生',
}

export function ProfilePage() {
  const { user } = useAuth()
  const [nameSubmitting, setNameSubmitting] = useState(false)
  const [pwdSubmitting, setPwdSubmitting] = useState(false)

  const nameForm = useForm<NameForm>({
    resolver: zodResolver(nameSchema),
    values: { full_name: user?.full_name ?? '' },
  })

  const pwdForm = useForm<PasswordForm>({
    resolver: zodResolver(passwordSchema),
    defaultValues: { current_password: '', new_password: '', confirm_password: '' },
  })

  const updateNameMutation = useMutation({
    mutationFn: (data: { full_name?: string | null }) => updateMe(data),
  })

  const changePasswordMutation = useMutation({
    mutationFn: (data: { current_password: string; new_password: string }) =>
      changePassword(data),
  })

  function handleNameSubmit(data: NameForm) {
    setNameSubmitting(true)
    updateNameMutation.mutate(
      { full_name: data.full_name || null },
      {
        onSuccess: () => {
          toast.success('姓名已更新')
          setNameSubmitting(false)
        },
        onError: (err) => {
          toast.error(err instanceof Error ? err.message : '更新失败')
          setNameSubmitting(false)
        },
      },
    )
  }

  function handlePasswordSubmit(data: PasswordForm) {
    setPwdSubmitting(true)
    changePasswordMutation.mutate(
      { current_password: data.current_password, new_password: data.new_password },
      {
        onSuccess: () => {
          toast.success('密码已修改')
          pwdForm.reset()
          setPwdSubmitting(false)
        },
        onError: (err) => {
          toast.error(err instanceof Error ? err.message : '修改失败')
          setPwdSubmitting(false)
        },
      },
    )
  }

  if (!user) return null

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">个人中心</h1>

      {/* 基本信息 */}
      <Card>
        <CardHeader>
          <CardTitle>基本信息</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="text-sm text-muted-foreground">邮箱</p>
              <p className="font-medium">{user.email}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">角色</p>
              <div className="flex gap-1 mt-1">
                {user.roles.map((role) => (
                  <Badge key={role} variant="secondary">
                    {ROLE_LABELS[role] ?? role}
                  </Badge>
                ))}
              </div>
            </div>
          </div>

          {user.class_memberships.length > 0 && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">班级</p>
              <div className="space-y-1">
                {user.class_memberships.map((cm) => (
                  <div key={cm.class_id} className="flex items-center justify-between rounded-md border px-3 py-2">
                    <span className="text-sm">{cm.class_name}</span>
                    <Badge variant="outline">{cm.role}</Badge>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 编辑姓名 */}
      <Card>
        <CardHeader>
          <CardTitle>编辑姓名</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="full_name">姓名</Label>
            <Input id="full_name" placeholder="输入您的姓名" {...nameForm.register('full_name')} />
            {nameForm.formState.errors.full_name && (
              <p className="text-xs text-destructive">{nameForm.formState.errors.full_name.message}</p>
            )}
          </div>
          <Button
            type="button"
            disabled={nameSubmitting || !nameForm.formState.isDirty}
            onClick={() => nameForm.handleSubmit(handleNameSubmit)()}
          >
            {nameSubmitting ? '保存中...' : '保存'}
          </Button>
        </CardContent>
      </Card>

      <Separator />

      {/* 修改密码 */}
      <Card>
        <CardHeader>
          <CardTitle>修改密码</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="current_password">当前密码</Label>
            <Input
              id="current_password"
              type="password"
              {...pwdForm.register('current_password')}
            />
            {pwdForm.formState.errors.current_password && (
              <p className="text-xs text-destructive">{pwdForm.formState.errors.current_password.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="new_password">新密码</Label>
            <Input
              id="new_password"
              type="password"
              placeholder="至少 8 位"
              {...pwdForm.register('new_password')}
            />
            {pwdForm.formState.errors.new_password && (
              <p className="text-xs text-destructive">{pwdForm.formState.errors.new_password.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="confirm_password">确认新密码</Label>
            <Input
              id="confirm_password"
              type="password"
              {...pwdForm.register('confirm_password')}
            />
            {pwdForm.formState.errors.confirm_password && (
              <p className="text-xs text-destructive">{pwdForm.formState.errors.confirm_password.message}</p>
            )}
          </div>
          <Button
            type="button"
            disabled={pwdSubmitting}
            onClick={() => pwdForm.handleSubmit(handlePasswordSubmit)()}
          >
            {pwdSubmitting ? '修改中...' : '修改密码'}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
