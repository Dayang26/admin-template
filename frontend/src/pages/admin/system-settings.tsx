import { useEffect } from 'react'
import { useForm, useWatch } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Loader2, Save } from 'lucide-react'
import { toast } from 'sonner'

import { ImageUploadField } from '@/components/system-settings/image-upload-field'
import { PageHeader } from '@/components/shared/page-header'
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
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
  const canUpdate = hasPermission('system_setting:update')
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
      const payload: SystemSettingUpdatePayload = {
        system_name: values.system_name.trim(),
        tagline: emptyToNull(values.tagline),
        copyright: emptyToNull(values.copyright),
        page_title_template: values.page_title_template.trim(),
        logo_light_file_id: values.logo_light_file_id,
        logo_dark_file_id: values.logo_dark_file_id,
        favicon_file_id: values.favicon_file_id,
        login_background_file_id: values.login_background_file_id,
      }

      await updateSettings(payload)
      toast.success('系统设置已保存')
    } catch (error) {
      const err = error as Error
      toast.error(err.message || '保存失败')
    }
  }

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <PageHeader title="系统设置" description="配置系统基础信息和品牌资源。" />
        {canUpdate && (
          <Button onClick={form.handleSubmit(onSubmit)} disabled={isUpdating}>
            {isUpdating ? <Loader2 className="mr-2 size-4 animate-spin" /> : <Save className="mr-2 size-4" />}
            保存设置
          </Button>
        )}
      </div>

      <Form {...form}>
        <form className="space-y-8">
          <Tabs defaultValue="basic" className="w-full max-w-4xl">
            <TabsList className="mb-6">
              <TabsTrigger value="basic">基础信息</TabsTrigger>
              <TabsTrigger value="brand">品牌资源</TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="space-y-6">
              <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                <FormField
                  control={form.control}
                  name="system_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>系统名称</FormLabel>
                      <FormControl>
                        <Input placeholder="输入系统名称" {...field} value={field.value || ''} disabled={!canUpdate} />
                      </FormControl>
                      <FormDescription>显示在登录页、侧边栏和浏览器标题中。</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="tagline"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>标题语</FormLabel>
                      <FormControl>
                        <Input placeholder="输入标题语" {...field} value={field.value || ''} disabled={!canUpdate} />
                      </FormControl>
                      <FormDescription>显示在登录页和侧边栏品牌信息中。</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="copyright"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Copyright</FormLabel>
                      <FormControl>
                        <Input placeholder="Copyright © 2026" {...field} value={field.value || ''} disabled={!canUpdate} />
                      </FormControl>
                      <FormDescription>用于登录页或页面底部展示版权信息。</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="page_title_template"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>页面标题格式</FormLabel>
                      <FormControl>
                        <Input placeholder="{page} - {systemName}" {...field} disabled={!canUpdate} />
                      </FormControl>
                      <FormDescription>
                        可使用变量 <code>{'{page}'}</code> 和 <code>{'{systemName}'}</code>。
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </TabsContent>

            <TabsContent value="brand" className="space-y-8">
              <div className="grid grid-cols-1 gap-x-8 gap-y-12 md:grid-cols-2">
                <ImageUploadField
                  label="浅色 Logo"
                  description="在浅色背景上显示。"
                  disabled={!canUpdate}
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
                  label="深色 Logo"
                  description="在深色背景上显示。"
                  disabled={!canUpdate}
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
                  description="浏览器书签和标签页小图标。"
                  disabled={!canUpdate}
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
                  label="登录页背景图"
                  description="登录页面背景图片。"
                  disabled={!canUpdate}
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
            </TabsContent>
          </Tabs>
        </form>
      </Form>
    </div>
  )
}
