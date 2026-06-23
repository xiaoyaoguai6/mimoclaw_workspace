import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useAppStore = defineStore('app', () => {
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

  const marketIndices = ref([])
  const marketStatus = ref({
    isOpen: false,
    label: '加载中…',
    dateLabel: '',
    statusLabel: '',
  })

  const account = ref({
    initial_capital: 1000000,
    available_cash: 1000000,
    total_market_value: 0,
    total_assets: 1000000,
    total_pnl: 0,
    total_pnl_pct: 0,
    unrealized_pnl: 0,
    realized_pnl: 0,
    today_pnl: 0,
    position_count: 0,
    position_usage: 0,
  })

  const holdings = ref([])

  const sidebarOpen = ref(false)
  const aiChatOpen = ref(false)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!user.value)

  async function fetchMarketStatus() {
    try {
      marketStatus.value = await api.getMarketStatus()
    } catch (e) {
      console.error('fetchMarketStatus:', e)
    }
  }

  async function fetchMarketIndices() {
    try {
      marketIndices.value = await api.getMarketIndices()
    } catch (e) {
      console.error('fetchMarketIndices:', e)
    }
  }

  async function fetchAccount() {
    try {
      const data = await api.getAccount()
      account.value = data
      holdings.value = data.holdings || []
    } catch (e) {
      console.error('fetchAccount:', e)
    }
  }

  async function fetchAll() {
    loading.value = true
    await Promise.allSettled([
      fetchMarketStatus(),
      fetchMarketIndices(),
      fetchAccount(),
    ])
    loading.value = false
  }

  async function executeTrade({ code, name, action, qty, price }) {
    const result = await api.executeTrade({ code, name, action, qty, price })
    if (result.account) {
      account.value = result.account
      holdings.value = result.account.holdings || []
    }
    return result
  }

  async function resetAccount() {
    const result = await api.resetAccount()
    if (result.account) {
      account.value = result.account
      holdings.value = result.account.holdings || []
    }
    return result
  }

  return {
    user,
    marketIndices,
    marketStatus,
    account,
    holdings,
    sidebarOpen,
    aiChatOpen,
    loading,
    isLoggedIn,
    fetchMarketStatus,
    fetchMarketIndices,
    fetchAccount,
    fetchAll,
    executeTrade,
    resetAccount,
  }
})
