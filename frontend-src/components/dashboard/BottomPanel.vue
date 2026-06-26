<template>
  <div class="bottom-panel panel">
    <div class="bottom-content">
      <!-- 今日统计 -->
      <div class="stats-section">
        <div class="panel-title" style="border-bottom: none; padding: 8px 12px; font-size: 12px;">今日统计</div>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="label">灌溉量</div>
            <div class="value number-glow">{{ statistics.irrigationVolume }}<span class="unit">L</span></div>
          </div>
          <div class="stat-card">
            <div class="label">施肥量</div>
            <div class="value number-glow">{{ statistics.fertilizerKg }}<span class="unit">kg</span></div>
          </div>
          <div class="stat-card">
            <div class="label">除害次数</div>
            <div class="value number-glow">{{ statistics.pestControlCount }}<span class="unit">次</span></div>
          </div>
          <div class="stat-card">
            <div class="label">通风时长</div>
            <div class="value number-glow">{{ statistics.ventilationMin }}<span class="unit">min</span></div>
          </div>
        </div>
      </div>

      <!-- 成熟度预测 -->
      <div class="maturity-section">
        <div class="panel-title" style="border-bottom: none; padding: 8px 12px; font-size: 12px;">成熟度预测</div>
        <div class="maturity-list">
          <div v-for="item in maturityPredictions" :key="item.crop" class="maturity-item">
            <div class="maturity-header">
              <span class="maturity-crop">{{ item.crop }}</span>
              <span class="maturity-variety">{{ item.variety }}</span>
              <span class="maturity-days" :style="{ color: item.color }">
                {{ item.daysLeft }}天
              </span>
            </div>
            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{
                  width: ((item.total - item.daysLeft) / item.total * 100) + '%',
                  background: item.color,
                  boxShadow: '0 0 8px ' + item.color,
                }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 历史产量 -->
      <div class="yield-section">
        <div class="panel-title" style="border-bottom: none; padding: 8px 12px; font-size: 12px;">历史产量对比</div>
        <div class="yield-chart" ref="yieldChart"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { useDashboardStore } from '@/stores/dashboard'
import { storeToRefs } from 'pinia'

const dashboard = useDashboardStore()
const { statistics, maturityPredictions, yieldHistory } = storeToRefs(dashboard)

const yieldChart = ref(null)
let chart = null

onMounted(() => {
  chart = echarts.init(yieldChart.value)
  chart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(13, 33, 55, 0.9)',
      borderColor: '#00d4ff',
      textStyle: { color: '#e0f0ff', fontSize: 11 },
    },
    legend: {
      data: ['实际产量', '目标产量'],
      right: 10,
      top: 0,
      textStyle: { color: '#8bb9e0', fontSize: 10 },
    },
    grid: { top: 30, right: 20, bottom: 25, left: 45 },
    xAxis: {
      type: 'category',
      data: yieldHistory.map(d => d.month),
      axisLine: { lineStyle: { color: '#5a8ab5' } },
      axisLabel: { color: '#5a8ab5', fontSize: 10 },
    },
    yAxis: {
      type: 'value',
      name: '吨',
      splitLine: { lineStyle: { color: 'rgba(90, 138, 181, 0.15)' } },
      axisLabel: { color: '#5a8ab5', fontSize: 9 },
    },
    series: [
      {
        name: '实际产量',
        type: 'bar',
        data: yieldHistory.map(d => d.yield),
        barWidth: 14,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#00d4ff' },
            { offset: 1, color: 'rgba(0, 212, 255, 0.2)' },
          ]),
          borderRadius: [4, 4, 0, 0],
        },
      },
      {
        name: '目标产量',
        type: 'bar',
        data: yieldHistory.map(d => d.target),
        barWidth: 14,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#ff9100' },
            { offset: 1, color: 'rgba(255, 145, 0, 0.2)' },
          ]),
          borderRadius: [4, 4, 0, 0],
          opacity: 0.6,
        },
      },
    ],
  })

  const resizeHandler = () => chart?.resize()
  window.addEventListener('resize', resizeHandler)
  onUnmounted(() => {
    chart?.dispose()
    window.removeEventListener('resize', resizeHandler)
  })
})
</script>

<style scoped>
.bottom-panel {
  height: 100%;
}

.bottom-content {
  display: flex;
  height: 100%;
}

/* 统计区域 */
.stats-section {
  flex: 0 0 28%;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 6px;
  padding: 6px 10px 10px;
  flex: 1;
}

/* 成熟度预测 */
.maturity-section {
  flex: 0 0 30%;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.maturity-list {
  padding: 6px 12px 10px;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
}

.maturity-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.maturity-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.maturity-crop {
  font-size: 12px;
  color: var(--text-primary);
  font-weight: bold;
}

.maturity-variety {
  font-size: 10px;
  color: var(--text-muted);
  flex: 1;
}

.maturity-days {
  font-size: 12px;
  font-weight: bold;
  font-family: var(--font-mono);
}

.progress-bar {
  height: 6px;
  background: rgba(90, 138, 181, 0.15);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 1s ease;
}

/* 产量图 */
.yield-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.yield-chart {
  flex: 1;
  min-height: 0;
  padding: 0 8px;
}
</style>
