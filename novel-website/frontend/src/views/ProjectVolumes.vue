<template>
  <div class="page-container">
    <div class="step-indicator">
      <div v-for="(step, idx) in steps" :key="idx" :class="['step', { active: idx === currentStep, completed: idx < currentStep }]" @click="goToStep(idx)">{{ step }}</div>
    </div>

    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
        <h2 class="section-title" style="margin-bottom: 0;">分卷大纲</h2>
        <el-button type="primary" :icon="Plus" @click="addVolume">添加分卷</el-button>
      </div>

      <div v-if="volumes.length === 0" class="empty-state">
        <el-empty description="还没有分卷，点击添加分卷开始规划故事结构" />
      </div>

      <div v-for="(vol, idx) in volumes" :key="idx" class="volume-card">
        <el-collapse>
          <el-collapse-item>
            <template #title>
              <span style="font-weight: 500;">第{{ vol.volume_number }}卷：{{ vol.volume_title }}</span>
              <el-tag size="small" style="margin-left: 8px;">预计{{ vol.chapters_estimated }}章</el-tag>
            </template>
            <div class="volume-form">
              <el-input v-model="vol.volume_title" placeholder="分卷名称" style="margin-bottom: 12px;" />
              <el-input v-model="vol.summary" type="textarea" :rows="3" placeholder="分卷简介" style="margin-bottom: 12px;" />
              <el-input-number v-model="vol.chapters_estimated" :min="1" :max="50" label="预计章节数" />
              <div style="margin-top: 12px; display: flex; gap: 8px;">
                <el-button size="small" type="primary" :icon="MagicStick" @click="aiGenerateVolume(idx)">AI生成</el-button>
                <el-button size="small" :icon="Upload" @click="saveVolume(idx)">保存</el-button>
                <el-button size="small" type="danger" @click="deleteVolume(idx)">删除</el-button>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>

      <div class="form-footer">
        <el-button @click="prevStep">上一步：标签简介</el-button>
        <el-button type="primary" @click="nextStep">下一步：章节管理</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, MagicStick, Upload } from '@element-plus/icons-vue'
import { listVolumesApi, createVolumeApi, updateVolumeApi, deleteVolumeApi } from '@/api/volume'

const route = useRoute()
const router = useRouter()
const projectId = Number(route.params.id)
const currentStep = 2
const steps = ['核心设定', '标签简介', '分卷大纲', '章节管理', '正文创作']

interface VolumeItem { volume_number: number; volume_title: string; summary: string; chapters_estimated: number; id?: number }
const volumes = ref<VolumeItem[]>([])

const goToStep = (idx: number) => {
  const paths = ['settings', 'tags', 'volumes', 'chapters', 'chapters']
  router.push(`/project/${projectId}/${paths[idx]}`)
}
const prevStep = () => router.push(`/project/${projectId}/tags`)
const nextStep = () => router.push(`/project/${projectId}/chapters`)

const addVolume = () => {
  volumes.value.push({
    volume_number: volumes.value.length + 1,
    volume_title: '',
    summary: '',
    chapters_estimated: 10,
  })
}

const aiGenerateVolume = (idx: number) => {
  const templates = [
    { title: '初遇篇', summary: '主角相遇，埋下感情伏笔，展现世界观。' },
    { title: '发展篇', summary: '感情升温，矛盾初现，配角登场。' },
    { title: '冲突篇', summary: '主要矛盾爆发，感情面临考验。' },
    { title: '转折篇', summary: '真相大白，关系逆转，高潮迭起。' },
    { title: '结局篇', summary: '所有线索收束，感情归宿，圆满结局。' },
  ]
  const t = templates[idx] || templates[0]
  volumes.value[idx].volume_title = t.title
  volumes.value[idx].summary = t.summary
  ElMessage.success('已生成分卷内容')
}

const saveVolume = async (idx: number) => {
  const vol = volumes.value[idx]
  try {
    if (vol.id) {
      await updateVolumeApi(projectId, vol.id, { volume_title: vol.volume_title, summary: vol.summary, chapters_estimated: vol.chapters_estimated })
    } else {
      const res = await createVolumeApi(projectId, { volume_number: vol.volume_number, volume_title: vol.volume_title, summary: vol.summary, chapters_estimated: vol.chapters_estimated })
      vol.id = res.data.id
    }
    ElMessage.success('保存成功')
  } catch (err: any) { ElMessage.error(err.response?.data?.detail || '保存失败') }
}

const deleteVolume = async (idx: number) => {
  const vol = volumes.value[idx]
  if (vol.id) {
    try { await deleteVolumeApi(projectId, vol.id) } catch { /* ignore */ }
  }
  volumes.value.splice(idx, 1)
  ElMessage.success('已删除')
}

onMounted(async () => {
  try {
    const res = await listVolumesApi(projectId)
    volumes.value = res.data.map((v: any) => ({
      id: v.id, volume_number: v.volume_number, volume_title: v.volume_title,
      summary: v.summary || '', chapters_estimated: v.chapters_estimated,
    }))
  } catch { /* no volumes */ }
})
</script>

<style scoped>
.volume-card { margin-bottom: 12px; border: 1px solid var(--border-color); border-radius: 8px; }
.volume-form { padding: 16px; }
.form-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border-color); }
</style>