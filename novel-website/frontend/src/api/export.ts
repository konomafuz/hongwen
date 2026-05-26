import apiClient from './index'

export const exportWordApi = (projectId: number, includeOutline = true) =>
  apiClient.post('/export/word', { project_id: projectId, format: 'word', include_outline: includeOutline }, {
    responseType: 'blob',
  })