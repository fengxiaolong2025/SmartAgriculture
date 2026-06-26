<template>
  <div class="devices-page">
    <el-card class="admin-card">
      <template #header>
        <span class="card-title">设备管理</span>
      </template>

      <!-- 搜索筛选区 -->
      <div class="toolbar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索设备名称/编码..."
          clearable
          style="width: 240px"
          @clear="fetchDevices"
          @keyup.enter="fetchDevices"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="filterType" placeholder="设备类型" clearable style="width: 160px" @change="fetchDevices">
          <el-option label="传感器" value="sensor" />
          <el-option label="控制器" value="controller" />
          <el-option label="执行器" value="actuator" />
          <el-option label="网关" value="gateway" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="设备状态" clearable style="width: 140px" @change="fetchDevices">
          <el-option label="在线" value="online" />
          <el-option label="离线" value="offline" />
          <el-option label="维护" value="maintenance" />
        </el-select>
        <el-button type="primary" @click="fetchDevices">
          <el-icon><Search /></el-icon> 查询
        </el-button>
        <div class="toolbar-spacer" />
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon> 新增设备
        </el-button>
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
      >
        <el-table-column prop="device_code" label="设备编码" min-width="140" />
        <el-table-column prop="name" label="设备名称" min-width="140" />
        <el-table-column prop="device_type" label="设备类型" width="110">
          <template #default="{ row }">
            <el-tag :type="deviceTypeTag(row.device_type)" size="small">
              {{ deviceTypeLabel(row.device_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sub_type" label="子类型" width="120">
          <template #default="{ row }">
            {{ row.sub_type || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="所属地块" width="120">
          <template #default="{ row }">
            {{ row.plot_name || (row.plot_id ? `地块#${row.plot_id}` : '-') }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最后在线" width="170">
          <template #default="{ row }">
            {{ row.last_online || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="openEditDialog(row)">编辑</el-button>
            <el-button
              v-if="row.device_type === 'controller' || row.device_type === 'actuator'"
              size="small"
              text
              type="warning"
              @click="openControlDialog(row)"
            >
              控制
            </el-button>
            <el-popconfirm
              title="确定删除该设备？"
              confirm-button-text="确定"
              cancel-button-text="取消"
              @confirm="deleteDevice(row.id)"
            >
              <template #reference>
                <el-button size="small" text type="danger">删除</el-button>
              </template>
            </el-popconfirm>
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
          @size-change="fetchDevices"
          @current-change="fetchDevices"
        />
      </div>
    </el-card>

    <!-- 新增/编辑 Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑设备' : '新增设备'"
      width="560px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="设备编码" prop="device_code">
          <el-input v-model="form.device_code" placeholder="请输入设备编码" />
        </el-form-item>
        <el-form-item label="设备名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入设备名称" />
        </el-form-item>
        <el-form-item label="设备类型" prop="device_type">
          <el-select v-model="form.device_type" placeholder="请选择设备类型" style="width: 100%">
            <el-option label="传感器" value="sensor" />
            <el-option label="控制器" value="controller" />
            <el-option label="执行器" value="actuator" />
            <el-option label="网关" value="gateway" />
          </el-select>
        </el-form-item>
        <el-form-item label="子类型" prop="sub_type">
          <el-select v-model="form.sub_type" placeholder="请选择子类型" style="width: 100%">
            <el-option v-if="form.device_type === 'sensor'" label="温度传感器" value="temperature" />
            <el-option v-if="form.device_type === 'sensor'" label="湿度传感器" value="humidity" />
            <el-option v-if="form.device_type === 'sensor'" label="土壤传感器" value="soil" />
            <el-option v-if="form.device_type === 'sensor'" label="光照传感器" value="light" />
            <el-option v-if="form.device_type === 'sensor'" label="CO2传感器" value="co2" />
            <el-option v-if="form.device_type === 'controller'" label="灌溉控制器" value="irrigation" />
            <el-option v-if="form.device_type === 'controller'" label="环境控制器" value="environment" />
            <el-option v-if="form.device_type === 'actuator'" label="灌溉阀" value="valve" />
            <el-option v-if="form.device_type === 'actuator'" label="风机" value="fan" />
            <el-option v-if="form.device_type === 'actuator'" label="除害设备" value="pest_control" />
            <el-option v-if="form.device_type === 'actuator'" label="遮阳网" value="shade" />
            <el-option v-if="form.device_type === 'gateway'" label="4G网关" value="4g" />
            <el-option v-if="form.device_type === 'gateway'" label="WiFi网关" value="wifi" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属地块" prop="plot_id">
          <el-select v-model="form.plot_id" placeholder="请选择地块" style="width: 100%" clearable>
            <el-option
              v-for="plot in plots"
              :key="plot.id"
              :label="plot.name || `地块#${plot.id}`"
              :value="plot.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="通信协议" prop="protocol">
          <el-select v-model="form.protocol" placeholder="请选择协议" style="width: 100%">
            <el-option label="MQTT" value="mqtt" />
            <el-option label="Modbus RTU" value="modbus_rtu" />
            <el-option label="Modbus TCP" value="modbus_tcp" />
            <el-option label="HTTP" value="http" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 远程控制 Dialog -->
    <el-dialog
      v-model="controlVisible"
      title="远程控制"
      width="420px"
      destroy-on-close
    >
      <div class="control-body">
        <p style="margin-bottom: 16px; color: var(--text-secondary)">
          当前设备：<strong style="color: var(--accent)">{{ controlDevice?.name }}</strong>
          （{{ controlDevice?.device_code }}）
        </p>
        <div class="control-actions">
          <el-button
            :type="controlState === 'on' ? 'success' : 'default'"
            size="large"
            @click="sendCommand('on')"
            :loading="controlLoading && controlAction === 'on'"
          >
            <el-icon><VideoPlay /></el-icon> 开启
          </el-button>
          <el-button
            :type="controlState === 'off' ? 'danger' : 'default'"
            size="large"
            @click="sendCommand('off')"
            :loading="controlLoading && controlAction === 'off'"
          >
            <el-icon><VideoPause /></el-icon> 关闭
          </el-button>
        </div>
      </div>
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
const plots = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchKeyword = ref('')
const filterType = ref('')
const filterStatus = ref('')

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const formRef = ref(null)

const form = reactive({
  device_code: '',
  name: '',
  device_type: '',
  sub_type: '',
  plot_id: null,
  protocol: '',
})

const formRules = {
  device_code: [{ required: true, message: '请输入设备编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  device_type: [{ required: true, message: '请选择设备类型', trigger: 'change' }],
}

const controlVisible = ref(false)
const controlDevice = ref(null)
const controlState = ref('off')
const controlLoading = ref(false)
const controlAction = ref('')

function deviceTypeLabel(type) {
  const map = { sensor: '传感器', controller: '控制器', actuator: '执行器', gateway: '网关' }
  return map[type] || type || '-'
}

function deviceTypeTag(type) {
  const map = { sensor: 'success', controller: '', actuator: 'warning', gateway: 'info' }
  return map[type] || 'info'
}

function statusLabel(status) {
  const map = { online: '在线', offline: '离线', maintenance: '维护' }
  return map[status] || status || '未知'
}

function statusTag(status) {
  const map = { online: 'success', offline: 'danger', maintenance: 'warning' }
  return map[status] || 'info'
}

async function fetchDevices() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (searchKeyword.value) params.name = searchKeyword.value
    if (filterType.value) params.device_type = filterType.value
    if (filterStatus.value) params.status = filterStatus.value
    const res = await apiClient.get('/devices', { params })
    const data = res.data || res
    tableData.value = data.items || data || []
    total.value = data.total || tableData.value.length
  } catch {
    ElMessage.error('获取设备列表失败')
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

function resetForm() {
  form.device_code = ''
  form.name = ''
  form.device_type = ''
  form.sub_type = ''
  form.plot_id = null
  form.protocol = ''
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
  form.device_code = row.device_code || ''
  form.name = row.name || ''
  form.device_type = row.device_type || ''
  form.sub_type = row.sub_type || ''
  form.plot_id = row.plot_id || null
  form.protocol = row.protocol || ''
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    const payload = {
      device_code: form.device_code,
      name: form.name,
      device_type: form.device_type,
      sub_type: form.sub_type,
      plot_id: form.plot_id,
      protocol: form.protocol,
    }
    if (isEdit.value) {
      await apiClient.put(`/devices/${editingId.value}`, payload)
      ElMessage.success('设备更新成功')
    } else {
      await apiClient.post('/devices', payload)
      ElMessage.success('设备创建成功')
    }
    dialogVisible.value = false
    fetchDevices()
  } catch {
    ElMessage.error(isEdit.value ? '设备更新失败' : '设备创建失败')
  } finally {
    submitLoading.value = false
  }
}

async function deleteDevice(id) {
  try {
    await apiClient.delete(`/devices/${id}`)
    ElMessage.success('设备已删除')
    fetchDevices()
  } catch {
    ElMessage.error('删除失败')
  }
}

function openControlDialog(row) {
  controlDevice.value = row
  controlState.value = 'off'
  controlVisible.value = true
}

async function sendCommand(command) {
  if (!controlDevice.value) return
  controlLoading.value = true
  controlAction.value = command
  try {
    await apiClient.post(`/devices/${controlDevice.value.id}/command`, {
      command,
      params: {},
    })
    controlState.value = command
    ElMessage.success(`设备${command === 'on' ? '已开启' : '已关闭'}`)
  } catch {
    ElMessage.error('命令发送失败')
  } finally {
    controlLoading.value = false
  }
}

onMounted(() => {
  fetchDevices()
  fetchPlots()
})
</script>

<style scoped>
.devices-page { min-height: 100%; }

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

.toolbar-spacer { flex: 1; }

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.control-body { text-align: center; }

.control-actions {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 8px;
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
  --el-dialog-title-font-size: 16px;
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

:deep(.el-input__wrapper.is-focus),
:deep(.el-select .el-input__wrapper.is-focus) {
  border-color: var(--accent);
  box-shadow: 0 0 0 1px var(--accent-dim) inset;
}
</style>
