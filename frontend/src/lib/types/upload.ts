export interface UploadFileResponse {
  id: string
  original_filename: string
  stored_filename: string
  extension: string
  content_type: string
  size_bytes: number
  sha256: string
  file_type: string
  visibility: string
  storage_provider: string
  storage_key: string
  public_url: string | null
  purpose: string | null
  created_by_id: string | null
  created_at: string
  updated_at: string
}
