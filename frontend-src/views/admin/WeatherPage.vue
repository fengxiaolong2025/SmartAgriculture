<template>
  <div class="weather-page">
    <el-card class="admin-card" v-loading="loading">
      <template #header>
        <span class="card-title">气象数据</span>
      </template>

      <div v-if="error" class="error-text">{{ error }}</div>

      <template v-if="currentWeather">
        <div class="weather-hero">
          <div class="weather-icon">{{ weatherIcon(currentWeather.condition) }}</div>
          <div class="weather-info">
            <div class="weather-temp">{{ currentWeather.temperature?.toFixed(1) || '--' }}°C</div>
            <div class="weather-desc">{{ currentWeather.description || currentWeather.condition || '--' }}</div>
            <div class="weather-details">
              <span>湿度 {{ currentWeather.humidity || '--' }}%</span>
              <span>风速 {{ currentWeather.wind_speed || '--' }} m/s</span>
              <span>风向 {{ currentWeather.wind_direction || '--' }}</span>
            </div>
          </div>
        </div>

        <h3 class="section-title">7天预报</h3>
        <div class="forecast-row">
          <div class="forecast-card" v-for="(day, idx) in forecast" :key="idx">
            <div class="forecast-day">{{ day.date || day.day || `第${idx + 1}天` }}</div>
            <div class="forecast-icon">{{ weatherIcon(day.condition) }}</div>
            <div class="forecast-temp">{{ day.temp_high || '--' }}° / {{ day.temp_low || '--' }}°</div>
            <div class="forecast-desc">{{ day.condition || day.description || '--' }}</div>
          </div>
        </div>

        <h3 class="section-title">24小时趋势</h3>
        <div ref="trendChartRef" class="chart-container"></div>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import apiClient from '@/api/index.js'

const loading = ref(false)
const error = ref('')
const currentWeather = ref(null)
const forecast = ref([])
const trendChartRef = ref(null)
let trendChart = null

const weatherIcons = {
  sunny: '☀️', clear: '☀️', cloudy: '⛅', overcast: '☁️',
  rain: '🌧️', light_rain: '🌦️', heavy_rain: '⛈️',
  snow: '🌨️', fog: '🌫️', windy: '💨', thunder: '⚡',
}

function weatherIcon(condition) {
  return weatherIcons[condition?.toLowerCase()] || '🌤️'
}

async function fetchWeather() {
  loading.value = true
  error.value = ''
  try {
    const res = await apiClient.get('/dashboard/weather')
    const data = res.data || res
    if (data) {
      currentWeather.value = {
        temperature: data.temperature ?? data.temp,
        humidity: data.humidity,
        wind_speed: data.wind_speed,
        wind_direction: data.wind_direction,
        condition: data.condition || data.weather,
        description: data.description,
      }
      forecast.value = data.forecast || data.daily || []
    }
  } catch {
    // 降级：使用模拟数据
    error.value = ''
    generateMockWeather()
  } finally {
    loading.value = false
    await nextTick()
    renderTrendChart()
  }
}

function generateMockWeather() {
  const conditions = ['sunny', 'cloudy', 'overcast', 'light_rain', 'clear']
  currentWeather.value = {
    temperature: 24 + Math.random() * 8,
    humidity: 50 + Math.random() * 30,
    wind_speed: 1 + Math.random() * 5,
    wind_direction: ['北风', '东北风', '东风', '南风', '西南风'][Math.floor(Math.random() * 5)],
    condition: conditions[Math.floor(Math.random() * conditions.length)],
    description: '模拟气象数据',
  }

  forecast.value = Array.from({ length: 7 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() + i)
    return {
      date: `${d.getMonth() + 1}/${d.getDate()}`,
      condition: conditions[Math.floor(Math.random() * conditions.length)],
      temp_high: (22 + Math.random() * 10).toFixed(1),
      temp_low: (12 + Math.random() * 10).toFixed(1),
    }
  })
}

function renderTrendChart() {
  if (!trendChartRef.value) return
  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value, null, { renderer: 'canvas' })
  }

  const hours = Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2, '0')}:00`)
  const tempData = hours.map(() => (18 + Math.random() * 14).toFixed(1))
  const humData = hours.map(() => (45 + Math.random() * 35).toFixed(0))

  trendChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,39,68,0.95)', borderColor: 'rgba(0,212,255,0.3)', textStyle: { color: '#e0f0ff' } },
    legend: { data: ['温度(°C)', '湿度(%)'], textStyle: { color: '#8bb9e0' }, top: 0 },
    grid: { left: 50, right: 60, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: hours, axisLine: { lineStyle: { color: 'rgba(0,212,255,0.2)' } }, axisLabel: { color: '#5a8ab5', fontSize: 11 } },
    yAxis: [
      { type: 'value', name: '°C', nameTextStyle: { color: '#5a8ab5' }, splitLine: { lineStyle: { color: 'rgba(0,212,255,0.08)' } }, axisLabel: { color: '#5a8ab5' } },
      { type: 'value', name: '%', nameTextStyle: { color: '#5a8ab5' }, splitLine: { show: false }, axisLabel: { color: '#5a8ab5' } },
    ],
    series: [
      {
        name: '温度(°C)', type: 'line', yAxisIndex: 0, data: tempData, smooth: true,
        lineStyle: { color: '#ff6b6b', width: 2 }, symbol: 'none',
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(255,107,107,0.25)' }, { offset: 1, color: 'rgba(255,107,107,0.02)' }]) },
      },
      {
        name: '湿度(%)', type: 'line', yAxisIndex: 1, data: humData, smooth: true,
        lineStyle: { color: '#00d4ff', width: 2 }, symbol: 'none',
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(0,212,255,0.25)' }, { offset: 1, color: 'rgba(0,212,255,0.02)' }]) },
      },
    ],
  }, true)
}

function handleResize() {
  trendChart?.resize()
}

onMounted(() => {
  fetchWeather()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
})
</script>

<style scoped>
.weather-page { min-height: 100%; }

.admin-card {
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
}

.admin-card :deep(.el-card__header) {
  border-bottom: 1px solid var(--border-color);
  padding: 14px 20px;
  background: linear-gradient(180deg, rgba(0,212,255,0.05) 0%, transparent 100%);
}

.card-title {
  font-size: 15px;
  font-weight: bold;
  color: var(--accent);
  letter-spacing: 1px;
}

.error-text {
  text-align: center;
  padding: 40px;
  color: var(--danger);
}

.weather-hero {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 24px;
  background: linear-gradient(135deg, rgba(0,212,255,0.08) 0%, rgba(0,212,255,0.02) 100%);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  margin-bottom: 24px;
}

.weather-icon {
  font-size: 56px;
}

.weather-info {
  flex: 1;
}

.weather-temp {
  font-size: 36px;
  font-weight: bold;
  color: var(--accent);
}

.weather-desc {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 4px 0 8px;
}

.weather-details {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: var(--text-muted);
}

.section-title {
  font-size: 14px;
  font-weight: bold;
  color: var(--accent);
  margin-bottom: 12px;
}

.forecast-row {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 8px;
  margin-bottom: 24px;
}

.forecast-card {
  flex: 0 0 130px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}

.forecast-day {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.forecast-icon {
  font-size: 28px;
  margin: 6px 0;
}

.forecast-temp {
  font-size: 14px;
  color: var(--accent);
  font-weight: bold;
}

.forecast-desc {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
}

.chart-container {
  width: 100%;
  height: 320px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-card);
}
</style>
