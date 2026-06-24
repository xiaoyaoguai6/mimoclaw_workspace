<script setup>
import { ref, computed, onMounted } from 'vue'
import RiskBanner from '@/components/RiskBanner.vue'
import { useAppStore } from '@/stores/app'
import api from '@/api'

const store = useAppStore()
const activeTab = ref('current')
const riskExpanded = ref(true)

const tradeHistory = ref([])

onMounted(async () => {
  store.fetchAccount()
  try {
    tradeHistory.value = await api.getTradeHistory(50)
  } catch (e) {
    console.error(e)
  }
})

const fmt = (v) => v.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const summaryStats = computed(() => {
  const a = store.account
  return [
    { label: '今日盈亏', value: `${a.today_pnl >= 0 ? '+' : ''}¥${fmt(a.today_pnl)}`, color: a.today_pnl >= 0 ? '#dc2626' : '#16a34a' },
    { label: '累计收益率', value: `${a.total_pnl_pct >= 0 ? '+' : ''}${a.total_pnl_pct}%`, color: a.total_pnl_pct >= 0 ? '#dc2626' : '#16a34a' },
    { label: '总浮动盈亏', value: `${a.unrealized_pnl >= 0 ? '+' : ''}¥${fmt(a.unrealized_pnl)}`, color: a.unrealized_pnl >= 0 ? '#dc2626' : '#16a34a' },
    { label: '可用资金', value: `¥${fmt(a.available_cash)}`, color: '#0f172a' },
  ]
})

const positions = computed(() => {
  return store.holdings.map(h => ({
    code: h.code,
    name: h.name,
    shares: `${h.qty.toLocaleString()} 股`,
    costAvg: `¥${h.cost_avg}`,
    current: `¥${h.current_price}`,
    costTotal: `¥${fmt(h.cost_total)}`,
    marketValue: `¥${fmt(h.market_value)}`,
    pnl: `${h.pnl >= 0 ? '+' : ''}¥${fmt(h.pnl)}`,
    pnlPct: `${h.pnl_pct >= 0 ? '+' : ''}${h.pnl_pct}%`,
    pnlRaw: h.pnl,
    pnlPctRaw: h.pnl_pct,
    changePct: h.change_pct,
    builtDate: (h.built_at || '').slice(5, 10).replace('-', '/'),
    aiStatus: '持有中',
    aiSub: '',
    aiStatusColor: '#16a34a',
  }))
})

const totals = computed(() => {
  const a = store.account
  return {
    costTotal: `¥${fmt(store.holdings.reduce((s, h) => s + h.cost_total, 0))}`,
    marketValue: `¥${fmt(a.total_market_value)}`,
    pnl: `${a.unrealized_pnl >= 0 ? '+' : ''}¥${fmt(a.unrealized_pnl)}`,
    pnlPct: store.holdings.length
      ? `${(store.holdings.reduce((s, h) => s + h.pnl_pct, 0) / store.holdings.length).toFixed(2)}%`
      : '0.00%',
  }
})

const riskConcentration = computed(() => {
  const total = store.account.total_market_value || 1
  return store.holdings
    .map(h => ({
      name: h.name,
      pct: (h.market_value / total * 100).toFixed(1),
      color: h.market_value / total * 100 > 50 ? '#d97706' : '#f59e0b',
    }))
    .sort((a, b) => parseFloat(b.pct) - parseFloat(a.pct))
})

const maxSinglePosition = computed(() => {
  if (!riskConcentration.value.length) return '0.0%'
  return riskConcentration.value[0].pct + '%'
})

const drawdownMin = computed(() => {
  if (!store.holdings.length) return null
  const min = store.holdings.reduce((m, h) => h.pnl_pct < m.pnl_pct ? h : m, store.holdings[0])
  return {
    name: min.name,
    pct: `${min.pnl_pct >= 0 ? '+' : ''}${min.pnl_pct}%`,
    profit: `${min.pnl >= 0 ? '盈利' : '亏损'} ¥${fmt(Math.abs(min.pnl))}`,
    status: '持有中',
  }
})

const fmtHistory = (h) => {
  const d = new Date(h.ts)
  return `${(d.getMonth()+1).toString().padStart(2,'0')}/${d.getDate().toString().padStart(2,'0')} ${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`
}
</script>

