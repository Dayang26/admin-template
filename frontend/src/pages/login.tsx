import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { toast } from 'sonner'
import { useAuth } from '@/lib/auth/context'
import { getDefaultRoute } from '@/lib/auth/routes'
import { login as loginApi } from '@/lib/api/auth'
import { loginFormSchema, type LoginFormValues } from '@/lib/schemas/login'
import { useSystemSettingsContext } from '@/lib/system-settings/context'

import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'

export function LoginPage() {
  const [searchParams] = useSearchParams()
  const returnUrl = searchParams.get('returnUrl')

  const { login } = useAuth()
  const navigate = useNavigate()
  const [submitting, setSubmitting] = useState(false)
  const { settings } = useSystemSettingsContext()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginFormSchema),
    defaultValues: {
      email: '',
      password: '',
    },
    mode: 'onBlur',
  })

  async function onSubmit(data: LoginFormValues) {
    setSubmitting(true)
    try {
      const response = await loginApi(data.email, data.password)
      const user = await login(response.access_token)
      toast.success('登录成功')

      if (returnUrl) {
        navigate(returnUrl, { replace: true })
      } else {
        navigate(getDefaultRoute(user, settings?.default_home_path), { replace: true })
      }
    } catch (err: unknown) {
      console.error('登录失败:', err)

      let message: string
      if (err instanceof TypeError && err.message.includes('fetch')) {
        message = '登录失败，请检查网络连接'
      } else if (err instanceof Error) {
        // 将常见英文错误信息转为中文
        const msg = err.message
        if (/incorrect|wrong|invalid.*password/i.test(msg)) {
          message = '邮箱或密码错误'
        } else if (/inactive/i.test(msg)) {
          message = '该账号已被禁用'
        } else {
          message = msg || '登录失败，请检查账号密码'
        }
      } else {
        message = '登录失败，请检查账号密码'
      }

      toast.error(message)
    } finally {
      setSubmitting(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !submitting) {
      handleSubmit(onSubmit)()
    }
  }

  return (
    <div 
      className="flex min-h-screen items-center justify-center bg-muted/50 px-4 bg-cover bg-center relative"
      style={settings?.login_background_url ? { backgroundImage: `url(${settings.login_background_url})` } : undefined}
    >
      <Card className="w-full max-w-md shadow-2xl bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80">
        <CardHeader>
          <div className="flex flex-col items-center justify-center space-y-3 mb-2">
            <div className="flex h-12 items-center justify-center">
              {settings?.logo_light_url ? (
                <>
                  <img src={settings.logo_light_url} className="h-full object-contain dark:hidden" alt="Logo" />
                  {settings?.logo_dark_url ? (
                    <img src={settings.logo_dark_url} className="h-full object-contain hidden dark:block" alt="Logo" />
                  ) : (
                    <img src={settings.logo_light_url} className="h-full object-contain hidden dark:block" alt="Logo" />
                  )}
                </>
              ) : null}
            </div>
            <CardTitle className="text-center text-2xl">
              {settings?.system_name || '欢迎回来'}
            </CardTitle>
          </div>
          <CardDescription className="text-center">
            {settings?.tagline || '请输入您的账号和密码进行登录'}
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">邮箱</Label>
            <Input
              id="email"
              type="email"
              placeholder="name@example.com"
              disabled={submitting}
              aria-invalid={!!errors.email}
              aria-describedby={errors.email ? 'email-error' : undefined}
              onKeyDown={handleKeyDown}
              {...register('email')}
            />
            {errors.email && (
              <p id="email-error" className="text-xs text-destructive">
                {errors.email.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">密码</Label>
            <Input
              id="password"
              type="password"
              disabled={submitting}
              aria-invalid={!!errors.password}
              aria-describedby={errors.password ? 'password-error' : undefined}
              onKeyDown={handleKeyDown}
              {...register('password')}
            />
            {errors.password && (
              <p id="password-error" className="text-xs text-destructive">
                {errors.password.message}
              </p>
            )}
          </div>
        </CardContent>

        <CardFooter>
          <Button
            type="button"
            className="w-full"
            disabled={submitting}
            onClick={() => handleSubmit(onSubmit)()}
          >
            {submitting ? '登录中...' : '登录'}
          </Button>
        </CardFooter>
      </Card>

      {settings?.copyright && (
        <div className="absolute bottom-6 left-0 right-0 text-center text-sm text-muted-foreground/80 backdrop-blur-sm">
          {settings.copyright}
        </div>
      )}
    </div>
  )
}
