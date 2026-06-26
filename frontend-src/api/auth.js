import apiClient from './index'

export function login(username, password) {
  return apiClient.post('/auth/login', { username, password })
}

export function refreshToken(token) {
  return apiClient.post('/auth/refresh', { refreshToken: token })
}

export function logout() {
  return apiClient.post('/auth/logout')
}

export function getMe() {
  return apiClient.get('/auth/me')
}
