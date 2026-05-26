import apiClient from './index'
import type { ProjectResponse, ProjectCreate } from '@/types'

export const listProjectsApi = () =>
  apiClient.get<ProjectResponse[]>('/projects')

export const createProjectApi = (data: ProjectCreate) =>
  apiClient.post<ProjectResponse>('/projects', data)

export const getProjectApi = (id: number) =>
  apiClient.get<ProjectResponse>(`/projects/${id}`)

export const updateProjectApi = (id: number, data: Partial<ProjectCreate>) =>
  apiClient.put<ProjectResponse>(`/projects/${id}`, data)

export const deleteProjectApi = (id: number) =>
  apiClient.delete(`/projects/${id}`)

export const duplicateProjectApi = (id: number) =>
  apiClient.post<ProjectResponse>(`/projects/${id}/duplicate`)