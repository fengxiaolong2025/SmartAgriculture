import apiClient from './index'

export function getOverview() {
  return apiClient.get('/dashboard/overview')
}

export function getSensors() {
  return apiClient.get('/dashboard/sensors')
}

export function getTrend() {
  return apiClient.get('/dashboard/trend')
}

export function getPlotsStatus() {
  return apiClient.get('/dashboard/plots-status')
}

export function getStatistics() {
  return apiClient.get('/dashboard/statistics')
}

export function getMaturity() {
  return apiClient.get('/dashboard/maturity')
}

export function getYieldHistory() {
  return apiClient.get('/dashboard/yield-history')
}

export function getWeather() {
  return apiClient.get('/dashboard/weather')
}

export function getDeviceOnline() {
  return apiClient.get('/dashboard/device-online')
}

export function postDeviceControl(deviceId, action) {
  return apiClient.post('/dashboard/devices/control', { deviceId, action })
}

export function getAlerts() {
  return apiClient.get('/dashboard/alerts')
}
