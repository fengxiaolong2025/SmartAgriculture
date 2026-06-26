<template>
  <div class="left-panel">
    <!-- 仪表盘区域 -->
    <div class="panel gauges-section">
      <div class="panel-title">环境仪表盘</div>
      <div class="panel-body gauges-grid">
        <div class="gauge-item" ref="gaugeTemp"></div>
        <div class="gauge-item" ref="gaugeHumidity"></div>
        <div class="gauge-item" ref="gaugeLight"></div>
        <div class="gauge-item" ref="gaugeCO2"></div>
      </div>
    </div>

    <!-- 趋势图 -->
    <div class="panel trend-section">
      <div class="panel-title">24小时趋势</div>
      <div class="panel-body">
        <div class="trend-chart" ref="trendChart"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { useDashboardStore } from '@/stores/dashboard'
import { storeToRefs } from 'pinia'

const dashboard = useDashboardStore()
const { sensors, trendData } = storeToRefs(dashboard)

const gaugeTemp = ref(null)
const gaugeHumidity = ref(null)
const gaugeLight = ref(null)
const gaugeCO2 = ref(null)
const trendChart = ref(null)

let gaugeCharts = []
let lineChart = null
let resizeHandler = null

// 创建仪表盘
function createGauge(dom, name, value, max, unit) {
  const chart = echarts.init(dom)
  chart.setOption({
    series: [{
      type: 'gauge',
      radius: '85%',
      center: ['50%', '55%'],
      startAngle: 210,
      endAngle: -30,
      min: 0,
      max: max,
      splitNumber: 10,
      axisLine: {
        show: true,
        lineStyle: {
          width: 10,
          color: [
            [0.3, '#00e676'],
            [0.7, '#ffab00'],
            [1, '#ff3d4f'],
          ],
        },
      },
      pointer: {
        length: '60%',
        width: 4,
        itemStyle: { color: '#00d4ff' },
      },
      axisTick: {
        distance: -10,
        length: 6,
        lineStyle: { width: 1, color: '#5a8ab5' },
      },
      splitLine: {
        distance: -12,
        length: 12,
        lineStyle: { width: 2, color: '#5a8ab5' },
      },
      axisLabel: {
        color: '#5a8ab5',
        fontSize: 8,
        distance: 20,
      },
      anchor: {
        show: true,
        showAbove: true,
        size: 10,
        itemStyle: { borderWidth: 2, borderColor: '#00d4ff' },
      },
      title: {
        show: true,
        offsetCenter: [0, '75%'],
        fontSize: 10,
        color: '#8bb9e0',
      },
      detail: {
        valueAnimation: true,
        fontSize: 14,
        fontWeight: 'bold',
        offsetCenter: [0, '55%'],
        formatter: function (val) {
          return val.toFixed(1) + '\n' + unit
        },
        color: '#00d4ff',
      },
      data: [{ value: value, name: name }],
    }],
  })
  return chart
}

// 创建趋势图
function createTrendChart(dom) {
  const chart = echarts.init(dom)
  chart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(13, 33, 55, 0.9)',
      borderColor: '#00d4ff',
      textStyle: { color: '#e0f0ff', fontSize: 11 },
    },
    legend: {
      data: ['温度 °C', '湿度 %'],
      right: 10,
      top: 0,
      textStyle: { color: '#8bb9e0', fontSize: 10 },
    },
    grid: { top: 30, right: 20, bottom: 25, left: 40 },
    xAxis: {
      type: 'category',
      data: trendData.timestamps,
      axisLine: { lineStyle: { color: '#5a8ab5' } },
      axisLabel: { color: '#5a8ab5', fontSize: 9, rotate: 45 },
    },
    yAxis: [
      {
        type: 'value',
        name: '°C',
        min: 10,
        max: 40,
        splitLine: { lineStyle: { color: 'rgba(90, 138, 181, 0.15)' } },
        axisLabel: { color: '#5a8ab5', fontSize: 9 },
      },
      {
        type: 'value',
        name: '%',
        min: 30,
        max: 100,
        splitLine: { show: false },
        axisLabel: { color: '#5a8ab5', fontSize: 9 },
      },
    ],
    series: [
      {
        name: '温度 °C',
        type: 'line',
        data: trendData.temperatures,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#ff9100', width: 1.5 },
        itemStyle: { color: '#ff9100' },
      },
      {
        name: '湿度 %',
        type: 'line',
        yAxisIndex: 1,
        data: trendData.humidities,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#00d4ff', width: 1.5 },
        itemStyle: { color: '#00d4ff' },
      },
    ],
  })
  return chart
}

onMounted(() => {
  gaugeCharts = [
    createGauge(gaugeTemp.value, '空气温度', sensors.airTemp, 60, '°C'),
    createGauge(gaugeHumidity.value, '空气湿度', sensors.airHumidity, 100, '%'),
    createGauge(gaugeLight.value, '光照强度', sensors.lightIntensity, 120000, 'Lux'),
    createGauge(gaugeCO2.value, 'CO₂浓度', sensors.co2, 1000, 'ppm'),
  ]

  lineChart = createTrendChart(trendChart.value)

  resizeHandler = () => {
    gaugeCharts.forEach(c => c.resize())
    lineChart?.resize()
  }
  window.addEventListener('resize', resizeHandler)
})

onUnmounted(() => {
  gaugeCharts.forEach(c => c.dispose())
  lineChart?.dispose()
  window.removeEventListener('resize', resizeHandler)
})

// 监听传感器数据变化，更新仪表盘
watch(() => sensors.airTemp, (v) => {
  gaugeCharts[0]?.setOption({ series: [{ data: [{ value: v }] }] })
})
watch(() => sensors.airHumidity, (v) => {
  gaugeCharts[1]?.setOption({ series: [{ data: [{ value: v }] }] })
})
watch(() => sensors.lightIntensity, (v) => {
  gaugeCharts[2]?.setOption({ series: [{ data: [{ value: v }] }] })
})
watch(() => sensors.co2, (v) => {
  gaugeCharts[3]?.setOption({ series: [{ data: [{ value: v }] }] })
})

// 监听趋势数据变化
watch(() => trendData.timestamps.length, () => {
  lineChart?.setOption({
    xAxis: { data: [...trendData.timestamps] },
    series: [
      { data: [...trendData.temperatures] },
      { data: [...trendData.humidities] },
    ],
  })
})
</script>

<style scoped>
.left-panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
  height: 100%;
}

.gauges-section {
  flex: 0 0 48%;
}

.gauges-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 4px;
  height: calc(100% - 40px);
}

.gauge-item {
  min-height: 0;
}

.trend-section {
  flex: 1;
}

.trend-chart {
  height: 100%;
  min-height: 150px;
}
</style>
