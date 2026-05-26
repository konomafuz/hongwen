// User
export interface UserResponse {
  id: number
  email: string
  nickname: string
  role: string
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: UserResponse
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  nickname: string
}

// Project
export interface ProjectResponse {
  id: number
  user_id: number
  title: string
  mode: string
  status: string
  word_count: number
  created_at: string
  updated_at: string
}

export interface ProjectCreate {
  title: string
  mode: string
}

// Settings
export interface SettingResponse {
  id: number
  project_id: number
  genre: string | null
  world_view: string | null
  characters: Record<string, any> | null
  relationship_map: Record<string, any> | null
  conflict_system: Record<string, any> | null
  raw_content: string | null
  updated_at: string
}

// Tags
export interface TagResponse {
  id: number
  project_id: number
  tags: string[] | null
  synopsis_versions: string[] | null
  recommendation: string | null
  status: string | null
  updated_at: string
}

// Volume
export interface VolumeResponse {
  id: number
  project_id: number
  volume_number: number
  volume_title: string
  summary: string | null
  plot_arc: Record<string, any> | null
  chapters_estimated: number
  created_at: string
  updated_at: string
}

// Chapter
export interface ChapterResponse {
  id: number
  project_id: number
  volume_id: number | null
  chapter_number: number
  title: string
  outline: string | null
  content: string | null
  word_count: number
  status: string
  created_at: string
  updated_at: string
}

// AI
export interface AIGenerateRequest {
  prompt: string
  mode: string
  context?: string
  temperature?: number
  max_tokens?: number
  style?: string
}

export interface AIGenerateResponse {
  content: string
  finish_reason: string
  usage?: Record<string, any>
}