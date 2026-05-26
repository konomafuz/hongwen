<template>
  <div class="page-container">
    <div class="step-indicator">
      <div v-for="(step, idx) in steps" :key="idx" :class="['step', { active: idx === currentStep }]" @click="goToStep(idx)">
        {{ step }}
      </div>
    </div>

    <div class="card">
      <h2 class="section-title">核心设定</h2>
      <el-form :model="form" label-width="100px" v-loading="loading">
        <el-form-item label="小说类型">
          <el-select v-model="form.genre" placeholder="选择类型" style="width: 100%">
            <el-option label="现代言情" value="现代言情" />
            <el-option label="古代言情" value="古代言情" />
            <el-option label="玄幻言情" value="玄幻言情" />
            <el-option label="仙侠言情" value="仙侠言情" />
            <el-option label="科幻言情" value="科幻言情" />
            <el-option label="悬疑言情" value="悬疑言情" />
            <el-option label="青春校园" value="青春校园" />
            <el-option label="重生穿越" value="重生穿越" />
          </el-select>
        </el-form-item>
        <el-form-item label="世界观设定">
          <el-input v-model="form.world_view" type="textarea" :rows="4" placeholder="描述故事的世界观背景，时代、地域、社会规则等" />
        </el-form-item>
        <el-form-item label="人物设定">
          <el-input v-model="form.charactersText" type="textarea" :rows="6" placeholder="主角、配角的人物设定，包括姓名、性格、背景、外貌等（JSON格式或文字描述）" />
        </el-form-item>
        <el-form-item label="感情线">
          <el-input v-model="form.relationshipText" type="textarea" :rows="4" placeholder="主要人物之间的感情关系和发展方向" />
        </el-form-item>
        <el-form-item label="冲突体系">
          <el-input v-model="form.conflictText" type="textarea" :rows="4" placeholder="故事的主要矛盾冲突，包括内部冲突和外部冲突" />
        </el-form-item>
      </el-form>

      <div class="form-footer">
        <el-button :icon="MagicStick" type="primary" :loading="aiLoading" @click="aiGenerate">AI辅助生成</el-button>
        <el-button :icon="Upload" @click="saveSettings">保存</el-button>
        <el-button type="primary" @click="nextStep">下一步：标签简介</el-button>
      </div>
    </div>

    <AIGenerateDialog v-model:visible="showAIDialog" mode="setting" contextTitle="核心设定" @content="onAIContent" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MagicStick, Upload } from '@element-plus/icons-vue'
import { getSettingsApi, createSettingsApi, updateSettingsApi } from '@/api/settings'
import AIGenerateDialog from '@/components/AIGenerateDialog.vue'

const route = useRoute()
const router = useRouter()
const projectId = Number(route.params.id)

const loading = ref(false)
const aiLoading = ref(false)
const showAIDialog = ref(false)
const currentStep = 0

const steps = ['核心设定', '标签简介', '分卷大纲', '章节管理', '正文创作']

const form = reactive({
  genre: '',
  world_view: '',
  charactersText: '',
  relationshipText: '',
  conflictText: '',
})

const goToStep = (idx: number) => {
  const paths = ['settings', 'tags', 'volumes', 'chapters', 'chapters']
  router.push(`/project/${projectId}/${paths[idx]}`)
}

const nextStep = () => router.push(`/project/${projectId}/tags`)

const aiGenerate = () => { showAIDialog.value = true }

const onAIContent = (content: string) => {
  form.world_view = form.world_view || content.slice(0, 500)
  ElMessage.success('已应用AI生成内容')
}

const saveSettings = async () => {
  loading.value = true
  try {
    const data = {
      genre: form.genre || null,
      world_view: form.world_view || null,
      characters: form.charactersText ? { text: form.charactersText } : null,
      relationship_map: form.relationshipText ? { text: form.relationshipText } : null,
      conflict_system: form.conflictText ? { text: form.conflictText } : null,
    }
    try {
      await getSettingsApi(projectId)
      await updateSettingsApi(projectId, data)
    } catch {
      await createSettingsApi(projectId, data)
    }
    ElMessage.success('保存成功')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '保存失败')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const res = await getSettingsApi(projectId)
    const s = res.data
    form.genre = s.genre || ''
    form.world_view = s.world_view || ''
    form.charactersText = s.characters?.text || ''
    form.relationshipText = s.relationship_map?.text || ''
    form.conflictText = s.conflict_system?.text || ''
  } catch { /* no settings yet */ }
})
</script>

<style scoped>
.form-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}
</style>