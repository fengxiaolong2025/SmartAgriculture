import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, refreshToken as refreshTokenApi, logout as logoutApi, getMe } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('accessToken') || '')
  const refreshTokenValue = ref(localStorage.getItem('refreshToken') || '')

  const isAuthenticated = computed(() => !!accessToken.value)

  function setTokens(access, refresh) {
    accessToken.value = access
    refreshTokenValue.value = refresh
    localStorage.setItem('accessToken', access)
    if (refresh) localStorage.setItem('refreshToken', refresh)
  }

  function clearTokens() {
    accessToken.value = ''
    refreshTokenValue.value = ''
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
  }

  async function login(username, password) {
    // apiClient 响应拦截器已将 response.data 解包
    // 后端返回 {code, message, data: {access_token, refresh_token, user}}
    // 拦截器返回 {code, message, data: {...}}
    const res = await loginApi(username, password)
    const payload = res.data || res
    setTokens(payload.access_token, payload.refresh_token)
    user.value = payload.user || { username }
    return true
  }

  async function doRefreshToken() {
    const res = await refreshTokenApi(refreshTokenValue.value)
    const payload = res.data || res
    setTokens(payload.access_token, payload.refresh_token)
    return true
  }

  async function logout() {
    try {
      await logoutApi()
    } catch {
      // ignore
    }
    user.value = null
    clearTokens()
  }

  async function fetchUser() {
    try {
      const res = await getMe()
      user.value = res
    } catch {
      if (import.meta.env.DEV) {
        user.value = { username: 'admin', role: 'admin' }
      }
    }
  }

  return {
    user,
    accessToken,
    refreshTokenValue,
    isAuthenticated,
    login,
    logout,
    doRefreshToken,
    fetchUser,
    setTokens,
    clearTokens,
  }
})
