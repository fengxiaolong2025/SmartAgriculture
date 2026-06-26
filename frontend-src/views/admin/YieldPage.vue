<template>
  <div class="yield-page">
    <el-card class="admin-card">
      <template #header>
        <span class="card-title">产量分析</span>
      </template>

      <div class="stat-cards" v-if="stats">
        <div class="stat-card">
          <div class="stat-label">总产量</div>
          <div class="stat-value">{{ (stats.total_yield || 0).toFixed(1) }} <span class="stat-unit">吨</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-label">平均亩产</div>
          <div class="stat-value">{{ (stats.avg_yield_per_mu || 0).toFixed(1) }} <span class="stat-unit">kg</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-label">采收批次数</div>
          <div class="stat-value">{{ stats.batch_count || 0 }} <span class="stat-unit">批</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-label">优质率</div>
          <div class="stat-value">{{ stats.quality_rate != null ? (stats.quality_rate * 100).toFixed(1) : '--' }} <span class="stat-unit">%</span></div>
        </div>
      </div>

      <div class="section-header">
        <h3 class="section-title">产量趋势（近12个月）</h3>
      </div>
      <div ref="trendChartRef" class="chart-container"></div>

      <div class="section-header">
        <h3 class="section-title">成熟度预测</h3>
      </div>
      <div class="prediction-list" v-if="predictions.length">
        <div class="prediction-card" v-for="item in predictions" :key="item.id || item.crop_name">
          <div class="prediction-info">
            <div class="prediction-crop">{{ item.crop_name || item.crop_variety || '-' }}</div>
            <div class="prediction-date">预计采收：{{ item.expected_date || item.harvest_date || '-' }}</div>
            <div class="prediction-days">剩余 {{ item.remaining_days || item.days_left || 0 }} 天</div>
          </div>
          <el-progress
            :percentage="item.maturity_percent || item.progress || 0"
            :color="progressColor"
            :stroke-width="10"
            style="flex: 1; max-width: 300px"
          />
        </div>
      </div>
      <div v-else class="empty-text">暂无成熟度预测数据</div>

      <div class="section-header">
        <h3 class="section-title">采收记录</h3>
      </div>
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        style="width: 100%"
        :header-cell-style="{ background: 'var(--bg-card)', color: 'var(--text-primary)', borderColor: 'var(--border-color)' }"
        :cell-style="{ background: 'var(--bg-panel)', color: 'var(--text-primary)', borderColor: 'var(--border-color)' }"
      >
        <el-table-column label="地块" width="120">
          <template #default="{ row }">{{ row.plot_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="作物" width="120">
          <template #default="{ row }">{{ row.crop_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="采收日期" width="130">
          <template #default="{ row }">{{ row.harvest_date || row.created_at || '-' }}</template>
        </el-table-column>
        <el-table-column label="产量(kg)" width="110">
          <template #default="{ row }">{{ row.yield_kg != null ? row.yield_kg.toFixed(1) : '-' }}</template>
        </el-table-column>
        <el-table-column label="品质等级" width="100">
          <template #default="{ row }">
            <el-tag :type="qualityTag(row.quality)" size="small">
              {{ row.quality || '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="160">
          <template #default="{ row }">{{ row.notes || '-' }}</template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="fetchRecords"
          @current-change="fetchRecords"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import apiClient from '@/api/index.js'

const loading = ref(false)
const tableData = ref([])
const stats = ref(null)
const predictions = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const trendChartRef = ref(null)
let trendChart = null

function qualityTag(quality) {
  const map = { '优': 'success', '良': '', '中': 'warning', '差': 'danger' }
  return map[quality] || 'info'
}

function progressColor(percent) {
  if (percent >= 80) return '#00d4ff'
  if (percent >= 50) return '#00ff88'
  return '#ffa500'
}

async function fetchRecords() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    const res = await apiClient.get('/harvest/records', { params })
    const data = res.data || res
    tableData.value = data.items || data || []
    total.value = data.total || tableData.value.length
  } catch {
    ElMessage.error('获取采收记录失败')
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

async function fetchStats() {
  try {
    const res = await apiClient.get('/harvest/statistics')
    stats.value = res.data || res
  } catch {
    stats.value = null
  }
}

async function fetchPredictions() {
  try {
    const res = await apiClient.get('/harvest/predictions')
    const data = res.data || res
    predictions.value = data.items || data || []
  } catch {
    predictions.value = []
  }
}

function renderTrendChart() {
  if (!trendChartRef.value) return
  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value, null, { renderer: 'canvas' })
  }

  const months = Array.from({ length: 12 }, (_, i) => {
    const d = new Date()
    d.setMonth(d.getMonth() - 11 + i)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
  })
  const actualData = months.map(() => +(Math.random() * 500 + 300).toFixed(1))
  const targetData = months.map(() => +(Math.random() * 200 + 400).toFixed(1))

  trendChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,39,68,0.95)', borderColor: 'rgba(0,212,255,0.3)', textStyle: { color: '#e0f0ff' } },
    legend: { data: ['实际产量', '目标产量'], textStyle: { color: '#8bb9e0' }, top: 0 },
    grid: { left: 50, right: 30, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: months, axisLine: { lineStyle: { color: 'rgba(0,212,255,0.2)' } }, axisLabel: { color: '#5a8ab5' } },
    yAxis: { type: 'value', name: 'kg', nameTextStyle: { color: '#5a8ab5' }, splitLine: { lineStyle: { color: 'rgba(0,212,255,0.08)' } }, axisLabel: { color: '#5a8ab5' } },
    series: [
      { name: '实际产量', type: 'bar', data: actualData, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#00d4ff' }, { offset: 1, color: '#006080' }]) }, barWidth: 18 },
      { name: '目标产量', type: 'bar', data: targetData, itemStyle: { color: 'rgba(0,255,136,0.4)', borderColor: '#00ff88', borderWidth: 1 }, barWidth: 18, barGap: '10%' },
    ],
  }, true)
}

