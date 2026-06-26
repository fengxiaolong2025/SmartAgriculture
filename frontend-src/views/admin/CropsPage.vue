<template>
  <div class="crops-page">
    <el-card class="admin-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">作物管理</span>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon> 新增作物
          </el-button>
        </div>
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
        <el-table-column prop="name" label="名称" min-width="120" />
        <el-table-column prop="variety" label="品种" min-width="120" />
        <el-table-column label="生物学零度(℃)" width="130">
          <template #default="{ row }">
            {{ row.t_base != null ? row.t_base + ' ℃' : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="成熟积温(GDD)" width="140">
          <template #default="{ row }">
            {{ row.gdd_maturity != null ? row.gdd_maturity + ' ℃·d' : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="预期生长天数" width="120">
          <template #default="{ row }">
            {{ row.expected_days != null ? row.expected_days + ' 天' : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="最适温度" width="120">
          <template #default="{ row }">
            {{ row.temp_min != null ? `${row.temp_min}~${row.temp_max}℃` : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="最适湿度" width="120">
          <template #default="{ row }">
            {{ row.humidity_min != null ? `${row.humidity_min}~${row.humidity_max}%` : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm
              title="确定删除该作物？"
              confirm-button-text="确定"
              cancel-button-text="取消"
              @confirm="deleteCrop(row.id)"
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
          @size-change="fetchCrops"
          @current-change="fetchCrops"
        />
      </div>
    </el-card>

    <!-- 新增/编辑 Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑作物' : '新增作物'"
      width="560px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="130px">
        <el-form-item label="作物名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入作物名称" />
        </el-form-item>
        <el-form-item label="品种" prop="variety">
          <el-input v-model="form.variety" placeholder="请输入品种" />
        </el-form-item>
        <el-form-item label="生物学零度(℃)" prop="t_base">
          <el-input-number v-model="form.t_base" :min="-50" :max="50" :step="0.1" :precision="1" style="width: 100%" placeholder="如: 10.0" />
        </el-form-item>
        <el-form-item label="成熟所需积温(GDD)" prop="gdd_maturity">
          <el-input-number v-model="form.gdd_maturity" :min="0" :max="10000" :step="10" style="width: 100%" placeholder="如: 2500" />
        </el-form-item>
        <el-form-item label="预期生长天数" prop="expected_days">
          <el-input-number v-model="form.expected_days" :min="1" :max="999" style="width: 100%" placeholder="如: 120" />
        </el-form-item>
        <el-form-item label="最适温度范围(℃)">
          <div style="display: flex; gap: 8px; align-items: center; width: 100%">
            <el-input-number v-model="form.temp_min" :min="-50" :max="50" :step="0.5" :precision="1" placeholder="最低" style="flex: 1" />
            <span style="color: var(--text-muted)">~</span>
            <el-input-number v-model="form.temp_max" :min="-50" :max="50" :step="0.5" :precision="1" placeholder="最高" style="flex: 1" />
          </div>
        </el-form-item>
        <el-form-item label="最适湿度范围(%)">
          <div style="display: flex; gap: 8px; align-items: center; width: 100%">
            <el-input-number v-model="form.humidity_min" :min="0" :max="100" :step="1" placeholder="最低" style="flex: 1" />
            <span style="color: var(--text-muted)">~</span>
            <el-input-number v-model="form.humidity_max" :min="0" :max="100" :step="1" placeholder="最高" style="flex: 1" />
          </div>
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
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const formRef = ref(null)

const form = reactive({
  name: '',
  variety: '',
  t_base: null,
  gdd_maturity: null,
  expected_days: null,
  temp_min: null,
  temp_max: null,
  humidity_min: null,
  humidity_max: null,
})

const formRules = {
  name: [{ required: true, message: '请输入作物名称', trigger: 'blur' }],
  variety: [{ required: true, message: '请输入品种', trigger: 'blur' }],
  t_base: [{ required: true, message: '请输入生物学零度', trigger: 'blur' }],
  gdd_maturity: [{ required: true, message: '请输入成熟积温', trigger: 'blur' }],
  expected_days: [{ required: true, message: '请输入预期生长天数', trigger: 'blur' }],
}

async function fetchCrops() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    const res = await apiClient.get('/crops', { params })
    const data = res.data || res
    tableData.value = data.items || data || []
    total.value = data.total || tableData.value.length
  } catch {
    ElMessage.error('获取作物列表失败')
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.name = ''
  form.variety = ''
  form.t_base = null
  form.gdd_maturity = null
  form.expected_days = null
  form.temp_min = null
  form.temp_max = null
  form.humidity_min = null
  form.humidity_max = null
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
  form.name = row.name || ''
  form.variety = row.variety || ''
  form.t_base = row.t_base ?? null
  form.gdd_maturity = row.gdd_maturity ?? null
  form.expected_days = row.expected_days ?? null
  form.temp_min = row.temp_min ?? null
  form.temp_max = row.temp_max ?? null
  form.humidity_min = row.humidity_min ?? null
  form.humidity_max = row.humidity_max ?? null
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    const payload = {
      name: form.name,
      variety: form.variety,
      t_base: form.t_base,
      gdd_maturity: form.gdd_maturity,
      expected_days: form.expected_days,
      temp_min: form.temp_min,
      temp_max: form.temp_max,
      humidity_min: form.humidity_min,
      humidity_max: form.humidity_max,
    }
    if (isEdit.value) {
      await apiClient.put(`/crops/${editingId.value}`, payload)
      ElMessage.success('作物更新成功')
    } else {
      await apiClient.post('/crops', payload)
      ElMessage.success('作物创建成功')
    }
    dialogVisible.value = false
    fetchCrops()
  } catch {
    ElMessage.error(isEdit.value ? '作物更新失败' : '作物创建失败')
  } finally {
    submitLoading.value = false
  }
}

async function deleteCrop(id) {
  try {
    await apiClient.delete(`/crops/${id}`)
    ElMessage.success('作物已删除')
    fetchCrops()
  } catch {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchCrops()
})
</script>

<style scoped>
.crops-page { min-height: 100%; }

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
