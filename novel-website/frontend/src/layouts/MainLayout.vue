<template>
  <el-container class="app-container">
    <el-aside :width="isCollapsed ? '64px' : '220px'" class="app-sidebar">
      <div class="sidebar-header">
        <div v-if="!isCollapsed" class="logo">红文织梦</div>
        <el-button :icon="isCollapsed ? Expand : Fold" text @click="isCollapsed = !isCollapsed" />
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :router="true"
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Platform /></el-icon>
          <template #title>控制台</template>
        </el-menu-item>
        <el-sub-menu v-if="hasProject" index="project">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>当前项目</span>
          </template>
          <el-menu-item :index="`/project/${projectId}/settings`">
            <el-icon><Setting /></el-icon>
            <template #title>核心设定</template>
          </el-menu-item>
          <el-menu-item :index="`/project/${projectId}/tags`">
            <el-icon><CollectionTag /></el-icon>
            <template #title>标签简介</template>
          </el-menu-item>
          <el-menu-item :index="`/project/${projectId}/volumes`">
            <el-icon><Document /></el-icon>
            <template #title>分卷大纲</template>
          </el-menu-item>
          <el-menu-item :index="`/project/${projectId}/chapters`">
            <el-icon><Notebook /></el-icon>
            <template #title>章节管理</template>
          </el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <template #title>个人中心</template>
        </el-menu-item>
        <el-menu-item index="/pricing">
          <el-icon><Coin /></el-icon>
          <template #title>会员服务</template>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="app-header">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item v-if="breadcrumbTitle">{{ breadcrumbTitle }}</el-breadcrumb-item>
        </el-breadcrumb>
        <div class="header-right">
          <el-tag size="small" type="success" v-if="authStore.isVip">VIP</el-tag>
          <el-dropdown trigger="click">
            <span class="user-dropdown">
              {{ authStore.user?.nickname || '用户' }}
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/profile')">个人中心</el-dropdown-item>
                <el-dropdown-item @click="router.push('/pricing')">会员服务</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProjectStore } from '@/stores/project'
import { Expand, Fold, Platform, Document, Setting, CollectionTag, Notebook, User, Coin, ArrowDown } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const projectStore = useProjectStore()
const isCollapsed = ref(false)

const activeMenu = computed(() => route.path)
const projectId = computed(() => route.params.id as string)
const hasProject = computed(() => !!route.params.id)

const breadcrumbTitle = computed(() => {
  const nameMap: Record<string, string> = {
    Dashboard: '控制台',
    ProjectSettings: '核心设定',
    ProjectTags: '标签简介',
    ProjectVolumes: '分卷大纲',
    ProjectChapters: '章节管理',
    ChapterEditor: '章节编辑',
    Profile: '个人中心',
    Pricing: '会员服务',
  }
  return nameMap[route.name as string] || ''
})

const handleLogout = () => {
  authStore.logout()
}
</script>

<style scoped>
.app-container { height: 100vh; }
.app-sidebar {
  background: #fff;
  border-right: 1px solid var(--border-color);
  transition: width 0.3s;
  overflow: hidden;
}
.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-bottom: 1px solid var(--border-color);
  padding: 0 12px;
}
.logo {
  font-size: 18px;
  font-weight: bold;
  color: var(--primary-color);
  white-space: nowrap;
}
.sidebar-menu { border-right: none; }
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid var(--border-color);
  padding: 0 24px;
  height: 60px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.user-dropdown {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-primary);
}
.app-main {
  background: var(--bg-color);
  overflow-y: auto;
}
</style>