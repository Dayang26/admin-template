import { useEffect } from 'react'
import { useForm, useWatch } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Loader2, Save, Settings2, Palette, Globe } from 'lucide-react'
import { toast } from 'sonner'

import { ImageUploadField } from '@/components/system-settings/image-upload-field'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { useAuth } from '@/lib/auth/context'
import { useAdminSystemSettings, useUpdateSystemSettings } from '@/lib/hooks/use-system-settings'
import type { SystemSettingUpdatePayload } from '@/lib/types/system-setting'

const formSchema = z.object({
  system_name: z.string().min(1, '系统名称不能为空').max(100),
  tagline: z.string().max(200).nullable(),
  copyright: z.string().max(255).nullable(),
  page_title_template: z.string().min(1, '页面标题格式不能为空').max(100),

  logo_light_file_id: z.string().nullable(),
  logo_light_url: z.string().nullable(),
  logo_dark_file_id: z.string().nullable(),
  logo_dark_url: z.string().nullable(),
  favicon_file_id: z.string().nullable(),
  favicon_url: z.string().nullable(),
  login_background_file_id: z.string().nullable(),
  login_background_url: z.string().nullable(),
})

type FormValues = z.infer<typeof formSchema>

function emptyToNull(value: string | null) {
  const trimmed = value?.trim()
  return trimmed ? trimmed : null
}

