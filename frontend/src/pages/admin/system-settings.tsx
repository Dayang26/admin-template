import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
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
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useAdminSystemSettings, useUpdateSystemSettings } from '@/lib/hooks/use-system-settings'
import { useAuth } from '@/lib/auth/context'
import { Loader2, Save } from 'lucide-react'
import { toast } from 'sonner'
import { ImageUploadField } from '@/components/system-settings/image-upload-field'

const formSchema = z.object({
  system_name: z.string().min(1, '系统名称不能为空').max(100),
  tagline: z.string().max(200).nullable(),
  copyright: z.string().max(255).nullable(),
  page_title_template: z.string().min(1).max(100),
  default_home_path: z.string().startsWith('/', '路径必须以 / 开头'),

  logo_light_file_id: z.string().nullable(),
  logo_light_url: z.string().nullable(),
  logo_dark_file_id: z.string().nullable(),
  logo_dark_url: z.string().nullable(),
  favicon_file_id: z.string().nullable(),
  favicon_url: z.string().nullable(),
  login_background_file_id: z.string().nullable(),
  login_background_url: z.string().nullable(),

  primary_color: z.string().regex(/^#[0-9a-fA-F]{6}$/, '必须为 6 位 HEX 颜色'),
  theme_mode: z.enum(['light', 'dark', 'system']),
  layout_mode: z.enum(['sidebar', 'top', 'mixed']),

  menu_collapsed_default: z.boolean(),
  fixed_header: z.boolean(),
  fixed_sidebar: z.boolean(),
  page_animation_enabled: z.boolean(),
})

type FormValues = z.infer<typeof formSchema>

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
      default_home_path: '/admin',

      logo_light_file_id: null,
      logo_light_url: null,
      logo_dark_file_id: null,
      logo_dark_url: null,
      favicon_file_id: null,
      favicon_url: null,
      login_background_file_id: null,
      login_background_url: null,

      primary_color: '#2563eb',
      theme_mode: 'system',
      layout_mode: 'sidebar',

      menu_collapsed_default: false,
      fixed_header: true,
      fixed_sidebar: true,
      page_animation_enabled: true,
    },
  })

  useEffect(() => {
    if (settings) {
      form.reset({
        system_name: settings.system_name,
        tagline: settings.tagline,
        copyright: settings.copyright,
        page_title_template: settings.page_title_template,
        default_home_path: settings.default_home_path,

        logo_light_file_id: settings.logo_light_file_id,
        logo_light_url: settings.logo_light_url,
        logo_dark_file_id: settings.logo_dark_file_id,
        logo_dark_url: settings.logo_dark_url,
        favicon_file_id: settings.favicon_file_id,
        favicon_url: settings.favicon_url,
        login_background_file_id: settings.login_background_file_id,
        login_background_url: settings.login_background_url,

        primary_color: settings.primary_color,
        theme_mode: settings.theme_mode,
        layout_mode: settings.layout_mode,

        menu_collapsed_default: settings.menu_collapsed_default,
        fixed_header: settings.fixed_header,
        fixed_sidebar: settings.fixed_sidebar,
        page_animation_enabled: settings.page_animation_enabled,
      })
    }
  }, [settings, form])

  const onSubmit = async (values: FormValues) => {
    try {
      const payload = { ...values } as Partial<FormValues>
      delete payload.logo_light_url
      delete payload.logo_dark_url
      delete payload.favicon_url
      delete payload.login_background_url

      await updateSettings(payload as import('@/lib/types/system-setting').SystemSettingUpdatePayload)
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
      <div className="flex items-center justify-between">
        <PageHeader title="系统设置" description="配置系统基础信息、品牌形象及界面风格。" />
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
              <TabsTrigger value="theme">界面主题</TabsTrigger>
              <TabsTrigger value="behavior">系统行为</TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <FormField
                  control={form.control}
                  name="system_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>系统名称</FormLabel>
                      <FormControl>
                        <Input placeholder="输入系统名称" {...field} value={field.value || ''} disabled={!canUpdate} />
                      </FormControl>
                      <FormDescription>主要显示在浏览器标题栏、登录页和左上角。</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="tagline"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>副标题 / Slogan</FormLabel>
                      <FormControl>
                        <Input placeholder="输入副标题" {...field} value={field.value || ''} disabled={!canUpdate} />
                      </FormControl>
                      <FormDescription>辅助展示在部分页面的显眼位置。</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="copyright"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Copyright 声明</FormLabel>
                      <FormControl>
                        <Input placeholder="Copyright © 2026" {...field} value={field.value || ''} disabled={!canUpdate} />
                      </FormControl>
                      <FormDescription>显示在系统底部的版权信息。</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="default_home_path"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>默认登录跳转页</FormLabel>
                      <FormControl>
                        <Input placeholder="/admin" {...field} disabled={!canUpdate} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="page_title_template"
                  render={({ field }) => (
                    <FormItem className="col-span-2">
                      <FormLabel>页面标题格式模板</FormLabel>
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
              <div className="grid grid-cols-2 gap-y-12 gap-x-8">
                <ImageUploadField
                  label="浅色 Logo"
                  description="在浅色侧边栏或白底上显示。"
                  disabled={!canUpdate}
                  value={{
                    file_id: form.watch('logo_light_file_id'),
                    url: form.watch('logo_light_url'),
                  }}
                  onChange={({ file_id, url }) => {
                    form.setValue('logo_light_file_id', file_id, { shouldDirty: true })
                    form.setValue('logo_light_url', url)
                  }}
                />

                <ImageUploadField
                  label="深色 Logo"
                  description="在深色侧边栏或黑底上显示。"
                  disabled={!canUpdate}
                  value={{
                    file_id: form.watch('logo_dark_file_id'),
                    url: form.watch('logo_dark_url'),
                  }}
                  onChange={({ file_id, url }) => {
                    form.setValue('logo_dark_file_id', file_id, { shouldDirty: true })
                    form.setValue('logo_dark_url', url)
                  }}
                />

                <ImageUploadField
                  label="Favicon 图标"
                  description="浏览器书签和标签页小图标。"
                  disabled={!canUpdate}
                  value={{
                    file_id: form.watch('favicon_file_id'),
                    url: form.watch('favicon_url'),
                  }}
                  onChange={({ file_id, url }) => {
                    form.setValue('favicon_file_id', file_id, { shouldDirty: true })
                    form.setValue('favicon_url', url)
                  }}
                />

                <ImageUploadField
                  label="登录页背景图"
                  description="替换登录页面大面积留白区域。"
                  disabled={!canUpdate}
                  value={{
                    file_id: form.watch('login_background_file_id'),
                    url: form.watch('login_background_url'),
                  }}
                  onChange={({ file_id, url }) => {
                    form.setValue('login_background_file_id', file_id, { shouldDirty: true })
                    form.setValue('login_background_url', url)
                  }}
                />
              </div>
            </TabsContent>

            <TabsContent value="theme" className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <FormField
                  control={form.control}
                  name="primary_color"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>主题色 (HEX)</FormLabel>
                      <div className="flex gap-2">
                        <FormControl>
                          <Input
                            type="color"
                            className="h-10 w-16 p-1 cursor-pointer"
                            {...field}
                            disabled={!canUpdate}
                          />
                        </FormControl>
                        <FormControl>
                          <Input
                            placeholder="#2563eb"
                            className="uppercase font-mono w-32"
                            {...field}
                            disabled={!canUpdate}
                          />
                        </FormControl>
                      </div>
                      <FormDescription>将会实时转换为 CSS 变量作用于全局 UI。</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="theme_mode"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>默认主题模式</FormLabel>
                      <Select disabled={!canUpdate} onValueChange={field.onChange} value={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="选择主题模式" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="system">跟随系统</SelectItem>
                          <SelectItem value="light">浅色模式</SelectItem>
                          <SelectItem value="dark">深色模式</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormDescription>全局默认主题，当用户本地无偏好时生效。</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </TabsContent>

            <TabsContent value="behavior" className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <FormField
                  control={form.control}
                  name="layout_mode"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>布局模式</FormLabel>
                      <Select disabled={!canUpdate} onValueChange={field.onChange} value={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="选择布局模式" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="sidebar">经典侧边栏布局</SelectItem>
                          <SelectItem value="top">顶部菜单布局</SelectItem>
                          <SelectItem value="mixed">混合布局</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormDescription>系统的整体菜单导航结构。</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="menu_collapsed_default"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                      <div className="space-y-0.5">
                        <FormLabel className="text-base">默认折叠菜单</FormLabel>
                        <FormDescription>
                          新用户首次登录时，侧边栏是否默认处于折叠状态。
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                          disabled={!canUpdate}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="fixed_header"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                      <div className="space-y-0.5">
                        <FormLabel className="text-base">固定顶栏</FormLabel>
                        <FormDescription>
                          页面向下滚动时，顶部导航栏始终吸顶显示。
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                          disabled={!canUpdate}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="fixed_sidebar"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                      <div className="space-y-0.5">
                        <FormLabel className="text-base">固定侧边栏</FormLabel>
                        <FormDescription>
                          固定左侧菜单，仅右侧内容区域可滚动。
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                          disabled={!canUpdate}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="page_animation_enabled"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                      <div className="space-y-0.5">
                        <FormLabel className="text-base">启用页面切换动画</FormLabel>
                        <FormDescription>
                          在不同路由页面间跳转时，展示渐显过渡效果。
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                          disabled={!canUpdate}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
              </div>
            </TabsContent>
          </Tabs>
        </form>
      </Form>
    </div>
  )
}
