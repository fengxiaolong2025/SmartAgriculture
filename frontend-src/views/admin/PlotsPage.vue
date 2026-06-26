<template>
  <div class="plots-page">
    <el-card class="admin-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">地块管理</span>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon> 新增地块
          </el-button>
        </div>
      </template>

      <div class="toolbar">
        <el-select v-model="filterType" placeholder="类型筛选" clearable style="width: 160px" @change="fetchPlots">
          <el-option label="温室" value="greenhouse" />
          <el-option label="大田" value="field" />
          <el-option label="果园" value="orchard" />
          <el-option label="菌菇房" value="mushroom" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 140px" @change="fetchPlots">
          <el-option label="种植中" value="planted" />
          <el-option label="空闲" value="idle" />
          <el-option label="休耕" value="fallow" />
        </el-select>
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
        <el-table-column prop="code" label="地块编号" width="120" />
        <el-table-column prop="name" label="名称" min-width="140" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="plotTypeTag(row.plot_type)" size="small">
              {{ plotTypeLabel(row.plot_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="面积(m²)" width="100">
          <template #default="{ row }">
            {{ row.area_sqm != null ? row.area_sqm.toLocaleString() : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="当前作物" width="120">
          <template #default="{ row }">
            {{ row.crop_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="定植日期" width="120">
          <template #default="{ row }">
            {{ row.planting_date || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm
              title="确定删除该地块？"
              confirm-button-text="确定"
              cancel-button-text="取消"
              @confirm="deletePlot(row.id)"
            >
              <template #reference>
                <el-button size="small" text type="danger">删除</el-button>
              </template>
            </el-popconfirm>
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
          @size-change="fetchPlots"
          @current-change="fetchPlots"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑地块' : '新增地块'"
      width="560px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="地块编号" prop="code">
          <el-input v-model="form.code" placeholder="如: PLOT-001" />
        </el-form-item>
        <el-form-item label="地块名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入地块名称" />
        </el-form-item>
        <el-form-item label="地块类型" prop="plot_type">
          <el-select v-model="form.plot_type" placeholder="请选择类型" style="width: 100%">
            <el-option label="温室" value="greenhouse" />
            <el-option label="大田" value="field" />
            <el-option label="果园" value="orchard" />
            <el-option label="菌菇房" value="mushroom" />
          </el-select>
        </el-form-item>
        <el-form-item label="面积(m²)" prop="area_sqm">
          <el-input-number v-model="form.area_sqm" :min="0" :precision="1" style="width: 100%" placeholder="请输入面积" />
        </el-form-item>
        <el-form-item label="纬度">
          <el-input-number v-model="form.location_lat" :min="-90" :max="90" :precision="6" style="width: 100%" placeholder="纬度" />
        </el-form-item>
        <el-form-item label="经度">
          <el-input-number v-model="form.location_lng" :min="-180" :max="180" :precision="6" style="width: 100%" placeholder="经度" />
        </el-form-item>
        <el-form-item label="当前作物">
          <el-select v-model="form.current_crop_id" placeholder="请选择作物" style="width: 100%" clearable>
            <el-option
              v-for="crop in crops"
              :key="crop.id"
              :label="`${crop.name} ${crop.variety || ''}`"
              :value="crop.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="定植日期">
          <el-date-picker v-model="form.planting_date" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
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
const crops = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterType = ref('')
const filterStatus = ref('')

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const formRef = ref(null)

const form = reactive({
  code: '',
  name: '',
  plot_type: '',
  area_sqm: null,
  location_lat: null,
  location_lng: null,
  current_crop_id: null,
  planting_date: '',
})

const formRules = {
  code: [{ required: true, message: '请输入地块编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入地块名称', trigger: 'blur' }],
  plot_type: [{ required: true, message: '请选择地块类型', trigger: 'change' }],
  area_sqm: [{ required: true, message: '请输入面积', trigger: 'blur' }],
}

function plotTypeLabel(type) {
  const map = { greenhouse: '温室', field: '大田', orchard: '果园', mushroom: '菌菇房' }
  return map[type] || type || '-'
}

function plotTypeTag(type) {
  const map = { greenhouse: 'success', field: '', orchard: 'warning', mushroom: 'info' }
  return map[type] || 'info'
}

function statusLabel(status) {
  const map = { planted: '种植中', idle: '空闲', fallow: '休耕' }
  return map[status] || status || '-'
}

function statusTag(status) {
  const map = { planted: 'success', idle: 'info', fallow: 'warning' }
  return map[status] || 'info'
}

async function fetchPlots() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterType.value) params.plot_type = filterType.value
    if (filterStatus.value) params.status = filterStatus.value
    const res = await apiClient.get('/plots', { params })
    const data = res.data || res
    tableData.value = data.items || data || []
    total.value = data.total || tableData.value.length
  } catch {
    ElMessage.error('获取地块列表失败')
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

async function fetchCrops() {
  try {
    const res = await apiClient.get('/crops', { params: { page_size: 200 } })
    const data = res.data || res
    crops.value = data.items || data || []
  } catch {
    crops.value = []
  }
}

function resetForm() {
  form.code = ''
  form.name = ''
  form.plot_type = ''
  form.area_sqm = null
  form.location_lat = null
  form.location_lng = null
  form.current_crop_id = null
  form.planting_date = ''
}

function openCreateDialog() {
  isEdit.value = false
  editingId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(row) {
  isEdit.value = true
  editingId.value = row.id
  form.code = row.code || ''
  form.name = row.name || ''
  form.plot_type = row.plot_type || ''
  form.area_sqm = row.area_sqm ?? null
  form.location_lat = row.location_lat ?? null
  form.location_lng = row.location_lng ?? null
  form.current_crop_id = row.current_crop_id ?? null
  form.planting_date = row.planting_date || ''
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    const payload = {
      code: form.code,
      name: form.name,
      plot_type: form.plot_type,
      area_sqm: form.area_sqm,
      location_lat: form.location_lat,
      location_lng: form.location_lng,
      current_crop_id: form.current_crop_id,
      planting_date: form.planting_date,
    }
    if (isEdit.value) {
      await apiClient.put(`/plots/${editingId.value}`, payload)
      ElMessage.success('地块更新成功')
    } else {
      await apiClient.post('/plots', payload)
      ElMessage.success('地块创建成功')
    }
    dialogVisible.value = false
    fetchPlots()
  } catch {
    ElMessage.error(isEdit.value ? '地块更新失败' : '地块创建失败')
  } finally {
    submitLoading.value = false
  }
}

async function deletePlot(id) {
  try {
    await apiClient.delete(`/plots/${id}`)
    ElMessage.success('地块已删除')
    fetchPlots()
  } catch {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchPlots()
  fetchCrops()
})
</script>

<style scoped>
.plots-page { min-height: 100%; }

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

.toolbar {
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
</style>