export function SystemSettingsPage() {
  const { hasPermission } = useAuth()
  const canUpdateSystemName = hasPermission('system_setting:update_system_name')
  const canUpdateTagline = hasPermission('system_setting:update_tagline')
  const canUpdateCopyright = hasPermission('system_setting:update_copyright')
  const canUpdatePageTitleTemplate = hasPermission('system_setting:update_page_title_template')
  const canUploadLogo = hasPermission('system_setting:upload_logo')
  const canUploadFavicon = hasPermission('system_setting:upload_favicon')
  const canUploadLoginBackground = hasPermission('system_setting:upload_login_background')
  const canSave =
    canUpdateSystemName ||
    canUpdateTagline ||
    canUpdateCopyright ||
    canUpdatePageTitleTemplate ||
    canUploadLogo ||
    canUploadFavicon ||
    canUploadLoginBackground
  const { data: settings, isLoading } = useAdminSystemSettings()
  const { mutateAsync: updateSettings, isPending: isUpdating } = useUpdateSystemSettings()

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      system_name: '',
      tagline: null,
      copyright: null,
      page_title_template: '{page} - {systemName}',

      logo_light_file_id: null,
      logo_light_url: null,
      logo_dark_file_id: null,
      logo_dark_url: null,
      favicon_file_id: null,
      favicon_url: null,
      login_background_file_id: null,
      login_background_url: null,
    },
  })

  const logoLightFileId = useWatch({ control: form.control, name: 'logo_light_file_id' })
  const logoLightUrl = useWatch({ control: form.control, name: 'logo_light_url' })
  const logoDarkFileId = useWatch({ control: form.control, name: 'logo_dark_file_id' })
  const logoDarkUrl = useWatch({ control: form.control, name: 'logo_dark_url' })
  const faviconFileId = useWatch({ control: form.control, name: 'favicon_file_id' })
  const faviconUrl = useWatch({ control: form.control, name: 'favicon_url' })
  const loginBackgroundFileId = useWatch({ control: form.control, name: 'login_background_file_id' })
  const loginBackgroundUrl = useWatch({ control: form.control, name: 'login_background_url' })

  useEffect(() => {
    if (!settings) return

    form.reset({
      system_name: settings.system_name,
      tagline: settings.tagline,
      copyright: settings.copyright,
      page_title_template: settings.page_title_template,

      logo_light_file_id: settings.logo_light_file_id,
      logo_light_url: settings.logo_light_url,
      logo_dark_file_id: settings.logo_dark_file_id,
      logo_dark_url: settings.logo_dark_url,
      favicon_file_id: settings.favicon_file_id,
      favicon_url: settings.favicon_url,
      login_background_file_id: settings.login_background_file_id,
      login_background_url: settings.login_background_url,
    })
  }, [settings, form])

  const onSubmit = async (values: FormValues) => {
    try {
      const payload: SystemSettingUpdatePayload = {}
      if (canUpdateSystemName) payload.system_name = values.system_name.trim()
      if (canUpdateTagline) payload.tagline = emptyToNull(values.tagline)
      if (canUpdateCopyright) payload.copyright = emptyToNull(values.copyright)
      if (canUpdatePageTitleTemplate) payload.page_title_template = values.page_title_template.trim()
      if (canUploadLogo) {
        payload.logo_light_file_id = values.logo_light_file_id
        payload.logo_dark_file_id = values.logo_dark_file_id
      }
      if (canUploadFavicon) payload.favicon_file_id = values.favicon_file_id
      if (canUploadLoginBackground) payload.login_background_file_id = values.login_background_file_id

      await updateSettings(payload)
      toast.success('系统设置已保存')
    } catch (error) {
      const err = error as Error
      toast.error(err.message || '保存失败')
    }
  }

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-primary/60" />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-5xl space-y-10 pb-20">
      {/* Sticky Header */}
      <div className="sticky top-0 z-20 -mx-4 flex items-center justify-between border-b bg-background/95 px-4 py-4 backdrop-blur sm:mx-0 sm:px-0">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">系统设置</h1>
          <p className="text-sm text-muted-foreground">配置系统基础信息和资源资产。</p>
        </div>
        {canSave && (
          <Button onClick={form.handleSubmit(onSubmit)} disabled={isUpdating} className="shadow-sm">
            {isUpdating ? <Loader2 className="mr-2 size-4 animate-spin" /> : <Save className="mr-2 size-4" />}
            保存所有更改
          </Button>
        )}
      </div>

      <Form {...form}>
        <form className="space-y-10">
          {/* 基础设置 */}
          <section className="space-y-6">
            <div className="flex items-center gap-2 px-1">
              <Settings2 className="size-5 text-primary" />
              <h2 className="text-lg font-semibold">基础设置</h2>
            </div>
            <Card className="shadow-sm">
              <CardContent className="grid gap-8 p-6 md:grid-cols-2">
                <FormField
                  control={form.control}
                  name="system_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>系统名称</FormLabel>
                      <FormControl>
                        <Input placeholder="输入系统名称" {...field} value={field.value || ''} disabled={!canUpdateSystemName} className="bg-muted/30 focus-visible:bg-background" />
                      </FormControl>
                      <FormDescription>用于页头、浏览器标签等位置。</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="tagline"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>标题语 (Tagline)</FormLabel>
                      <FormControl>
                        <Input placeholder="输入标语或简短描述" {...field} value={field.value || ''} disabled={!canUpdateTagline} className="bg-muted/30 focus-visible:bg-background" />
                      </FormControl>
                      <FormDescription>显示在登录页和品牌说明中。</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="md:col-span-2">
                  <FormField
                    control={form.control}
                    name="copyright"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>版权信息</FormLabel>
                        <FormControl>
                          <Input placeholder="Copyright © 2026 Your Company" {...field} value={field.value || ''} disabled={!canUpdateCopyright} className="bg-muted/30 focus-visible:bg-background" />
                        </FormControl>
                        <FormDescription>页面底部的法律声明信息。</FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </CardContent>
            </Card>
          </section>

          <Separator />

          {/* 资源设置 */}
          <section className="space-y-6">
            <div className="flex items-center gap-2 px-1">
              <Palette className="size-5 text-primary" />
              <h2 className="text-lg font-semibold">资源设置</h2>
            </div>
            <div className="grid gap-6 md:grid-cols-2">
              <ImageUploadField
                label="浅色模式 Logo"
                description="通常用于浅色顶栏或侧栏背景。"
                purpose="system_setting_logo"
                disabled={!canUploadLogo}
                value={{
                  file_id: logoLightFileId,
                  url: logoLightUrl,
                }}
                onChange={({ file_id, url }) => {
                  form.setValue('logo_light_file_id', file_id, { shouldDirty: true })
                  form.setValue('logo_light_url', url)
                }}
              />

              <ImageUploadField
                label="深色模式 Logo"
                description="通常用于深色顶栏或侧栏背景。"
                purpose="system_setting_logo"
                disabled={!canUploadLogo}
                value={{
                  file_id: logoDarkFileId,
                  url: logoDarkUrl,
                }}
                onChange={({ file_id, url }) => {
                  form.setValue('logo_dark_file_id', file_id, { shouldDirty: true })
                  form.setValue('logo_dark_url', url)
                }}
              />

              <ImageUploadField
                label="Favicon"
                description="浏览器页签显示的小图标 (建议 32x32)。"
                purpose="system_setting_favicon"
                disabled={!canUploadFavicon}
                value={{
                  file_id: faviconFileId,
                  url: faviconUrl,
                }}
                onChange={({ file_id, url }) => {
                  form.setValue('favicon_file_id', file_id, { shouldDirty: true })
                  form.setValue('favicon_url', url)
                }}
              />

              <ImageUploadField
                label="登录背景图"
                description="登录页面的主视觉背景图片。"
                purpose="system_setting_login_background"
                disabled={!canUploadLoginBackground}
                value={{
                  file_id: loginBackgroundFileId,
                  url: loginBackgroundUrl,
                }}
                onChange={({ file_id, url }) => {
                  form.setValue('login_background_file_id', file_id, { shouldDirty: true })
                  form.setValue('login_background_url', url)
                }}
              />
            </div>
          </section>

          <Separator />

          {/* SEO 设置 */}
          <section className="space-y-6">
            <div className="flex items-center gap-2 px-1">
              <Globe className="size-5 text-primary" />
              <h2 className="text-lg font-semibold">SEO 与显示设置</h2>
            </div>
            <Card className="shadow-sm">
              <CardContent className="p-6">
                <FormField
                  control={form.control}
                  name="page_title_template"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>浏览器标题模板</FormLabel>
                      <FormControl>
                        <Input placeholder="{page} - {systemName}" {...field} disabled={!canUpdatePageTitleTemplate} className="max-w-md bg-muted/30 focus-visible:bg-background" />
                      </FormControl>
                      <FormDescription>
                        动态构建页面标题。可用变量：<code>{'{page}'}</code> (当前页面名) 和 <code>{'{systemName}'}</code> (系统名称)。
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </CardContent>
            </Card>
          </section>
        </form>
      </Form>
    </div>
  )
}
