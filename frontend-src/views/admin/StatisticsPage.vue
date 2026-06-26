<template>
  <div class="statistics-page">
    <el-card class="admin-card">
      <template #header>
        <span class="card-title">数据统计</span>
      </template>

      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <el-tab-pane label="日报" name="daily" />
        <el-tab-pane label="周报" name="weekly" />
        <el-tab-pane label="月报" name="monthly" />
      </el-tabs>

      <!-- 日报 -->
      <template v-if="activeTab === 'daily'">
        <div class="date-row">
          <el-date-picker v-model="dailyDate" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" @change="fetchDaily" />
        </div>
        <div class="stat-cards" v-if="dailyData">
          <div class="stat-card">
            <div class="stat-label">灌溉量</div>
            <div class="stat-value">{{ dailyData.irrigation_volume || 0 }} <span class="stat-unit">m³</span></div>
          </div>
          <div class="stat-card">
            <div class="stat-label">施肥量</div>
            <div class="stat-value">{{ dailyData.fertilizer_amount || 0 }} <span class="stat-unit">kg</span></div>
          </div>
          <div class="stat-card">
            <div class="stat-label">除害次数</div>
            <div class="stat-value">{{ dailyData.pest_control_count || 0 }} <span class="stat-unit">次</span></div>
          </div>
          <div class="stat-card">
            <div class="stat-label">通风时长</div>
            <div class="stat-value">{{ dailyData.ventilation_hours || 0 }} <span class="stat-unit">h</span></div>
          </div>
          <div class="stat-card">
            <div class="stat-label">采收量</div>
            <div class="stat-value">{{ dailyData.harvest_amount || 0 }} <span class="stat-unit">kg</span></div>
          </div>
        </div>
        <div ref="dailyChartRef" class="chart-container" v-if="dailyData"></div>
      </template>

      <!-- 周报 -->
      <template v-if="activeTab === 'weekly'">
        <div class="date-row">
          <el-date-picker v-model="weeklyDate" type="week" placeholder="选择周" format="YYYY 第 ww 周" value-format="YYYY-MM-DD" @change="fetchWeekly" />
        </div>
        <div class="stat-cards" v-if="weeklyData">
          <div class="stat-card">
            <div class="stat-label">周灌溉量</div>
            <div class="stat-value">{{ weeklyData.total_irrigation || 0 }} <span class="stat-unit">m³</span></div>
          </div>
          <div class="stat-card">
            <div class="stat-label">周施肥量</div>
            <div class="stat-value">{{ weeklyData.total_fertilizer || 0 }} <span class="stat-unit">kg</span></div>
          </div>
          <div class="stat-card">
            <div class="stat-label">周采收量</div>
            <div class="stat-value">{{ weeklyData.total_harvest || 0 }} <span class="stat-unit">kg</span></div>
          </div>
          <div class="stat-card">
            <div class="stat-label">日均温度</div>
            <div class="stat-value">{{ weeklyData.avg_temperature?.toFixed(1) || '--' }} <span class="stat-unit">°C</span></div>
          </div>
        </div>
        <div ref="weeklyChartRef" class="chart-container" v-if="weeklyData"></div>
      </template>

      <!-- 月报 -->
      <template v-if="activeTab === 'monthly'">
        <div class="date-row">
          <el-date-picker v-model="monthlyDate" type="month" placeholder="选择月份" value-format="YYYY-MM" @change="fetchMonthly" />
        </div>
        <div class="stat-cards" v-if="monthlyData">
          <div class="stat-card">
            <div class="stat-label">月灌溉量</div>
            <div class="stat-value">{{ monthlyData.total_irrigation || 0 }} <span class="stat-unit">m³</span></div>
          </div>
          <div class="stat-card">
            <div class="stat-label">月施肥量</div>
            <div class="stat-value">{{ monthlyData.total_fertilizer || 0 }} <span class="stat-unit">kg</span></div>
          </div>
          <div class="stat-card">
            <div class="stat-label">月采收量</div>
            <div class="stat-value">{{ monthlyData.total_harvest || 0 }} <span class="stat-unit">kg</span></div>
          </div>
          <div class="stat-card">
            <div class="stat-label">日均温度</div>
            <div class="stat-value">{{ monthlyData.avg_temperature?.toFixed(1) || '--' }} <span class="stat-unit">°C</span></div>
          </div>
        </div>
        <div ref="monthlyChartRef" class="chart-container" v-if="monthlyData"></div>
      </template>

      <div v-if="loading" style="text-align:center;padding:60px 0;color:var(--text-muted)">加载中...</div>
      <div v-if="error" style="text-align:center;padding:60px 0;color:var(--danger)">{{ error }}</div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import apiClient from '@/api/index.js'

