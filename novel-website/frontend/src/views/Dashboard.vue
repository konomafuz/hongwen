<template>
  <div class="page-container">
    <div class="dashboard-header">
      <h2>我的项目</h2>
      <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">新建项目</el-button>
    </div>

    <el-table v-if="projectStore.projectList.length" :data="projectStore.projectList" stripe @row-click="openProject">
      <el-table-column prop="title" label="项目名称" min-width="200" />
      <el-table-column prop="mode" label="模式" width="100">
        <template #default="{ row }">
          <el-tag :type="row.mode === 'guide' ? 'primary' : 'success'" size="small">
            {{ row.mode === 'guide' ? '引导模式' : '专家模式' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'completed' ? 'success' : 'warning'" size="small">
            {{ row.status === 'completed' ? '已完成' : '创作中' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="word_count" label="字数" width="120" :formatter="(r: any) => formatWordCount(r.word_count)" />
      <el-table-column prop="created_at" label="创建时间" width="180" :formatter="(r: any) => formatDate(r.created_at)" />
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button text size="small" @click.stop="handleDuplicate(row)">复制</el-button>
          <el-button text size="small" type="danger" @click.stop="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-else description="还没有项目，点击右上角新建项目开始创作" />

    <!-- Create Dialog -->
    <el-dialog v-model="showCreateDialog" title="新建项目" width="500px">
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="80px">
        <el-form-item label="项目名称" prop="title">
          <el-input v-model="createForm.title" placeholder="给你的小说取个名字" maxlength="200" />
        </el-form-item>
        <el-form-item label="创作模式" prop="mode">
          <el-radio-group v-model="createForm.mode">
            <el-radio value="guide">
              <div>
                <div>引导模式</div>
                <small style="color: var(--text-secondary)">适合新人，每一步有模板和AI辅助</small>
              </div>
            </el-radio>
            <el-radio value="expert">
              <div>
                <div>专家模式</div>
                <small style="color: var(--text-secondary)">自由创作，支持导入已有设定</small>
              </div>
            </el-radio>
          </el-radio-group>
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useProjectStore } from '@/stores/project'
import { Plus } from '@element-plus/icons-vue'
import { formatDate, formatWordCount } from '@/utils/format'
import type { FormInstance } from 'element-plus'

const router = useRouter()
const projectStore = useProjectStore()

const showCreateDialog = ref(false)
const creating = ref(false)
const createFormRef = ref<FormInstance>()
const createForm = reactive({ title: '', mode: 'guide' })
const createRules = {
  title: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  mode: [{ required: true, message: '请选择创作模式', trigger: 'change' }],
}

onMounted(() => projectStore.fetchProjects())

const openProject = (row: any) => router.push(`/project/${row.id}/settings`)

const handleCreate = async () => {
  const valid = await createFormRef.value?.validate().catch(() => false)
  if (!valid) return
  creating.value = true
  try {
    const project = await projectStore.createProject(createForm.title, createForm.mode)
    showCreateDialog.value = false
    ElMessage.success('项目创建成功')
    router.push(`/project/${project.id}/settings`)
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '创建失败')
  } finally {
    creating.value = false
  }
}

const handleDuplicate = async (row: any) => {
  try {
    await projectStore.duplicateProject(row.id)
    ElMessage.success('已复制项目')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '复制失败')
  }
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定删除该项目？此操作不可恢复。', '确认删除', { type: 'warning' })
    await projectStore.deleteProject(row.id)
    ElMessage.success('已删除')
  } catch { /* cancelled */ }
}
</script>

<style scoped>
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.dashboard-header h2 { font-size: 22px; font-weight: 600; }
</style>