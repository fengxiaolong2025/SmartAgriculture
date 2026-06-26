<template>
  <div class="center-map panel">
    <div class="panel-title">农场数字孪生地图</div>
    <div class="panel-body map-body">
      <canvas ref="mapCanvas" class="map-canvas"></canvas>
      <div
        v-for="plot in plots"
        :key="plot.id"
        class="plot-overlay"
        :class="{ 'plot-warning': plot.status === 'warning' }"
        :style="getPlotStyle(plot.id)"
        @click="selectPlot(plot)"
      >
        <div class="plot-header">
          <span class="plot-id">{{ plot.id }}</span>
          <span class="plot-crop">{{ plot.crop }}</span>
        </div>
        <div class="plot-data">
          <span class="plot-temp">{{ plot.temp.toFixed(1) }}°C</span>
          <span class="plot-humidity">{{ plot.humidity.toFixed(0) }}%</span>
        </div>
        <div class="plot-devices">
          <span class="device-icon" :class="{ active: plot.irrigating }" title="灌溉">💧</span>
          <span class="device-icon" :class="{ active: plot.fan }" title="风机">🌀</span>
        </div>
      </div>

      <!-- Tooltip -->
      <div v-if="selectedPlot" class="plot-tooltip" :style="tooltipStyle">
        <div class="tooltip-title">{{ selectedPlot.name }}</div>
        <div class="tooltip-row">温度：{{ selectedPlot.temp.toFixed(1) }}°C</div>
        <div class="tooltip-row">湿度：{{ selectedPlot.humidity.toFixed(0) }}%</div>
        <div class="tooltip-row">作物：{{ selectedPlot.crop }}</div>
        <div class="tooltip-row">灌溉：{{ selectedPlot.irrigating ? '开启' : '关闭' }}</div>
        <div class="tooltip-row">风机：{{ selectedPlot.fan ? '运行' : '停止' }}</div>
        <div class="tooltip-row">状态：{{ selectedPlot.status === 'warning' ? '⚠ 预警' : '✓ 正常' }}</div>
      </div>
    </div>

    <!-- 图例 -->
    <div class="legend">
      <span class="legend-item"><span class="legend-dot normal"></span> 正常</span>
      <span class="legend-item"><span class="legend-dot warning"></span> 预警</span>
      <span class="legend-item">💧 灌溉</span>
      <span class="legend-item">🌀 风机</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import { storeToRefs } from 'pinia'

const dashboard = useDashboardStore()
const { plots } = storeToRefs(dashboard)

const mapCanvas = ref(null)
const selectedPlot = ref(null)
const tooltipStyle = ref({})

// 地块布局 - 手动定义每个地块在 canvas 上的位置
const plotLayouts = {
  A1: { x: 40, y: 50, w: 180, h: 130 },
  A2: { x: 250, y: 50, w: 180, h: 130 },
  B1: { x: 40, y: 210, w: 180, h: 130 },
  B2: { x: 250, y: 210, w: 180, h: 130 },
  C1: { x: 460, y: 50, w: 170, h: 160 },
  C2: { x: 460, y: 230, w: 170, h: 160 },
  D1: { x: 660, y: 50, w: 170, h: 160 },
  D2: { x: 660, y: 230, w: 170, h: 160 },
}

function getPlotStyle(id) {
  const layout = plotLayouts[id]
  if (!layout) return {}
  return {
    left: layout.x + 'px',
    top: layout.y + 'px',
    width: layout.w + 'px',
    height: layout.h + 'px',
  }
}

function selectPlot(plot) {
  if (selectedPlot.value?.id === plot.id) {
    selectedPlot.value = null
    return
  }
  selectedPlot.value = plot
  const layout = plotLayouts[plot.id]
  tooltipStyle.value = {
    left: (layout.x + layout.w + 10) + 'px',
    top: layout.y + 'px',
  }
}

