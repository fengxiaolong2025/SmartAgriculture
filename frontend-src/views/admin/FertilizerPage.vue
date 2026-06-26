<template>
  <div class="fertilizer-page">
    <el-card class="admin-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">施肥管理</span>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon> 新增记录
          </el-button>
        </div>
      </template>

      <div class="stat-cards" v-if="stats">
        <div class="stat-card">
          <div class="stat-label">今日施肥总量</div>
          <div class="stat-value">{{ stats.total_amount || 0 }} <span class="stat-unit">kg</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-label">施肥次数</div>
          <div class="stat-value">{{ stats.record_count || 0 }} <span class="stat-unit">次</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-label">平均EC</div>
          <div class="stat-value">{{ stats.avg_ec?.toFixed(2) || '--' }} <span class="stat-unit">mS/cm</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-label">平均pH</div>
          <div class="stat-value">{{ stats.avg_ph?.toFixed(1) || '--' }}</div>
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        style="width: 100%; margin-top: 16px"
        :header-cell-style="{ background: 'var(--bg-card)', color: 'var(--text-primary)', borderColor: 'var(--border-color)' }"
        :cell-style="{ background: 'var(--bg-panel)', color: 'var(--text-primary)', borderColor: 'var(--border-color)' }"
      >
        <el-table-column label="地块" width="120">
          <template #default="{ row }">
            {{ row.plot_name || (row.plot_id ? `地块#${row.plot_id}` : '-') }}
          </template>
        </el-table-column>
        <el-table-column prop="fertilizer_type" label="肥料种类" width="120" />
        <el-table-column label="用量(kg)" width="100">
          <template #default="{ row }">{{ row.amount_kg ?? '-' }}</template>
        </el-table-column>
        <el-table-column label="实测EC" width="100">
          <template #default="{ row }">{{ row.ec_measured != null ? row.ec_measured.toFixed(2) : '-' }}</template>
        </el-table-column>
        <el-table-column label="实测pH" width="100">
          <template #default="{ row }">{{ row.ph_measured != null ? row.ph_measured.toFixed(1) : '-' }}</template>
        </el-table-column>
        <el-table-column label="触发类型" width="120">
          <template #default="{ row }">
            <el-tag :type="triggerTag(row.trigger_type)" size="small">
              {{ triggerLabel(row.trigger_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="施肥时间" min-width="160">
          <template #default="{ row }">{{ row.created_at || row.fertilized_at || '-' }}</template>
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

    <el-dialog
      v-model="dialogVisible"
      title="新增施肥记录"
      width="500px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="选择地块" prop="plot_id">
          <el-select v-model="form.plot_id" placeholder="请选择地块" style="width: 100%">
            <el-option v-for="p in plots" :key="p.id" :label="p.name || `地块#${p.id}`" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="肥料种类" prop="fertilizer_type">
          <el-select v-model="form.fertilizer_type" placeholder="请选择" style="width: 100%">
            <el-option label="氮肥" value="nitrogen" />
            <el-option label="磷肥" value="phosphorus" />
            <el-option label="钾肥" value="potassium" />
            <el-option label="复合肥" value="compound" />
            <el-option label="有机肥" value="organic" />
            <el-option label="微量元素" value="micro" />
          </el-select>
        </el-form-item>
        <el-form-item label="用量(kg)" prop="amount_kg">
          <el-input-number v-model="form.amount_kg" :min="0" :precision="1" style="width: 100%" placeholder="请输入用量" />
        </el-form-item>
        <el-form-item label="实测EC">
          <el-input-number v-model="form.ec_measured" :min="0" :precision="2" :step="0.1" style="width: 100%" placeholder="mS/cm" />
        </el-form-item>
        <el-form-item label="实测pH">
          <el-input-number v-model="form.ph_measured" :min="0" :max="14" :precision="1" :step="0.1" style="width: 100%" placeholder="pH值" />
        </el-form-item>
        <el-form-item label="触发类型" prop="trigger_type">
          <el-select v-model="form.trigger_type" placeholder="请选择" style="width: 100%">
            <el-option label="手动" value="manual" />
            <el-option label="自动" value="auto" />
            <el-option label="计划" value="scheduled" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import apiClient from '@/api/index.js'

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref([])
const stats = ref(null)
const plots = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const dialogVisible = ref(false)
const formRef = ref(null)

const form = reactive({
  plot_id: null,
  fertilizer_type: '',
  amount_kg: null,
  ec_measured: null,
  ph_measured: null,
  trigger_type: '',
})

const formRules = {
  plot_id: [{ required: true, message: '请选择地块', trigger: 'change' }],
  fertilizer_type: [{ required: true, message: '请选择肥料种类', trigger: 'change' }],
  amount_kg: [{ required: true, message: '请输入用量', trigger: 'blur' }],
  trigger_type: [{ required: true, message: '请选择触发类型', trigger: 'change' }],
}

function triggerLabel(type) {
  const map = { manual: '手动', auto: '自动', scheduled: '计划' }
  return map[type] || type || '-'
}

function triggerTag(type) {
  const map = { manual: '', auto: 'success', scheduled: 'warning' }
  return map[type] || 'info'
}

async function fetchRecords() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    const res = await apiClient.get('/fertilization/records', { params })
    const data = res.data || res
    tableData.value = data.items || data || []
    total.value = data.total || tableData.value.length
  } catch {
    ElMessage.error('获取施肥记录失败')
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

async function fetchStats() {
  try {
    const res = await apiClient.get('/fertilization/statistics')
    stats.value = res.data || res
  } catch {
    stats.value = null
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

function resetForm() {
  form.plot_id = null
  form.fertilizer_type = ''
  form.amount_kg = null
  form.ec_measured = null
  form.ph_measured = null
  form.trigger_type = ''
}

function openCreateDialog() {
  resetForm()
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    const payload = {
      plot_id: form.plot_id,
      fertilizer_type: form.fertilizer_type,
      amount_kg: form.amount_kg,
      ec_measured: form.ec_measured,
      ph_measured: form.ph_measured,
      trigger_type: form.trigger_type,
    }
    await apiClient.post('/fertilization/records', payload)
    ElMessage.success('施肥记录创建成功')
    dialogVisible.value = false
    fetchRecords()
    fetchStats()
  } catch {
    ElMessage.error('创建施肥记录失败')
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  fetchRecords()
  fetchStats()
  fetchPlots()
})
</script>

<style scoped>
.fertilizer-page { min-height: 100%; }

.admin-card {
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
}

.admin-card :deep(.el-card__header) {
  border-bottom: 1px solid var(--border-color);
  padding: 14px 20px;
  background: linear-gradient(180deg, rgba(0,212,255,0.05) 0%, transparent 100%);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  margin-bottom: 4px;
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

:deep(.el-form-item__label) {
  color: var(--text-secondary);
}
</style>