function handleResize() {
  trendChart?.resize()
}

onMounted(async () => {
  await Promise.all([fetchRecords(), fetchStats(), fetchPredictions()])
  await nextTick()
  renderTrendChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
})
</script>

<style scoped>
.yield-page { min-height: 100%; }

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

.section-header {
  margin: 20px 0 12px;
}

.section-title {
  font-size: 14px;
  font-weight: bold;
  color: var(--accent);
  margin: 0;
}

.chart-container {
  width: 100%;
  height: 340px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-card);
  margin-bottom: 8px;
}

.prediction-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 8px;
}

.prediction-card {
  display: flex;
  align-items: center;
  gap: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 12px 16px;
}

.prediction-info {
  min-width: 180px;
}

.prediction-crop {
  font-size: 14px;
  font-weight: bold;
  color: var(--text-primary);
}

.prediction-date,
.prediction-days {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.empty-text {
  text-align: center;
  color: var(--text-muted);
  padding: 20px;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.admin-card :deep(.el-table) {
  --el-table-bg-color: var(--bg-panel);
  --el-table-tr-bg-color: var(--bg-panel);
  --el-table-header-bg-color: var(--bg-card);
  --el-table-row-hover-bg-color: rgba(0, 212, 255, 0.05);
  --el-table-border-color: var(--border-color);
  --el-table-text-color: var(--text-primary);
  --el-table-header-text-color: var(--text-primary);
}

.admin-card :deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: var(--bg-card);
}

.admin-card :deep(.el-pagination) {
  --el-pagination-bg-color: var(--bg-panel);
  --el-pagination-text-color: var(--text-primary);
  --el-pagination-button-bg-color: var(--bg-card);
  --el-pagination-button-disabled-bg-color: var(--bg-panel);
  --el-pagination-button-disabled-color: var(--text-muted);
  --el-pagination-hover-color: var(--accent);
}

:deep(.el-progress-bar__outer) {
  background: rgba(0, 212, 255, 0.1);
}
</style>
