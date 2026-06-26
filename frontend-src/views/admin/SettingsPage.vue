<template>
  <div class="settings-page">
    <!-- 系统配置表单 -->
    <el-card class="admin-card">
      <template #header>
        <span class="card-title">系统配置</span>
      </template>

      <el-form
        ref="formRef"
        :model="configForm"
        label-width="140px"
        :loading="configLoading"
      >
        <el-form-item label="系统名称">
          <el-input v-model="configForm.system_name" placeholder="农业物联网监控平台" style="max-width: 400px" />
        </el-form-item>

        <el-divider content-position="left">
          <span style="color: var(--text-secondary); font-size: 13px">告警推送配置</span>
        </el-divider>

        <el-form-item label="短信推送">
          <el-switch v-model="configForm.sms_enabled" active-text="开启" inactive-text="关闭" />
        </el-form-item>
        <el-form-item label="微信推送">
          <el-switch v-model="configForm.wechat_enabled" active-text="开启" inactive-text="关闭" />
        </el-form-item>

        <el-divider content-position="left">
          <span style="color: var(--text-secondary); font-size: 13px">数据管理</span>
        </el-divider>

        <el-form-item label="数据保留天数">
          <el-input-number
            v-model="configForm.data_retention_days"
            :min="7"
            :max="3650"
            :step="30"
            style="width: 200px"
          />
          <span style="color: var(--text-muted); margin-left: 8px; font-size: 12px">超过天数的历史数据将被自动清理</span>
        </el-form-item>

        <el-form-item label="采集频率(秒)">
          <el-input-number
            v-model="configForm.collect_interval"
            :min="5"
            :max="3600"
            :step="5"
            style="width: 200px"
          />
          <span style="color: var(--text-muted); margin-left: 8px; font-size: 12px">传感器数据采集间隔</span>
        </el-form-item>

        <el-divider content-position="left">
          <span style="color: var(--text-secondary); font-size: 13px">通用设置</span>
        </el-divider>

        <el-form-item label="默认语言">
          <el-select v-model="configForm.default_language" style="width: 200px">
            <el-option label="简体中文" value="zh-CN" />
            <el-option label="English" value="en-US" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="saveLoading" @click="saveConfig">
            保存配置
          </el-button>
          <el-button @click="fetchConfig">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 系统健康检查 -->
    <el-card class="admin-card" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span class="card-title">系统健康检查</span>
          <el-button size="small" :loading="healthLoading" @click="fetchHealth">
            <el-icon><Refresh /></el-icon> 刷新
          </el-button>
        </div>
      </template>

      <div v-loading="healthLoading">
        <div v-if="healthData" class="health-grid">
          <div class="health-item">
            <span class="health-label">服务状态</span>
            <span class="health-value" :class="healthData.status === 'ok' ? 'ok' : 'error'">
              <span class="health-dot" :class="healthData.status === 'ok' ? 'ok' : 'error'" />
              {{ healthData.status === 'ok' ? '正常运行' : '异常' }}
            </span>
          </div>
          <div class="health-item">
            <span class="health-label">运行时间</span>
            <span class="health-value">{{ healthData.uptime || '-' }}</span>
          </div>
          <div class="health-item">
            <span class="health-label">API 版本</span>
            <span class="health-value">{{ healthData.version || '-' }}</span>
          </div>
          <div class="health-item">
            <span class="health-label">数据库</span>
            <span class="health-value" :class="healthData.database === 'connected' ? 'ok' : 'error'">
              <span class="health-dot" :class="healthData.database === 'connected' ? 'ok' : 'error'" />
              {{ healthData.database === 'connected' ? '已连接' : '断开' }}
            </span>
          </div>
          <div class="health-item">
            <span class="health-label">内存使用</span>
            <span class="health-value">{{ healthData.memory_usage || '-' }}</span>
          </div>
          <div class="health-item">
            <span class="health-label">CPU 使用</span>
            <span class="health-value">{{ healthData.cpu_usage || '-' }}</span>
          </div>
        </div>
        <div v-else-if="!healthLoading" class="health-empty">
          点击刷新按钮获取系统健康状态
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import apiClient from '@/api/index.js'

const configLoading = ref(false)
const saveLoading = ref(false)
const healthLoading = ref(false)
const formRef = ref(null)

const configForm = reactive({
  system_name: '',
  sms_enabled: false,
  wechat_enabled: false,
  data_retention_days: 90,
  collect_interval: 30,
  default_language: 'zh-CN',
})

const healthData = ref(null)

async function fetchConfig() {
  configLoading.value = true
  try {
    const res = await apiClient.get('/system/config')
    const data = res.data || res
    if (data && typeof data === 'object') {
      configForm.system_name = data.system_name || ''
      configForm.sms_enabled = !!data.sms_enabled
      configForm.wechat_enabled = !!data.wechat_enabled
      configForm.data_retention_days = data.data_retention_days ?? 90
      configForm.collect_interval = data.collect_interval ?? 30
      configForm.default_language = data.default_language || 'zh-CN'
    }
  } catch {
    ElMessage.error('获取系统配置失败')
  } finally {
    configLoading.value = false
  }
}

async function saveConfig() {
  saveLoading.value = true
  try {
    await apiClient.put('/system/config', {
      system_name: configForm.system_name,
      sms_enabled: configForm.sms_enabled,
      wechat_enabled: configForm.wechat_enabled,
      data_retention_days: configForm.data_retention_days,
      collect_interval: configForm.collect_interval,
      default_language: configForm.default_language,
    })
    ElMessage.success('系统配置已保存')
  } catch {
    ElMessage.error('保存配置失败')
  } finally {
    saveLoading.value = false
  }
}

async function fetchHealth() {
  healthLoading.value = true
  try {
    const res = await apiClient.get('/system/health')
    healthData.value = res.data || res
  } catch {
    ElMessage.error('获取健康检查信息失败')
    healthData.value = null
  } finally {
    healthLoading.value = false
  }
}

onMounted(() => {
  fetchConfig()
  fetchHealth()
})
</script>

<style scoped>
.settings-page { min-height: 100%; }

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

.health-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.health-item {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.health-label {
  font-size: 12px;
  color: var(--text-muted);
}

.health-value {
  font-size: 14px;
  font-weight: bold;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.health-value.ok { color: var(--success); }
.health-value.error { color: var(--danger); }

.health-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.health-dot.ok {
  background: var(--success);
  box-shadow: 0 0 6px var(--success);
}

.health-dot.error {
  background: var(--danger);
  box-shadow: 0 0 6px var(--danger);
}

.health-empty {
  text-align: center;
  padding: 40px 0;
  color: var(--text-muted);
  font-size: 14px;
}

/* Element Plus 深色主题覆盖 */
:deep(.el-divider__text) {
  background: var(--bg-panel);
}

:deep(.el-divider--horizontal) {
  border-color: var(--border-color);
  margin: 24px 0;
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

:deep(.el-switch.is-checked .el-switch__core) {
  background-color: var(--accent);
  border-color: var(--accent);
}

:deep(.el-switch__label) {
  color: var(--text-secondary);
}

:deep(.el-switch__label.is-active) {
  color: var(--accent);
}
</style>
