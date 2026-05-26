import apiClient from './index'
import type { AIGenerateRequest, AIGenerateResponse } from '@/types'

export const generateContentApi = (data: AIGenerateRequest) =>
  apiClient.post<AIGenerateResponse>('/ai/generate', data)

export const draftChapterApi = (data: AIGenerateRequest) =>
  apiClient.post<AIGenerateResponse>('/ai/draft', data)

export const searchRagApi = (q: string) =>
  apiClient.get<{ results: any[] }>('/ai/rag', { params: { q } })