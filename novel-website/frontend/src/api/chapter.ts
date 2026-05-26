import apiClient from './index'
import type { ChapterResponse } from '@/types'

export const listChaptersApi = (projectId: number) =>
  apiClient.get<ChapterResponse[]>(`/projects/${projectId}/chapters`)

export const createChapterApi = (projectId: number, data: Record<string, any>) =>
  apiClient.post<ChapterResponse>(`/projects/${projectId}/chapters`, data)

export const getChapterApi = (projectId: number, chapterId: number) =>
  apiClient.get<ChapterResponse>(`/projects/${projectId}/chapters/${chapterId}`)

export const updateChapterApi = (projectId: number, chapterId: number, data: Record<string, any>) =>
  apiClient.put<ChapterResponse>(`/projects/${projectId}/chapters/${chapterId}`, data)

export const deleteChapterApi = (projectId: number, chapterId: number) =>
  apiClient.delete(`/projects/${projectId}/chapters/${chapterId}`)