function drawMap() {
  const canvas = mapCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const dpr = window.devicePixelRatio || 1
  const rect = canvas.getBoundingClientRect()
  canvas.width = rect.width * dpr
  canvas.height = rect.height * dpr
  ctx.scale(dpr, dpr)

  const w = rect.width
  const h = rect.height

  // 背景网格
  ctx.strokeStyle = 'rgba(0, 212, 255, 0.08)'
  ctx.lineWidth = 0.5
  const gridSize = 40
  for (let x = 0; x < w; x += gridSize) {
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x, h)
    ctx.stroke()
  }
  for (let y = 0; y < h; y += gridSize) {
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(w, y)
    ctx.stroke()
  }

  // 绘制地块
  Object.values(plotLayouts).forEach((layout, i) => {
    const plot = plots[i]
    if (!plot) return

    const isWarning = plot.status === 'warning'

    // 填充
    ctx.fillStyle = isWarning
      ? 'rgba(255, 61, 79, 0.1)'
      : 'rgba(0, 212, 255, 0.05)'
    ctx.fillRect(layout.x, layout.y, layout.w, layout.h)

    // 边框
    ctx.strokeStyle = isWarning ? 'rgba(255, 61, 79, 0.5)' : 'rgba(0, 212, 255, 0.3)'
    ctx.lineWidth = 1
    ctx.strokeRect(layout.x, layout.y, layout.w, layout.h)

    // 角落装饰
    const cornerLen = 10
    ctx.strokeStyle = isWarning ? '#ff3d4f' : '#00d4ff'
    ctx.lineWidth = 1.5
    // 左上角
    ctx.beginPath()
    ctx.moveTo(layout.x, layout.y + cornerLen)
    ctx.lineTo(layout.x, layout.y)
    ctx.lineTo(layout.x + cornerLen, layout.y)
    ctx.stroke()
    // 右上角
    ctx.beginPath()
    ctx.moveTo(layout.x + layout.w - cornerLen, layout.y)
    ctx.lineTo(layout.x + layout.w, layout.y)
    ctx.lineTo(layout.x + layout.w, layout.y + cornerLen)
    ctx.stroke()
    // 左下角
    ctx.beginPath()
    ctx.moveTo(layout.x, layout.y + layout.h - cornerLen)
    ctx.lineTo(layout.x, layout.y + layout.h)
    ctx.lineTo(layout.x + cornerLen, layout.y + layout.h)
    ctx.stroke()
    // 右下角
    ctx.beginPath()
    ctx.moveTo(layout.x + layout.w - cornerLen, layout.y + layout.h)
    ctx.lineTo(layout.x + layout.w, layout.y + layout.h)
    ctx.lineTo(layout.x + layout.w, layout.y + layout.h - cornerLen)
    ctx.stroke()
  })
}

let resizeObserver = null

onMounted(() => {
  drawMap()
  resizeObserver = new ResizeObserver(() => {
    drawMap()
  })
  if (mapCanvas.value?.parentElement) {
    resizeObserver.observe(mapCanvas.value.parentElement)
  }
})

onUnmounted(() => {
  resizeObserver?.disconnect()
})
</script>

<style scoped>
.center-map {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.map-body {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.map-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.plot-overlay {
  position: absolute;
  cursor: pointer;
  border-radius: 3px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
  z-index: 2;
}

.plot-overlay:hover {
  background: rgba(0, 212, 255, 0.08);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
}

.plot-warning {
  animation: breathe 2s ease-in-out infinite;
}

.plot-header {
  display: flex;
  align-items: center;
  gap: 6px;
}

.plot-id {
  font-size: 12px;
  font-weight: bold;
  color: var(--accent);
  background: rgba(0, 212, 255, 0.15);
  padding: 1px 6px;
  border-radius: 2px;
}

.plot-crop {
  font-size: 10px;
  color: var(--text-muted);
}

.plot-data {
  display: flex;
  gap: 12px;
  font-size: 11px;
  font-family: var(--font-mono);
}

.plot-temp {
  color: #ff9100;
}

.plot-humidity {
  color: var(--accent);
}

.plot-devices {
  display: flex;
  gap: 10px;
}

.device-icon {
  font-size: 14px;
  opacity: 0.3;
  transition: all 0.3s;
}

.device-icon.active {
  opacity: 1;
  text-shadow: 0 0 6px currentColor;
}

.plot-tooltip {
  position: absolute;
  background: rgba(13, 33, 55, 0.95);
  border: 1px solid var(--accent);
  border-radius: 4px;
  padding: 10px 14px;
  z-index: 10;
  min-width: 160px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
}

.tooltip-title {
  font-size: 13px;
  font-weight: bold;
  color: var(--accent);
  margin-bottom: 6px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border-color);
}

.tooltip-row {
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.8;
}

.legend {
  display: flex;
  gap: 16px;
  padding: 8px 16px;
  border-top: 1px solid var(--border-color);
  background: rgba(0, 0, 0, 0.2);
}

.legend-item {
  font-size: 11px;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 4px;
}

.legend-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-dot.normal {
  background: var(--accent);
  box-shadow: 0 0 4px var(--accent);
}

.legend-dot.warning {
  background: var(--danger);
  box-shadow: 0 0 4px var(--danger);
}
</style>
