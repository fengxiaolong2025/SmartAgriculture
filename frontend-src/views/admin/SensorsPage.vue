<template>
  <div class="sensors-page">
    <el-card class="admin-card">
      <template #header>
        <span class="card-title">传感器数据</span>
      </template>

      <div class="toolbar">
        <el-select v-model="selectedDevice" placeholder="选择设备" clearable style="width: 200px" @change="onDeviceChange">
          <el-option
            v-for="d in devices"
            :key="d.id"
            :label="`${d.name || d.device_code} (${d.sub_type || d.device_type})`"
            :value="d.id"
          />
        </el-select>
        <el-select v-model="selectedMetric" placeholder="选择指标" style="width: 160px" @change="fetchHistory">
          <el-option label="温度" value="temperature" />
          <el-option label="湿度" value="humidity" />
          <el-option label="光照" value="light" />
          <el-option label="CO₂" value="co2" />
          <el-option label="土壤湿度" value="soil_moisture" />
          <el-option label="土壤pH" value="soil_ph" />
          <el-option label="土壤EC" value="soil_ec" />
          <el-option label="风速" value="wind_speed" />
          <el-option label="雨量" value="rainfall" />
        </el-select>
        <el-radio-group v-model="timeRange" @change="fetchHistory">
          <el-radio-button value="today">今天</el-radio-button>
          <el-radio-button value="7d">近7天</el-radio-button>
          <el-radio-button value="30d">近30天</el-radio-button>
          <el-radio-button value="custom">自定义</el-radio-button>
        </el-radio-group>
        <template v-if="timeRange === 'custom'">
          <el-date-picker
            v-model="customRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始"
            end-placeholder="结束"
            value-format="YYYY-MM-DD HH:mm:ss"
            @change="fetchHistory"
          />
        </template>
      </div>

      <div ref="chartRef" class="chart-container" v-loading="chartLoading"></div>

      <div class="realtime-section">
        <h3 class="section-title">实时数据</h3>
        <div class="realtime-grid">
          <div class="realtime-card" v-for="item in realtimeData" :key="item.metric">
            <div class="realtime-label">{{ metricLabel(item.metric) }}</div>
            <div class="realtime-value">
              {{ item.value != null ? item.value.toFixed(item.metric === 'soil_ph' ? 1 : 1) : '--' }}
              <span class="realtime-unit">{{ metricUnit(item.metric) }}</span>
            </div>
            <div class="realtime-time">{{ item.updated_at || '--' }}</div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import apiClient from '@/api/index.js'

const devices = ref([])
const selectedDevice = ref(null)
const selectedMetric = ref('temperature')
const timeRange = ref('today')
const customRange = ref([])
const chartRef = ref(null)
const chartLoading = ref(false)
const realtimeData = ref([])

let chartInstance = null

const metricLabels = {
  temperature: '温度', humidity: '湿度', light: '光照',
  co2: 'CO₂', soil_moisture: '土壤湿度', soil_ph: '土壤pH',
  soil_ec: '土壤EC', wind_speed: '风速', rainfall: '雨量',
}

const metricUnits = {
  temperature: '°C', humidity: '%', light: 'lux',
  co2: 'ppm', soil_moisture: '%', soil_ph: 'pH',
  soil_ec: 'mS/cm', wind_speed: 'm/s', rainfall: 'mm',
}

function metricLabel(m) { return metricLabels[m] || m }
function metricUnit(m) { return metricUnits[m] || '' }

function getTimeRange() {
  const now = new Date()
  let start
  switch (timeRange.value) {
    case 'today':
      start = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      break
    case '7d':
      start = new Date(now.getTime() - 7 * 24 * 3600 * 1000)
      break
    case '30d':
      start = new Date(now.getTime() - 30 * 24 * 3600 * 1000)
      break
    case 'custom':
      if (customRange.value && customRange.value.length === 2) {
        return { start: customRange.value[0], end: customRange.value[1] }
      }
      start = new Date(now.getTime() - 7 * 24 * 3600 * 1000)
      break
    default:
      start = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  }
  return { start: formatDateTime(start), end: formatDateTime(now) }
}

