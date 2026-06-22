<script setup>
import { ref } from 'vue'
import { useAppStore } from '@/stores/app'
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

const kpiCards = [
  { label: '模拟总资产', value: '¥1,081,219.97', sub: '初始资金 ¥1,000,000', change: '今日变化 +¥0 (+0.00%)', changeType: 'up', icon: 'ri-funds-line', iconBg: 'rgba(245,166,35,0.094)', iconColor: '#f5a623' },
  { label: '累计盈亏', value: '+¥81,220', valueColor: '#dc2626', sub: '+8.12% 总收益', change: '今日 +¥0（落袋 + 浮动）', changeType: 'up', icon: 'ri-percent-line', iconBg: 'rgba(220,38,38,0.094)', iconColor: '#dc2626' },
  { label: '落袋盈亏', value: '+¥50,804', valueColor: '#dc2626', sub: '累计止盈 +¥72,321 · 累计止损 -¥24,816 · 手续费 -¥2,797', change: '今日卖出兑现 +¥0', changeType: 'up', icon: 'ri-safe-line', iconBg: 'rgba(220,38,38,0.094)', iconColor: '#dc2626' },
  { label: '浮动盈亏', value: '+¥33,213', valueColor: '#dc2626', sub: '4 只持仓 mark-to-market', change: '今日涨跌 +¥0', changeType: 'up', icon: 'ri-line-chart-line', iconBg: 'rgba(220,38,38,0.094)', iconColor: '#dc2626' },
  { label: '持仓股票数', value: '4 只', sub: '仓位使用率 52%', change: '今日无持仓变动', changeType: 'neutral', icon: 'ri-briefcase-3-line', iconBg: 'rgba(245,166,35,0.094)', iconColor: '#f5a623' },
]

const dynamicColorMap = {
  skip: { bg: 'rgba(59,130,246,0.06)', border: 'rgba(59,130,246,0.15)', tagBg: 'rgba(59,130,246,0.08)', tagColor: '#3b82f6', tagBorder: 'rgba(59,130,246,0.15)' },
  watch: { bg: 'rgba(245,166,35,0.07)', border: 'rgba(245,166,35,0.2)', tagBg: 'rgba(245,166,35,0.08)', tagColor: '#d97706', tagBorder: 'rgba(245,166,35,0.2)' },
  execute: { bg: 'rgba(34,197,94,0.06)', border: 'rgba(34,197,94,0.15)', tagBg: 'rgba(34,197,94,0.08)', tagColor: '#16a34a', tagBorder: 'rgba(34,197,94,0.15)' },
}
</script>

