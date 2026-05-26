import apiClient from './index'
import type { TagResponse } from '@/types'

export const getTagsApi = (projectId: number) =>
  apiClient.get<TagResponse>(`/projects/${projectId}/tags`)

export const createTagsApi = (projectId: number, data: Record<string, any>) =>
  apiClient.post<TagResponse>(`/projects/${projectId}/tags`, data)

export const updateTagsApi = (projectId: number, data: Record<string, any>) =>
  apiClient.put<TagResponse>(`/projects/${projectId}/tags`, data)