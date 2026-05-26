import apiClient from './index'
import type { VolumeResponse } from '@/types'

export const listVolumesApi = (projectId: number) =>
  apiClient.get<VolumeResponse[]>(`/projects/${projectId}/volumes`)

export const createVolumeApi = (projectId: number, data: Record<string, any>) =>
  apiClient.post<VolumeResponse>(`/projects/${projectId}/volumes`, data)

export const updateVolumeApi = (projectId: number, volumeId: number, data: Record<string, any>) =>
  apiClient.put<VolumeResponse>(`/projects/${projectId}/volumes/${volumeId}`, data)

export const deleteVolumeApi = (projectId: number, volumeId: number) =>
  apiClient.delete(`/projects/${projectId}/volumes/${volumeId}`)