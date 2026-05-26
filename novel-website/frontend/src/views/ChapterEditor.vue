<template>
  <div class="chapter-editor" v-loading="loading">
    <div class="editor-header">
      <div>
        <h2>第{{ chapter.chapter_number }}章 {{ chapter.title }}</h2>
        <span v-if="chapter.word_count" class="word-count">字数：{{ formatWordCount(chapter.word_count) }}</span>
      </div>
      <div class="header-actions">
        <el-button :icon="MagicStick" type="primary" :loading="generating" @click="aiDraft">AI生成正文</el-button>
        <el-button :icon="Upload" @click="saveContent">保存</el-button>
        <el-button @click="goBack">返回章节列表</el-button>
      </div>
    </div>

    <div class="editor-body">
      <div class="outline-section">
        <h3>章节大纲</h3>
        <el-input v-model="chapter.outline" type="textarea" :rows="5" placeholder="本章大纲内容..." @change="dirty = true" />
      </div>

      <div class="content-section">
        <h3>正文</h3>
        <el-input
          v-model="chapter.content"
          type="textarea"
          :rows="20"
          placeholder="在此处开始创作..."
          @change="dirty = true"
          input-style="font-size: 16px; line-height: 1.8; font-family: 'Noto Serif SC', 'SimSun', serif;"
        />
      </div>

      <div class="rag-section" v-if="showRag">
        <h3>RAG 语感参考</h3>
        <el-input v-model="ragQuery" placeholder="搜索语感参考..." size="small" @keyup.enter="searchRag">
          <template #append>
            <el-button @click="searchRag">搜索</el-button>
          </template>
        </el-input>
        <div v-if="ragResults.length" class="rag-results">
          <div v-for="r in ragResults" :key="r.filename" class="rag-item">
            <div class="rag-filename">{{ r.filename }}</div>
            <pre class="rag-content">{{ r.content }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MagicStick, Upload } from '@element-plus/icons-vue'
import { getChapterApi, updateChapterApi } from '@/api/chapter'
import { draftChapterApi, searchRagApi } from '@/api/ai'
import { formatWordCount } from '@/utils/format'
import type { ChapterResponse } from '@/types'

const route = useRoute()
const router = useRouter()
const projectId = Number(route.params.id)
const chapterId = Number(route.params.chapterId)

const chapter = ref<ChapterResponse>({ id: 0, project_id: 0, volume_id: null, chapter_number: 0, title: '', outline: '', content: '', word_count: 0, status: 'outline', created_at: '', updated_at: '' })
const loading = ref(false)
const generating = ref(false)
const dirty = ref(false)
const showRag = ref(false)
const ragQuery = ref('')
const ragResults = ref<any[]>([])

const goBack = () => router.push(`/project/${projectId}/chapters`)

const saveContent = async () => {
  loading.value = true
  try {
    const data = {
      title: chapter.value.title,
      outline: chapter.value.outline || null,
      content: chapter.value.content || null,
      status: chapter.value.content ? 'drafting' : 'outline',
    }
    const res = await updateChapterApi(projectId, chapterId, data)
    chapter.value = res.data
    dirty.value = false
    ElMessage.success('保存成功')
  } catch (err: any) { ElMessage.error(err.response?.data?.detail || '保存失败') }
  finally { loading.value = false }
}

const aiDraft = async () => {
  generating.value = true
  try {
    const context = `章节：第${chapter.value.chapter_number}章 ${chapter.value.title}\n大纲：${chapter.value.outline || '无'}`
    const res = await draftChapterApi({ prompt: `请根据以下大纲创作第${chapter.value.chapter_number}章正文，字数1800-2200字`, mode: 'draft', context, temperature: 0.8 })
    chapter.value.content = res.data.content
    dirty.value = true
    ElMessage.success('AI正文生成完成，请检查内容并保存')
  } catch (err: any) { ElMessage.error(err.response?.data?.detail || '生成失败') }
  finally { generating.value = false }
}

const searchRag = async () => {
  if (!ragQuery.value) return
  try {
    const res = await searchRagApi(ragQuery.value)
    ragResults.value = res.data.results || []
  } catch { ElMessage.error('搜索失败') }
}

onMounted(async () => {
  try {
    const res = await getChapterApi(projectId, chapterId)
    chapter.value = res.data
  } catch { ElMessage.error('章节不存在'); goBack() }
})
</script>

<style scoped>
.chapter-editor { padding: 24px; max-width: 1000px; margin: 0 auto; }
.editor-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.editor-header h2 { font-size: 20px; margin-bottom: 4px; }
.word-count { color: var(--text-secondary); font-size: 13px; }
.header-actions { display: flex; gap: 8px; flex-shrink: 0; }
.editor-body > div { margin-bottom: 24px; }
.editor-body h3 { font-size: 15px; font-weight: 600; margin-bottom: 8px; color: var(--text-primary); }
.outline-section, .rag-section { background: var(--card-bg); border-radius: 8px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.content-section { background: var(--card-bg); border-radius: 8px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.rag-results { margin-top: 12px; }
.rag-item { padding: 12px; border: 1px solid var(--border-color); border-radius: 4px; margin-bottom: 8px; }
.rag-filename { font-weight: 500; font-size: 13px; margin-bottom: 4px; color: var(--primary-color); }
.rag-content { font-size: 12px; color: var(--text-secondary); white-space: pre-wrap; max-height: 200px; overflow-y: auto; }
</style>