function formatDateTime(d) {
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

async function fetchDevices() {
  try {
    const res = await apiClient.get('/devices', { params: { device_type: 'sensor', page_size: 200 } })
    const data = res.data || res
    devices.value = data.items || data || []
  } catch {
    devices.value = []
  }
}

async function fetchHistory() {
  if (!selectedDevice.value) return
  chartLoading.value = true
  try {
    const { start, end } = getTimeRange()
    const params = { device_id: selectedDevice.value, metric: selectedMetric.value, start, end, limit: 500 }
    const res = await apiClient.get('/sensor-data/history', { params })
    const data = res.data || res
    const items = data.items || data || []
    renderChart(items)
  } catch {
    ElMessage.error('获取历史数据失败')
    renderChart([])
  } finally {
    chartLoading.value = false
  }
}

async function fetchRealtime() {
  try {
    const res = await apiClient.get('/sensor-data/realtime')
    const data = res.data || res
    const items = data.items || data || []
    const metrics = ['temperature', 'humidity', 'light', 'co2', 'soil_moisture', 'soil_ph', 'soil_ec', 'wind_speed', 'rainfall']
    realtimeData.value = metrics.map(m => {
      const found = items.find(i => i.metric === m)
      return { metric: m, value: found?.value, updated_at: found?.updated_at || found?.timestamp }
    })
  } catch {
    realtimeData.value = []
  }
}

function onDeviceChange() {
  fetchHistory()
}

function renderChart(items) {
  if (!chartRef.value) return
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value, null, { renderer: 'canvas' })
  }
  const times = items.map(i => i.timestamp || i.created_at || '')
  const values = items.map(i => i.value ?? null)

  chartInstance.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,39,68,0.95)',
      borderColor: 'rgba(0,212,255,0.3)',
      textStyle: { color: '#e0f0ff', fontSize: 12 },
    },
    grid: { left: 60, right: 30, top: 30, bottom: 40 },
    xAxis: {
      type: 'category',
      data: times,
      axisLine: { lineStyle: { color: 'rgba(0,212,255,0.2)' } },
      axisTick: { show: false },
      axisLabel: { color: '#5a8ab5', fontSize: 11, rotate: 30 },
    },
    yAxis: {
      type: 'value',
      name: metricUnit(selectedMetric.value),
      nameTextStyle: { color: '#5a8ab5' },
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(0,212,255,0.08)' } },
      axisLabel: { color: '#5a8ab5' },
    },
    series: [{
      type: 'line',
      data: values,
      smooth: true,
      symbol: 'none',
      lineStyle: { color: '#00d4ff', width: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0,212,255,0.3)' },
          { offset: 1, color: 'rgba(0,212,255,0.02)' },
        ]),
      },
    }],
  }, true)
}

function handleResize() {
  chartInstance?.resize()
}

onMounted(async () => {
  await fetchDevices()
  fetchRealtime()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>

<style scoped>
.sensors-page { min-height: 100%; }

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

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.chart-container {
  width: 100%;
  height: 400px;
  margin-top: 20px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-card);
}

.realtime-section { margin-top: 24px; }

.section-title {
  font-size: 14px;
  font-weight: bold;
  color: var(--accent);
  margin-bottom: 12px;
}

.realtime-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
}

.realtime-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 14px;
  text-align: center;
}

.realtime-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.realtime-value {
  font-size: 22px;
  font-weight: bold;
  color: var(--accent);
}

.realtime-unit {
  font-size: 12px;
  color: var(--text-secondary);
  margin-left: 2px;
}

.realtime-time {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
}

:deep(.el-select .el-input__wrapper),
:deep(.el-input__wrapper) {
  background: var(--bg-card);
  border-color: var(--border-color);
  box-shadow: none;
}

:deep(.el-select .el-input__wrapper:hover),
:deep(.el-input__wrapper:hover) {
  border-color: var(--accent);
}

:deep(.el-input__inner),
:deep(.el-select .el-input__inner) {
  color: var(--text-primary);
}

:deep(.el-radio-group .el-radio-button__inner) {
  background: var(--bg-card);
  border-color: var(--border-color);
  color: var(--text-secondary);
}

:deep(.el-radio-group .el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: rgba(0,212,255,0.15);
  border-color: var(--accent);
  color: var(--accent);
  box-shadow: none;
}
</style>
