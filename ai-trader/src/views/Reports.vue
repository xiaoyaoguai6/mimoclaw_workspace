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
  if (v > 3000) return { bg: 'rgba(220,38,38,0.25)', color: '#dc2626', border: 'rgba(220,38,38,0.3)' }
  if (v > 0) return { bg: 'rgba(220,38,38,0.12)', color: '#dc2626', border: 'rgba(220,38,38,0.2)' }
  return { bg: 'rgba(22,163,74,0.12)', color: '#16a34a', border: 'rgba(22,163,74,0.2)' }
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
        ? `rgba(220,38,38,${Math.min(0.1 + absPct / 30, 0.5)})`
        : `rgba(22,163,74,${Math.min(0.1 + absPct / 30, 0.5)})`
      return {
        name: h.name,
        weight: `${weight}%`,
        pnl: `${pnlPct >= 0 ? '+' : ''}${pnlPct}%`,
        pnlColor: pnlPct >= 0 ? '#dc2626' : '#16a34a',
        color,
        borderColor: pnlPct >= 0 ? 'rgba(220,38,38,0.25)' : 'rgba(22,163,74,0.25)',
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
    actionColor: d.action === '买入' ? '#16a34a' : d.action === '卖出' ? '#dc2626' : '#64748b',
    reason: d.reason || '',
    confidence: d.confidence || '—',
  }))
})
</script>

