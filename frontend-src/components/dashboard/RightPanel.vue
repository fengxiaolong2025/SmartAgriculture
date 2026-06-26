<template>
  <div class="right-panel">
    <!-- 预警列表 -->
    <div class="panel alerts-section">
      <div class="panel-title">
        预警列表
        <span class="alert-count">{{ alerts.length }}</span>
      </div>
      <div class="panel-body alerts-body">
        <div class="alerts-scroll" ref="alertsScroll">
          <div
            v-for="alert in alerts"
            :key="alert.id"
            class="alert-item"
            :class="[
              'alert-' + alert.level,
              { 'alert-new': alert.isNew }
            ]"
          >
            <span class="alert-time">{{ alert.time }}</span>
            <span class="alert-tag" :class="'tag-' + alert.level">
              {{ levelLabel(alert.level) }}
            </span>
            <span class="alert-content">{{ alert.content }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 设备控制 -->
    <div class="panel controls-section">
      <div class="panel-title">设备快捷控制</div>
      <div class="panel-body controls-body">
        <div class="control-row">
          <span class="control-label">灌溉总阀</span>
          <button
            class="btn"
            :class="devices.irrigationValve ? 'btn-on' : 'btn-off'"
            @click="toggleDevice('irrigationValve')"
          >
            {{ devices.irrigationValve ? '● 开启' : '○ 关闭' }}
          </button>
        </div>
        <div class="control-row">
          <span class="control-label">风机</span>
          <button
            class="btn"
            :class="devices.fan ? 'btn-on' : 'btn-off'"
            @click="toggleDevice('fan')"
          >
            {{ devices.fan ? '● 运行' : '○ 停止' }}
          </button>
        </div>
        <div class="control-row">
          <span class="control-label">除害设备</span>
          <button
            class="btn"
            :class="devices.pestControl ? 'btn-on' : 'btn-off'"
            @click="toggleDevice('pestControl')"
          >
            {{ devices.pestControl ? '● 开启' : '○ 关闭' }}
          </button>
        </div>
        <div class="control-row">
          <span class="control-label">遮阳网</span>
          <button
            class="btn"
            :class="devices.shadeNet ? 'btn-on' : 'btn-off'"
            @click="toggleDevice('shadeNet')"
          >
            {{ devices.shadeNet ? '● 展开' : '○ 收起' }}
          </button>
        </div>
        <div class="control-row mode-row">
          <span class="control-label">运行模式</span>
          <div class="mode-toggle">
            <span class="mode-label" :class="{ active: !devices.autoMode }">手动</span>
            <label class="toggle-switch">
              <input type="checkbox" v-model="devices.autoMode" />
              <span class="toggle-slider"></span>
            </label>
            <span class="mode-label" :class="{ active: devices.autoMode }">自动</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import { storeToRefs } from 'pinia'

const dashboard = useDashboardStore()
const { alerts, devices } = storeToRefs(dashboard)

const alertsScroll = ref(null)

function levelLabel(level) {
  const map = { danger: '严重', warning: '警告', info: '提示', orange: '注意' }
  return map[level] || level
}

function toggleDevice(key) {
  devices[key] = !devices[key]
}
</script>

<style scoped>
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
  height: 100%;
}

.alerts-section {
  flex: 0 0 58%;
  display: flex;
  flex-direction: column;
}

.alert-count {
  font-size: 11px;
  background: var(--danger);
  color: #fff;
  border-radius: 10px;
  padding: 0 6px;
  margin-left: 6px;
}

.alerts-body {
  flex: 1;
  overflow: hidden;
  padding: 0;
}

.alerts-scroll {
  height: 100%;
  overflow-y: auto;
  padding: 8px;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 6px 8px;
  margin-bottom: 4px;
  border-radius: 3px;
  background: rgba(0, 0, 0, 0.15);
  border-left: 3px solid transparent;
  transition: all 0.3s;
  font-size: 11px;
}

.alert-item.alert-danger {
  border-left-color: var(--danger);
  background: rgba(255, 61, 79, 0.08);
}

.alert-item.alert-warning {
  border-left-color: var(--warning);
  background: rgba(255, 171, 0, 0.08);
}

.alert-item.alert-info {
  border-left-color: var(--accent);
  background: rgba(0, 212, 255, 0.05);
}

.alert-new {
  animation: blink-warning 1s ease-in-out 3;
}

.alert-time {
  font-family: var(--font-mono);
  color: var(--text-muted);
  white-space: nowrap;
  font-size: 10px;
  min-width: 55px;
}

.alert-tag {
  font-size: 10px;
  padding: 0 4px;
  border-radius: 2px;
  white-space: nowrap;
  font-weight: bold;
  min-width: 28px;
  text-align: center;
}

.tag-danger {
  background: rgba(255, 61, 79, 0.2);
  color: var(--danger);
}

.tag-warning {
  background: rgba(255, 171, 0, 0.2);
  color: var(--warning);
}

.tag-info {
  background: rgba(0, 212, 255, 0.15);
  color: var(--accent);
}

.alert-content {
  color: var(--text-secondary);
  line-height: 1.4;
  flex: 1;
}

/* 设备控制 */
.controls-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.controls-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.control-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 3px;
}

.control-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.mode-row {
  margin-top: auto;
}

.mode-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mode-label {
  font-size: 11px;
  color: var(--text-muted);
  transition: color 0.3s;
}

.mode-label.active {
  color: var(--accent);
  text-shadow: 0 0 6px var(--accent-dim);
}

/* 按钮点击反馈 */
.btn:active {
  transform: scale(0.95);
}
</style>
