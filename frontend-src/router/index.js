import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { title: '可视化大屏' },
  },
  {
    path: '/admin',
    component: () => import('@/views/admin/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/admin/overview',
      },
      {
        path: 'overview',
        name: 'AdminOverview',
        component: () => import('@/views/admin/OverviewPage.vue'),
        meta: { title: '管理概览' },
      },
      {
        path: 'plots',
        name: 'AdminPlots',
        component: () => import('@/views/admin/PlotsPage.vue'),
        meta: { title: '地块管理' },
      },
      {
        path: 'devices',
        name: 'AdminDevices',
        component: () => import('@/views/admin/DevicesPage.vue'),
        meta: { title: '设备管理' },
      },
      {
        path: 'sensors',
        name: 'AdminSensors',
        component: () => import('@/views/admin/SensorsPage.vue'),
        meta: { title: '传感器数据' },
      },
      {
        path: 'alerts',
        name: 'AdminAlerts',
        component: () => import('@/views/admin/AlertsPage.vue'),
        meta: { title: '告警管理' },
      },
      {
        path: 'statistics',
        name: 'AdminStatistics',
        component: () => import('@/views/admin/StatisticsPage.vue'),
        meta: { title: '数据统计' },
      },
      {
        path: 'irrigation',
        name: 'AdminIrrigation',
        component: () => import('@/views/admin/IrrigationPage.vue'),
        meta: { title: '灌溉管理' },
      },
      {
        path: 'fertilizer',
        name: 'AdminFertilizer',
        component: () => import('@/views/admin/FertilizerPage.vue'),
        meta: { title: '施肥管理' },
      },
      {
        path: 'weather',
        name: 'AdminWeather',
        component: () => import('@/views/admin/WeatherPage.vue'),
        meta: { title: '气象数据' },
      },
      {
        path: 'crops',
        name: 'AdminCrops',
        component: () => import('@/views/admin/CropsPage.vue'),
        meta: { title: '作物管理' },
      },
      {
        path: 'yield',
        name: 'AdminYield',
        component: () => import('@/views/admin/YieldPage.vue'),
        meta: { title: '产量分析' },
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/UsersPage.vue'),
        meta: { title: '用户管理' },
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: () => import('@/views/admin/SettingsPage.vue'),
        meta: { title: '系统设置' },
      },
      {
        path: 'logs',
        name: 'AdminLogs',
        component: () => import('@/views/admin/LogsPage.vue'),
        meta: { title: '操作日志' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 智慧农业管理平台` : '智慧农业管理平台'

  if (to.matched.some(record => record.meta.requiresAuth)) {
    const token = localStorage.getItem('accessToken')
    if (!token) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }

  next()
})

export default router
