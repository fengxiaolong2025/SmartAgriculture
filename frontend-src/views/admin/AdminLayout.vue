<template>
  <el-container class="admin-container">
    <el-aside width="220px" class="admin-aside">
      <div class="aside-header">
        <div class="aside-logo">
          <span class="logo-icon-small"></span>
          <span class="aside-title">后台管理</span>
        </div>
      </div>
      <el-menu
        :default-active="activeMenu"
        :router="true"
        background-color="#0f2744"
        text-color="#8bb9e0"
        active-text-color="#00d4ff"
        class="admin-menu"
      >
        <el-menu-item index="/admin/overview">
          <el-icon><DataAnalysis /></el-icon>
          <span>管理概览</span>
        </el-menu-item>
        <el-menu-item index="/admin/plots">
          <el-icon><Grid /></el-icon>
          <span>地块管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/devices">
          <el-icon><Cpu /></el-icon>
          <span>设备管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/sensors">
          <el-icon><Odometer /></el-icon>
          <span>传感器数据</span>
        </el-menu-item>
        <el-menu-item index="/admin/alerts">
          <el-icon><Bell /></el-icon>
          <span>告警管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/statistics">
          <el-icon><TrendCharts /></el-icon>
          <span>数据统计</span>
        </el-menu-item>
        <el-menu-item index="/admin/irrigation">
          <el-icon><DishDot /></el-icon>
          <span>灌溉管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/fertilizer">
          <el-icon><Box /></el-icon>
          <span>施肥管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/weather">
          <el-icon><Sunny /></el-icon>
          <span>气象数据</span>
        </el-menu-item>
        <el-menu-item index="/admin/crops">
          <el-icon><Apple /></el-icon>
          <span>作物管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/yield">
          <el-icon><Histogram /></el-icon>
          <span>产量分析</span>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><UserFilled /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
        <el-menu-item index="/admin/logs">
          <el-icon><Document /></el-icon>
          <span>操作日志</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="admin-header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">大屏</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <span class="header-user">{{ authStore.user?.username || 'admin' }}</span>
          <el-button type="danger" text @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>

      <el-main class="admin-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta.title || '')

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-container {
  height: 100vh;
  background: var(--bg-primary);
}

.admin-aside {
  background: var(--bg-panel);
  border-right: 1px solid var(--border-color);
  overflow-y: auto;
}

.aside-header {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid var(--border-color);
}

.aside-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon-small {
  display: inline-block;
  width: 14px;
  height: 14px;
  background: var(--success);
  border-radius: 50% 0 50% 50%;
  transform: rotate(-45deg);
  box-shadow: 0 0 6px var(--success);
}

.aside-title {
  font-size: 16px;
  font-weight: bold;
  color: var(--accent);
  letter-spacing: 2px;
}

.admin-menu {
  border-right: none;
}

.admin-menu :deep(.el-menu-item) {
  font-size: 13px;
  height: 44px;
  line-height: 44px;
}

.admin-menu :deep(.el-menu-item.is-active) {
  background: rgba(0, 212, 255, 0.1) !important;
  border-right: 2px solid var(--accent);
}

.admin-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.header-left :deep(.el-breadcrumb__inner) {
  color: var(--text-secondary);
}

.header-left :deep(.el-breadcrumb__inner.is-link:hover) {
  color: var(--accent);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-user {
  color: var(--text-primary);
  font-size: 14px;
}

.admin-main {
  background: var(--bg-primary);
  padding: 20px;
  overflow-y: auto;
}
</style>
