import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listProjectsApi, createProjectApi, getProjectApi, updateProjectApi, deleteProjectApi, duplicateProjectApi } from '@/api/project'
import type { ProjectResponse } from '@/types'

export const useProjectStore = defineStore('project', () => {
  const currentProject = ref<ProjectResponse | null>(null)
  const projectList = ref<ProjectResponse[]>([])
  const loading = ref(false)

  async function fetchProjects() {
    loading.value = true
    try {
      const res = await listProjectsApi()
      projectList.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function fetchProject(id: number) {
    loading.value = true
    try {
      const res = await getProjectApi(id)
      currentProject.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function createProject(title: string, mode: string) {
    const res = await createProjectApi({ title, mode })
    projectList.value.unshift(res.data)
    return res.data
  }

  async function updateProject(id: number, data: Partial<ProjectResponse>) {
    const res = await updateProjectApi(id, data)
    if (currentProject.value?.id === id) {
      currentProject.value = res.data
    }
    const idx = projectList.value.findIndex((p) => p.id === id)
    if (idx !== -1) projectList.value[idx] = res.data
    return res.data
  }

  async function deleteProject(id: number) {
    await deleteProjectApi(id)
    projectList.value = projectList.value.filter((p) => p.id !== id)
    if (currentProject.value?.id === id) {
      currentProject.value = null
    }
  }

  async function duplicateProject(id: number) {
    const res = await duplicateProjectApi(id)
    projectList.value.unshift(res.data)
    return res.data
  }

  return { currentProject, projectList, loading, fetchProjects, fetchProject, createProject, updateProject, deleteProject, duplicateProject }
})