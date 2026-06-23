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
  <div class="max-w-screen-xl">
    <RiskBanner />

    <!-- 顶部统计 -->
    <div class="flex items-center justify-between mb-5">
      <div></div>
      <div class="flex items-center gap-3">
        <div
          v-for="stat in summaryStats"
          :key="stat.label"
          class="text-right"
          :class="stat !== summaryStats[summaryStats.length - 1] ? 'pr-3' : ''"
          :style="stat !== summaryStats[summaryStats.length - 1] ? { borderRight: '1px solid #e2e8f0' } : {}"
        >
          <p class="text-xs" style="color: #94a3b8">{{ stat.label }}</p>
          <p class="text-lg font-bold" :style="{ color: stat.color }">{{ stat.value }}</p>
        </div>
      </div>
    </div>

    <!-- 整体风险评估 -->
    <div v-if="positions.length" class="rounded-xl mb-5 overflow-hidden" style="background: #fff; border: 1px solid #e2e8f0">
      <button
        class="w-full flex items-center justify-between px-5 py-3.5 cursor-pointer"
        style="border-bottom: 1px solid #f1f5f9"
        @click="riskExpanded = !riskExpanded"
      >
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 flex items-center justify-center rounded-lg" style="background: rgba(220,38,38,0.08); border: 1px solid rgba(220,38,38,0.2)">
            <i class="ri-alarm-warning-line text-sm" style="color: #dc2626"></i>
          </div>
          <div class="text-left">
            <p class="text-sm font-bold" style="color: #0f172a">整体风险评估</p>
            <p class="text-xs" style="color: #94a3b8">基于当前 {{ positions.length }} 只持仓的综合风险分析</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <span class="px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap" :style="{
            background: parseFloat(maxSinglePosition) > 50 ? 'rgba(220,38,38,0.08)' : 'rgba(22,163,74,0.08)',
            color: parseFloat(maxSinglePosition) > 50 ? '#dc2626' : '#16a34a',
            border: `1px solid ${parseFloat(maxSinglePosition) > 50 ? 'rgba(220,38,38,0.2)' : 'rgba(22,163,74,0.2)'}`,
          }">
            <i class="ri-alarm-warning-line mr-1"></i>{{ parseFloat(maxSinglePosition) > 50 ? '高' : '低' }}风险
          </span>
          <i class="ri-arrow-up-s-line text-sm transition-transform duration-200" :style="{ color: '#94a3b8', transform: riskExpanded ? 'rotate(0deg)' : 'rotate(180deg)' }"></i>
        </div>
      </button>

      <Transition name="expand">
        <div v-if="riskExpanded" class="px-5 py-4">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
            <!-- 仓位集中度 -->
            <div class="rounded-xl p-4" style="background: #f8fafc; border: 1px solid #f1f5f9">
              <div class="flex items-center gap-2 mb-3">
                <div class="w-6 h-6 flex items-center justify-center rounded" style="background: rgba(245,166,35,0.1)">
                  <i class="ri-pie-chart-2-line text-xs" style="color: #d97706"></i>
                </div>
                <span class="text-xs font-semibold" style="color: #334155">仓位集中度</span>
              </div>
              <div class="mb-3 space-y-2">
                <div v-for="item in riskConcentration.slice(0, 5)" :key="item.name">
                  <div class="flex items-center justify-between mb-0.5">
                    <span class="text-xs" style="color: #64748b">{{ item.name }}</span>
                    <span class="text-xs font-semibold" :style="{ color: parseFloat(item.pct) > 50 ? '#d97706' : '#334155' }">{{ item.pct }}%</span>
                  </div>
                  <div class="h-1.5 rounded-full" style="background: #e2e8f0">
                    <div class="h-full rounded-full" :style="{ width: item.pct + '%', background: item.color }"></div>
                  </div>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-2 pt-2" style="border-top: 1px solid #e2e8f0">
                <div>
                  <p class="text-xs" style="color: #94a3b8">最大单仓</p>
                  <p class="text-sm font-bold mt-0.5" :style="{ color: parseFloat(maxSinglePosition) > 50 ? '#dc2626' : '#334155' }">{{ maxSinglePosition }}</p>
                </div>
                <div>
                  <p class="text-xs" style="color: #94a3b8">持仓数</p>
                  <p class="text-sm font-bold mt-0.5" style="color: #334155">{{ positions.length }} 只</p>
                </div>
              </div>
            </div>

            <!-- 最大回撤风险 -->
            <div class="rounded-xl p-4" style="background: #f8fafc; border: 1px solid #f1f5f9">
              <div class="flex items-center gap-2 mb-3">
                <div class="w-6 h-6 flex items-center justify-center rounded" style="background: rgba(220,38,38,0.08)">
                  <i class="ri-arrow-down-double-line text-xs" style="color: #dc2626"></i>
                </div>
                <span class="text-xs font-semibold" style="color: #334155">最大回撤风险</span>
              </div>
              <div class="relative mb-4">
                <div class="flex justify-between text-xs mb-1" style="color: #94a3b8">
                  <span>0%</span><span>-5%</span><span>-10%</span>
                </div>
                <div class="h-2 rounded-full" style="background: linear-gradient(to right, #22c55e, #f59e0b, #dc2626)">
                  <div
                    class="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full border-2 border-white"
                    :style="{
                      left: drawdownMin ? Math.min(Math.abs(drawdownMin.pct.replace('+','')) / 10 * 100, 100) + '%' : '0%',
                      background: drawdownMin && parseFloat(drawdownMin.pct) >= 0 ? '#22c55e' : '#dc2626',
                      marginTop: '4px',
                    }"
                  ></div>
                </div>
              </div>
              <div class="text-center mb-3" v-if="drawdownMin">
                <p class="text-2xl font-bold" :style="{ color: parseFloat(drawdownMin.pct) >= 0 ? '#dc2626' : '#16a34a' }">{{ drawdownMin.pct }}</p>
                <p class="text-xs mt-0.5" style="color: #94a3b8">最小单仓盈亏率</p>
              </div>
              <div v-if="drawdownMin" class="rounded-lg p-2.5" style="background: #f8fafc; border: 1px solid #f1f5f9">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-semibold" style="color: #334155">{{ drawdownMin.name }}</span>
                  <span class="text-xs font-semibold" :style="{ color: parseFloat(drawdownMin.pct) >= 0 ? '#dc2626' : '#16a34a' }">{{ drawdownMin.pct }}</span>
                </div>
                <p class="text-xs mt-1" style="color: #94a3b8">{{ drawdownMin.profit }} · AI状态：{{ drawdownMin.status }}</p>
              </div>
            </div>

            <!-- 止损距离 -->
            <div class="rounded-xl p-4" style="background: #f8fafc; border: 1px solid #f1f5f9">
              <div class="flex items-center gap-2 mb-3">
                <div class="w-6 h-6 flex items-center justify-center rounded" style="background: rgba(100,116,139,0.1)">
                  <i class="ri-price-tag-3-line text-xs" style="color: #64748b"></i>
                </div>
                <span class="text-xs font-semibold" style="color: #334155">持仓盈亏分布</span>
              </div>
              <div class="space-y-3 mb-3">
                <div v-for="p in positions" :key="p.code">
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-xs" style="color: #64748b">{{ p.name }}</span>
                    <span class="text-xs font-semibold" :style="{ color: p.pnlPctRaw >= 0 ? '#dc2626' : '#16a34a' }">
                      {{ p.pnlPct }}
                    </span>
                  </div>
                  <div class="flex items-center gap-1 text-xs" style="color: #94a3b8">
                    <span>现价 {{ p.current }}</span><span>→</span><span>成本 {{ p.costAvg }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>

    <!-- 标签切换 -->
    <div class="flex gap-1 p-1 rounded-full w-fit mb-5" style="background: #f1f5f9">
      <button
        class="px-6 py-2 rounded-full text-sm font-medium cursor-pointer whitespace-nowrap transition-all duration-200"
        :style="activeTab === 'current'
          ? { background: '#fff', color: '#d97706', border: '1px solid rgba(245,166,35,0.3)' }
          : { background: 'transparent', color: '#94a3b8', border: '1px solid transparent' }"
        @click="activeTab = 'current'"
      >当前持仓</button>
      <button
        class="px-6 py-2 rounded-full text-sm font-medium cursor-pointer whitespace-nowrap transition-all duration-200"
        :style="activeTab === 'history'
          ? { background: '#fff', color: '#d97706', border: '1px solid rgba(245,166,35,0.3)' }
          : { background: 'transparent', color: '#94a3b8', border: '1px solid transparent' }"
        @click="activeTab = 'history'"
      >历史交易</button>
    </div>

    <!-- 当前持仓表格 -->
    <div v-if="activeTab === 'current'" class="rounded-xl overflow-hidden" style="background: #fff; border: 1px solid #e2e8f0">
      <div v-if="positions.length" class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr style="border-bottom: 1px solid #f1f5f9; background: #fafbfc">
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">股票</th>
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">持仓股数</th>
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">成本均价</th>
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">现价</th>
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">持仓成本</th>
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">持仓市值</th>
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">浮动盈亏</th>
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">盈亏率</th>
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">今日涨跌</th>
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">建仓时间</th>
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">AI状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pos in positions" :key="pos.code" class="hover:bg-gray-50 transition-colors" style="border-bottom: 1px solid #f8fafc">
              <td class="px-4 py-4">
                <div class="font-semibold" style="color: #0f172a">{{ pos.name }}</div>
                <div class="text-xs mt-0.5" style="color: #94a3b8">{{ pos.code }}</div>
              </td>
              <td class="px-4 py-4" style="color: #334155">{{ pos.shares }}</td>
              <td class="px-4 py-4" style="color: #64748b">{{ pos.costAvg }}</td>
              <td class="px-4 py-4 font-semibold" style="color: #0f172a">{{ pos.current }}</td>
              <td class="px-4 py-4 whitespace-nowrap" style="color: #64748b">{{ pos.costTotal }}</td>
              <td class="px-4 py-4 whitespace-nowrap font-semibold" style="color: #334155">{{ pos.marketValue }}</td>
              <td class="px-4 py-4">
                <span class="font-semibold whitespace-nowrap" :style="{ color: pos.pnlRaw >= 0 ? '#dc2626' : '#16a34a' }">{{ pos.pnl }}</span>
              </td>
              <td class="px-4 py-4">
                <span class="font-semibold whitespace-nowrap" :style="{ color: pos.pnlPctRaw >= 0 ? '#dc2626' : '#16a34a' }">{{ pos.pnlPct }}</span>
              </td>
              <td class="px-4 py-4">
                <span class="font-semibold whitespace-nowrap" :style="{ color: pos.changePct >= 0 ? '#dc2626' : '#16a34a' }">
                  {{ pos.changePct >= 0 ? '+' : '' }}{{ pos.changePct }}%
                </span>
              </td>
              <td class="px-4 py-4 text-xs" style="color: #64748b">{{ pos.builtDate }}</td>
              <td class="px-4 py-4">
                <span class="px-2.5 py-1 rounded-full text-xs font-medium whitespace-nowrap" style="background: rgba(22,163,74,0.08); color: #16a34a; border: 1px solid rgba(22,163,74,0.15)">{{ pos.aiStatus }}</span>
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr style="border-top: 1px solid #f1f5f9; background: #fafbfc">
              <td colspan="4" class="px-4 py-3.5 text-sm font-bold" style="color: #0f172a">合计</td>
              <td class="px-4 py-3.5 text-sm font-bold whitespace-nowrap" style="color: #64748b">{{ totals.costTotal }}</td>
              <td class="px-4 py-3.5 text-sm font-bold whitespace-nowrap" style="color: #334155">{{ totals.marketValue }}</td>
              <td class="px-4 py-3.5"><span class="font-bold text-sm whitespace-nowrap" :style="{ color: store.account.unrealized_pnl >= 0 ? '#dc2626' : '#16a34a' }">{{ totals.pnl }}</span></td>
              <td class="px-4 py-3.5"><span class="font-bold text-sm whitespace-nowrap" :style="{ color: store.account.unrealized_pnl >= 0 ? '#dc2626' : '#16a34a' }">{{ totals.pnlPct }}</span></td>
              <td colspan="3"></td>
            </tr>
          </tfoot>
        </table>
      </div>
      <div v-else class="p-10 text-center">
        <i class="ri-inbox-line text-3xl" style="color: #cbd5e1"></i>
        <p class="text-sm mt-3" style="color: #94a3b8">暂无持仓，去模拟交易页建仓</p>
      </div>
      <div v-if="positions.length" class="px-4 py-3 flex items-center gap-2" style="border-top: 1px solid #f1f5f9; background: #fafbfc">
        <i class="ri-information-line text-xs" style="color: #d97706"></i>
        <span class="text-xs" style="color: #64748b">持仓数据实时同步，现价来自腾讯财经实时行情</span>
      </div>
    </div>

    <!-- 历史交易 -->
    <div v-else class="rounded-xl overflow-hidden" style="background: #fff; border: 1px solid #e2e8f0">
      <div v-if="tradeHistory.length" class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr style="border-bottom: 1px solid #f1f5f9; background: #fafbfc">
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">时间</th>
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">股票</th>
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">方向</th>
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">数量</th>
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">价格</th>
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">金额</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in tradeHistory" :key="t.id" class="hover:bg-gray-50 transition-colors" style="border-bottom: 1px solid #f8fafc">
              <td class="px-4 py-3 text-xs whitespace-nowrap" style="color: #94a3b8">{{ fmtHistory(t) }}</td>
              <td class="px-4 py-3">
                <div class="font-semibold text-xs" style="color: #0f172a">{{ t.name }}</div>
                <div class="text-xs" style="color: #94a3b8">{{ t.code }}</div>
              </td>
              <td class="px-4 py-3">
                <span
                  class="px-2.5 py-1 rounded-full text-xs font-bold"
                  :style="{
                    background: t.action === 'buy' ? 'rgba(22,163,74,0.08)' : 'rgba(220,38,38,0.08)',
                    color: t.action === 'buy' ? '#16a34a' : '#dc2626',
                    border: `1px solid ${t.action === 'buy' ? 'rgba(22,163,74,0.2)' : 'rgba(220,38,38,0.2)'}`,
                  }"
                >{{ t.action === 'buy' ? '买入' : '卖出' }}</span>
              </td>
              <td class="px-4 py-3 text-xs" style="color: #334155">{{ t.qty.toLocaleString() }} 股</td>
              <td class="px-4 py-3 text-xs" style="color: #334155">¥{{ t.price }}</td>
              <td class="px-4 py-3 text-xs font-semibold" style="color: #334155">¥{{ fmt(t.amount) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="p-10 text-center">
        <i class="ri-history-line text-3xl" style="color: #cbd5e1"></i>
        <p class="text-sm mt-3" style="color: #94a3b8">暂无历史交易记录</p>
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
