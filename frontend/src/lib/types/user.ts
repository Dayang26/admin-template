export interface UserPublic {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  created_at: string
  roles?: string[]
}

export interface ClassMembership {
  class_id: string
  class_name: string
  role: string
}

export interface UserDetail extends UserPublic {
  roles: string[]
  class_memberships: ClassMembership[]
}

export interface LoginResponse {
  access_token: string
  token_type: string
}
