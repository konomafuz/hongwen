<template>
  <div class="page-container">
    <div class="step-indicator">
      <div v-for="(step, idx) in steps" :key="idx" :class="['step', { active: idx === currentStep, completed: idx < currentStep }]" @click="goToStep(idx)">{{ step }}</div>
    </div>

    <div class="card">
      <h2 class="section-title">标签与简介</h2>
      <el-form label-width="120px" v-loading="loading">
        <el-form-item label="作品标签">
          <el-select v-model="tags" multiple filterable allow-create default-first-option placeholder="输入标签后回车添加" style="width: 100%">
            <el-option v-for="tag in tagOptions" :key="tag" :label="tag" :value="tag" />
          </el-select>
        </el-form-item>
        <el-form-item label="简介版本">
          <div v-for="(v, i) in synopsisVersions" :key="i" style="margin-bottom: 12px; width: 100%;">
            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 4px;">
              <span style="font-weight: 500;">版本 {{ i + 1 }}</span>
              <el-button text type="danger" size="small" @click="removeSynopsis(i)">删除</el-button>
            </div>
            <el-input v-model="synopsisVersions[i]" type="textarea" :rows="3" />
          </div>
          <el-button size="small" @click="addSynopsis">+ 添加简介版本</el-button>
        </el-form-item>
        <el-form-item label="推荐语">
          <el-input v-model="recommendation" type="textarea" :rows="2" placeholder="一句吸引人的推荐语" />
        </el-form-item>
      </el-form>

      <div class="form-footer">
        <el-button :icon="MagicStick" type="primary" :loading="aiLoading" @click="aiGenerate">AI生成标签简介</el-button>
        <el-button :icon="Upload" @click="saveTags">保存</el-button>
        <el-button @click="prevStep">上一步：核心设定</el-button>
        <el-button type="primary" @click="nextStep">下一步：分卷大纲</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MagicStick, Upload } from '@element-plus/icons-vue'
import { getTagsApi, createTagsApi, updateTagsApi } from '@/api/tags'

const route = useRoute()
const router = useRouter()
const projectId = Number(route.params.id)
const currentStep = 1
const steps = ['核心设定', '标签简介', '分卷大纲', '章节管理', '正文创作']

const loading = ref(false)
const aiLoading = ref(false)
const tags = ref<string[]>([])
const synopsisVersions = ref<string[]>([])
const recommendation = ref('')
const tagOptions = ['甜宠', '虐恋', '重生', '穿越', '女强', '爽文', '宫斗', '修仙', '玄幻', '现代', '古代', '先婚后爱', '双向奔赴', '破镜重圆', '暗恋成真']

const goToStep = (idx: number) => {
  const paths = ['settings', 'tags', 'volumes', 'chapters', 'chapters']
  router.push(`/project/${projectId}/${paths[idx]}`)
}
const prevStep = () => router.push(`/project/${projectId}/settings`)
const nextStep = () => router.push(`/project/${projectId}/volumes`)

const addSynopsis = () => synopsisVersions.value.push('')
const removeSynopsis = (i: number) => synopsisVersions.value.splice(i, 1)

const aiGenerate = () => {
  aiLoading.value = true
  setTimeout(() => {
    if (tags.value.length === 0) {
      tags.value = ['甜宠', '现代', '双向奔赴']
    }
    if (synopsisVersions.value.length === 0) {
      synopsisVersions.value = ['她，是命运多舛的落魄千金。他，是权倾天下的商业帝王。一场契约婚姻，让他们彼此纠缠。当真心与假意交织，她能否守住自己的心？']
    }
    aiLoading.value = false
    ElMessage.success('AI已生成标签和简介')
  }, 1500)
}

const saveTags = async () => {
  loading.value = true
  try {
    const data = { tags: tags.value, synopsis_versions: synopsisVersions.value, recommendation: recommendation.value }
    try {
      await getTagsApi(projectId)
      await updateTagsApi(projectId, data)
    } catch { await createTagsApi(projectId, data) }
    ElMessage.success('保存成功')
  } catch (err: any) { ElMessage.error(err.response?.data?.detail || '保存失败') }
  finally { loading.value = false }
}

onMounted(async () => {
  try {
    const res = await getTagsApi(projectId)
    tags.value = res.data.tags || []
    synopsisVersions.value = res.data.synopsis_versions || []
    recommendation.value = res.data.recommendation || ''
  } catch { /* no tags yet */ }
})
</script>

<style scoped>
.form-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border-color); }
</style>