<template>
  <div class="max-w-screen-xl animate-fade-in">
    <RiskBanner />

    <!-- 顶部统计 -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div v-for="stat in summaryStats" :key="stat.label" class="card p-5">
        <p class="text-xs" style="color: var(--color-text-muted)">{{ stat.label }}</p>
        <p class="text-2xl font-bold mt-1.5 tabular-nums" :style="{ color: stat.color }">{{ stat.value }}</p>
      </div>
    </div>

    <!-- 整体风险评估 -->
    <div v-if="positions.length" class="card mb-6 overflow-hidden">
      <button
        class="w-full flex items-center justify-between px-5 py-4 cursor-pointer transition-colors hover:bg-slate-50"
        @click="riskExpanded = !riskExpanded"
      >
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center" :style="{ background: parseFloat(maxSinglePosition) > 50 ? 'var(--color-danger-light)' : 'var(--color-success-light)' }">
            <i class="ri-alarm-warning-line text-lg" :style="{ color: parseFloat(maxSinglePosition) > 50 ? 'var(--color-danger)' : 'var(--color-success)' }"></i>
          </div>
          <div class="text-left">
            <p class="text-sm font-bold" style="color: var(--color-text-primary)">整体风险评估</p>
            <p class="text-xs mt-0.5" style="color: var(--color-text-muted)">基于当前 {{ positions.length }} 只持仓的综合风险分析</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <span class="badge" :style="{
            background: parseFloat(maxSinglePosition) > 50 ? 'var(--color-danger-light)' : 'var(--color-success-light)',
            color: parseFloat(maxSinglePosition) > 50 ? 'var(--color-danger)' : 'var(--color-success)',
          }">
            {{ parseFloat(maxSinglePosition) > 50 ? '高风险' : '低风险' }}
          </span>
          <i class="ri-arrow-up-s-line text-base transition-transform duration-200" :style="{ color: 'var(--color-text-muted)', transform: riskExpanded ? 'rotate(0deg)' : 'rotate(180deg)' }"></i>
        </div>
      </button>

      <Transition name="expand">
        <div v-if="riskExpanded" class="px-5 py-5" style="border-top: 1px solid var(--color-border-light)">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
            <!-- 仓位集中度 -->
            <div class="rounded-xl p-5" style="background: var(--color-border-light)">
              <div class="flex items-center gap-2 mb-4">
                <div class="w-7 h-7 rounded-lg flex items-center justify-center" style="background: var(--color-primary-light)">
                  <i class="ri-pie-chart-2-line text-sm" style="color: var(--color-primary)"></i>
                </div>
                <span class="text-sm font-semibold" style="color: var(--color-text-primary)">仓位集中度</span>
              </div>
              <div class="mb-3 space-y-3">
                <div v-for="item in riskConcentration.slice(0, 5)" :key="item.name">
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-xs" style="color: var(--color-text-secondary)">{{ item.name }}</span>
                    <span class="text-xs font-bold tabular-nums" :style="{ color: parseFloat(item.pct) > 50 ? 'var(--color-warning)' : 'var(--color-text-primary)' }">{{ item.pct }}%</span>
                  </div>
                  <div class="h-2 rounded-full" style="background: #e2e8f0">
                    <div class="h-full rounded-full transition-all" :style="{ width: item.pct + '%', background: item.color }"></div>
                  </div>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-3 pt-3" style="border-top: 1px solid var(--color-border)">
                <div>
                  <p class="text-xs" style="color: var(--color-text-muted)">最大单仓</p>
                  <p class="text-base font-bold mt-0.5 tabular-nums" :style="{ color: parseFloat(maxSinglePosition) > 50 ? 'var(--color-danger)' : 'var(--color-text-primary)' }">{{ maxSinglePosition }}</p>
                </div>
                <div>
                  <p class="text-xs" style="color: var(--color-text-muted)">持仓数</p>
                  <p class="text-base font-bold mt-0.5" style="color: var(--color-text-primary)">{{ positions.length }} 只</p>
                </div>
              </div>
            </div>

            <!-- 最大回撤风险 -->
            <div class="rounded-xl p-5" style="background: var(--color-border-light)">
              <div class="flex items-center gap-2 mb-4">
                <div class="w-7 h-7 rounded-lg flex items-center justify-center" style="background: var(--color-danger-light)">
                  <i class="ri-arrow-down-double-line text-sm" style="color: var(--color-danger)"></i>
                </div>
                <span class="text-sm font-semibold" style="color: var(--color-text-primary)">盈亏分布</span>
              </div>
              <div v-if="drawdownMin" class="text-center mb-4">
                <p class="text-3xl font-black tabular-nums" :style="{ color: parseFloat(drawdownMin.pct) >= 0 ? 'var(--color-up)' : 'var(--color-down)' }">{{ drawdownMin.pct }}</p>
                <p class="text-xs mt-1" style="color: var(--color-text-muted)">最小单仓盈亏率</p>
              </div>
              <div v-if="drawdownMin" class="rounded-lg p-3" style="background: var(--color-bg-card); border: 1px solid var(--color-border)">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-semibold" style="color: var(--color-text-primary)">{{ drawdownMin.name }}</span>
                  <span class="text-xs font-semibold tabular-nums" :style="{ color: parseFloat(drawdownMin.pct) >= 0 ? 'var(--color-up)' : 'var(--color-down)' }">{{ drawdownMin.pct }}</span>
                </div>
                <p class="text-xs mt-1" style="color: var(--color-text-muted)">{{ drawdownMin.profit }}</p>
              </div>
            </div>

            <!-- 持仓盈亏 -->
            <div class="rounded-xl p-5" style="background: var(--color-border-light)">
              <div class="flex items-center gap-2 mb-4">
                <div class="w-7 h-7 rounded-lg flex items-center justify-center" style="background: rgba(100,116,139,0.1)">
                  <i class="ri-price-tag-3-line text-sm" style="color: var(--color-text-secondary)"></i>
                </div>
                <span class="text-sm font-semibold" style="color: var(--color-text-primary)">持仓明细</span>
              </div>
              <div class="space-y-3">
                <div v-for="p in positions" :key="p.code">
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-xs font-medium" style="color: var(--color-text-secondary)">{{ p.name }}</span>
                    <span class="text-xs font-bold tabular-nums" :style="{ color: p.pnlPctRaw >= 0 ? 'var(--color-up)' : 'var(--color-down)' }">{{ p.pnlPct }}</span>
                  </div>
                  <div class="flex items-center gap-1.5 text-xs" style="color: var(--color-text-muted)">
                    <span class="tabular-nums">{{ p.current }}</span><span>→</span><span class="tabular-nums">{{ p.costAvg }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>

    <!-- 标签切换 -->
    <div class="flex gap-1 p-1 rounded-xl w-fit mb-6" style="background: var(--color-border-light)">
      <button
        class="px-5 py-2 rounded-lg text-sm font-medium cursor-pointer whitespace-nowrap transition-all"
        :style="activeTab === 'current'
          ? { background: 'var(--color-bg-card)', color: 'var(--color-primary)', boxShadow: 'var(--shadow-sm)' }
          : { background: 'transparent', color: 'var(--color-text-muted)' }"
        @click="activeTab = 'current'"
      >当前持仓</button>
      <button
        class="px-5 py-2 rounded-lg text-sm font-medium cursor-pointer whitespace-nowrap transition-all"
        :style="activeTab === 'history'
          ? { background: 'var(--color-bg-card)', color: 'var(--color-primary)', boxShadow: 'var(--shadow-sm)' }
          : { background: 'transparent', color: 'var(--color-text-muted)' }"
        @click="activeTab = 'history'"
      >历史交易</button>
    </div>

    <!-- 当前持仓表格 -->
    <div v-if="activeTab === 'current'" class="card overflow-hidden">
      <div v-if="positions.length" class="overflow-x-auto">
        <table class="modern-table">
          <thead>
            <tr>
              <th>股票</th>
              <th>持仓股数</th>
              <th>成本均价</th>
              <th>现价</th>
              <th>持仓成本</th>
              <th>持仓市值</th>
              <th>浮动盈亏</th>
              <th>盈亏率</th>
              <th>今日涨跌</th>
              <th>建仓时间</th>
              <th>AI状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pos in positions" :key="pos.code">
              <td>
                <div class="font-semibold" style="color: var(--color-text-primary)">{{ pos.name }}</div>
                <div class="text-xs mt-0.5 font-mono" style="color: var(--color-text-muted)">{{ pos.code }}</div>
              </td>
              <td style="color: var(--color-text-secondary)" class="tabular-nums">{{ pos.shares }}</td>
              <td style="color: var(--color-text-muted)" class="tabular-nums">{{ pos.costAvg }}</td>
              <td class="font-semibold tabular-nums" style="color: var(--color-text-primary)">{{ pos.current }}</td>
              <td style="color: var(--color-text-muted)" class="tabular-nums whitespace-nowrap">{{ pos.costTotal }}</td>
              <td class="font-semibold tabular-nums whitespace-nowrap" style="color: var(--color-text-primary)">{{ pos.marketValue }}</td>
              <td>
                <span class="font-semibold whitespace-nowrap tabular-nums" :style="{ color: pos.pnlRaw >= 0 ? 'var(--color-up)' : 'var(--color-down)' }">{{ pos.pnl }}</span>
              </td>
              <td>
                <span class="font-semibold whitespace-nowrap tabular-nums" :style="{ color: pos.pnlPctRaw >= 0 ? 'var(--color-up)' : 'var(--color-down)' }">{{ pos.pnlPct }}</span>
              </td>
              <td>
                <span class="font-semibold whitespace-nowrap tabular-nums" :style="{ color: pos.changePct >= 0 ? 'var(--color-up)' : 'var(--color-down)' }">
                  {{ pos.changePct >= 0 ? '+' : '' }}{{ pos.changePct }}%
                </span>
              </td>
              <td class="text-xs tabular-nums" style="color: var(--color-text-muted)">{{ pos.builtDate }}</td>
              <td>
                <span class="badge" style="background: var(--color-success-light); color: var(--color-success)">{{ pos.aiStatus }}</span>
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr style="background: #f8fafc; font-weight: bold">
              <td colspan="4" class="px-4 py-3.5 text-sm" style="color: var(--color-text-primary)">合计</td>
              <td class="px-4 py-3.5 text-sm tabular-nums whitespace-nowrap" style="color: var(--color-text-secondary)">{{ totals.costTotal }}</td>
              <td class="px-4 py-3.5 text-sm tabular-nums whitespace-nowrap" style="color: var(--color-text-primary)">{{ totals.marketValue }}</td>
              <td class="px-4 py-3.5"><span class="font-bold text-sm tabular-nums whitespace-nowrap" :style="{ color: store.account.unrealized_pnl >= 0 ? 'var(--color-up)' : 'var(--color-down)' }">{{ totals.pnl }}</span></td>
              <td class="px-4 py-3.5"><span class="font-bold text-sm tabular-nums whitespace-nowrap" :style="{ color: store.account.unrealized_pnl >= 0 ? 'var(--color-up)' : 'var(--color-down)' }">{{ totals.pnlPct }}</span></td>
              <td colspan="3"></td>
            </tr>
          </tfoot>
        </table>
      </div>
      <div v-else class="p-16 text-center">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4" style="background: var(--color-border-light)">
          <i class="ri-inbox-line text-3xl" style="color: var(--color-text-faint)"></i>
        </div>
        <p class="text-sm" style="color: var(--color-text-muted)">暂无持仓</p>
        <router-link to="/simtrade" class="inline-block mt-3 text-sm font-medium" style="color: var(--color-primary)">去模拟交易建仓 →</router-link>
      </div>
      <div v-if="positions.length" class="px-5 py-3 flex items-center gap-2" style="border-top: 1px solid var(--color-border-light); background: #f8fafc">
        <i class="ri-information-line text-xs" style="color: var(--color-primary)"></i>
        <span class="text-xs" style="color: var(--color-text-muted)">持仓数据实时同步，现价来自腾讯财经实时行情</span>
      </div>
    </div>

    <!-- 历史交易 -->
    <div v-else class="card overflow-hidden">
      <div v-if="tradeHistory.length" class="overflow-x-auto">
        <table class="modern-table">
          <thead>
            <tr>
              <th>时间</th><th>股票</th><th>方向</th><th>数量</th><th>价格</th><th>金额</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in tradeHistory" :key="t.id">
              <td class="text-xs whitespace-nowrap tabular-nums" style="color: var(--color-text-muted)">{{ fmtHistory(t) }}</td>
              <td>
                <div class="font-semibold text-sm" style="color: var(--color-text-primary)">{{ t.name }}</div>
                <div class="text-xs font-mono" style="color: var(--color-text-muted)">{{ t.code }}</div>
              </td>
              <td>
                <span class="badge" :style="{
                  background: t.action === 'buy' ? 'var(--color-success-light)' : 'var(--color-danger-light)',
                  color: t.action === 'buy' ? 'var(--color-success)' : 'var(--color-danger)',
                }">{{ t.action === 'buy' ? '买入' : '卖出' }}</span>
              </td>
              <td class="tabular-nums" style="color: var(--color-text-secondary)">{{ t.qty.toLocaleString() }} 股</td>
              <td class="tabular-nums" style="color: var(--color-text-secondary)">¥{{ t.price }}</td>
              <td class="font-semibold tabular-nums" style="color: var(--color-text-primary)">¥{{ fmt(t.amount) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="p-16 text-center">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4" style="background: var(--color-border-light)">
          <i class="ri-history-line text-3xl" style="color: var(--color-text-faint)"></i>
        </div>
        <p class="text-sm" style="color: var(--color-text-muted)">暂无历史交易记录</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}
.expand-enter-from,
.expand-leave-to {
  opacity: 0;
}
</style>
