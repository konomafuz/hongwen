<template>
  <div class="page-container">
    <div class="step-indicator">
      <div v-for="(step, idx) in steps" :key="idx" :class="['step', { active: idx === currentStep, completed: idx < currentStep }]" @click="goToStep(idx)">{{ step }}</div>
    </div>

    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
        <h2 class="section-title" style="margin-bottom: 0;">章节管理</h2>
        <div style="display: flex; gap: 8px;">
          <el-button :icon="Download" @click="handleExport">导出Word</el-button>
          <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">新建章节</el-button>
        </div>
      </div>

      <el-table :data="chapters" stripe empty-text="还没有章节，点击新建章节开始创作" @row-click="openEditor">
        <el-table-column prop="chapter_number" label="章号" width="80" />
        <el-table-column prop="title" label="章节标题" min-width="200">
          <template #default="{ row }">
            <span style="cursor: pointer; color: var(--primary-color);">第{{ row.chapter_number }}章 {{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="word_count" label="字数" width="100" :formatter="(r: any) => formatWordCount(r.word_count)" />
        <el-table-column prop="updated_at" label="更新时间" width="180" :formatter="(r: any) => formatDate(r.updated_at)" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" type="danger" @click.stop="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Create Chapter Dialog -->
    <el-dialog v-model="showCreateDialog" title="新建章节" width="500px">
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="章节标题" prop="title">
          <el-input v-model="createForm.title" placeholder="输入章节标题" />
        </el-form-item>
        <el-form-item label="章节大纲">
          <el-input v-model="createForm.outline" type="textarea" :rows="4" placeholder="可选：输入本章大纲" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download } from '@element-plus/icons-vue'
import { listChaptersApi, createChapterApi, deleteChapterApi } from '@/api/chapter'
import { exportWordApi } from '@/api/export'
import { formatDate, formatWordCount, downloadBlob } from '@/utils/format'
import type { ChapterResponse } from '@/types'
import type { FormInstance } from 'element-plus'

const route = useRoute()
const router = useRouter()
const projectId = Number(route.params.id)
const currentStep = 3
const steps = ['核心设定', '标签简介', '分卷大纲', '章节管理', '正文创作']

const chapters = ref<ChapterResponse[]>([])
const showCreateDialog = ref(false)
const creating = ref(false)
const createFormRef = ref<FormInstance>()
const createForm = ref({ title: '', outline: '' })
const createRules = { title: [{ required: true, message: '请输入章节标题', trigger: 'blur' }] }

const statusType = (s: string) => ({ outline: 'info', drafting: 'warning', reviewing: 'primary', completed: 'success' }[s] || 'info')
const statusLabel = (s: string) => ({ outline: '大纲', drafting: '创作中', reviewing: '审查中', completed: '已完成' }[s] || s)

const goToStep = (idx: number) => {
  const paths = ['settings', 'tags', 'volumes', 'chapters', 'chapters']
  router.push(`/project/${projectId}/${paths[idx]}`)
}

const openEditor = (row: any) => router.push(`/project/${projectId}/chapter/${row.id}`)

const handleCreate = async () => {
  creating.value = true
  try {
    const nextNumber = chapters.value.length + 1
    const res = await createChapterApi(projectId, { chapter_number: nextNumber, title: createForm.value.title, outline: createForm.value.outline || null })
    chapters.value.push(res.data)
    showCreateDialog.value = false
    createForm.value = { title: '', outline: '' }
    ElMessage.success('章节创建成功')
  } catch (err: any) { ElMessage.error(err.response?.data?.detail || '创建失败') }
  finally { creating.value = false }
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定删除此章节？', '确认删除', { type: 'warning' })
    await deleteChapterApi(projectId, row.id)
    chapters.value = chapters.value.filter((c) => c.id !== row.id)
    ElMessage.success('已删除')
  } catch { /* cancelled */ }
}

const handleExport = async () => {
  try {
    const res = await exportWordApi(projectId)
    downloadBlob(res.data, `novel_${projectId}.docx`)
    ElMessage.success('导出成功')
  } catch (err: any) { ElMessage.error('导出失败') }
}

onMounted(async () => {
  try {
    const res = await listChaptersApi(projectId)
    chapters.value = res.data
  } catch { /* no chapters */ }
})
</script>