<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const router = useRouter()
const store = useAppStore()

const mainLinks = [
  { path: '/dashboard', icon: 'ri-dashboard-3-line', label: '总览仪表盘' },
  { path: '/news', icon: 'ri-radar-line', label: '热点新闻' },
  { path: '/stocks', icon: 'ri-line-chart-line', label: '行情概览' },
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
    class="fixed left-0 bottom-0 z-20 flex flex-col transition-transform duration-300"
    :class="store.sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
    style="width: var(--sidebar-width); top: var(--header-height); background: var(--color-bg-sidebar)"
  >
    <nav class="flex-1 py-6 px-3 overflow-y-auto">
      <div class="px-3 mb-3">
        <span class="text-[10px] font-semibold uppercase tracking-[0.15em]" style="color: rgba(255,255,255,0.25)">主功能</span>
      </div>

      <a
        v-for="link in mainLinks"
        :key="link.path"
        class="nav-link"
        :class="route.path === link.path ? 'nav-active' : ''"
        @click="navigate(link.path)"
      >
        <i :class="link.icon" class="text-lg shrink-0"></i>
        <span class="text-sm font-medium">{{ link.label }}</span>
      </a>

      <div class="px-3 mt-6 mb-3">
        <span class="text-[10px] font-semibold uppercase tracking-[0.15em]" style="color: rgba(255,255,255,0.25)">工具</span>
      </div>

      <a
        v-for="link in toolLinks"
        :key="link.path"
        class="nav-link"
        :class="route.path === link.path ? 'nav-active' : ''"
        @click="navigate(link.path)"
      >
        <i :class="link.icon" class="text-lg shrink-0"></i>
        <span class="text-sm font-medium">{{ link.label }}</span>
      </a>
    </nav>

    <!-- AI 状态卡片 -->
    <div class="p-4" style="border-top: 1px solid rgba(255,255,255,0.06)">
      <div class="rounded-2xl p-4 relative overflow-hidden" style="background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.15)">
        <div class="absolute -top-4 -right-4 w-20 h-20 rounded-full opacity-20" style="background: radial-gradient(circle, #6366f1 0%, transparent 70%)"></div>
        <div class="relative">
          <div class="flex items-center gap-2 mb-2">
            <div class="w-7 h-7 rounded-lg flex items-center justify-center gradient-primary">
              <i class="ri-robot-2-line text-sm text-white"></i>
            </div>
            <div>
              <p class="text-xs font-semibold text-white">AI 交易员</p>
              <div class="flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full animate-pulse" :style="{ background: store.marketStatus.isOpen ? '#34d399' : '#64748b' }"></span>
                <span class="text-[10px]" style="color: rgba(255,255,255,0.4)">{{ store.marketStatus.isOpen ? '运行中' : '待机中' }}</span>
              </div>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2 mt-3">
            <div class="rounded-lg px-2.5 py-2" style="background: rgba(255,255,255,0.03)">
              <p class="text-[10px]" style="color: rgba(255,255,255,0.4)">持仓</p>
              <p class="text-sm font-bold text-white tabular-nums">{{ store.account.position_count }} <span class="text-[10px] font-normal" style="color: rgba(255,255,255,0.4)">只</span></p>
            </div>
            <div class="rounded-lg px-2.5 py-2" style="background: rgba(255,255,255,0.03)">
              <p class="text-[10px]" style="color: rgba(255,255,255,0.4)">总收益</p>
              <p class="text-sm font-bold tabular-nums" :style="{ color: store.account.total_pnl >= 0 ? 'var(--color-up)' : 'var(--color-down)' }">
                {{ store.account.total_pnl >= 0 ? '+' : '' }}{{ store.account.total_pnl_pct }}%
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 16px;
  border-radius: var(--radius-md);
  margin-bottom: 4px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.55);
  transition: all 0.2s ease;
  position: relative;
}
.nav-link:hover {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.85);
}
.nav-active {
  background: rgba(99, 102, 241, 0.12);
  color: #a5b4fc;
}
.nav-active::before {
  content: '';
  position: absolute;
  left: -12px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  border-radius: 999px;
  background: var(--color-primary);
}
.nav-active i {
  color: var(--color-primary);
}
</style>
