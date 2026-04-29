export interface SystemSettingPublic {
  system_name: string
  tagline: string | null
  copyright: string | null
  page_title_template: string

  logo_light_url: string | null
  logo_dark_url: string | null
  favicon_url: string | null
  login_background_url: string | null
}

export interface SystemSettingAdmin extends SystemSettingPublic {
  logo_light_file_id: string | null
  logo_dark_file_id: string | null
  favicon_file_id: string | null
  login_background_file_id: string | null
}

export type SystemSettingUpdatePayload = Partial<SystemSettingAdmin>
