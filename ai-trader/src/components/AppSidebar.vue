<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const router = useRouter()
const store = useAppStore()

const mainLinks = [
  { path: '/dashboard', icon: 'ri-dashboard-3-line', label: '总览仪表盘' },
  { path: '/news', icon: 'ri-radar-line', label: '热点新闻' },
  { path: '/stocks', icon: 'ri-robot-2-line', label: 'AI交易模拟盘', badge: true },
  { path: '/simtrade', icon: 'ri-swap-line', label: '模拟交易' },
  { path: '/positions', icon: 'ri-briefcase-line', label: '交易持仓' },
]

const toolLinks = [
  { path: '/reports', icon: 'ri-bar-chart-2-line', label: '交易报表' },
  { path: '/settings', icon: 'ri-settings-4-line', label: '账户设置' },
]

const navigate = (path) => {
  router.push(path)
  store.sidebarOpen = false
}
</script>

<template>
  <aside
    class="fixed left-0 top-14 bottom-0 z-20 flex flex-col transition-transform duration-300"
    :class="store.sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
    style="width: 220px; background: rgb(30, 50, 84); border-right: 1px solid rgba(255,255,255,0.1)"
  >
    <nav class="flex-1 py-4 px-3 overflow-y-auto">
      <div class="px-2 mb-2">
        <span class="text-xs font-semibold uppercase tracking-widest" style="color: rgba(255,255,255,0.2)">主功能</span>
      </div>

      <a
        v-for="link in mainLinks"
        :key="link.path"
        class="flex items-center gap-3 px-4 py-3 rounded-xl mb-1 transition-all duration-200 cursor-pointer"
        :class="route.path === link.path ? 'active-link' : 'inactive-link'"
        @click="navigate(link.path)"
      >
        <div class="w-5 h-5 flex items-center justify-center">
          <i :class="link.icon" class="text-base"></i>
        </div>
        <span class="text-sm font-medium">{{ link.label }}</span>
        <span
          v-if="link.badge"
          class="ml-auto w-1.5 h-1.5 rounded-full"
          style="background: #f5a623"
        ></span>
      </a>

      <div class="px-2 mt-5 mb-2">
        <span class="text-xs font-semibold uppercase tracking-widest" style="color: rgba(255,255,255,0.2)">工具</span>
      </div>

      <a
        v-for="link in toolLinks"
        :key="link.path"
        class="flex items-center gap-3 px-4 py-3 rounded-xl mb-1 transition-all duration-200 cursor-pointer"
        :class="route.path === link.path ? 'active-link' : 'inactive-link'"
        @click="navigate(link.path)"
      >
        <div class="w-5 h-5 flex items-center justify-center">
          <i :class="link.icon" class="text-base"></i>
        </div>
        <span class="text-sm font-medium">{{ link.label }}</span>
      </a>
    </nav>

    <!-- AI 状态卡片 -->
    <div class="px-4 py-4" style="border-top: 1px solid rgba(255,255,255,0.08)">
      <div class="px-4 py-3 rounded-xl" style="background: rgba(245,166,35,0.1); border: 1px solid rgba(245,166,35,0.15)">
        <div class="flex items-center gap-2 mb-1">
          <span class="w-2 h-2 rounded-full" style="background: #64748b"></span>
          <span class="text-xs font-semibold" style="color: #94a3b8">AI 待命中</span>
        </div>
        <p class="text-xs" style="color: rgba(255,255,255,0.5)">
          今日 AI 决策 0 条<br />实际下单 0 笔
        </p>
        <p class="text-xs mt-1" style="color: #dc2626">浮盈 +¥33,213</p>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.active-link {
  background: rgba(245, 166, 35, 0.15);
  color: #f5a623;
}
.inactive-link {
  background: transparent;
  color: rgba(255, 255, 255, 0.6);
}
.inactive-link:hover {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.9);
}
</style>
