import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loginApi, registerApi, fetchProfileApi } from '@/api/auth'
import type { UserResponse } from '@/types'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<UserResponse | null>(
    localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')!) : null
  )

  const isLoggedIn = computed(() => !!token.value)
  const isPremium = computed(() => user.value?.role === 'premium')
  const isVip = computed(() => user.value?.role === 'vip' || user.value?.role === 'premium')
  const roleLabel = computed(() => {
    const labels: Record<string, string> = { free: '免费用户', vip: '普通会员', premium: '高级会员' }
    return labels[user.value?.role || 'free'] || '免费用户'
  })

  async function login(email: string, password: string) {
    const res = await loginApi({ email, password })
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    router.push('/dashboard')
  }

  async function register(email: string, password: string, nickname: string) {
    const res = await registerApi({ email, password, nickname })
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    router.push('/dashboard')
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }

  async function fetchProfile() {
    try {
      const res = await fetchProfileApi()
      user.value = res.data
      localStorage.setItem('user', JSON.stringify(res.data))
    } catch {
      logout()
    }
  }

  return { token, user, isLoggedIn, isPremium, isVip, roleLabel, login, register, logout, fetchProfile }
})