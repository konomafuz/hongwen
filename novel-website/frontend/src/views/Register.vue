<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-title">创建账号</h1>
      <p class="auth-subtitle">加入红文织梦，开启创作之旅</p>
      <el-form :model="form" :rules="rules" ref="formRef" @submit.prevent="handleRegister" size="large">
        <el-form-item prop="email">
          <el-input v-model="form.email" placeholder="邮箱" :prefix-icon="Message" />
        </el-form-item>
        <el-form-item prop="nickname">
          <el-input v-model="form.nickname" placeholder="昵称" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" :prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="确认密码" :prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" style="width: 100%">注册</el-button>
        </el-form-item>
      </el-form>
      <div class="auth-footer">已有账号？<router-link to="/login">立即登录</router-link></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { Message, Lock, User } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'

const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const form = reactive({ email: '', nickname: '', password: '', confirmPassword: '' })
const rules = {
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }, { min: 1, max: 50, message: '昵称1-50字', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码至少6位', trigger: 'blur' }],
  confirmPassword: [{ required: true, message: '请确认密码', trigger: 'blur' }, {
    validator: (_: any, value: string) => value === form.password ? Promise.resolve() : Promise.reject('两次密码不一致'),
    trigger: 'blur',
  }],
}

const handleRegister = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await authStore.register(form.email, form.password, form.nickname)
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.auth-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  width: 400px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}
.auth-title { text-align: center; font-size: 28px; color: var(--primary-color); margin-bottom: 4px; }
.auth-subtitle { text-align: center; color: var(--text-secondary); margin-bottom: 32px; font-size: 14px; }
.auth-footer { text-align: center; color: var(--text-secondary); font-size: 13px; }
</style>