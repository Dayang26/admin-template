export interface UserPublic {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  created_at: string
  roles?: string[]
}

export interface UserDetail extends UserPublic {
  roles: string[]
  permissions: string[]
}

export interface LoginResponse {
  access_token: string
  token_type: string
}
