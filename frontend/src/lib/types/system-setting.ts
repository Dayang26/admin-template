export interface SystemSettingPublic {
  system_name: string
  tagline: string | null
  copyright: string | null
  page_title_template: string

  logo_light_url: string | null
  logo_dark_url: string | null
  favicon_url: string | null
  login_background_url: string | null

  primary_color: string
  theme_mode: 'light' | 'dark' | 'system'
  layout_mode: 'sidebar' | 'top' | 'mixed'

  menu_collapsed_default: boolean
  fixed_header: boolean
  fixed_sidebar: boolean
  page_animation_enabled: boolean

  default_home_path: string
}

export interface SystemSettingAdmin extends SystemSettingPublic {
  logo_light_file_id: string | null
  logo_dark_file_id: string | null
  favicon_file_id: string | null
  login_background_file_id: string | null

  tab_view_enabled: boolean
  route_cache_enabled: boolean
  request_timeout_ms: number
}

export type SystemSettingUpdatePayload = Partial<SystemSettingAdmin>
