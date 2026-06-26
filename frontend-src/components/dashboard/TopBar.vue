<template>
  <header class="top-bar">
    <div class="top-left">
      <div class="logo">
        <div class="logo-icon">
          <span class="logo-leaf"></span>
        </div>
        <span class="logo-text">智慧农业管理平台</span>
      </div>
    </div>
    <div class="top-center">
      <div class="datetime">
        <span class="date">{{ dateStr }}</span>
        <span class="time">{{ timeStr }}</span>
      </div>
    </div>
    <div class="top-right">
      <div class="weather-info">
        <span class="weather-icon">{{ weather.icon }}</span>
        <span class="weather-temp">{{ weather.temp }}°C</span>
        <span class="weather-humidity">湿度 {{ weather.humidity }}%</span>
      </div>
      <div class="device-status">
        <span class="status-dot online"></span>
        <span class="status-text">设备在线</span>
        <span class="status-count">{{ deviceOnline.online }}/{{ deviceOnline.total }}</span>
        <span class="status-percent">{{ (deviceOnline.online / deviceOnline.total * 100).toFixed(0) }}%</span>
      </div>
    </div>
    <div class="bottom-line"></div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import { storeToRefs } from 'pinia'

const dashboard = useDashboardStore()
const { weather, deviceOnline } = storeToRefs(dashboard)

const dateStr = ref('')
const timeStr = ref('')
let timer = null

function updateTime() {
  const now = new Date()
  const year = now.getFullYear()
  const month = (now.getMonth() + 1).toString().padStart(2, '0')
  const day = now.getDate().toString().padStart(2, '0')
  const weekDays = ['日', '一', '二', '三', '四', '五', '六']
  const weekDay = weekDays[now.getDay()]
  dateStr.value = `${year}年${month}月${day}日 星期${weekDay}`

  const h = now.getHours().toString().padStart(2, '0')
  const m = now.getMinutes().toString().padStart(2, '0')
  const s = now.getSeconds().toString().padStart(2, '0')
  timeStr.value = `${h}:${m}:${s}`
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.top-bar {
  height: 60px;
  background: linear-gradient(180deg, rgba(13, 33, 55, 0.95) 0%, rgba(10, 26, 46, 0.95) 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: relative;
  z-index: 10;
}

.bottom-line {
  position: absolute;
  bottom: 0;
  left: 5%;
  right: 5%;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  box-shadow: 0 0 10px var(--accent-dim), 0 0 20px var(--accent-dim);
}

/* 左侧 Logo */
.top-left {
  flex: 0 0 auto;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(0,230,118,0.2));
  border: 1px solid var(--accent-dim);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.logo-leaf {
  width: 16px;
  height: 16px;
  background: var(--success);
  border-radius: 50% 0 50% 50%;
  transform: rotate(-45deg);
  box-shadow: 0 0 8px var(--success);
}

.logo-text {
  font-size: 20px;
  font-weight: bold;
  background: linear-gradient(90deg, var(--accent), var(--success));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 3px;
}

/* 中间时间 */
.top-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.datetime {
  display: flex;
  align-items: center;
  gap: 20px;
}

.date {
  font-size: 14px;
  color: var(--text-secondary);
  letter-spacing: 1px;
}

.time {
  font-size: 28px;
  font-weight: bold;
  font-family: var(--font-mono);
  color: var(--accent);
  text-shadow: 0 0 10px var(--accent-dim);
  animation: pulse-glow 2s ease-in-out infinite;
}

/* 右侧信息 */
.top-right {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 24px;
}

.weather-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.weather-icon {
  font-size: 22px;
}

.weather-temp {
  font-size: 16px;
  font-weight: bold;
  color: var(--accent);
}

.weather-humidity {
  font-size: 12px;
  color: var(--text-muted);
}

.device-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.online {
  background: var(--success);
  box-shadow: 0 0 6px var(--success);
}

.status-text {
  font-size: 12px;
  color: var(--text-secondary);
}

.status-count {
  font-size: 14px;
  font-weight: bold;
  color: var(--text-primary);
  font-family: var(--font-mono);
}

.status-percent {
  font-size: 12px;
  color: var(--success);
  font-weight: bold;
}
</style>
