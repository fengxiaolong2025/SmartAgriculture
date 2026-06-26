import { reactive } from 'vue'

// ========== 随机数工具 ==========
function rand(min, max) {
  return Math.round((Math.random() * (max - min) + min) * 10) / 10
}

function randInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

function fluctuate(val, range, min, max) {
  const change = (Math.random() - 0.5) * range
  return Math.round(Math.min(max, Math.max(min, val + change)) * 10) / 10
}

// ========== 传感器数据 ==========
export const sensors = reactive({
  airTemp: 26.5,
  airHumidity: 65,
  lightIntensity: 32000,
  co2: 420,
})

// ========== 24小时趋势数据 ==========
export const trendData = reactive({
  temperatures: [],
  humidities: [],
  timestamps: [],
})

// 初始化 24 个历史数据点
const now = new Date()
for (let i = 23; i >= 0; i--) {
  const t = new Date(now - i * 60 * 60 * 1000)
  trendData.timestamps.push(
    t.getHours().toString().padStart(2, '0') + ':' + t.getMinutes().toString().padStart(2, '0')
  )
  trendData.temperatures.push(rand(18, 32))
  trendData.humidities.push(rand(50, 90))
}

// ========== 地块数据 ==========
export const plots = reactive([
  { id: 'A1', name: '水稻试验田', temp: 27.2, humidity: 72, crop: '水稻', status: 'normal', irrigating: true, fan: true },
  { id: 'A2', name: '小麦育种区', temp: 25.8, humidity: 65, crop: '小麦', status: 'normal', irrigating: false, fan: false },
  { id: 'B1', name: '蔬菜大棚1号', temp: 30.1, humidity: 80, crop: '番茄', status: 'warning', irrigating: true, fan: true },
  { id: 'B2', name: '蔬菜大棚2号', temp: 28.5, humidity: 75, crop: '黄瓜', status: 'normal', irrigating: false, fan: true },
  { id: 'C1', name: '果树种植区', temp: 24.3, humidity: 58, crop: '苹果', status: 'normal', irrigating: true, fan: false },
  { id: 'C2', name: '花卉培育区', temp: 26.0, humidity: 68, crop: '玫瑰', status: 'normal', irrigating: false, fan: false },
  { id: 'D1', name: '中药材基地', temp: 23.5, humidity: 55, crop: '人参', status: 'normal', irrigating: false, fan: false },
  { id: 'D2', name: '菌菇培育房', temp: 22.0, humidity: 92, crop: '香菇', status: 'normal', irrigating: true, fan: true },
])

// ========== 预警列表 ==========
export const alerts = reactive([])

const alertContents = [
  { text: 'B1大棚温度超过阈值 (≥30℃)', level: 'danger' },
  { text: 'C1区域土壤湿度偏低 (<60%)', level: 'warning' },
  { text: 'A2区域光照强度不足', level: 'info' },
  { text: 'D2菌菇房CO₂浓度偏高', level: 'warning' },
  { text: '灌溉系统水压异常波动', level: 'danger' },
  { text: 'B2区域风机运行时间过长', level: 'info' },
  { text: '气象站预报未来2小时有强降雨', level: 'warning' },
  { text: 'C2花卉区土壤pH值偏离正常', level: 'info' },
  { text: 'A1区域虫害监测发现异常', level: 'danger' },
  { text: 'D1中药材区需要追肥提醒', level: 'info' },
  { text: '遮阳网电机温度偏高', level: 'warning' },
  { text: '灌溉水泵电量不足预警', level: 'danger' },
]

// 初始化预警
alertContents.forEach((item, i) => {
  const time = new Date(now - (alertContents.length - i) * randInt(1, 30) * 60000)
  alerts.push({
    id: Date.now() + i,
    time: time.getHours().toString().padStart(2, '0') + ':' + time.getMinutes().toString().padStart(2, '0') + ':' + time.getSeconds().toString().padStart(2, '0'),
    level: item.level,
    content: item.text,
    isNew: i === 0,
  })
})

// ========== 设备状态 ==========
export const devices = reactive({
  irrigationValve: true,
  fan: true,
  pestControl: false,
  shadeNet: false,
  autoMode: true,
})

// ========== 统计数据 ==========
export const statistics = reactive({
  irrigationVolume: 1520,
  fertilizerKg: 86,
  pestControlCount: 3,
  ventilationMin: 480,
  baseIrrigation: 1520,
  baseFertilizer: 86,
  basePestControl: 3,
  baseVentilation: 480,
})

// ========== 成熟度预测 ==========
export const maturityPredictions = reactive([
  { crop: '水稻', variety: '五优稻4号', daysLeft: 45, total: 140, color: '#00d4ff' },
  { crop: '番茄', variety: '金棚一号', daysLeft: 18, total: 90, color: '#ff3d4f' },
  { crop: '黄瓜', variety: '津优35号', daysLeft: 7, total: 60, color: '#ffab00' },
  { crop: '苹果', variety: '红富士', daysLeft: 85, total: 200, color: '#00e676' },
  { crop: '小麦', variety: '济麦22', daysLeft: 32, total: 230, color: '#ff9100' },
])

