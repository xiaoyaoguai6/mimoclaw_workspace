<script setup>
import { ref, computed, onMounted } from 'vue'
import RiskBanner from '@/components/RiskBanner.vue'
import { useAppStore } from '@/stores/app'
import api from '@/api'

const store = useAppStore()
const period = ref('month')
const returnMode = ref('amount')
const currentMonth = ref('2026年6月')
const activeSection = ref('all')

const periods = [
  { key: 'week', label: '本周' },
  { key: 'month', label: '本月' },
  { key: 'quarter', label: '本季度' },
  { key: 'custom', label: '自定义' },
]

const aiDecisions = ref([])

onMounted(async () => {
  store.fetchAccount()
  try {
    aiDecisions.value = await api.getAiDecisions(50)
  } catch (e) {
    console.error(e)
  }
})

const fmt = (v) => v.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const calendarData = [
  { day: '', offset: true },
  { day: '', offset: true },
  { day: 1, value: 0 },
  { day: 2, value: 0 },
  { day: 3, value: 0 },
  { day: 4, value: 0 },
  { day: 5, value: 0 },
  { day: 6, value: 0 },
  { day: 7, value: 0 },
  { day: 8, value: 0 },
  { day: 9, value: 0 },
  { day: 10, value: 0 },
  { day: 11, value: 0 },
  { day: 12, value: 0 },
  { day: 13, value: 0 },
  { day: 14, value: 0 },
  { day: 15, value: 0 },
  { day: 16, value: 0 },
  { day: 17, value: 0 },
  { day: 18, value: 0 },
  { day: 19, value: 0 },
  { day: 20, value: 0 },
  { day: 21, value: 0 },
  { day: 22, value: 0 },
  { day: 23, value: 0, today: true },
]

const getCalendarColor = (v) => {
  if (!v || v === 0) return { bg: '#f8fafc', color: '#94a3b8', border: '#f1f5f9' }
  if (v > 3000) return { bg: 'rgba(239,68,68,0.25)', color: '#ef4444', border: 'rgba(239,68,68,0.3)' }
  if (v > 0) return { bg: 'rgba(239,68,68,0.12)', color: '#ef4444', border: 'rgba(239,68,68,0.2)' }
  return { bg: 'rgba(16,185,129,0.12)', color: '#10b981', border: 'rgba(16,185,129,0.2)' }
}

const heatmapItems = computed(() => {
  if (!store.holdings.length) return []
  const totalMv = store.account.total_market_value || 1
  return store.holdings
    .map(h => {
      const weight = (h.market_value / totalMv * 100).toFixed(1)
      const pnlPct = h.pnl_pct
      const absPct = Math.abs(pnlPct)
      const color = pnlPct >= 0
        ? `rgba(239,68,68,${Math.min(0.1 + absPct / 30, 0.5)})`
        : `rgba(16,185,129,${Math.min(0.1 + absPct / 30, 0.5)})`
      return {
        name: h.name,
        weight: `${weight}%`,
        pnl: `${pnlPct >= 0 ? '+' : ''}${pnlPct}%`,
        pnlColor: pnlPct >= 0 ? '#ef4444' : '#10b981',
        color,
        borderColor: pnlPct >= 0 ? 'rgba(239,68,68,0.25)' : 'rgba(16,185,129,0.25)',
        flex: Math.max(h.market_value / 100000, 0.5),
      }
    })
    .sort((a, b) => parseFloat(b.weight) - parseFloat(a.weight))
})

const lossItems = computed(() => {
  return store.holdings
    .filter(h => h.pnl < 0)
    .map(h => ({
      name: h.name,
      code: h.code,
      industry: '',
      trades: '1 次',
      lossPct: `${h.pnl_pct}%`,
      lossAmt: `-¥${fmt(Math.abs(h.pnl))}`,
    }))
})

const decisions = computed(() => {
  return aiDecisions.value.map(d => ({
    time: d.ts ? new Date(d.ts).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) : '',
    name: d.name,
    action: d.action,
    actionColor: d.action === '买入' ? '#10b981' : d.action === '卖出' ? '#ef4444' : '#64748b',
    reason: d.reason || '',
    confidence: d.confidence || '—',
  }))
})
</script>

