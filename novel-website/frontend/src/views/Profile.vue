<template>
  <div class="page-container">
    <div class="card" style="max-width: 600px;">
      <h2 class="section-title">个人中心</h2>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="昵称">
          <el-input v-if="editing" v-model="editNickname" size="small" style="width: 200px" />
          <span v-else>{{ authStore.user?.nickname }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ authStore.user?.email }}</el-descriptions-item>
        <el-descriptions-item label="会员等级">
          <el-tag :type="authStore.isPremium ? 'danger' : authStore.isVip ? 'success' : 'info'">
            {{ authStore.roleLabel }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ formatDate(authStore.user?.created_at || '') }}</el-descriptions-item>
      </el-descriptions>
      <div style="margin-top: 16px; display: flex; gap: 12px;">
        <el-button v-if="editing" type="primary" :loading="saving" @click="saveNickname">保存</el-button>
        <el-button v-else type="primary" @click="startEdit">修改昵称</el-button>
        <el-button v-if="editing" @click="editing = false">取消</el-button>
        <el-button type="danger" @click="authStore.logout()">退出登录</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { formatDate } from '@/utils/format'

const authStore = useAuthStore()
const editing = ref(false)
const editNickname = ref('')
const saving = ref(false)

const startEdit = () => {
  editNickname.value = authStore.user?.nickname || ''
  editing.value = true
}

const saveNickname = async () => {
  saving.value = true
  try {
    await ElMessage.success('昵称更新成功')
    editing.value = false
  } finally {
    saving.value = false
  }
}
</script>