// ========== 历史产量 ==========
export const yieldHistory = reactive([
  { month: '1月', yield: 12.5, target: 13 },
  { month: '2月', yield: 11.8, target: 12.5 },
  { month: '3月', yield: 14.2, target: 14 },
  { month: '4月', yield: 15.6, target: 15 },
  { month: '5月', yield: 16.8, target: 16 },
  { month: '6月', yield: 18.2, target: 17 },
])

// ========== 天气数据 ==========
export const weather = reactive({
  temp: 28,
  humidity: 62,
  icon: '☀',
  description: '晴',
})

// ========== 设备在线 ==========
export const deviceOnline = reactive({
  online: 48,
  total: 50,
})

// ========== 模拟定时更新 ==========
let simulationTimer = null

export function startSimulation() {
  simulationTimer = setInterval(() => {
    // 传感器数据微调
    sensors.airTemp = fluctuate(sensors.airTemp, 1, 15, 40)
    sensors.airHumidity = fluctuate(sensors.airHumidity, 3, 30, 98)
    sensors.lightIntensity = fluctuate(sensors.lightIntensity, 2000, 0, 120000)
    sensors.co2 = fluctuate(sensors.co2, 30, 300, 800)

    // 趋势数据追加新点
    const now = new Date()
    const timeStr = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0')
    trendData.timestamps.push(timeStr)
    trendData.temperatures.push(sensors.airTemp)
    trendData.humidities.push(sensors.airHumidity)

    // 保持 24 个数据点
    if (trendData.timestamps.length > 24) {
      trendData.timestamps.shift()
      trendData.temperatures.shift()
      trendData.humidities.shift()
    }

    // 地块数据微调
    plots.forEach(p => {
      p.temp = fluctuate(p.temp, 0.5, 15, 40)
      p.humidity = fluctuate(p.humidity, 2, 30, 98)
    })

    // 统计数据微增
    statistics.irrigationVolume = Math.round(statistics.baseIrrigation + Math.random() * 10)
    statistics.fertilizerKg = Math.round(statistics.baseFertilizer + Math.random() * 2)
    statistics.ventilationMin = Math.round(statistics.baseVentilation + Math.random() * 5)

    // 设备在线率微调
    if (Math.random() < 0.1) {
      deviceOnline.online = Math.min(deviceOnline.total, deviceOnline.online + (Math.random() > 0.5 ? 1 : -1))
      deviceOnline.online = Math.max(45, deviceOnline.online)
    }

    // 天气微调
    weather.temp = fluctuate(weather.temp, 1, -5, 45)
    weather.humidity = fluctuate(weather.humidity, 5, 20, 100)
    const icons = ['☀', '⛅', '☁', '🌧']
    if (Math.random() < 0.05) {
      weather.icon = icons[randInt(0, 3)]
    }
  }, 3000) // 每3秒更新

  // 每秒更新时间（独立的）
  setInterval(() => {
    // 时间更新由 TopBar 组件自行处理
  }, 1000)

  // 随机新增预警
  setInterval(() => {
    if (Math.random() < 0.3) {
      const content = alertContents[randInt(0, alertContents.length - 1)]
      const now = new Date()
      // 标记旧预警为非新
      alerts.forEach(a => a.isNew = false)
      alerts.unshift({
        id: Date.now(),
        time: now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0') + ':' + now.getSeconds().toString().padStart(2, '0'),
        level: content.level,
        content: content.text + (Math.random() > 0.5 ? ' (二次告警)' : ''),
        isNew: true,
      })
      // 保持最多 20 条
      if (alerts.length > 20) {
        alerts.pop()
      }
    }
  }, 8000)
}

export function stopSimulation() {
  if (simulationTimer) {
    clearInterval(simulationTimer)
    simulationTimer = null
  }
}

// 返回完整的大屏数据快照（供 Pinia store 降级使用）
export function mockDashboardData() {
  return {
    sensors: {
      airTemp: sensors.airTemp,
      airHumidity: sensors.airHumidity,
      lightIntensity: sensors.lightIntensity,
      co2: sensors.co2,
    },
    trendData: {
      temperatures: [...trendData.temperatures],
      humidities: [...trendData.humidities],
      timestamps: [...trendData.timestamps],
    },
    plots: plots.map(p => ({ ...p })),
    alerts: alerts.map(a => ({ ...a })),
    devices: { ...devices },
    statistics: { ...statistics },
    maturityPredictions: maturityPredictions.map(m => ({ ...m })),
    yieldHistory: yieldHistory.map(y => ({ ...y })),
    weather: { ...weather },
    deviceOnline: { ...deviceOnline },
  }
}
