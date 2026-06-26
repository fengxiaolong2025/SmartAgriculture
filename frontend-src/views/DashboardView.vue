<template>
  <div class="dashboard">
    <div class="area area-top">
      <TopBar />
    </div>
    <div class="area area-left">
      <LeftPanel />
    </div>
    <div class="area area-center">
      <CenterMap />
    </div>
    <div class="area area-right">
      <RightPanel />
    </div>
    <div class="area area-bottom">
      <BottomPanel />
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import TopBar from '@/components/dashboard/TopBar.vue'
import LeftPanel from '@/components/dashboard/LeftPanel.vue'
import CenterMap from '@/components/dashboard/CenterMap.vue'
import RightPanel from '@/components/dashboard/RightPanel.vue'
import BottomPanel from '@/components/dashboard/BottomPanel.vue'
import { startSimulation, stopSimulation } from '@/mock/data.js'

const dashboard = useDashboardStore()

onMounted(async () => {
  await dashboard.fetchAll()
  startSimulation()
  dashboard.startPolling(3000)
})

onUnmounted(() => {
  stopSimulation()
  dashboard.stopPolling()
})
</script>

<style scoped>
.dashboard {
  width: 100vw;
  height: 100vh;
  display: grid;
  grid-template-columns: 22% 1fr 22%;
  grid-template-rows: 60px 1fr 20%;
  grid-template-areas:
    "top top top"
    "left center right"
    "bottom bottom bottom";
  gap: 0;
  background: var(--bg-primary);
}

.area-top {
  grid-area: top;
}

.area-left {
  grid-area: left;
  overflow: hidden;
  padding: 8px;
}

.area-center {
  grid-area: center;
  overflow: hidden;
  padding: 8px 0;
}

.area-right {
  grid-area: right;
  overflow: hidden;
  padding: 8px;
}

.area-bottom {
  grid-area: bottom;
  overflow: hidden;
  padding: 0 8px 8px;
}
</style>
