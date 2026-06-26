<template>
  <div class="irrigation-page">
    <!-- 灌溉状态卡片 -->
    <div class="status-cards">
      <el-card class="status-card" :class="{ active: irrigationStatus?.is_active }">
        <div class="status-header">
          <span class="status-dot" :class="irrigationStatus?.is_active ? 'online' : 'offline'" />
          <span class="status-title">当前灌溉状态</span>
        </div>
        <template v-if="irrigationStatus?.is_active">
          <div class="status-body">
            <div class="status-info">
              <span class="info-label">灌溉地块</span>
              <span class="info-value">{{ irrigationStatus.plot_name || `地块#${irrigationStatus.plot_id}` || '-' }}</span>
            </div>
            <div class="status-info">
              <span class="info-label">剩余时间</span>
              <span class="info-value highlight">{{ formatDuration(irrigationStatus.remaining_time) }}</span>
            </div>
            <div class="status-info">
              <span class="info-label">开始时间</span>
              <span class="info-value">{{ irrigationStatus.started_at || '-' }}</span>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="status-idle">当前无灌溉进行中</div>
        </template>
      </el-card>

      <!-- 统计卡片 -->
      <el-card class="stat-card">
        <div class="stat-header">今日灌溉统计</div>
        <div class="stat-grid">
          <div class="stat-box">
            <span class="stat-num">{{ irrigationStats?.total_water || 0 }}</span>
            <span class="stat-unit">L</span>
            <span class="stat-desc">总灌溉量</span>
          </div>
          <div class="stat-box">
            <span class="stat-num">{{ irrigationStats?.total_count || 0 }}</span>
            <span class="stat-unit">次</span>
            <span class="stat-desc">灌溉次数</span>
          </div>
          <div class="stat-box">
            <span class="stat-num">{{ irrigationStats?.total_duration || 0 }}</span>
            <span class="stat-unit">min</span>
            <span class="stat-desc">总时长</span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 手动控制区 -->
    <el-card class="admin-card">
      <template #header>
        <span class="card-title">手动灌溉控制</span>
      </template>
      <div class="control-panel">
        <el-select v-model="controlPlotId" placeholder="选择地块" style="width: 200px">
          <el-option
            v-for="plot in plots"
            :key="plot.id"
            :label="plot.name || `地块#${plot.id}`"
            :value="plot.id"
          />
        </el-select>
        <el-select v-model="controlAction" placeholder="操作" style="width: 140px">
          <el-option label="开始灌溉" value="start" />
          <el-option label="停止灌溉" value="stop" />
        </el-select>
        <el-input-number
          v-if="controlAction === 'start'"
          v-model="controlDuration"
          :min="1"
          :max="1440"
          :step="5"
          style="width: 160px"
        />
        <span v-if="controlAction === 'start'" style="color: var(--text-secondary); margin-left: -8px">分钟</span>
        <el-button
          type="primary"
          :loading="controlLoading"
          @click="executeControl"
        >
          执行
        </el-button>
      </div>
    </el-card>

    <!-- 灌溉记录 -->
    <el-card class="admin-card" style="margin-top: 16px">
      <template #header>
        <span class="card-title">灌溉记录</span>
      </template>
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        style="width: 100%"
        :header-cell-style="{ background: 'var(--bg-card)', color: 'var(--text-primary)', borderColor: 'var(--border-color)' }"
        :cell-style="{ background: 'var(--bg-panel)', color: 'var(--text-primary)', borderColor: 'var(--border-color)' }"
      >
        <el-table-column label="地块" width="130">
          <template #default="{ row }">
            {{ row.plot_name || `地块#${row.plot_id}` || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="trigger_type" label="触发类型" width="100">
          <template #default="{ row }">
            <el-tag :type="triggerTypeTag(row.trigger_type)" size="small">
              {{ triggerTypeLabel(row.trigger_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="started_at" label="开始时间" width="170" />
        <el-table-column prop="ended_at" label="结束时间" width="170" />
        <el-table-column label="时长" width="100">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column label="用水量" width="110">
          <template #default="{ row }">
            {{ row.water_volume != null ? row.water_volume + ' L' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="recordStatusTag(row.status)" size="small">
              {{ recordStatusLabel(row.status) }}
            </el-tag>
          </template>
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
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import apiClient from '@/api/index.js'

const loading = ref(false)
const tableData = ref([])
const plots = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const irrigationStatus = ref(null)
const irrigationStats = ref(null)

const controlPlotId = ref(null)
const controlAction = ref('start')
const controlDuration = ref(30)
const controlLoading = ref(false)

let statusTimer = null

function triggerTypeLabel(type) {
  const map = { auto: '自动', manual: '手动', scheduled: '定时' }
  return map[type] || type || '-'
}

function triggerTypeTag(type) {
  const map = { auto: 'success', manual: 'warning', scheduled: '' }
  return map[type] || 'info'
}

function recordStatusLabel(status) {
  const map = { running: '进行中', completed: '已完成', stopped: '已停止', failed: '失败' }
  return map[status] || status || '-'
}

function recordStatusTag(status) {
  const map = { running: 'success', completed: '', stopped: 'warning', failed: 'danger' }
  return map[status] || 'info'
}

function formatDuration(seconds) {
  if (seconds == null) return '-'
  const s = Number(seconds)
  if (s < 60) return `${s}秒`
  const m = Math.floor(s / 60)
  const remainS = s % 60
  if (m < 60) return remainS > 0 ? `${m}分${remainS}秒` : `${m}分钟`
  const h = Math.floor(m / 60)
  const remainM = m % 60
  return remainM > 0 ? `${h}小时${remainM}分` : `${h}小时`
}

async function fetchStatus() {
  try {
    const res = await apiClient.get('/irrigation/status')
    irrigationStatus.value = res.data || res
  } catch {
    irrigationStatus.value = null
  }
}

async function fetchStats() {
  try {
    const res = await apiClient.get('/irrigation/statistics')
    irrigationStats.value = res.data || res
  } catch {
    irrigationStats.value = null
  }
}

async function fetchRecords() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    const res = await apiClient.get('/irrigation/records', { params })
    const data = res.data || res
    tableData.value = data.items || data || []
    total.value = data.total || tableData.value.length
  } catch {
    ElMessage.error('获取灌溉记录失败')
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

async function fetchPlots() {
  try {
    const res = await apiClient.get('/plots', { params: { page_size: 200 } })
    const data = res.data || res
    plots.value = data.items || data || []
  } catch {
    plots.value = []
  }
}

async function executeControl() {
  if (!controlPlotId.value) {
    ElMessage.warning('请选择地块')
    return
  }
  if (!controlAction.value) {
    ElMessage.warning('请选择操作')
    return
  }
  controlLoading.value = true
  try {
    const payload = {
      plot_id: controlPlotId.value,
      action: controlAction.value,
    }
    if (controlAction.value === 'start') {
      payload.duration = controlDuration.value * 60
    }
    await apiClient.post('/irrigation/control', payload)
    ElMessage.success(controlAction.value === 'start' ? '灌溉已开始' : '灌溉已停止')
    fetchStatus()
    fetchStats()
    fetchRecords()
  } catch {
    ElMessage.error('控制指令发送失败')
  } finally {
    controlLoading.value = false
  }
}

onMounted(() => {
  fetchStatus()
  fetchStats()
  fetchRecords()
  fetchPlots()
  statusTimer = setInterval(fetchStatus, 10000)
})

onUnmounted(() => {
  if (statusTimer) clearInterval(statusTimer)
})
</script>

<style scoped>
.irrigation-page { min-height: 100%; }

.status-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.status-card {
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
}

.status-card.active {
  border-color: var(--success);
  box-shadow: 0 0 12px rgba(0, 230, 118, 0.15);
}

.status-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-dot.online {
  background: var(--success);
  box-shadow: 0 0 6px var(--success);
  animation: pulse-glow 2s ease-in-out infinite;
}

.status-dot.offline {
  background: var(--text-muted);
}

.status-title {
  font-size: 14px;
  font-weight: bold;
  color: var(--text-primary);
}

.status-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  color: var(--text-muted);
  font-size: 13px;
}

.info-value {
  color: var(--text-primary);
  font-size: 14px;
  font-weight: bold;
}

.info-value.highlight {
  color: var(--accent);
  font-family: var(--font-mono);
}

.status-idle {
  text-align: center;
  color: var(--text-muted);
  padding: 16px 0;
  font-size: 14px;
}

.stat-card {
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
}

.stat-header {
  font-size: 14px;
  font-weight: bold;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.stat-grid {
  display: flex;
  gap: 16px;
}

.stat-box {
  flex: 1;
  text-align: center;
  padding: 12px 8px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.stat-num {
  font-size: 24px;
  font-weight: bold;
  font-family: var(--font-mono);
  color: var(--accent);
}

.stat-unit {
  font-size: 12px;
  color: var(--text-muted);
  margin-left: 2px;
}

.stat-desc {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
}

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

.control-panel {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* Element Plus 深色主题覆盖 */
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

:deep(.el-input__wrapper),
:deep(.el-select .el-input__wrapper),
:deep(.el-input-number .el-input__wrapper) {
  background: var(--bg-card);
  border-color: var(--border-color);
  box-shadow: none;
}

:deep(.el-input__wrapper:hover),
:deep(.el-select .el-input__wrapper:hover),
:deep(.el-input-number .el-input__wrapper:hover) {
  border-color: var(--accent);
}

:deep(.el-input__inner),
:deep(.el-select .el-input__inner),
:deep(.el-input-number .el-input__inner) {
  color: var(--text-primary);
}

:deep(.el-input-number__decrease),
:deep(.el-input-number__increase) {
  background: var(--bg-card);
  color: var(--text-primary);
  border-color: var(--border-color);
}

:deep(.el-input-number__decrease:hover),
:deep(.el-input-number__increase:hover) {
  color: var(--accent);
}

:deep(.el-card__body) {
  color: var(--text-primary);
}
</style>