<template>
  <div class="max-w-screen-xl space-y-6 animate-fade-in">
    <RiskBanner />

    <!-- 顶部工具栏 -->
    <div class="flex items-center justify-end">
      <div class="flex items-center gap-3">
        <div class="flex gap-1 p-1 rounded-xl" style="background: var(--color-border-light)">
          <button
            v-for="p in periods"
            :key="p.key"
            class="px-4 py-1.5 rounded-lg text-xs font-medium cursor-pointer whitespace-nowrap transition-all"
            :style="period === p.key
              ? { background: 'var(--color-bg-card)', color: 'var(--color-primary)', boxShadow: 'var(--shadow-sm)' }
              : { background: 'transparent', color: 'var(--color-text-muted)' }"
            @click="period = p.key"
          >{{ p.label }}</button>
        </div>
        <button
          class="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-medium cursor-pointer whitespace-nowrap transition-all hover:shadow-md"
          style="background: var(--color-primary-light); border: 1px solid rgba(99,102,241,0.2); color: var(--color-primary)"
        >
          <i class="ri-download-cloud-line"></i>导出PDF
        </button>
      </div>
    </div>

    <!-- 累计收益率 + 资产净值曲线 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <div class="card p-6">
        <p class="text-xs mb-2" style="color: var(--color-text-muted)">累计收益率</p>
        <div class="text-5xl font-black mb-2 tabular-nums" :style="{ color: store.account.total_pnl_pct >= 0 ? 'var(--color-up)' : 'var(--color-down)' }">
          {{ store.account.total_pnl_pct >= 0 ? '+' : '' }}{{ store.account.total_pnl_pct }}%
        </div>
        <div class="flex items-center gap-2 mb-4">
          <span class="text-xs" style="color: var(--color-text-muted)">基于实时持仓计算</span>
        </div>
        <div class="pt-4" style="border-top: 1px solid var(--color-border-light)">
          <p class="text-xs mb-1" style="color: var(--color-text-muted)">资产净值</p>
          <p class="text-xl font-bold tabular-nums" style="color: var(--color-text-primary)">¥{{ fmt(store.account.total_assets) }}</p>
        </div>
      </div>
      <div class="lg:col-span-2 card p-6">
        <div class="flex items-center justify-between mb-4">
          <p class="text-sm font-semibold" style="color: var(--color-text-primary)">资产净值曲线</p>
          <div class="flex gap-4">
            <div class="flex items-center gap-1.5">
              <div class="w-4 h-0.5" style="background: var(--color-primary)"></div>
              <span class="text-xs" style="color: var(--color-text-muted)">我的资产</span>
            </div>
            <div class="flex items-center gap-1.5">
              <div class="w-4 h-0.5 border-t border-dashed" style="border-color: var(--color-accent)"></div>
              <span class="text-xs" style="color: var(--color-text-muted)">qlib 量化基线</span>
            </div>
          </div>
        </div>
        <div class="h-[200px] flex items-center justify-center rounded-xl" style="background: var(--color-border-light); color: var(--color-text-muted)">
          <div class="text-center">
            <i class="ri-line-chart-line text-3xl mb-2 block"></i>
            <span class="text-sm">资产净值曲线图表区域（接入 ECharts）</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 每日收益日历 -->
    <div class="card p-6">
      <div class="flex items-center justify-between mb-5 flex-wrap gap-3">
        <div class="flex items-center gap-3">
          <h4 class="text-base font-bold" style="color: var(--color-text-primary)">每日收益</h4>
          <div class="flex gap-1 p-1 rounded-xl" style="background: var(--color-border-light)">
            <button
              class="px-3 py-1 rounded-lg text-xs font-medium cursor-pointer transition-all"
              :style="returnMode === 'amount'
                ? { background: 'var(--color-bg-card)', color: 'var(--color-primary)', boxShadow: 'var(--shadow-sm)' }
                : { background: 'transparent', color: 'var(--color-text-muted)' }"
              @click="returnMode = 'amount'"
            >收益额</button>
            <button
              class="px-3 py-1 rounded-lg text-xs font-medium cursor-pointer transition-all"
              :style="returnMode === 'rate'
                ? { background: 'var(--color-bg-card)', color: 'var(--color-primary)', boxShadow: 'var(--shadow-sm)' }
                : { background: 'transparent', color: 'var(--color-text-muted)' }"
              @click="returnMode = 'rate'"
            >收益率</button>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button class="w-8 h-8 rounded-lg flex items-center justify-center transition-all cursor-pointer" style="background: var(--color-border-light); color: var(--color-text-secondary)">
            <i class="ri-arrow-left-s-line"></i>
          </button>
          <span class="text-sm font-semibold min-w-[100px] text-center" style="color: var(--color-text-primary)">{{ currentMonth }}</span>
          <button disabled class="w-8 h-8 rounded-lg flex items-center justify-center" style="background: var(--color-border-light); color: var(--color-text-faint); cursor: not-allowed">
            <i class="ri-arrow-right-s-line"></i>
          </button>
        </div>
      </div>
      <div class="grid grid-cols-5 gap-2 mb-2">
        <div v-for="d in ['周一','周二','周三','周四','周五']" :key="d" class="text-center text-xs font-medium" style="color: var(--color-text-muted)">{{ d }}</div>
      </div>
      <div class="grid grid-cols-5 gap-2">
        <template v-for="(cell, idx) in calendarData" :key="idx">
          <div v-if="cell.offset" class="h-14"></div>
          <div
            v-else
            class="h-14 rounded-xl flex flex-col items-center justify-center text-xs transition-all"
            :style="{
              background: cell.today ? 'var(--color-primary-light)' : getCalendarColor(cell.value).bg,
              border: cell.today ? '2px solid var(--color-primary)' : '1px solid ' + getCalendarColor(cell.value).border,
            }"
          >
            <span class="font-medium" :style="{ color: cell.today ? 'var(--color-primary)' : 'var(--color-text-primary)' }">{{ cell.day }}</span>
            <span v-if="cell.value" class="text-[10px] font-bold mt-0.5 tabular-nums" :style="{ color: getCalendarColor(cell.value).color }">
              {{ returnMode === 'amount' ? (cell.value > 0 ? '+' : '') + '¥' + cell.value.toLocaleString() : (cell.value > 0 ? '+' : '') + (cell.value / 10000).toFixed(2) + '%' }}
            </span>
          </div>
        </template>
      </div>
    </div>

    <!-- AI 决策记录 -->
    <div class="card p-6">
      <div class="flex items-center justify-between mb-5">
        <h4 class="text-base font-bold" style="color: var(--color-text-primary)">AI 决策记录</h4>
        <span class="badge" style="background: var(--color-primary-light); color: var(--color-primary)">共 {{ decisions.length }} 条</span>
      </div>
      <div v-if="decisions.length" class="overflow-x-auto">
        <table class="modern-table">
          <thead>
            <tr>
              <th>时间</th><th>股票</th><th>决策</th><th>AI 分析理由</th><th>置信度</th><th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(d, i) in decisions" :key="i">
              <td class="text-xs whitespace-nowrap tabular-nums" style="color: var(--color-text-muted)">{{ d.time }}</td>
              <td>
                <div class="font-semibold text-sm" style="color: var(--color-text-primary)">{{ d.name }}</div>
                <div class="text-xs" style="color: var(--color-text-muted)">{{ d.action }}</div>
              </td>
              <td>
                <span class="badge" :style="{
                  background: d.action === '买入' ? 'var(--color-success-light)' : d.action === '卖出' ? 'var(--color-danger-light)' : 'var(--color-border-light)',
                  color: d.actionColor,
                }">{{ d.action }}</span>
              </td>
              <td class="max-w-xs">
                <p class="text-xs leading-relaxed line-clamp-2" style="color: var(--color-text-secondary)">{{ d.reason }}</p>
              </td>
              <td>
                <span class="text-xs font-semibold tabular-nums" style="color: var(--color-text-muted)">{{ d.confidence }}</span>
              </td>
              <td>
                <div class="flex items-center gap-1.5 whitespace-nowrap">
                  <button class="px-2.5 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition-all hover:shadow-sm" style="background: rgba(124,58,237,0.06); border: 1px solid rgba(124,58,237,0.15); color: #7c3aed">
                    <i class="ri-history-line mr-1"></i>复盘
                  </button>
                  <button class="px-2.5 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition-all hover:shadow-sm" style="background: var(--color-primary-light); border: 1px solid rgba(99,102,241,0.15); color: var(--color-primary)">追问 AI</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="py-12 text-center">
        <div class="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-3" style="background: var(--color-border-light)">
          <i class="ri-history-line text-2xl" style="color: var(--color-text-faint)"></i>
        </div>
        <p class="text-sm" style="color: var(--color-text-muted)">暂无 AI 决策记录</p>
      </div>
    </div>

    <!-- 持仓热力图 -->
    <div class="card p-6">
      <div class="flex items-center justify-between mb-5">
        <h4 class="text-base font-bold" style="color: var(--color-text-primary)">持仓热力图</h4>
        <div class="flex items-center gap-3 text-xs" style="color: var(--color-text-muted)">
          <span>面积 = 持仓市值</span>
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded" style="background: var(--color-up)"></span>盈利
            <span class="w-3 h-3 rounded" style="background: var(--color-border)"></span>持平
            <span class="w-3 h-3 rounded" style="background: var(--color-down)"></span>亏损
          </div>
        </div>
      </div>
      <div v-if="heatmapItems.length" class="flex gap-2.5 h-56">
        <div
          v-for="item in heatmapItems"
          :key="item.name"
          role="button"
          tabindex="0"
          class="flex flex-col justify-between p-4 rounded-2xl cursor-pointer transition-all hover:scale-105"
          :style="{ background: item.color, border: '1px solid ' + item.borderColor, flex: item.flex + ' 1 0%' }"
        >
          <div>
            <p class="text-sm font-bold" style="color: var(--color-text-primary)">{{ item.name }}</p>
            <p class="text-xs mt-0.5" style="color: var(--color-text-secondary)">{{ item.weight }}</p>
          </div>
          <p class="text-lg font-black tabular-nums" :style="{ color: item.pnlColor }">{{ item.pnl }}</p>
        </div>
      </div>
      <div v-else class="h-56 flex items-center justify-center rounded-xl" style="background: var(--color-border-light)">
        <span class="text-sm" style="color: var(--color-text-muted)">暂无持仓数据</span>
      </div>
    </div>

    <!-- 板块配置 -->
    <div class="card p-6">
      <div class="flex items-center justify-between mb-5">
        <h4 class="text-base font-bold" style="color: var(--color-text-primary)">当前板块配置</h4>
        <span class="text-xs" style="color: var(--color-text-muted)">颜色深度 = AI仓位权重</span>
      </div>
      <div v-if="store.holdings.length" class="space-y-3">
        <div class="flex items-center gap-3">
          <span class="text-xs w-28 shrink-0 font-medium" style="color: var(--color-text-secondary)">持仓分布</span>
          <div class="flex-1 min-w-0 h-8 rounded-xl overflow-hidden relative" style="background: var(--color-primary-light)">
            <div
              class="absolute inset-y-0 left-0 rounded-xl flex items-center px-3 transition-all"
              :style="{ width: store.account.position_usage + '%', minWidth: '60px', background: 'linear-gradient(135deg, var(--color-primary), var(--color-primary-dark))' }"
            >
              <span class="text-xs font-bold whitespace-nowrap text-white tabular-nums">{{ store.account.position_usage }}%</span>
            </div>
          </div>
          <span class="text-xs w-10 shrink-0 text-right tabular-nums" style="color: var(--color-text-muted)">{{ store.holdings.length }}只</span>
        </div>
      </div>
      <div v-else class="py-8 text-center">
        <span class="text-sm" style="color: var(--color-text-muted)">暂无持仓</span>
      </div>
    </div>

    <!-- AI 亏损复盘 -->
    <div class="card p-6">
      <div class="flex items-center gap-2 mb-5">
        <h4 class="text-base font-bold" style="color: var(--color-text-primary)">AI 亏损复盘</h4>
        <span class="badge" style="background: var(--color-danger-light); color: var(--color-danger)">亏损仓位</span>
        <span class="text-xs ml-1" style="color: var(--color-text-muted)">透明展示AI的亏损，建立信任</span>
      </div>
      <div v-if="lossItems.length" class="overflow-x-auto">
        <table class="modern-table">
          <thead>
            <tr>
              <th>股票</th><th>行业</th><th>亏损幅度</th><th>亏损金额</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in lossItems" :key="item.code">
              <td>
                <div class="font-semibold text-sm" style="color: var(--color-text-primary)">{{ item.name }}</div>
                <div class="text-xs font-mono" style="color: var(--color-text-muted)">{{ item.code }}</div>
              </td>
              <td class="text-sm" style="color: var(--color-text-secondary)">{{ item.industry || '—' }}</td>
              <td>
                <span class="text-base font-bold tabular-nums" style="color: var(--color-down)">{{ item.lossPct }}</span>
              </td>
              <td>
                <span class="text-base font-bold tabular-nums" style="color: var(--color-down)">{{ item.lossAmt }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="py-12 text-center">
        <div class="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-3" style="background: var(--color-success-light)">
          <i class="ri-emotion-happy-line text-2xl" style="color: var(--color-success)"></i>
        </div>
        <p class="text-sm font-medium" style="color: var(--color-success)">当前无亏损持仓</p>
      </div>
    </div>
  </div>
</template>