<template>
  <div class="max-w-screen-xl space-y-5">
    <RiskBanner />

    <!-- 顶部工具栏 -->
    <div class="flex items-center justify-between">
      <div></div>
      <div class="flex items-center gap-3">
        <div class="flex gap-1 p-1 rounded-full" style="background: #f1f5f9">
          <button
            v-for="p in periods"
            :key="p.key"
            class="px-4 py-1.5 rounded-full text-xs font-medium cursor-pointer whitespace-nowrap transition-all"
            :style="period === p.key
              ? { background: '#fff', color: '#d97706', border: '1px solid rgba(245,166,35,0.3)' }
              : { background: 'transparent', color: '#94a3b8', border: '1px solid transparent' }"
            @click="period = p.key"
          >{{ p.label }}</button>
        </div>
        <button
          title="使用浏览器打印对话框另存为 PDF（Cmd/Ctrl+P）"
          class="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium cursor-pointer whitespace-nowrap transition-all hover:bg-orange-50"
          style="background: rgba(245,166,35,0.08); border: 1px solid rgba(245,166,35,0.2); color: #d97706"
        >
          <i class="ri-download-cloud-line"></i>导出PDF
        </button>
      </div>
    </div>

    <!-- 累计收益率 + 资产净值曲线 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <div class="lg:col-span-1 rounded-xl p-5" style="background: #fff; border: 1px solid #e2e8f0">
        <p class="text-xs mb-2" style="color: #64748b">累计收益率</p>
        <div class="text-5xl font-black mb-1" :style="{ color: store.account.total_pnl_pct >= 0 ? '#dc2626' : '#16a34a' }">
          {{ store.account.total_pnl_pct >= 0 ? '+' : '' }}{{ store.account.total_pnl_pct }}%
        </div>
        <div class="flex items-center gap-2 mb-4">
          <span class="text-xs" style="color: #94a3b8">基于实时持仓计算</span>
        </div>
        <div class="pt-3" style="border-top: 1px solid #f1f5f9">
          <p class="text-xs mb-1" style="color: #94a3b8">资产净值</p>
          <p class="text-xl font-bold" style="color: #0f172a">¥{{ fmt(store.account.total_assets) }}</p>
        </div>
      </div>
      <div class="lg:col-span-2 rounded-xl p-5" style="background: #fff; border: 1px solid #e2e8f0">
        <div class="flex items-center justify-between mb-3">
          <p class="text-xs font-semibold" style="color: #334155">资产净值曲线</p>
          <div class="flex gap-4">
            <div class="flex items-center gap-1.5 cursor-help" title="你的真实账户净值（基于真实成交 + 实时市价计算）">
              <div class="w-4 h-0.5" style="background: #f5a623"></div>
              <span class="text-xs" style="color: #94a3b8">我的资产</span>
            </div>
            <div class="flex items-center gap-1.5 cursor-help" title="qlib 策略级回测对照线，跟你的账户操作无关，仅作 alpha 对照">
              <div class="w-4 h-0.5 border-t border-dashed" style="border-color: #6366f1"></div>
              <span class="text-xs" style="color: #94a3b8">qlib 量化基线 <i class="ri-information-line text-[10px]" style="color: #cbd5e1"></i></span>
            </div>
          </div>
        </div>
        <!-- SVG 曲线图 -->
        <div class="relative">
          <svg viewBox="0 0 560 160" class="w-full" style="height: 180px">
            <defs>
              <linearGradient id="rptGradLight" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#F5A623" stop-opacity="0.18" />
                <stop offset="100%" stop-color="#F5A623" stop-opacity="0" />
              </linearGradient>
            </defs>
            <!-- 网格线 -->
            <g><line x1="52" y1="132" x2="544" y2="132" stroke="#f1f5f9" stroke-width="1" /><text x="46" y="136" text-anchor="end" font-size="9" fill="#94a3b8">19万</text></g>
            <g><line x1="52" y1="72" x2="544" y2="72" stroke="#f1f5f9" stroke-width="1" /><text x="46" y="76" text-anchor="end" font-size="9" fill="#94a3b8">64万</text></g>
            <g><line x1="52" y1="12" x2="544" y2="12" stroke="#f1f5f9" stroke-width="1" /><text x="46" y="16" text-anchor="end" font-size="9" fill="#94a3b8">109万</text></g>
            <!-- X轴标签 -->
            <text x="52" y="156" text-anchor="middle" font-size="9" fill="#94a3b8">2026-05-25</text>
            <text x="306" y="156" text-anchor="middle" font-size="9" fill="#94a3b8">2026-06-09</text>
            <text x="544" y="156" text-anchor="middle" font-size="9" fill="#94a3b8">2026-06-23</text>
            <!-- 我的资产曲线 -->
            <path d="M52,24 L137,24 L222,24 L306,24 L323,24 L340,26 L357,28 L374,28 L391,28 L408,23 L425,20 L442,17 L459,13 L476,13 L493,13 L510,13 L527,12 L544,12 L544,132 L52,132 Z" fill="url(#rptGradLight)" />
            <path d="M52,24 L137,24 L222,24 L306,24 L323,24 L340,26 L357,28 L374,28 L391,28 L408,23 L425,20 L442,17 L459,13 L476,13 L493,13 L510,13 L527,12 L544,12" fill="none" stroke="#F5A623" stroke-width="2.5" stroke-linecap="round">
              <title>我的资产 — 真实账户净值，基于 sim_orders 实际成交</title>
            </path>
            <circle cx="544" cy="12" r="4" fill="#F5A623" stroke="#ffffff" stroke-width="2" />
            <!-- qlib 基线 -->
            <path d="M52,24 L75,23 L99,22 L122,22 L146,20 L169,21 L193,22 L216,23 L239,22 L263,21 L286,21 L310,78 L333,89 L357,89 L380,89 L403,88 L427,132 L450,121 L474,23 L497,23 L521,22 L544,24" fill="none" stroke="#6366f1" stroke-width="1.8" stroke-dasharray="4 3" stroke-linecap="round">
              <title>qlib 量化基线 — 策略级回测，与你的账户操作无关，用作 alpha 对照</title>
            </path>
            <circle cx="544" cy="24" r="3" fill="#6366f1" stroke="#ffffff" stroke-width="2" />
          </svg>
          <div class="text-[10px] mt-1 text-right" style="color: #94a3b8">首次资产变动: 2026-06-10</div>
        </div>
      </div>
    </div>

    <!-- 每日收益日历 -->
    <div class="rounded-xl p-5" style="background: #fff; border: 1px solid #e2e8f0">
      <div class="flex items-center justify-between mb-4 flex-wrap gap-3">
        <div class="flex items-center gap-3">
          <h4 class="text-sm font-semibold" style="color: #0f172a">每日收益</h4>
          <div class="flex gap-1 p-1 rounded-full" style="background: #f1f5f9">
            <button
              class="px-3 py-1 rounded-full text-xs font-medium cursor-pointer transition-all"
              :style="returnMode === 'amount'
                ? { background: '#fff', color: '#d97706', border: '1px solid rgba(245,166,35,0.3)' }
                : { background: 'transparent', color: '#94a3b8', border: '1px solid transparent' }"
              @click="returnMode = 'amount'"
            >收益额</button>
            <button
              class="px-3 py-1 rounded-full text-xs font-medium cursor-pointer transition-all"
              :style="returnMode === 'rate'
                ? { background: '#fff', color: '#d97706', border: '1px solid rgba(245,166,35,0.3)' }
                : { background: 'transparent', color: '#94a3b8', border: '1px solid transparent' }"
              @click="returnMode = 'rate'"
            >收益率</button>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button class="w-7 h-7 rounded-lg flex items-center justify-center transition-all" style="background: #f8fafc; border: 1px solid #e2e8f0; color: #64748b; cursor: pointer">
            <i class="ri-arrow-left-s-line"></i>
          </button>
          <span class="text-sm font-semibold min-w-[88px] text-center" style="color: #0f172a">{{ currentMonth }}</span>
          <button disabled class="w-7 h-7 rounded-lg flex items-center justify-center transition-all" style="background: #f8fafc; border: 1px solid #e2e8f0; color: #cbd5e1; cursor: not-allowed">
            <i class="ri-arrow-right-s-line"></i>
          </button>
        </div>
      </div>
      <div class="grid grid-cols-5 gap-2 mb-2">
        <div v-for="d in ['周一','周二','周三','周四','周五']" :key="d" class="text-center text-xs" style="color: #94a3b8">{{ d }}</div>
      </div>
      <div class="grid grid-cols-5 gap-2">
        <template v-for="(cell, idx) in calendarData" :key="idx">
          <div v-if="cell.offset" class="h-12"></div>
          <div
            v-else
            class="h-12 rounded-lg flex flex-col items-center justify-center text-xs transition-all"
            :style="{
              background: cell.today ? 'rgba(245,166,35,0.1)' : getCalendarColor(cell.value).bg,
              border: cell.today ? '2px solid #f5a623' : '1px solid ' + getCalendarColor(cell.value).border,
            }"
          >
            <span class="font-medium" :style="{ color: cell.today ? '#d97706' : '#334155' }">{{ cell.day }}</span>
            <span v-if="cell.value" class="text-[10px] font-semibold mt-0.5" :style="{ color: getCalendarColor(cell.value).color }">
              {{ returnMode === 'amount' ? (cell.value > 0 ? '+' : '') + '¥' + cell.value.toLocaleString() : (cell.value > 0 ? '+' : '') + (cell.value / 10000).toFixed(2) + '%' }}
            </span>
          </div>
        </template>
      </div>
    </div>

    <!-- AI 决策记录 -->
    <div class="rounded-xl p-5" style="background: #fff; border: 1px solid #e2e8f0">
      <div class="flex items-center justify-between mb-4">
        <h4 class="text-sm font-semibold" style="color: #0f172a">AI 决策记录</h4>
        <span class="text-xs" style="color: #94a3b8">共 {{ decisions.length }} 条决策</span>
      </div>
      <div v-if="decisions.length" class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr style="border-bottom: 1px solid #f1f5f9">
              <th class="text-left px-3 py-3 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">时间</th>
              <th class="text-left px-3 py-3 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">股票</th>
              <th class="text-left px-3 py-3 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">决策</th>
              <th class="text-left px-3 py-3 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">AI 分析理由</th>
              <th class="text-left px-3 py-3 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">置信度</th>
              <th class="text-left px-3 py-3 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(d, i) in decisions" :key="i" class="hover:bg-gray-50 transition-colors" style="border-bottom: 1px solid #f8fafc">
              <td class="px-3 py-3.5 text-xs whitespace-nowrap" style="color: #94a3b8">{{ d.time }}</td>
              <td class="px-3 py-3.5">
                <div class="font-semibold text-xs" style="color: #0f172a">{{ d.name }}</div>
                <div class="text-xs" style="color: #94a3b8">{{ d.action }}</div>
              </td>
              <td class="px-3 py-3.5">
                <span
                  class="px-2.5 py-1 rounded-full text-xs font-bold"
                  :style="{
                    background: d.action === '买入' ? 'rgba(22,163,74,0.08)' : d.action === '卖出' ? 'rgba(220,38,38,0.08)' : 'rgba(100,116,139,0.08)',
                    color: d.actionColor,
                    border: '1px solid ' + (d.action === '买入' ? 'rgba(22,163,74,0.2)' : d.action === '卖出' ? 'rgba(220,38,38,0.2)' : 'rgba(100,116,139,0.2)')
                  }"
                >{{ d.action }}</span>
              </td>
              <td class="px-3 py-3.5 max-w-xs">
                <p class="text-xs leading-relaxed line-clamp-2" style="color: #64748b">{{ d.reason }}</p>
              </td>
              <td class="px-3 py-3.5">
                <span class="text-xs font-semibold" style="color: #94a3b8">{{ d.confidence }}</span>
              </td>
              <td class="px-3 py-3.5">
                <div class="flex items-center gap-1.5 whitespace-nowrap">
                  <button class="px-2.5 py-1.5 rounded-lg text-xs font-medium cursor-pointer hover:bg-violet-50" style="background: rgba(124,58,237,0.06); border: 1px solid rgba(124,58,237,0.2); color: #7c3aed">
                    <i class="ri-history-line mr-1"></i>复盘
                  </button>
                  <button class="px-2.5 py-1.5 rounded-lg text-xs font-medium cursor-pointer hover:bg-orange-50" style="background: rgba(245,166,35,0.06); border: 1px solid rgba(245,166,35,0.2); color: #d97706">追问 AI</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="py-8 text-center">
        <i class="ri-history-line text-2xl" style="color: #cbd5e1"></i>
        <p class="text-sm mt-2" style="color: #94a3b8">暂无 AI 决策记录</p>
      </div>
    </div>

    <!-- 持仓热力图 -->
    <div class="rounded-xl p-5" style="background: #fff; border: 1px solid #e2e8f0">
      <div class="flex items-center justify-between mb-4">
        <h4 class="text-sm font-semibold" style="color: #0f172a">持仓热力图</h4>
        <div class="flex items-center gap-3 text-xs" style="color: #94a3b8">
          <span>面积 = 持仓市值</span>
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded" style="background: #dc2626"></span>深红=高盈利
            <span class="w-3 h-3 rounded" style="background: #e2e8f0"></span>持平
            <span class="w-3 h-3 rounded" style="background: #16a34a"></span>亏损
          </div>
        </div>
      </div>
      <div v-if="heatmapItems.length" class="flex gap-2 h-52">
          <div
            v-for="item in heatmapItems"
            :key="item.name"
            role="button"
            tabindex="0"
            title="点击查看 AI 决策 + 成交全过程复盘"
            class="flex flex-col justify-between p-3 rounded-xl cursor-pointer transition-all hover:scale-105"
            :style="{ background: item.color, border: '1px solid ' + item.borderColor, flex: item.flex + ' 1 0%' }"
          >
            <div>
              <p class="text-xs font-bold" style="color: #0f172a">{{ item.name }}</p>
              <p class="text-xs" style="color: #64748b">{{ item.weight }}</p>
            </div>
            <p class="text-sm font-black" :style="{ color: item.pnlColor || '#dc2626' }">{{ item.pnl }}</p>
          </div>
        </div>
        <div v-else class="h-52 flex items-center justify-center">
          <span class="text-sm" style="color: #94a3b8">暂无持仓数据</span>
        </div>
    </div>

    <!-- 板块配置 -->
    <div class="rounded-xl p-5" style="background: #fff; border: 1px solid #e2e8f0">
      <div class="flex items-center justify-between mb-4">
        <h4 class="text-sm font-semibold" style="color: #0f172a">当前板块配置</h4>
        <span class="text-xs" style="color: #94a3b8">颜色深度 = AI仓位权重</span>
      </div>
      <div v-if="store.holdings.length" class="space-y-2">
          <div class="flex items-center gap-3">
            <span class="text-xs w-28 shrink-0" style="color: #334155">持仓分布</span>
            <div class="flex-1 min-w-0 h-7 rounded-lg overflow-hidden relative" style="background: rgba(245,166,35,0.06)">
              <div
                class="absolute inset-y-0 left-0 rounded-lg flex items-center px-2 transition-all"
                :style="{ width: store.account.position_usage + '%', minWidth: '48px', background: 'rgba(245,166,35,0.65)', border: '1px solid rgba(245,166,35,0.75)' }"
              >
                <span class="text-xs font-semibold whitespace-nowrap" style="color: #d97706">{{ store.account.position_usage }}%</span>
              </div>
            </div>
            <span class="text-xs w-8 shrink-0 text-right" style="color: #94a3b8">{{ store.holdings.length }}只</span>
          </div>
        </div>
        <div v-else class="text-center py-4">
          <span class="text-sm" style="color: #94a3b8">暂无持仓</span>
        </div>
    </div>

    <!-- AI 亏损复盘 -->
    <div class="rounded-xl p-5" style="background: #fff; border: 1px solid #e2e8f0">
      <div class="flex items-center gap-2 mb-4">
        <h4 class="text-sm font-semibold" style="color: #0f172a">AI 亏损复盘</h4>
        <span class="text-xs px-2 py-0.5 rounded-full" style="background: rgba(220,38,38,0.06); color: #dc2626; border: 1px solid rgba(220,38,38,0.15)">亏损仓位</span>
        <span class="text-xs ml-1" style="color: #94a3b8">透明展示AI的亏损，建立信任</span>
      </div>
      <div v-if="lossItems.length" class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr style="border-bottom: 1px solid #f1f5f9">
              <th class="text-left px-3 py-3 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">股票</th>
              <th class="text-left px-3 py-3 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">行业</th>
              <th class="text-left px-3 py-3 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">亏损幅度</th>
              <th class="text-left px-3 py-3 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">亏损金额</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in lossItems" :key="item.code" class="hover:bg-gray-50 transition-colors" style="border-bottom: 1px solid #f8fafc">
              <td class="px-3 py-4">
                <div class="font-semibold text-xs" style="color: #0f172a">{{ item.name }}</div>
                <div class="text-xs" style="color: #94a3b8">{{ item.code }}</div>
              </td>
              <td class="px-3 py-4 text-xs" style="color: #64748b">{{ item.industry || '—' }}</td>
              <td class="px-3 py-4">
                <span class="text-sm font-bold" style="color: #16a34a">{{ item.lossPct }}</span>
              </td>
              <td class="px-3 py-4">
                <span class="text-sm font-bold" style="color: #16a34a">{{ item.lossAmt }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="py-8 text-center">
        <i class="ri-emotion-happy-line text-2xl" style="color: #22c55e"></i>
        <p class="text-sm mt-2" style="color: #94a3b8">当前无亏损持仓 🎉</p>
      </div>
    </div>
  </div>
</template>