<template>
  <div class="space-y-5">
    <RiskBanner />

    <!-- 日期 + 状态 -->
    <div class="flex items-center justify-between">
      <div class="text-xs" style="color: #64748b">{{ store.marketStatus.dateLabel }} · {{ store.marketStatus.label }}</div>
      <div class="flex items-center gap-2 px-3 py-2 rounded-lg" style="background: #f1f5f9; border: 1px solid #e2e8f0">
        <span class="w-2 h-2 rounded-full" style="background: #64748b"></span>
        <span class="text-xs font-medium" style="color: #475569">{{ store.marketStatus.statusLabel }}</span>
      </div>
    </div>

    <!-- KPI 卡片 -->
    <div class="grid grid-cols-2 lg:grid-cols-5 gap-4">
      <div
        v-for="card in kpiCards"
        :key="card.label"
        class="rounded-xl p-5 transition-all duration-200 hover:shadow-md hover:-translate-y-0.5"
        style="background: #fff; border: 1px solid #e2e8f0"
      >
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-medium" style="color: #64748b">{{ card.label }}</span>
          <div class="w-8 h-8 flex items-center justify-center rounded-lg" :style="{ background: card.iconBg }">
            <i :class="card.icon" class="text-sm" :style="{ color: card.iconColor }"></i>
          </div>
        </div>
        <div class="text-xl font-bold mb-1" :style="{ color: card.valueColor || '#0f172a' }">{{ card.value }}</div>
        <div class="text-[11px]" style="color: #94a3b8">{{ card.sub }}</div>
        <div
          class="text-[11px] mt-1 pt-1.5 font-medium"
          :style="{
            color: card.changeType === 'up' ? '#dc2626' : card.changeType === 'down' ? '#16a34a' : '#475569',
            borderTop: '1px dashed #e2e8f0',
          }"
        >
          {{ card.change }}
        </div>
      </div>
    </div>

    <!-- 时段播报 -->
    <div>
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm font-semibold" style="color: #0f172a">今日时段播报</h3>
        <span class="text-xs" style="color: #94a3b8">A股交易日四时段</span>
      </div>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div
          v-for="b in broadcasts"
          :key="b.time"
          class="rounded-xl p-4 flex flex-col gap-2.5 transition-all duration-200 hover:bg-gray-50"
          style="background: #f8fafc; border: 1px solid #e2e8f0; opacity: 0.75"
        >
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold" style="color: #0f172a">{{ b.time }} {{ b.title }}</span>
            <i class="ri-error-warning-line text-sm" style="color: #f59e0b"></i>
          </div>
          <span class="text-xs" style="color: #94a3b8">{{ b.time }} 生成</span>
          <p class="text-xs leading-relaxed" style="color: #cbd5e1">{{ b.content }}</p>
        </div>
      </div>
    </div>

    <!-- 资产曲线 + AI决策 -->
    <div class="grid grid-cols-1 lg:grid-cols-5 gap-5">
      <!-- 资产曲线 -->
      <div class="lg:col-span-3 rounded-xl p-5" style="background: #fff; border: 1px solid #e2e8f0">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-sm font-semibold" style="color: #0f172a">资产曲线</h3>
            <div class="flex items-center gap-1.5 mt-0.5">
              <span class="text-xs font-semibold" style="color: #dc2626">+8.12%</span>
              <span class="text-xs" style="color: #94a3b8">近30日收益</span>
            </div>
            <div class="flex items-center gap-3 mt-1">
              <span class="text-xs" style="color: #94a3b8">夏普 <strong style="color: #d97706">7.72</strong></span>
              <span class="text-xs" style="color: #94a3b8">最大回撤 <strong style="color: #dc2626">3.59%</strong></span>
            </div>
          </div>
          <el-radio-group v-model="chartPeriod" size="small">
            <el-radio-button value="week">周</el-radio-button>
            <el-radio-button value="month">月</el-radio-button>
            <el-radio-button value="quarter">季</el-radio-button>
          </el-radio-group>
        </div>
        <div class="h-[180px] flex items-center justify-center" style="color: #94a3b8">
          <span class="text-sm">📈 资产曲线图表区域（接入 ECharts）</span>
        </div>
      </div>

      <!-- AI 决策摘要 -->
      <div class="lg:col-span-2 rounded-xl p-5 flex flex-col" style="background: #fff; border: 1px solid #e2e8f0">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <h3 class="text-sm font-semibold" style="color: #0f172a">AI 今日决策摘要</h3>
            <span class="text-[10px] px-1.5 py-0.5 rounded" style="background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0">建议口播</span>
          </div>
          <span class="text-xs px-2 py-1 rounded-full" style="background: rgba(245,166,35,0.1); color: #d97706; border: 1px solid rgba(245,166,35,0.2)">2026年06月19日</span>
        </div>
        <div class="flex items-start gap-4 mb-4 flex-1">
          <div class="w-12 h-12 rounded-full shrink-0 flex items-center justify-center" style="border: 2px solid rgba(245,166,35,0.3); background: rgba(245,166,35,0.1)">
            <i class="ri-robot-2-line text-xl" style="color: #d97706"></i>
          </div>
          <div>
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xs font-semibold" style="color: #d97706">AI 交易员</span>
              <span class="w-1.5 h-1.5 rounded-full animate-pulse" style="background: #22c55e"></span>
            </div>
            <p class="text-sm leading-relaxed" style="color: #334155">今日暂无执行决策，AI 持续监控市场中…</p>
          </div>
        </div>
        <div class="flex items-center gap-4 mb-4 py-3 rounded-xl px-4" style="background: #f8fafc; border: 1px solid #f1f5f9">
          <div class="flex-1 text-center">
            <div class="text-xs font-bold" style="color: #d97706">20只</div>
            <div class="text-xs mt-0.5" style="color: #94a3b8">今日扫描</div>
          </div>
          <div class="flex-1 text-center">
            <div class="text-xs font-bold" style="color: #d97706">—</div>
            <div class="text-xs mt-0.5" style="color: #94a3b8">执行</div>
          </div>
          <div class="flex-1 text-center">
            <div class="text-xs font-bold" style="color: #d97706">15只</div>
            <div class="text-xs mt-0.5" style="color: #94a3b8">候选</div>
          </div>
          <div class="flex-1 text-center">
            <div class="text-xs font-bold" style="color: #d97706">100%</div>
            <div class="text-xs mt-0.5" style="color: #94a3b8">仓位</div>
          </div>
        </div>
        <el-button class="w-full !py-3 !rounded-xl !text-sm !font-medium" style="background: rgba(245,166,35,0.08); border: 1px solid rgba(245,166,35,0.25); color: #d97706">
          <i class="ri-route-line mr-2"></i>查看今日完整决策过程
        </el-button>
      </div>
    </div>

    <!-- AI 动态 + 持仓 -->
    <div class="grid grid-cols-1 lg:grid-cols-5 gap-5">
      <!-- AI 动态 -->
      <div class="lg:col-span-3 rounded-xl p-5 flex flex-col" style="background: #fff; border: 1px solid #e2e8f0; min-height: 380px">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <h3 class="text-sm font-semibold" style="color: #0f172a">AI 实时分析动态</h3>
            <div class="flex items-center gap-1">
              <span class="w-1.5 h-1.5 rounded-full" style="background: #22c55e"></span>
              <span class="text-xs" style="color: #16a34a">实时</span>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <div class="hidden sm:flex items-center gap-3">
              <div class="flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full" style="background: #3b82f6"></span><span class="text-xs" style="color: #94a3b8">分析跳过</span></div>
              <div class="flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full" style="background: #f5a623"></span><span class="text-xs" style="color: #94a3b8">列入观察</span></div>
              <div class="flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full" style="background: #22c55e"></span><span class="text-xs" style="color: #94a3b8">执行决策</span></div>
            </div>
            <span class="text-xs font-medium cursor-pointer" style="color: #d97706">查看全部</span>
          </div>
        </div>
        <div class="flex-1 overflow-hidden space-y-2">
          <div
            v-for="d in aiDynamics"
            :key="d.time + d.type"
            class="flex items-start gap-3 py-2.5 px-3 rounded-lg transition-all duration-200 hover:translate-x-0.5"
            :style="{ background: dynamicColorMap[d.type].bg, border: `1px solid ${dynamicColorMap[d.type].border}` }"
          >
            <span class="text-xs font-mono shrink-0 mt-0.5" style="color: #94a3b8">{{ d.time }}</span>
            <span
              class="text-xs px-2 py-0.5 rounded-md font-medium shrink-0 mt-0.5"
              :style="{ background: dynamicColorMap[d.type].tagBg, color: dynamicColorMap[d.type].tagColor, border: `1px solid ${dynamicColorMap[d.type].tagBorder}` }"
            >
              {{ d.label }}
            </span>
            <p class="text-xs leading-relaxed flex-1" style="color: #334155">{{ d.text }}</p>
          </div>
        </div>
        <div class="mt-4 pt-3 flex items-center gap-4" style="border-top: 1px solid #f1f5f9">
          <div class="flex items-center gap-1.5"><span class="text-xs" style="color: #94a3b8">今日已分析</span><span class="text-xs font-bold" style="color: #334155">50只</span></div>
          <div class="flex items-center gap-1.5"><span class="text-xs" style="color: #94a3b8">候选</span><span class="text-xs font-bold" style="color: #d97706">40只</span></div>
          <div class="flex items-center gap-1.5"><span class="text-xs" style="color: #94a3b8">执行</span><span class="text-xs font-bold" style="color: #16a34a">0笔</span></div>
        </div>
      </div>

      <!-- 持仓快照 -->
      <div class="lg:col-span-2 rounded-xl p-5 flex flex-col" style="background: #fff; border: 1px solid #e2e8f0; min-height: 380px">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold" style="color: #0f172a">持仓快照</h3>
          <router-link to="/positions" class="text-xs font-medium" style="color: #d97706">查看全部 <i class="ri-arrow-right-line"></i></router-link>
        </div>
        <el-table :data="store.holdings" size="small" class="flex-1">
          <el-table-column label="股票" min-width="100">
            <template #default="{ row }">
              <div class="font-semibold text-xs" style="color: #0f172a">{{ row.name }}</div>
              <div class="text-[10px]" style="color: #94a3b8">{{ row.code }}</div>
            </template>
          </el-table-column>
          <el-table-column label="浮动盈亏" align="right" min-width="80">
            <template #default="{ row }">
              <div class="text-xs font-semibold" :style="{ color: row.pnl >= 0 ? '#dc2626' : '#16a34a' }">
                {{ row.pnl >= 0 ? '+' : '' }}{{ (row.pnl / 10000).toFixed(2) }}万
              </div>
              <div class="text-[10px]" :style="{ color: row.pnl >= 0 ? '#dc2626' : '#16a34a' }">
                {{ row.pnlPercent >= 0 ? '+' : '' }}{{ row.pnlPercent }}%
              </div>
            </template>
          </el-table-column>
          <el-table-column label="市值占比" align="right" min-width="80">
            <template #default="{ row }">
              <div class="flex items-center justify-end gap-2">
                <div class="w-12 h-1.5 rounded-full overflow-hidden hidden sm:block" style="background: #f1f5f9">
                  <div class="h-full rounded-full" :style="{ width: row.weight + '%', background: '#f5a623' }"></div>
                </div>
                <span class="text-xs" style="color: #64748b">{{ row.weight }}%</span>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <div class="mt-3 pt-3 flex items-center justify-between" style="border-top: 1px solid #f1f5f9">
          <span class="text-xs" style="color: #94a3b8">总浮动盈亏</span>
          <span class="text-sm font-bold" style="color: #dc2626">+¥33,213</span>
        </div>
      </div>
    </div>

    <!-- 底部两列 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div class="rounded-xl p-4" style="background: #fff; border: 1px solid #e2e8f0">
        <div class="flex items-center justify-between mb-3">
          <h4 class="text-sm font-semibold flex items-center gap-2" style="color: #0f172a">
            <i class="ri-calendar-event-line text-sm" style="color: #f5a623"></i>财报日历
          </h4>
          <span class="text-xs" style="color: #94a3b8">持仓 4 只</span>
        </div>
        <div class="text-xs text-center py-6" style="color: #94a3b8">近期无重要日程（财报披露/业绩预告/限售解禁）</div>
      </div>
      <div class="rounded-xl p-4" style="background: #fff; border: 1px solid #e2e8f0">
        <div class="flex items-center justify-between mb-3">
          <h4 class="text-sm font-semibold flex items-center gap-2" style="color: #0f172a">
            <i class="ri-line-chart-line text-sm" style="color: #f5a623"></i>持仓股今日涨跌
          </h4>
          <div class="flex items-center gap-3 text-xs" style="color: #94a3b8">
            <span>4 只</span><span style="color: #cbd5e1">·</span><span>截至 19:01</span>
          </div>
        </div>
        <div v-for="h in store.holdings" :key="h.code" class="grid items-center gap-3 py-2" style="grid-template-columns: 110px 1fr 64px">
          <div>
            <div class="text-xs font-medium" style="color: #0f172a">{{ h.name }}</div>
            <div class="text-[10px] font-mono" style="color: #94a3b8">{{ h.code }}</div>
          </div>
          <div class="relative h-2 rounded-full" style="background: #f1f5f9">
            <div
              class="absolute inset-y-0 left-0 rounded-full"
              :style="{
                width: Math.abs(h.pnlPercent) / 14 * 100 + '%',
                background: h.pnl >= 0 ? 'rgba(220,38,38,0.85)' : 'rgba(22,163,74,0.85)',
              }"
            ></div>
          </div>
          <div class="text-right text-sm font-semibold tabular-nums" :style="{ color: h.pnl >= 0 ? '#dc2626' : '#16a34a' }">
            {{ h.pnlPercent >= 0 ? '+' : '' }}{{ h.pnlPercent }}%
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