const activeTab = ref('daily')
const loading = ref(false)
const error = ref('')

const dailyDate = ref('')
const weeklyDate = ref('')
const monthlyDate = ref('')
const dailyData = ref(null)
const weeklyData = ref(null)
const monthlyData = ref(null)

const dailyChartRef = ref(null)
const weeklyChartRef = ref(null)
const monthlyChartRef = ref(null)

let dailyChart = null
let weeklyChart = null
let monthlyChart = null

function todayStr() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

async function fetchDaily() {
  loading.value = true
  error.value = ''
  try {
    const params = { date: dailyDate.value || todayStr() }
    const res = await apiClient.get('/statistics/daily', { params })
    dailyData.value = res.data || res
    await nextTick()
    renderDailyChart()
  } catch {
    error.value = '获取日报数据失败'
    dailyData.value = null
  } finally {
    loading.value = false
  }
}

async function fetchWeekly() {
  loading.value = true
  error.value = ''
  try {
    const params = { date: weeklyDate.value || todayStr() }
    const res = await apiClient.get('/statistics/weekly', { params })
    weeklyData.value = res.data || res
    await nextTick()
    renderWeeklyChart()
  } catch {
    error.value = '获取周报数据失败'
    weeklyData.value = null
  } finally {
    loading.value = false
  }
}

async function fetchMonthly() {
  loading.value = true
  error.value = ''
  try {
    const params = { month: monthlyDate.value || todayStr().slice(0, 7) }
    const res = await apiClient.get('/statistics/monthly', { params })
    monthlyData.value = res.data || res
    await nextTick()
    renderMonthlyChart()
  } catch {
    error.value = '获取月报数据失败'
    monthlyData.value = null
  } finally {
    loading.value = false
  }
}

function renderDailyChart() {
  if (!dailyChartRef.value || !dailyData.value) return
  if (!dailyChart) {
    dailyChart = echarts.init(dailyChartRef.value, null, { renderer: 'canvas' })
  }
  const cats = ['灌溉量', '施肥量', '除害次数', '通风时长', '采收量']
  const vals = [
    dailyData.value.irrigation_volume || 0,
    dailyData.value.fertilizer_amount || 0,
    dailyData.value.pest_control_count || 0,
    dailyData.value.ventilation_hours || 0,
    dailyData.value.harvest_amount || 0,
  ]
  dailyChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,39,68,0.95)', borderColor: 'rgba(0,212,255,0.3)', textStyle: { color: '#e0f0ff' } },
    grid: { left: 50, right: 30, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: cats, axisLine: { lineStyle: { color: 'rgba(0,212,255,0.2)' } }, axisLabel: { color: '#5a8ab5' } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(0,212,255,0.08)' } }, axisLabel: { color: '#5a8ab5' } },
    series: [{
      type: 'bar', data: vals,
      itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#00d4ff' }, { offset: 1, color: '#006080' }]) },
      barWidth: 36,
    }],
  }, true)
}

