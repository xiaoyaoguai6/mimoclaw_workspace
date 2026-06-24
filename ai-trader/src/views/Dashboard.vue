<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import api from '@/api'
import RiskBanner from '@/components/RiskBanner.vue'

const store = useAppStore()
const chartPeriod = ref('month')

const broadcasts = [
  { time: '09:30', title: '开盘观察', status: 'pending', content: '本时段播报暂未生成，请稍后查看。' },
  { time: '10:30', title: '盘中节奏', status: 'pending', content: '本时段播报暂未生成，请稍后查看。' },
  { time: '14:00', title: '午后开盘', status: 'pending', content: '本时段播报暂未生成，请稍后查看。' },
  { time: '15:10', title: '全天复盘', status: 'pending', content: '本时段播报暂未生成，请稍后查看。' },
]

const aiDynamics = [
  { time: '14:56', type: 'skip', label: '🔍 分析跳过', text: '工业富联(601138) 买入 未成交，风控:行业持仓超过40%上限，跳过。' },
  { time: '14:47', type: 'watch', label: '⚠️ 列入观察', text: '中天科技(600522) 观察，基本面估值最健康（PE18.2x/PEG0.9）。' },
  { time: '14:38', type: 'watch', label: '⚠️ 列入观察', text: '中天科技(600522) 观察，唯一获"强买"评级且无近期重复操作记录。' },
  { time: '14:26', type: 'watch', label: '⚠️ 列入观察', text: '中天科技(600522) 观察，基本面受益G7资源协议且估值最健康。' },
]

const dynamicColorMap = {
  skip: { bg: 'rgba(59,130,246,0.06)', border: 'rgba(59,130,246,0.15)', tagBg: 'rgba(59,130,246,0.08)', tagColor: '#3b82f6', tagBorder: 'rgba(59,130,246,0.15)' },
  watch: { bg: 'rgba(245,166,35,0.07)', border: 'rgba(245,166,35,0.2)', tagBg: 'rgba(245,166,35,0.08)', tagColor: '#d97706', tagBorder: 'rgba(245,166,35,0.2)' },
  execute: { bg: 'rgba(34,197,94,0.06)', border: 'rgba(34,197,94,0.15)', tagBg: 'rgba(34,197,94,0.08)', tagColor: '#16a34a', tagBorder: 'rgba(34,197,94,0.15)' },
}

const fmt = (v) => v.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const fmtPnl = (v) => (v >= 0 ? '+' : '') + fmt(Math.abs(v))

const kpiCards = computed(() => {
  const a = store.account
  const todayUp = a.today_pnl >= 0
  return [
    {
      label: '模拟总资产', value: `¥${fmt(a.total_assets)}`, sub: `初始资金 ¥${fmt(a.initial_capital)}`,
      change: `今日变化 ${fmtPnl(a.today_pnl)} (${fmtPnl(a.today_pnl / a.total_assets * 100)}%)`,
      changeType: todayUp ? 'up' : 'down',
      icon: 'ri-funds-line', iconBg: 'rgba(245,166,35,0.094)', iconColor: '#f5a623',
    },
    {
      label: '累计盈亏', value: `${fmtPnl(a.total_pnl)}`, valueColor: a.total_pnl >= 0 ? '#dc2626' : '#16a34a',
      sub: `${fmtPnl(a.total_pnl_pct)}% 总收益`,
      change: `今日 ${fmtPnl(a.today_pnl)}（落袋 + 浮动）`, changeType: a.total_pnl >= 0 ? 'up' : 'down',
      icon: 'ri-percent-line', iconBg: a.total_pnl >= 0 ? 'rgba(220,38,38,0.094)' : 'rgba(22,163,74,0.094)', iconColor: a.total_pnl >= 0 ? '#dc2626' : '#16a34a',
    },
    {
      label: '落袋盈亏', value: `${fmtPnl(a.realized_pnl)}`, valueColor: a.realized_pnl >= 0 ? '#dc2626' : '#16a34a',
      sub: '已平仓兑现盈亏', change: '基于真实成交计算', changeType: 'neutral',
      icon: 'ri-safe-line', iconBg: 'rgba(245,166,35,0.094)', iconColor: '#f5a623',
    },
    {
      label: '浮动盈亏', value: `${fmtPnl(a.unrealized_pnl)}`, valueColor: a.unrealized_pnl >= 0 ? '#dc2626' : '#16a34a',
      sub: `${a.position_count} 只持仓 mark-to-market`,
      change: `今日涨跌 ${fmtPnl(a.today_pnl)}`, changeType: a.unrealized_pnl >= 0 ? 'up' : 'down',
      icon: 'ri-line-chart-line', iconBg: a.unrealized_pnl >= 0 ? 'rgba(220,38,38,0.094)' : 'rgba(22,163,74,0.094)', iconColor: a.unrealized_pnl >= 0 ? '#dc2626' : '#16a34a',
    },
    {
      label: '持仓股票数', value: `${a.position_count} 只`, sub: `仓位使用率 ${a.position_usage}%`,
      change: '实时同步', changeType: 'neutral',
      icon: 'ri-briefcase-3-line', iconBg: 'rgba(245,166,35,0.094)', iconColor: '#f5a623',
    },
  ]
})

