<template>
  <div class="logs-page">
    <el-card class="admin-card">
      <template #header>
        <span class="card-title">操作日志</span>
      </template>

      <div class="toolbar">
        <el-select v-model="filterType" placeholder="操作类型" clearable style="width: 150px" @change="fetchLogs">
          <el-option label="登录" value="login" />
          <el-option label="创建" value="create" />
          <el-option label="更新" value="update" />
          <el-option label="删除" value="delete" />
          <el-option label="控制" value="control" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          @change="fetchLogs"
        />
        <el-input
          v-model="searchKeyword"
          placeholder="搜索操作内容..."
          clearable
          style="width: 200px"
          @clear="fetchLogs"
          @keyup.enter="fetchLogs"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="fetchLogs">
          <el-icon><Search /></el-icon> 查询
        </el-button>
      </div>

      <el-table
        v-loading="loading"
        :data="pagedData"
        stripe
        border
        style="width: 100%; margin-top: 16px"
        :header-cell-style="{ background: 'var(--bg-card)', color: 'var(--text-primary)', borderColor: 'var(--border-color)' }"
        :cell-style="{ background: 'var(--bg-panel)', color: 'var(--text-primary)', borderColor: 'var(--border-color)' }"
      >
        <el-table-column label="时间" width="170">
          <template #default="{ row }">{{ row.time }}</template>
        </el-table-column>
        <el-table-column label="操作人" width="120">
          <template #default="{ row }">{{ row.operator }}</template>
        </el-table-column>
        <el-table-column label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag :type="actionTypeTag(row.action_type)" size="small">
              {{ actionTypeLabel(row.action_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作内容" min-width="200">
          <template #default="{ row }">{{ row.content }}</template>
        </el-table-column>
        <el-table-column label="IP地址" width="150">
          <template #default="{ row }">{{ row.ip }}</template>
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
          @size-change="onPageChange"
          @current-change="onPageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const loading = ref(false)
const filterType = ref('')
const dateRange = ref([])
const searchKeyword = ref('')
const page = ref(1)
const pageSize = ref(20)
const allLogs = ref([])

const operators = ['admin', '张管理', '李技术', '王操作', '赵维护']
const actionTypes = ['login', 'create', 'update', 'delete', 'control']
const contents = [
  '登录系统',
  '创建地块 PLOT-001',
  '更新地块信息',
  '删除设备 SENSOR-003',
  '新增作物 番茄',
  '编辑作物 黄瓜',
  '删除作物记录',
  '启动灌溉系统',
  '关闭通风设备',
  '修改施肥计划',
  '创建告警规则',
  '更新用户权限',
  '导出数据报表',
  '修改系统配置',
  '手动触发数据采集',
  '批量导入地块数据',
  '调整灌溉参数',
  '重置设备连接',
  '审核采收记录',
  '添加传感器设备',
  '修改阈值设置',
  '创建施肥记录',
  '删除告警规则',
  '更新作物品种信息',
  '设置定时灌溉任务',
]
const ips = ['192.168.1.100', '192.168.1.101', '192.168.1.102', '10.0.0.50', '10.0.0.51']

function randomItem(arr) {
  return arr[Math.floor(Math.random() * arr.length)]
}

function generateMockLogs() {
  const logs = []
  const now = new Date()
  for (let i = 0; i < 50; i++) {
    const t = new Date(now.getTime() - i * 3600000 * (1 + Math.random() * 5))
    logs.push({
      id: i + 1,
      time: `${t.getFullYear()}-${String(t.getMonth() + 1).padStart(2, '0')}-${String(t.getDate()).padStart(2, '0')} ${String(t.getHours()).padStart(2, '0')}:${String(t.getMinutes()).padStart(2, '0')}:${String(t.getSeconds()).padStart(2, '0')}`,
      operator: randomItem(operators),
      action_type: randomItem(actionTypes),
      content: randomItem(contents),
      ip: randomItem(ips),
    })
  }
  allLogs.value = logs
}

const filteredLogs = computed(() => {
  let logs = [...allLogs.value]

  if (filterType.value) {
    logs = logs.filter(l => l.action_type === filterType.value)
  }

  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    logs = logs.filter(l => {
      const d = l.time.slice(0, 10)
      return d >= start && d <= end
    })
  }

  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    logs = logs.filter(l =>
      l.content.toLowerCase().includes(kw) ||
      l.operator.toLowerCase().includes(kw)
    )
  }

  return logs
})

const total = computed(() => filteredLogs.value.length)

const pagedData = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredLogs.value.slice(start, start + pageSize.value)
})

function actionTypeLabel(type) {
  const map = { login: '登录', create: '创建', update: '更新', delete: '删除', control: '控制' }
  return map[type] || type
}

function actionTypeTag(type) {
  const map = { login: 'info', create: 'success', update: '', delete: 'danger', control: 'warning' }
  return map[type] || 'info'
}

function fetchLogs() {
  page.value = 1
}

function onPageChange() {
  // 触发 computed 重新计算
}

onMounted(() => {
  generateMockLogs()
})
</script>

<style scoped>
.logs-page { min-height: 100%; }

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

:deep(.el-input__wrapper),
:deep(.el-select .el-input__wrapper) {
  background: var(--bg-card);
  border-color: var(--border-color);
  box-shadow: none;
}

:deep(.el-input__wrapper:hover),
:deep(.el-select .el-input__wrapper:hover) {
  border-color: var(--accent);
}

:deep(.el-input__inner),
:deep(.el-select .el-input__inner) {
  color: var(--text-primary);
}
</style>