function renderWeeklyChart() {
  if (!weeklyChartRef.value || !weeklyData.value) return
  if (!weeklyChart) {
    weeklyChart = echarts.init(weeklyChartRef.value, null, { renderer: 'canvas' })
  }
  const days = weeklyData.value.daily_breakdown || []
  const labels = days.map((_, i) => `第${i + 1}天`)
  const irrVals = days.map(d => d.irrigation || 0)
  const fertVals = days.map(d => d.fertilizer || 0)
  weeklyChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,39,68,0.95)', borderColor: 'rgba(0,212,255,0.3)', textStyle: { color: '#e0f0ff' } },
    legend: { data: ['灌溉量', '施肥量'], textStyle: { color: '#8bb9e0' }, top: 0 },
    grid: { left: 50, right: 30, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: labels, axisLine: { lineStyle: { color: 'rgba(0,212,255,0.2)' } }, axisLabel: { color: '#5a8ab5' } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(0,212,255,0.08)' } }, axisLabel: { color: '#5a8ab5' } },
    series: [
      { name: '灌溉量', type: 'line', data: irrVals, smooth: true, lineStyle: { color: '#00d4ff' }, symbol: 'circle', symbolSize: 6 },
      { name: '施肥量', type: 'line', data: fertVals, smooth: true, lineStyle: { color: '#00ff88' }, symbol: 'circle', symbolSize: 6 },
    ],
  }, true)
}

function renderMonthlyChart() {
  if (!monthlyChartRef.value || !monthlyData.value) return
  if (!monthlyChart) {
    monthlyChart = echarts.init(monthlyChartRef.value, null, { renderer: 'canvas' })
  }
  const months = monthlyData.value.comparison || []
  const labels = months.map(m => m.month || m.label || '')
  const currentVals = months.map(m => m.value || 0)
  const prevVals = months.map(m => m.prev_value || 0)
  monthlyChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,39,68,0.95)', borderColor: 'rgba(0,212,255,0.3)', textStyle: { color: '#e0f0ff' } },
    legend: { data: ['本月', '上月'], textStyle: { color: '#8bb9e0' }, top: 0 },
    grid: { left: 50, right: 30, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: labels, axisLine: { lineStyle: { color: 'rgba(0,212,255,0.2)' } }, axisLabel: { color: '#5a8ab5' } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(0,212,255,0.08)' } }, axisLabel: { color: '#5a8ab5' } },
    series: [
      { name: '本月', type: 'bar', data: currentVals, itemStyle: { color: '#00d4ff' }, barWidth: 20, barGap: '30%' },
      { name: '上月', type: 'bar', data: prevVals, itemStyle: { color: '#00ff88' }, barWidth: 20 },
    ],
  }, true)
}

function onTabChange() {
  error.value = ''
  if (activeTab.value === 'daily') { fetchDaily() }
  else if (activeTab.value === 'weekly') { fetchWeekly() }
  else if (activeTab.value === 'monthly') { fetchMonthly() }
}

function handleResize() {
  dailyChart?.resize()
  weeklyChart?.resize()
  monthlyChart?.resize()
}

onMounted(() => {
  dailyDate.value = todayStr()
  fetchDaily()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  dailyChart?.dispose()
  weeklyChart?.dispose()
  monthlyChart?.dispose()
})
</script>

<style scoped>
.statistics-page { min-height: 100%; }

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

.date-row {
  margin-bottom: 16px;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 16px;
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--accent);
}

.stat-unit {
  font-size: 12px;
  color: var(--text-secondary);
}

.chart-container {
  width: 100%;
  height: 380px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-card);
}

:deep(.el-tabs__header) {
  margin-bottom: 16px;
}

:deep(.el-tabs__nav-wrap::after) {
  background-color: var(--border-color);
  height: 1px;
}

:deep(.el-tabs__item) {
  color: var(--text-secondary);
}

:deep(.el-tabs__item.is-active) {
  color: var(--accent);
}

:deep(.el-tabs__active-bar) {
  background-color: var(--accent);
}

:deep(.el-input__wrapper),
:deep(.el-select .el-input__wrapper) {
  background: var(--bg-card);
  border-color: var(--border-color);
  box-shadow: none;
}

:deep(.el-input__inner),
:deep(.el-select .el-input__inner) {
  color: var(--text-primary);
}
</style>
