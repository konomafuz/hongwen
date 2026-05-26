import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/pricing',
    name: 'Pricing',
    component: () => import('@/views/Pricing.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
      },
      {
        path: 'project/:id',
        redirect: { name: 'ProjectSettings' },
        children: [
          {
            path: 'settings',
            name: 'ProjectSettings',
            component: () => import('@/views/ProjectSettings.vue'),
          },
          {
            path: 'tags',
            name: 'ProjectTags',
            component: () => import('@/views/ProjectTags.vue'),
          },
          {
            path: 'volumes',
            name: 'ProjectVolumes',
            component: () => import('@/views/ProjectVolumes.vue'),
          },
          {
            path: 'chapters',
            name: 'ProjectChapters',
            component: () => import('@/views/ProjectChapters.vue'),
          },
          {
            path: 'chapter/:chapterId',
            name: 'ChapterEditor',
            component: () => import('@/views/ChapterEditor.vue'),
          },
        ],
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)

  if (requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (!requiresAuth && token && (to.name === 'Login' || to.name === 'Register')) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router