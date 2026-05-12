import { useRef, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { zodResolver } from '@hookform/resolvers/zod'
import { Loader2, Trash2, Upload } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'
import { PageHeader } from '@/components/shared/page-header'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { useAuth } from '@/lib/auth/context'
import { changePassword, removeMyAvatar, updateMe, uploadMyAvatar } from '@/lib/api/me'
import { showApiError, showFormApiError } from '@/lib/utils/api-error'
import { getRoleLabel } from '@/lib/utils/role-labels'
import { getUserInitials } from '@/lib/utils/user-avatar'

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

export function ProfilePage() {
  const { user, updateCurrentUser } = useAuth()
  const [nameSubmitting, setNameSubmitting] = useState(false)
  const [pwdSubmitting, setPwdSubmitting] = useState(false)
  const avatarInputRef = useRef<HTMLInputElement>(null)

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

  const uploadAvatarMutation = useMutation({
    mutationFn: (file: File) => uploadMyAvatar(file),
  })

  const removeAvatarMutation = useMutation({
    mutationFn: () => removeMyAvatar(),
  })

  function handleNameSubmit(data: NameForm) {
    setNameSubmitting(true)
    updateNameMutation.mutate(
      { full_name: data.full_name || null },
      {
        onSuccess: (updatedUser) => {
          updateCurrentUser(updatedUser)
          nameForm.reset({ full_name: updatedUser.full_name ?? '' })
          toast.success('姓名已更新')
          setNameSubmitting(false)
        },
        onError: (err) => {
          showFormApiError(err, nameForm.setError, '更新失败')
          setNameSubmitting(false)
        },
      },
    )
  }

  function handleAvatarUpload(file: File) {
    uploadAvatarMutation.mutate(file, {
      onSuccess: (updatedUser) => {
        updateCurrentUser(updatedUser)
        toast.success('头像已更新')
      },
      onError: (err) => {
        showApiError(err, '头像上传失败')
      },
      onSettled: () => {
        if (avatarInputRef.current) {
          avatarInputRef.current.value = ''
        }
      },
    })
  }

  function handleAvatarRemove() {
    removeAvatarMutation.mutate(undefined, {
      onSuccess: (updatedUser) => {
        updateCurrentUser(updatedUser)
        toast.success('头像已移除')
      },
      onError: (err) => {
        showApiError(err, '头像移除失败')
      },
    })
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
          showFormApiError(err, pwdForm.setError, '修改失败')
          setPwdSubmitting(false)
        },
      },
    )
  }

  if (!user) return null

  const avatarMutationPending = uploadAvatarMutation.isPending || removeAvatarMutation.isPending

  return (
    <div className="space-y-6">
      <PageHeader title="个人资料" description="查看和维护当前账号信息" />

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>基本信息</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex flex-col gap-6 sm:flex-row sm:items-center">
            <Avatar className="h-24 w-24 border">
              {user.avatar_url && (
                <AvatarImage src={user.avatar_url} alt={user.full_name ?? user.email} className="object-cover" />
              )}
              <AvatarFallback className="bg-primary/10 text-primary text-2xl">
                {getUserInitials(user.full_name, user.email)}
              </AvatarFallback>
            </Avatar>

            <div className="space-y-3">
              <div>
                <p className="text-sm font-medium text-foreground">
                  {user.full_name ?? '未设置姓名'}
                </p>
                <p className="text-sm text-muted-foreground">{user.email}</p>
              </div>

              <input
                ref={avatarInputRef}
                type="file"
                accept="image/png,image/jpeg,image/webp,image/x-icon,image/vnd.microsoft.icon"
                className="hidden"
                disabled={avatarMutationPending}
                onChange={(event) => {
                  const file = event.target.files?.[0]
                  if (file) {
                    handleAvatarUpload(file)
                  }
                }}
              />

              <div className="flex flex-wrap gap-2">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => avatarInputRef.current?.click()}
                  disabled={avatarMutationPending}
                >
                  {uploadAvatarMutation.isPending ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Upload className="mr-2 h-4 w-4" />
                  )}
                  {user.avatar_url ? '更换头像' : '上传头像'}
                </Button>
                {user.avatar_url && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleAvatarRemove}
                    disabled={avatarMutationPending}
                  >
                    {removeAvatarMutation.isPending ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Trash2 className="mr-2 h-4 w-4" />
                    )}
                    移除头像
                  </Button>
                )}
              </div>

              <p className="text-xs text-muted-foreground">
                支持 PNG、JPG、WEBP、ICO，文件大小不超过 5MB。
              </p>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="text-sm text-muted-foreground">邮箱</p>
              <p className="font-medium">{user.email}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">角色</p>
              <div className="mt-1 flex flex-wrap gap-1">
                {user.roles.length > 0 ? (
                  user.roles.map((role) => (
                    <Badge key={role} variant="secondary">
                      {getRoleLabel(role)}
                    </Badge>
                  ))
                ) : (
                  <span className="text-sm text-muted-foreground">暂无角色</span>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="max-w-2xl">
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

      <Card className="max-w-2xl">
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
