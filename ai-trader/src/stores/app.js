import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 用户信息
  const user = ref({
    phone: '181****8452',
    fullPhone: '18138018452',
    avatar: '1',
    subscription: {
      status: 'active',
      expireDate: '2026-12-01',
      plan: 'quarterly',
    },
  })

  // 市场指数
  const marketIndices = ref([
    { name: '上证指数', value: '4,090.481', change: '-0.43%', direction: 'down' },
    { name: '深证成指', value: '16,030.702', change: '+0.94%', direction: 'up' },
    { name: '创业板指', value: '4,252.39', change: '+2.05%', direction: 'up' },
  ])

  // 市场状态
  const marketStatus = ref({
    isOpen: false,
    label: '今日已收盘',
    dateLabel: '2026年6月19日星期五',
    statusLabel: '非交易日 · AI 暂停',
  })

  // 账户资产
  const account = ref({
    totalAssets: 1081219.97,
    initialCapital: 1000000,
    totalPnl: 81220,
    totalPnlPercent: 8.12,
    realizedPnl: 50804,
    unrealizedPnl: 33213,
    positionCount: 4,
    positionUsage: 52,
    todayChange: 0,
    todayChangePercent: 0,
  })

  // 持仓列表
  const holdings = ref([
    { code: '600487', name: '亨通光电', qty: 4000, cost: 14.18, price: 14.04, pnl: -560, pnlPercent: -0.99, weight: 26 },
    { code: '688041', name: '海光信息', qty: 2000, cost: 88.50, price: 97.40, pnl: 17800, pnlPercent: 10.06, weight: 17 },
    { code: '600522', name: '中天科技', qty: 5000, cost: 15.32, price: 15.91, pnl: 2950, pnlPercent: 3.85, weight: 28 },
    { code: '002384', name: '东山精密', qty: 3000, cost: 14.38, price: 16.36, pnl: 5940, pnlPercent: 13.75, weight: 29 },
  ])

  // 侧边栏状态
  const sidebarOpen = ref(false)

  // AI 对话框状态
  const aiChatOpen = ref(false)

  // 计算属性
  const isLoggedIn = computed(() => !!user.value)

  return {
    user,
    marketIndices,
    marketStatus,
    account,
    holdings,
    sidebarOpen,
    aiChatOpen,
    isLoggedIn,
  }
})
