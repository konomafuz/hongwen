<template>
  <el-dialog :model-value="visible" title="AI 辅助生成" width="700px" @update:model-value="$emit('update:visible', $event)" @close="handleClose" top="5vh">
    <div v-loading="generating">
      <el-form label-width="80px">
        <el-form-item label="生成提示">
          <el-input v-model="prompt" type="textarea" :rows="4" placeholder="输入额外的生成要求或方向..." />
        </el-form-item>
        <el-form-item label="创意度">
          <el-slider v-model="temperature" :min="0.1" :max="1.5" :step="0.1" show-input />
        </el-form-item>
      </el-form>

      <div v-if="generatedContent" class="ai-panel">
        <div class="generated-content" v-html="renderedContent" />
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button v-if="generatedContent" type="success" @click="useResult">使用此结果</el-button>
      <el-button type="primary" :loading="generating" @click="handleGenerate">
        {{ generating ? '生成中...' : '开始生成' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { generateContentApi } from '@/api/ai'
import { marked } from 'marked'

const props = defineProps<{ visible: boolean; mode?: string; contextTitle?: string }>()
const emit = defineEmits(['update:visible', 'content'])

const prompt = ref('')
const temperature = ref(0.8)
const generating = ref(false)
const generatedContent = ref('')

const renderedContent = computed(() => {
  try { return marked(generatedContent.value) } catch { return generatedContent.value }
})

const handleGenerate = async () => {
  generating.value = true
  try {
    const res = await generateContentApi({
      prompt: prompt.value || `生成${props.contextTitle || '内容'}`,
      mode: props.mode || 'setting',
      temperature: temperature.value,
    })
    generatedContent.value = res.data.content
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '生成失败')
    // Fallback: return demo content for development
    generatedContent.value = `## AI生成结果（演示）\n\n这是AI辅助生成的内容示例。\n\n在实际运行中，这里会显示从DeepSeek API返回的生成内容。\n\n### 主要要点\n- 内容会根据你的提示和上下文生成\n- 你可以多次生成直到满意\n- 点击"使用此结果"将其应用到编辑区`
  } finally {
    generating.value = false
  }
}

const useResult = () => {
  emit('content', generatedContent.value)
  handleClose()
}

const handleClose = () => {
  prompt.value = ''
  generatedContent.value = ''
  emit('update:visible', false)
}
</script>

<style scoped>
.ai-panel { margin-top: 16px; padding: 16px; background: #f0f9ff; border-radius: 8px; border-left: 3px solid var(--primary-color); max-height: 400px; overflow-y: auto; }
.generated-content { line-height: 1.8; font-size: 14px; }
.generated-content :deep(p) { margin-bottom: 8px; }
</style>