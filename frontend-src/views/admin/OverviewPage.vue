<template>
  <div class="overview-page">
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card-custom">
          <div class="stat-icon" style="background: rgba(0, 212, 255, 0.15)">
            <el-icon :size="28" color="#00d4ff"><Cpu /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">设备总数</div>
            <div class="stat-value">{{ deviceOnline.total }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card-custom">
          <div class="stat-icon" style="background: rgba(0, 230, 118, 0.15)">
            <el-icon :size="28" color="#00e676"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">在线设备</div>
            <div class="stat-value">{{ deviceOnline.online }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card-custom">
          <div class="stat-icon" style="background: rgba(255, 61, 79, 0.15)">
            <el-icon :size="28" color="#ff3d4f"><Bell /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">今日告警</div>
            <div class="stat-value">{{ alerts.length }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card-custom">
          <div class="stat-icon" style="background: rgba(255, 171, 0, 0.15)">
            <el-icon :size="28" color="#ffab00"><Grid /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">活跃地块</div>
            <div class="stat-value">{{ plots.length }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="14">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span class="card-title">告警趋势</span>
          </template>
          <div ref="alertChart" class="chart-box"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span class="card-title">最近操作日志</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="log in logs"
              :key="log.id"
              :timestamp="log.time"
              :color="log.type === 'warning' ? '#ffab00' : '#00d4ff'"
            >
              {{ log.content }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span class="card-title">设备在线率</span>
          </template>
          <div class="online-rate">
            <el-progress
              type="dashboard"
              :percentage="Number(onlineRate)"
              :color="progressColor"
            >
              <template #default="{ percentage }">
                <span class="percentage-value">{{ percentage }}%</span>
              </template>
            </el-progress>
            <div class="online-text">
              在线 {{ deviceOnline.online }} / {{ deviceOnline.total }}
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span class="card-title">当前天气</span>
          </template>
          <div class="weather-display">
            <span class="weather-icon-large">{{ weather.icon }}</span>
            <div class="weather-detail">
              <div class="weather-temp">{{ weather.temp }}°C</div>
              <div class="weather-humidity">湿度 {{ weather.humidity }}%</div>
              <div class="weather-desc">{{ weather.description }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import * as echarts from 'echarts'
import { useDashboardStore } from '@/stores/dashboard'
import { storeToRefs } from 'pinia'

const dashboard = useDashboardStore()
const { deviceOnline, alerts, plots, weather } = storeToRefs(dashboard)

const onlineRate = computed(() =>
  dashboard.deviceOnline.total > 0
    ? (dashboard.deviceOnline.online / dashboard.deviceOnline.total * 100).toFixed(0)
    : 0
)

const progressColor = computed(() => {
  const rate = Number(onlineRate.value)
  if (rate >= 95) return '#00e676'
  if (rate >= 80) return '#ffab00'
  return '#ff3d4f'
})

const alertChart = ref(null)
let chart = null

const logs = [
  { id: 1, time: '2026-06-26 10:30', content: '系统管理员登录后台', type: 'info' },
  { id: 2, time: '2026-06-26 10:15', content: 'B1大棚温度超过阈值 (≥30℃)', type: 'warning' },
  { id: 3, time: '2026-06-26 09:45', content: '灌溉系统自动开启 A1 区域', type: 'info' },
  { id: 4, time: '2026-06-26 09:20', content: '设备固件更新完成 - 48台设备', type: 'info' },
  { id: 5, time: '2026-06-26 08:00', content: '每日巡检报告生成完毕', type: 'info' },
]

onMounted(() => {
  if (!alertChart.value) return
  chart = echarts.init(alertChart.value)

  const hours = ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00']

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(13, 33, 55, 0.9)',
      borderColor: '#00d4ff',
      textStyle: { color: '#e0f0ff', fontSize: 11 },
    },
    grid: { top: 20, right: 20, bottom: 30, left: 40 },
    xAxis: {
      type: 'category',
      data: hours,
      axisLine: { lineStyle: { color: '#5a8ab5' } },
      axisLabel: { color: '#5a8ab5', fontSize: 10 },
    },
    yAxis: {
      type: 'value',
      name: '次',
      splitLine: { lineStyle: { color: 'rgba(90, 138, 181, 0.15)' } },
      axisLabel: { color: '#5a8ab5', fontSize: 10 },
    },
    series: [
      {
        name: '告警次数',
        type: 'line',
        data: [2, 1, 0, 1, 3, 5, 4, 6, 4, 3, 2, 1],
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { color: '#ff3d4f', width: 2 },
        itemStyle: { color: '#ff3d4f' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255, 61, 79, 0.3)' },
            { offset: 1, color: 'rgba(255, 61, 79, 0)' },
          ]),
        },
      },
    ],
  })

  const resizeHandler = () => chart?.resize()
  window.addEventListener('resize', resizeHandler)
  onUnmounted(() => {
    chart?.dispose()
    window.removeEventListener('resize', resizeHandler)
  })
})
</script>

<style scoped>
.overview-page {
  min-height: 100%;
}

.stats-row {
  margin-bottom: 0;
}

.stat-card-custom {
  background: var(--bg-panel) !important;
  border: 1px solid var(--border-color) !important;
}

.stat-card-custom :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-primary);
  font-family: var(--font-mono);
}

.chart-card {
  background: var(--bg-panel) !important;
  border: 1px solid var(--border-color) !important;
}

.chart-card :deep(.el-card__header) {
  border-bottom: 1px solid var(--border-color);
  padding: 12px 20px;
}

.card-title {
  font-size: 14px;
  font-weight: bold;
  color: var(--accent);
}

.chart-box {
  height: 260px;
}

.online-rate {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.percentage-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--text-primary);
}

.online-text {
  margin-top: 8px;
  font-size: 14px;
  color: var(--text-secondary);
}

.weather-display {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 20px;
}

.weather-icon-large {
  font-size: 56px;
}

.weather-detail {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.weather-temp {
  font-size: 32px;
  font-weight: bold;
  color: var(--accent);
}

.weather-humidity {
  font-size: 14px;
  color: var(--text-secondary);
}

.weather-desc {
  font-size: 14px;
  color: var(--text-muted);
}

/* 时间线样式覆盖 */
:deep(.el-timeline-item__wrapper) {
  padding-left: 20px;
}

:deep(.el-timeline-item__timestamp) {
  color: var(--text-muted);
  font-size: 12px;
}

:deep(.el-timeline-item__content) {
  color: var(--text-secondary);
  font-size: 13px;
}
</style>
