export interface ClassPublic {
  id: string
  name: string
  description: string | null
  created_at: string
  updated_at: string
  member_count?: number
}

export interface ClassMember {
  user_id: string
  email: string
  full_name: string | null
  role: string
  joined_at: string
}
