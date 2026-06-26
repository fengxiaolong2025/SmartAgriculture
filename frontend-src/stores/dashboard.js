import { defineStore } from 'pinia'
import { ref, reactive, computed } from 'vue'
import * as dashboardApi from '@/api/dashboard'
import { mockDashboardData } from '@/mock/data.js'

export const useDashboardStore = defineStore('dashboard', () => {
  const loading = ref(false)
  const useMock = ref(true)

  // 传感器数据
  const sensors = reactive({
    airTemp: 26.5,
    airHumidity: 65,
    lightIntensity: 32000,
    co2: 420,
  })

  // 24小时趋势
  const trendData = reactive({
    temperatures: [],
    humidities: [],
    timestamps: [],
  })

  // 地块数据
  const plots = reactive([])

  // 预警列表
  const alerts = reactive([])

  // 设备状态
  const devices = reactive({
    irrigationValve: true,
    fan: true,
    pestControl: false,
    shadeNet: false,
    autoMode: true,
  })

  // 统计数据
  const statistics = reactive({
    irrigationVolume: 1520,
    fertilizerKg: 86,
    pestControlCount: 3,
    ventilationMin: 480,
    baseIrrigation: 1520,
    baseFertilizer: 86,
    basePestControl: 3,
    baseVentilation: 480,
  })

  // 成熟度预测
  const maturityPredictions = reactive([])

  // 历史产量
  const yieldHistory = reactive([])

  // 天气
  const weather = reactive({
    temp: 28,
    humidity: 62,
    icon: '☀',
    description: '晴',
  })

  // 设备在线
  const deviceOnline = reactive({
    online: 48,
    total: 50,
  })

  function applyMockData() {
    const mock = mockDashboardData()
    Object.assign(sensors, mock.sensors)
    trendData.temperatures.splice(0, trendData.temperatures.length, ...mock.trendData.temperatures)
    trendData.humidities.splice(0, trendData.humidities.length, ...mock.trendData.humidities)
    trendData.timestamps.splice(0, trendData.timestamps.length, ...mock.trendData.timestamps)
    plots.splice(0, plots.length, ...mock.plots)
    alerts.splice(0, alerts.length, ...mock.alerts)
    Object.assign(devices, mock.devices)
    Object.assign(statistics, mock.statistics)
    maturityPredictions.splice(0, maturityPredictions.length, ...mock.maturityPredictions)
    yieldHistory.splice(0, yieldHistory.length, ...mock.yieldHistory)
    Object.assign(weather, mock.weather)
    Object.assign(deviceOnline, mock.deviceOnline)
  }

  async function fetchAll() {
    loading.value = true
    try {
      const res = await dashboardApi.getOverview()
      // apiClient 响应拦截器返回 response.data，即 { code, message, data }
      // overview 接口的 data 包含 sensors, plotsStatus, recentAlerts 等
      const data = res.data || res
      if (data && data.sensors) {
        useMock.value = false
        Object.assign(sensors, data.sensors)

        // 趋势数据
        if (data.trend) {
          trendData.temperatures.splice(0, trendData.temperatures.length, ...(data.trend.temperatures || []))
          trendData.humidities.splice(0, trendData.humidities.length, ...(data.trend.humidities || []))
          trendData.timestamps.splice(0, trendData.timestamps.length, ...(data.trend.timestamps || []))
        }

        // 地块
        if (data.plotsStatus) plots.splice(0, plots.length, ...data.plotsStatus)

        // 预警
        if (data.recentAlerts) alerts.splice(0, alerts.length, ...data.recentAlerts)

        // 设备在线
        if (data.deviceOnline) Object.assign(deviceOnline, data.deviceOnline)

        // 今日统计
        if (data.todayStatistics) {
          Object.assign(statistics, data.todayStatistics)
          statistics.baseIrrigation = statistics.irrigationVolume
          statistics.baseFertilizer = statistics.fertilizerKg
          statistics.basePestControl = statistics.pestControlCount
          statistics.baseVentilation = statistics.ventilationMin
        }

        // 成熟度
        if (data.maturity) maturityPredictions.splice(0, maturityPredictions.length, ...data.maturity)

        // 历史产量
        if (data.yieldHistory) yieldHistory.splice(0, yieldHistory.length, ...data.yieldHistory)

        // 天气
        if (data.weather) Object.assign(weather, data.weather)
      } else {
        applyMockData()
      }
    } catch {
      applyMockData()
      useMock.value = true
    }

    // 并行获取其他数据（降级：子接口失败不影响主数据）
    try {
      const [trendRes, alertsRes, maturityRes, yieldRes, weatherRes, deviceRes] = await Promise.allSettled([
        dashboardApi.getTrend(),
        dashboardApi.getAlerts ? dashboardApi.getAlerts() : Promise.resolve(null),
        dashboardApi.getMaturity ? dashboardApi.getMaturity() : Promise.resolve(null),
        dashboardApi.getYieldHistory ? dashboardApi.getYieldHistory() : Promise.resolve(null),
        dashboardApi.getWeather ? dashboardApi.getWeather() : Promise.resolve(null),
        dashboardApi.getDeviceOnline ? dashboardApi.getDeviceOnline() : Promise.resolve(null),
      ])

      if (trendRes.status === 'fulfilled' && trendRes.value) {
        const d = trendRes.value.data || trendRes.value
        if (d.timestamps) {
          trendData.temperatures.splice(0, trendData.temperatures.length, ...(d.temperatures || []))
          trendData.humidities.splice(0, trendData.humidities.length, ...(d.humidities || []))
          trendData.timestamps.splice(0, trendData.timestamps.length, ...(d.timestamps || []))
        }
      }

      if (alertsRes.status === 'fulfilled' && alertsRes.value) {
        const a = alertsRes.value.data || alertsRes.value
        if (Array.isArray(a)) alerts.splice(0, alerts.length, ...a)
      }

      if (maturityRes.status === 'fulfilled' && maturityRes.value) {
        const m = maturityRes.value.data || maturityRes.value
        if (Array.isArray(m)) maturityPredictions.splice(0, maturityPredictions.length, ...m)
      }

      if (yieldRes.status === 'fulfilled' && yieldRes.value) {
        const y = yieldRes.value.data || yieldRes.value
        if (Array.isArray(y)) yieldHistory.splice(0, yieldHistory.length, ...y)
      }

      if (weatherRes.status === 'fulfilled' && weatherRes.value) {
        const w = weatherRes.value.data || weatherRes.value
        if (w) Object.assign(weather, w)
      }

      if (deviceRes.status === 'fulfilled' && deviceRes.value) {
        const dev = deviceRes.value.data || deviceRes.value
        if (dev) Object.assign(deviceOnline, dev)
      }
    } catch {
      // 降级：如果部分数据获取失败，使用已加载的 mock 数据
    }

    loading.value = false
  }

  async function fetchSensors() {
    try {
      const res = await dashboardApi.getSensors()
      if (res) {
        const data = res.data || res
        if (data && typeof data.airTemp !== 'undefined') {
          Object.assign(sensors, data)
        }
      }
    } catch {
      // 保持当前数据
    }
  }

  let pollTimer = null

  function startPolling(interval = 3000) {
    stopPolling()
    pollTimer = setInterval(() => {
      if (!useMock.value) {
        fetchSensors()
      }
    }, interval)
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  // Getters
  const alertCount = computed(() => alerts.length)
  const dangerAlerts = computed(() => alerts.filter(a => a.level === 'danger'))
  const onlineRate = computed(() =>
    deviceOnline.total > 0 ? (deviceOnline.online / deviceOnline.total * 100).toFixed(0) : 0
  )

  return {
    loading,
    useMock,
    sensors,
    trendData,
    plots,
    alerts,
    devices,
    statistics,
    maturityPredictions,
    yieldHistory,
    weather,
    deviceOnline,
    alertCount,
    dangerAlerts,
    onlineRate,
    fetchAll,
    fetchSensors,
    startPolling,
    stopPolling,
  }
})
