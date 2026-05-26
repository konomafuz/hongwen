import apiClient from './index'
import type { SettingResponse } from '@/types'

export const getSettingsApi = (projectId: number) =>
  apiClient.get<SettingResponse>(`/projects/${projectId}/settings`)

export const createSettingsApi = (projectId: number, data: Record<string, any>) =>
  apiClient.post<SettingResponse>(`/projects/${projectId}/settings`, data)

export const updateSettingsApi = (projectId: number, data: Record<string, any>) =>
  apiClient.put<SettingResponse>(`/projects/${projectId}/settings`, data)