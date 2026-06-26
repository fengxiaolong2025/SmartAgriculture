<template>
  <div class="alerts-page">
    <el-card class="admin-card">
      <template #header>
        <span class="card-title">告警管理</span>
      </template>

      <!-- 筛选区 -->
      <div class="toolbar">
        <el-select v-model="filterLevel" placeholder="告警级别" clearable style="width: 140px" @change="fetchAlerts">
          <el-option label="严重" value="critical" />
          <el-option label="重要" value="major" />
          <el-option label="次要" value="minor" />
          <el-option label="信息" value="info" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="告警状态" clearable style="width: 150px" @change="fetchAlerts">
          <el-option label="已触发" value="triggered" />
          <el-option label="已确认" value="acknowledged" />
          <el-option label="已处理" value="handled" />
          <el-option label="已关闭" value="closed" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 280px"
          @change="fetchAlerts"
        />
        <el-button type="primary" @click="fetchAlerts">
          <el-icon><Search /></el-icon> 查询
        </el-button>
      </div>

      <!-- 告警统计 -->
      <div class="stats-row" v-if="stats">
        <div class="stat-item">
          <span class="stat-value critical">{{ stats.critical || 0 }}</span>
          <span class="stat-label">严重</span>
        </div>
        <div class="stat-item">
          <span class="stat-value major">{{ stats.major || 0 }}</span>
          <span class="stat-label">重要</span>
        </div>
        <div class="stat-item">
          <span class="stat-value minor">{{ stats.minor || 0 }}</span>
          <span class="stat-label">次要</span>
        </div>
        <div class="stat-item">
          <span class="stat-value info">{{ stats.info || 0 }}</span>
          <span class="stat-label">信息</span>
        </div>
      </div>

      <!-- 表格 -->
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        style="width: 100%; margin-top: 16px"
        :header-cell-style="{ background: 'var(--bg-card)', color: 'var(--text-primary)', borderColor: 'var(--border-color)' }"
        :cell-style="{ background: 'var(--bg-panel)', color: 'var(--text-primary)', borderColor: 'var(--border-color)' }"
        @expand-change="handleExpand"
        row-key="id"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expand-content">
              <el-descriptions :column="2" border size="small">
                <el-descriptions-item label="告警描述">
                  {{ row.description || row.content || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="触发设备">
                  {{ row.device_name || row.device_code || row.device_id || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="触发值">
                  {{ row.trigger_value ?? '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="阈值">
                  {{ row.threshold ?? '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="确认人">
                  {{ row.acknowledged_by || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="确认时间">
                  {{ row.acknowledged_at || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="处理人">
                  {{ row.handled_by || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="处理时间">
                  {{ row.handled_at || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="处理备注" :span="2">
                  {{ row.handle_remark || '-' }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="170" />
        <el-table-column prop="level" label="级别" width="90">
          <template #default="{ row }">
            <el-tag :type="levelTag(row.level)" size="small" effect="dark">
              {{ levelLabel(row.level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="160" show-overflow-tooltip />
        <el-table-column label="内容摘要" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.content || row.description || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="触发设备" width="130">
          <template #default="{ row }">
            {{ row.device_name || row.device_code || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="alertStatusTag(row.status)" size="small">
              {{ alertStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'triggered'"
              size="small"
              type="warning"
              @click="acknowledgeAlert(row.id)"
              :loading="actionLoading === row.id"
            >
              确认
            </el-button>
            <el-button
              v-if="row.status === 'acknowledged'"
              size="small"
              type="primary"
              @click="openHandleDialog(row)"
            >
              处理
            </el-button>
            <el-button
              v-if="row.status === 'handled'"
              size="small"
              type="success"
              @click="closeAlert(row.id)"
              :loading="actionLoading === row.id"
            >
              关闭
            </el-button>
            <span v-if="row.status === 'closed'" style="color: var(--text-muted); font-size: 13px">已归档</span>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="fetchAlerts"
          @current-change="fetchAlerts"
        />
      </div>
    </el-card>

    <!-- 处理 Dialog -->
    <el-dialog
      v-model="handleVisible"
      title="处理告警"
      width="460px"
      destroy-on-close
    >
      <el-form>
        <el-form-item label="告警标题">
          <span style="color: var(--text-primary)">{{ handleTarget?.title }}</span>
        </el-form-item>
        <el-form-item label="处理备注" required>
          <el-input
            v-model="handleRemark"
            type="textarea"
            :rows="3"
            placeholder="请输入处理备注..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleVisible = false">取消</el-button>
        <el-button type="primary" :loading="handleLoading" @click="submitHandle">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import apiClient from '@/api/index.js'

const loading = ref(false)
const actionLoading = ref(null)
const tableData = ref([])
const stats = ref(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterLevel = ref('')
const filterStatus = ref('')
const dateRange = ref(null)

const handleVisible = ref(false)
const handleTarget = ref(null)
const handleRemark = ref('')
const handleLoading = ref(false)

function levelLabel(level) {
  const map = { critical: '严重', major: '重要', minor: '次要', info: '信息' }
  return map[level] || level || '-'
}

function levelTag(level) {
  const map = { critical: 'danger', major: 'warning', minor: '', info: 'info' }
  return map[level] || 'info'
}

function alertStatusLabel(status) {
  const map = { triggered: '已触发', acknowledged: '已确认', handled: '已处理', closed: '已关闭' }
  return map[status] || status || '-'
}

function alertStatusTag(status) {
  const map = { triggered: 'danger', acknowledged: 'warning', handled: '', closed: 'info' }
  return map[status] || 'info'
}

async function fetchAlerts() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterLevel.value) params.level = filterLevel.value
    if (filterStatus.value) params.status = filterStatus.value
    if (dateRange.value?.length === 2) {
      params.start_time = dateRange.value[0]
      params.end_time = dateRange.value[1]
    }
    const res = await apiClient.get('/alerts', { params })
    const data = res.data || res
    tableData.value = data.items || data || []
    total.value = data.total || tableData.value.length
  } catch {
    ElMessage.error('获取告警列表失败')
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

async function fetchStats() {
  try {
    const res = await apiClient.get('/alerts/statistics')
    stats.value = res.data || res
  } catch {
    stats.value = null
  }
}

function handleExpand(row, expandedRows) {
  // expand 行时不需要额外请求，数据已在 row 中
}

async function acknowledgeAlert(id) {
  actionLoading.value = id
  try {
    await apiClient.post(`/alerts/${id}/acknowledge`)
    ElMessage.success('告警已确认')
    fetchAlerts()
    fetchStats()
  } catch {
    ElMessage.error('确认告警失败')
  } finally {
    actionLoading.value = null
  }
}

function openHandleDialog(row) {
  handleTarget.value = row
  handleRemark.value = ''
  handleVisible.value = true
}

async function submitHandle() {
  if (!handleRemark.value.trim()) {
    ElMessage.warning('请输入处理备注')
    return
  }
  handleLoading.value = true
  try {
    await apiClient.post(`/alerts/${handleTarget.value.id}/handle`, {
      handle_remark: handleRemark.value.trim(),
    })
    ElMessage.success('告警已处理')
    handleVisible.value = false
    fetchAlerts()
    fetchStats()
  } catch {
    ElMessage.error('处理告警失败')
  } finally {
    handleLoading.value = false
  }
}

async function closeAlert(id) {
  actionLoading.value = id
  try {
    await apiClient.post(`/alerts/${id}/close`)
    ElMessage.success('告警已关闭')
    fetchAlerts()
    fetchStats()
  } catch {
    ElMessage.error('关闭告警失败')
  } finally {
    actionLoading.value = null
  }
}

onMounted(() => {
  fetchAlerts()
  fetchStats()
})
</script>

<style scoped>
.alerts-page { min-height: 100%; }

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

.stats-row {
  display: flex;
  gap: 20px;
  margin-top: 16px;
  padding: 12px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  font-family: var(--font-mono);
}

.stat-value.critical { color: var(--danger); }
.stat-value.major { color: var(--orange); }
.stat-value.minor { color: var(--warning); }
.stat-value.info { color: var(--accent); }

.stat-label {
  font-size: 12px;
  color: var(--text-muted);
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.expand-content {
  padding: 16px 24px;
  background: var(--bg-card);
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

:deep(.el-dialog) {
  --el-dialog-bg-color: var(--bg-panel);
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid var(--border-color);
}

:deep(.el-dialog__title) {
  color: var(--accent);
  font-weight: bold;
}

:deep(.el-input__wrapper),
:deep(.el-select .el-input__wrapper),
:deep(.el-textarea__inner) {
  background: var(--bg-card);
  border-color: var(--border-color);
  box-shadow: none;
}

:deep(.el-input__wrapper:hover),
:deep(.el-select .el-input__wrapper:hover) {
  border-color: var(--accent);
}

:deep(.el-input__inner),
:deep(.el-select .el-input__inner),
:deep(.el-textarea__inner) {
  color: var(--text-primary);
}

:deep(.el-form-item__label) {
  color: var(--text-secondary);
}

:deep(.el-descriptions) {
  --el-descriptions-item-bordered-label-background: var(--bg-panel);
}

:deep(.el-descriptions__label) {
  color: var(--text-secondary);
}

:deep(.el-descriptions__content) {
  color: var(--text-primary);
}

:deep(.el-descriptions--border .el-descriptions__cell) {
  border-color: var(--border-color);
}
</style>