const holdingsWithWeight = computed(() => {
  const totalMv = store.account.total_market_value || 1
  return store.holdings.map(h => ({
    ...h,
    weight: (h.market_value / totalMv * 100).toFixed(1),
  }))
})
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <RiskBanner />

    <!-- 日期 + 状态 -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold" style="color: var(--color-text-primary)">{{ store.marketStatus.dateLabel }}</h2>
        <p class="text-xs mt-1" style="color: var(--color-text-muted)">{{ store.marketStatus.statusLabel }}</p>
      </div>
      <div class="flex items-center gap-2 px-4 py-2.5 rounded-xl card">
        <span class="w-2 h-2 rounded-full animate-pulse" :style="{ background: store.marketStatus.isOpen ? 'var(--color-success)' : '#94a3b8' }"></span>
        <span class="text-sm font-medium" style="color: var(--color-text-secondary)">{{ store.marketStatus.statusLabel }}</span>
      </div>
    </div>

    <!-- KPI 卡片 -->
    <div class="grid grid-cols-2 lg:grid-cols-5 gap-4">
      <div
        v-for="(card, i) in kpiCards"
        :key="card.label"
        class="card card-hover p-5 animate-slide-up"
        :style="{ animationDelay: i * 0.05 + 's' }"
      >
        <div class="flex items-center justify-between mb-4">
          <span class="text-xs font-medium" style="color: var(--color-text-muted)">{{ card.label }}</span>
          <div class="w-9 h-9 flex items-center justify-center rounded-xl" :style="{ background: card.iconBg }">
            <i :class="card.icon" class="text-base" :style="{ color: card.iconColor }"></i>
          </div>
        </div>
        <div class="text-2xl font-bold mb-1.5 tabular-nums" :style="{ color: card.valueColor || 'var(--color-text-primary)' }">{{ card.value }}</div>
        <div class="text-xs" style="color: var(--color-text-muted)">{{ card.sub }}</div>
        <div
          class="text-xs mt-3 pt-3 font-medium tabular-nums"
          :style="{
            color: card.changeType === 'up' ? 'var(--color-up)' : card.changeType === 'down' ? 'var(--color-down)' : 'var(--color-text-secondary)',
            borderTop: '1px solid var(--color-border-light)',
          }"
        >
          {{ card.change }}
        </div>
      </div>
    </div>

    <!-- 时段播报 -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-base font-bold" style="color: var(--color-text-primary)">今日时段播报</h3>
        <span class="text-xs" style="color: var(--color-text-muted)">A股交易日四时段</span>
      </div>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          v-for="b in broadcasts"
          :key="b.time"
          class="card p-4 flex flex-col gap-2 transition-all hover:shadow-md"
          style="opacity: 0.85"
        >
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold tabular-nums" style="color: var(--color-text-primary)">{{ b.time }} {{ b.title }}</span>
            <i class="ri-error-warning-line text-sm" style="color: var(--color-warning)"></i>
          </div>
          <span class="text-xs" style="color: var(--color-text-muted)">{{ b.time }} 生成</span>
          <p class="text-xs leading-relaxed" style="color: var(--color-text-faint)">{{ b.content }}</p>
        </div>
      </div>
    </div>

    <!-- 资产曲线 + AI决策 -->
    <div class="grid grid-cols-1 lg:grid-cols-5 gap-5">
      <!-- 资产曲线 -->
      <div class="lg:col-span-3 card p-6">
        <div class="flex items-center justify-between mb-5">
          <div>
            <h3 class="text-base font-bold" style="color: var(--color-text-primary)">资产曲线</h3>
            <div class="flex items-center gap-2 mt-1">
              <span class="text-sm font-bold tabular-nums" :style="{ color: store.account.total_pnl_pct >= 0 ? 'var(--color-up)' : 'var(--color-down)' }">
                {{ store.account.total_pnl_pct >= 0 ? '+' : '' }}{{ store.account.total_pnl_pct }}%
              </span>
              <span class="text-xs" style="color: var(--color-text-muted)">总收益率</span>
            </div>
          </div>
          <el-radio-group v-model="chartPeriod" size="small">
            <el-radio-button value="week">周</el-radio-button>
            <el-radio-button value="month">月</el-radio-button>
            <el-radio-button value="quarter">季</el-radio-button>
          </el-radio-group>
        </div>
        <div class="h-[200px] flex items-center justify-center rounded-xl" style="background: var(--color-border-light); color: var(--color-text-muted)">
          <div class="text-center">
            <i class="ri-line-chart-line text-3xl mb-2 block"></i>
            <span class="text-sm">资产曲线图表区域（接入 ECharts）</span>
          </div>
        </div>
      </div>

      <!-- AI 决策摘要 -->
      <div class="lg:col-span-2 card p-6 flex flex-col">
        <div class="flex items-center justify-between mb-5">
          <div class="flex items-center gap-2">
            <h3 class="text-base font-bold" style="color: var(--color-text-primary)">AI 今日决策</h3>
            <span class="badge" style="background: var(--color-primary-light); color: var(--color-primary)">建议口播</span>
          </div>
        </div>
        <div class="flex items-start gap-4 mb-5 flex-1">
          <div class="w-14 h-14 rounded-2xl shrink-0 flex items-center justify-center gradient-primary" style="box-shadow: var(--shadow-glow)">
            <i class="ri-robot-2-line text-2xl text-white"></i>
          </div>
          <div>
            <div class="flex items-center gap-2 mb-2">
              <span class="text-sm font-bold gradient-text">AI 交易员</span>
              <span class="w-2 h-2 rounded-full animate-pulse" style="background: var(--color-success)"></span>
            </div>
            <p class="text-sm leading-relaxed" style="color: var(--color-text-secondary)">今日暂无执行决策，AI 持续监控市场中…</p>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3 mb-4 p-4 rounded-xl" style="background: var(--color-border-light)">
          <div class="text-center">
            <div class="text-lg font-bold tabular-nums" style="color: var(--color-primary)">{{ store.account.position_count }}</div>
            <div class="text-xs mt-0.5" style="color: var(--color-text-muted)">持仓</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-bold tabular-nums" style="color: var(--color-primary)">{{ store.account.position_usage }}%</div>
            <div class="text-xs mt-0.5" style="color: var(--color-text-muted)">仓位</div>
          </div>
        </div>
        <button class="w-full py-3 rounded-xl text-sm font-medium transition-all hover:shadow-md" style="background: var(--color-primary-light); border: 1px solid rgba(99,102,241,0.2); color: var(--color-primary)">
          <i class="ri-route-line mr-2"></i>查看今日完整决策过程
        </button>
      </div>
    </div>

    <!-- AI 动态 + 持仓 -->
    <div class="grid grid-cols-1 lg:grid-cols-5 gap-5">
      <!-- AI 动态 -->
      <div class="lg:col-span-3 card p-6 flex flex-col" style="min-height: 400px">
        <div class="flex items-center justify-between mb-5">
          <div class="flex items-center gap-2">
            <h3 class="text-base font-bold" style="color: var(--color-text-primary)">AI 实时分析动态</h3>
            <div class="flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full animate-pulse" style="background: var(--color-success)"></span>
              <span class="text-xs font-medium" style="color: var(--color-success)">实时</span>
            </div>
          </div>
          <div class="hidden sm:flex items-center gap-4">
            <div class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full" style="background: #3b82f6"></span><span class="text-xs" style="color: var(--color-text-muted)">跳过</span></div>
            <div class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full" style="background: var(--color-warning)"></span><span class="text-xs" style="color: var(--color-text-muted)">观察</span></div>
            <div class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full" style="background: var(--color-success)"></span><span class="text-xs" style="color: var(--color-text-muted)">执行</span></div>
          </div>
        </div>
        <div class="flex-1 overflow-hidden space-y-2.5">
          <div
            v-for="d in aiDynamics"
            :key="d.time + d.type"
            class="flex items-start gap-3 p-3.5 rounded-xl transition-all hover:translate-x-1"
            :style="{ background: dynamicColorMap[d.type].bg, border: `1px solid ${dynamicColorMap[d.type].border}` }"
          >
            <span class="text-xs font-mono shrink-0 mt-0.5 tabular-nums" style="color: var(--color-text-muted)">{{ d.time }}</span>
            <span
              class="text-xs px-2.5 py-1 rounded-lg font-medium shrink-0 mt-0.5"
              :style="{ background: dynamicColorMap[d.type].tagBg, color: dynamicColorMap[d.type].tagColor, border: `1px solid ${dynamicColorMap[d.type].tagBorder}` }"
            >
              {{ d.label }}
            </span>
            <p class="text-xs leading-relaxed flex-1" style="color: var(--color-text-secondary)">{{ d.text }}</p>
          </div>
        </div>
      </div>

      <!-- 持仓快照 -->
      <div class="lg:col-span-2 card p-6 flex flex-col" style="min-height: 400px">
        <div class="flex items-center justify-between mb-5">
          <h3 class="text-base font-bold" style="color: var(--color-text-primary)">持仓快照</h3>
          <router-link to="/positions" class="text-xs font-medium flex items-center gap-1 transition-colors hover:opacity-70" style="color: var(--color-primary)">
            查看全部 <i class="ri-arrow-right-line"></i>
          </router-link>
        </div>
        <el-table v-if="holdingsWithWeight.length" :data="holdingsWithWeight" size="small" class="flex-1">
          <el-table-column label="股票" min-width="100">
            <template #default="{ row }">
              <div class="font-semibold text-xs" style="color: var(--color-text-primary)">{{ row.name }}</div>
              <div class="text-[10px] font-mono" style="color: var(--color-text-muted)">{{ row.code }}</div>
            </template>
          </el-table-column>
          <el-table-column label="现价" align="right" min-width="70">
            <template #default="{ row }">
              <div class="text-xs font-semibold tabular-nums" style="color: var(--color-text-primary)">¥{{ row.current_price }}</div>
            </template>
          </el-table-column>
          <el-table-column label="浮动盈亏" align="right" min-width="80">
            <template #default="{ row }">
              <div class="text-xs font-semibold tabular-nums" :style="{ color: row.pnl >= 0 ? 'var(--color-up)' : 'var(--color-down)' }">
                {{ row.pnl >= 0 ? '+' : '' }}{{ (row.pnl / 10000).toFixed(2) }}万
              </div>
              <div class="text-[10px] tabular-nums" :style="{ color: row.pnl >= 0 ? 'var(--color-up)' : 'var(--color-down)' }">
                {{ row.pnl_pct >= 0 ? '+' : '' }}{{ row.pnl_pct }}%
              </div>
            </template>
          </el-table-column>
          <el-table-column label="市值占比" align="right" min-width="80">
            <template #default="{ row }">
              <div class="flex items-center justify-end gap-2">
                <div class="w-12 h-1.5 rounded-full overflow-hidden hidden sm:block" style="background: var(--color-border-light)">
                  <div class="h-full rounded-full transition-all" :style="{ width: row.weight + '%', background: 'var(--color-primary)' }"></div>
                </div>
                <span class="text-xs tabular-nums" style="color: var(--color-text-secondary)">{{ row.weight }}%</span>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <div v-else class="flex-1 flex flex-col items-center justify-center text-center">
          <div class="w-14 h-14 rounded-2xl flex items-center justify-center mb-3" style="background: var(--color-border-light)">
            <i class="ri-briefcase-3-line text-2xl" style="color: var(--color-text-faint)"></i>
          </div>
          <p class="text-sm" style="color: var(--color-text-muted)">暂无持仓</p>
          <router-link to="/simtrade" class="text-xs mt-2" style="color: var(--color-primary)">去模拟交易建仓 →</router-link>
        </div>
        <div v-if="holdingsWithWeight.length" class="mt-4 pt-4 flex items-center justify-between" style="border-top: 1px solid var(--color-border-light)">
          <span class="text-xs" style="color: var(--color-text-muted)">总浮动盈亏</span>
          <span class="text-base font-bold tabular-nums" :style="{ color: store.account.unrealized_pnl >= 0 ? 'var(--color-up)' : 'var(--color-down)' }">
            {{ store.account.unrealized_pnl >= 0 ? '+' : '' }}¥{{ Math.abs(store.account.unrealized_pnl).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
          </span>
        </div>
      </div>
    </div>

    <!-- 底部两列 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <div class="card p-5">
        <div class="flex items-center justify-between mb-4">
          <h4 class="text-sm font-bold flex items-center gap-2" style="color: var(--color-text-primary)">
            <i class="ri-calendar-event-line" style="color: var(--color-primary)"></i>财报日历
          </h4>
          <span class="text-xs" style="color: var(--color-text-muted)">持仓 {{ store.account.position_count }} 只</span>
        </div>
        <div class="text-xs text-center py-8" style="color: var(--color-text-muted)">
          <i class="ri-calendar-line text-2xl block mb-2" style="color: var(--color-text-faint)"></i>
          近期无重要日程
        </div>
      </div>
      <div class="card p-5">
        <div class="flex items-center justify-between mb-4">
          <h4 class="text-sm font-bold flex items-center gap-2" style="color: var(--color-text-primary)">
            <i class="ri-line-chart-line" style="color: var(--color-primary)"></i>持仓股今日涨跌
          </h4>
          <div class="flex items-center gap-2 text-xs" style="color: var(--color-text-muted)">
            <span>{{ store.account.position_count }} 只</span><span>·</span><span class="tabular-nums">{{ store.marketStatus.currentTime }}</span>
          </div>
        </div>
        <div v-if="holdingsWithWeight.length">
          <div v-for="h in holdingsWithWeight" :key="h.code" class="grid items-center gap-3 py-2.5" style="grid-template-columns: 120px 1fr 70px">
            <div>
              <div class="text-xs font-semibold" style="color: var(--color-text-primary)">{{ h.name }}</div>
              <div class="text-[10px] font-mono" style="color: var(--color-text-muted)">{{ h.code }}</div>
            </div>
            <div class="relative h-2 rounded-full" style="background: var(--color-border-light)">
              <div
                class="absolute inset-y-0 left-1/2 rounded-full transition-all"
                :style="{
                  width: Math.min(Math.abs(h.change_pct) / 10 * 50, 50) + '%',
                  left: h.change_pct >= 0 ? '50%' : 'auto',
                  right: h.change_pct >= 0 ? 'auto' : '50%',
                  background: h.change_pct >= 0 ? 'var(--color-up)' : 'var(--color-down)',
                }"
              ></div>
              <div class="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 w-px h-3" style="background: var(--color-border)"></div>
            </div>
            <div class="text-right text-sm font-bold tabular-nums" :style="{ color: h.change_pct >= 0 ? 'var(--color-up)' : 'var(--color-down)' }">
              {{ h.change_pct >= 0 ? '+' : '' }}{{ h.change_pct }}%
            </div>
          </div>
        </div>
        <div v-else class="text-xs text-center py-8" style="color: var(--color-text-muted)">暂无持仓数据</div>
      </div>
    </div>
  </div>
</template>
