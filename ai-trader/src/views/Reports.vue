<script setup>
import { ref, computed } from 'vue'
import RiskBanner from '@/components/RiskBanner.vue'

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

// 日历收益数据 (模拟)
const calendarData = [
  { day: '', offset: true },
  { day: '', offset: true },
  { day: 1, value: 0 },
  { day: 2, value: 1200 },
  { day: 3, value: -300 },
  { day: 4, value: 0 },
  { day: 5, value: 0 },
  { day: 6, value: 2800 },
  { day: 7, value: -150 },
  { day: 8, value: 0 },
  { day: 9, value: 3600 },
  { day: 10, value: 1500 },
  { day: 11, value: -200 },
  { day: 12, value: 0 },
  { day: 13, value: 0 },
  { day: 14, value: 800 },
  { day: 15, value: 4200 },
  { day: 16, value: -600 },
  { day: 17, value: 0 },
  { day: 18, value: 0 },
  { day: 19, value: 2100 },
  { day: 20, value: 500 },
  { day: 21, value: 0 },
  { day: 22, value: 1800 },
  { day: 23, value: 0, today: true },
]

const getCalendarColor = (v) => {
  if (!v || v === 0) return { bg: '#f8fafc', color: '#94a3b8', border: '#f1f5f9' }
  if (v > 3000) return { bg: 'rgba(220,38,38,0.25)', color: '#dc2626', border: 'rgba(220,38,38,0.3)' }
  if (v > 0) return { bg: 'rgba(220,38,38,0.12)', color: '#dc2626', border: 'rgba(220,38,38,0.2)' }
  return { bg: 'rgba(22,163,74,0.12)', color: '#16a34a', border: 'rgba(22,163,74,0.2)' }
}

// AI 决策记录
const decisions = [
  { time: '06/10 09:38', name: '圣泉集团', action: '观察', actionColor: '#64748b', reason: '综合四维分析：基本面中性偏暖但估值承压，新闻面API支撑有限，情绪与技术面短期共振但超买明显。当前已持仓2400股且为当日新建仓，严格遵循T+1规则，仅可持有观察。不追加、不减仓、不调仓，等待次日价格行为与量能验证。仅为模拟演示。', confidence: '置信度 3/5' },
  { time: '06/10 09:33', name: '圣泉集团', action: '买入', actionColor: '#16a34a', reason: '在全部候选标的中，圣泉集团是唯一获基本面分析师明确"买入"评级、且估值（PE 47.3x）显著低于行业均值（65.2x）与中位数（88x）的标的；其化工新材料逻辑独立于高估值AI链，抗扰动性强。新闻面人民币升值对其成本端构成温和利好，风险收益比最优。仅为模拟演示。', confidence: '置信度 3/5' },
  { time: '06/10 09:32', name: '天孚通信', action: '观察', actionColor: '#64748b', reason: '综合四位分析师判断，天孚通信在fundamental中获"持有"、news中未被覆盖但无负面、sentiment中明确标注"持有"且有010万大单异动支撑，是唯一在三维度均无卖出信号、且具备技术面与产业逻辑双重验证的标的。相较海光信息（PE 228x）与圣泉集团（纯题材涨停），其估值更可持续，适合作为AI硬件主线中的稳健持仓锚点。仅为模拟演示。', confidence: '置信度 4/5' },
]

// 持仓热力图
const heatmapItems = [
  { name: '圣泉集团', weight: '11.2%', pnl: '+4.25%', color: 'rgba(220,38,38,0.247)', borderColor: 'rgba(220,38,38,0.25)', flex: 1.117 },
  { name: '中际旭创', weight: '9.0%', pnl: '-2.29%', pnlColor: '#16a34a', color: 'rgba(22,163,74,0.18)', borderColor: 'rgba(22,163,74,0.25)', flex: 0.898 },
  { name: '亨通光电', weight: '22.2%', pnl: '+2.80%', color: 'rgba(220,38,38,0.2)', borderColor: 'rgba(220,38,38,0.25)', flex: 2.215 },
  { name: '宁德时代', weight: '9.6%', pnl: '+0.02%', color: 'rgba(220,38,38,0.1)', borderColor: 'rgba(220,38,38,0.25)', flex: 0.956 },
  { name: '海光信息', weight: '13.6%', pnl: '+6.58%', color: 'rgba(220,38,38,0.33)', borderColor: 'rgba(220,38,38,0.25)', flex: 1.363 },
  { name: '中天科技', weight: '23.8%', pnl: '+2.84%', color: 'rgba(220,38,38,0.2)', borderColor: 'rgba(220,38,38,0.25)', flex: 2.376 },
  { name: '东山精密', weight: '10.7%', pnl: '+8.98%', color: 'rgba(220,38,38,0.416)', borderColor: 'rgba(220,38,38,0.25)', flex: 1.075 },
]

// 板块配置
const sectorAllocation = [
  { name: 'C38电气机械和器材制造业', pct: 100, count: '2只' },
]

// AI 亏损复盘
const lossItems = [
  { name: '中际旭创', code: '300308', industry: 'C39计算机、通信和其他电子设备制造业', trades: '3 次', lossPct: '-2.29%', lossAmt: '-¥5,266' },
]
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
        <div class="text-5xl font-black mb-1" style="color: #dc2626">+8.44%</div>
        <div class="flex items-center gap-2 mb-4">
          <span class="text-xs" style="color: #94a3b8">最大回撤：3.59%</span>
        </div>
        <div class="pt-3" style="border-top: 1px solid #f1f5f9">
          <p class="text-xs mb-1" style="color: #94a3b8">资产净值</p>
          <p class="text-xl font-bold" style="color: #0f172a">¥1,084,407.41</p>
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
        <span class="text-xs" style="color: #94a3b8">本月共 {{ decisions.length }} 条决策</span>
      </div>
      <div class="overflow-x-auto">
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
                    background: d.action === '买入' ? 'rgba(22,163,74,0.08)' : 'rgba(100,116,139,0.08)',
                    color: d.actionColor,
                    border: '1px solid ' + (d.action === '买入' ? 'rgba(22,163,74,0.2)' : 'rgba(100,116,139,0.2)')
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
      <div class="flex gap-2 h-52">
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
    </div>

    <!-- 板块配置 -->
    <div class="rounded-xl p-5" style="background: #fff; border: 1px solid #e2e8f0">
      <div class="flex items-center justify-between mb-4">
        <h4 class="text-sm font-semibold" style="color: #0f172a">当前板块配置</h4>
        <span class="text-xs" style="color: #94a3b8">颜色深度 = AI仓位权重</span>
      </div>
      <div class="space-y-2">
        <div v-for="sector in sectorAllocation" :key="sector.name" class="flex items-center gap-3">
          <span class="text-xs w-28 shrink-0" style="color: #334155">{{ sector.name }}</span>
          <div class="flex-1 min-w-0 h-7 rounded-lg overflow-hidden relative" style="background: rgba(245,166,35,0.06)">
            <div
              class="absolute inset-y-0 left-0 rounded-lg flex items-center px-2 transition-all"
              :style="{ width: sector.pct + '%', minWidth: '48px', background: 'rgba(245,166,35,0.65)', border: '1px solid rgba(245,166,35,0.75)' }"
            >
              <span class="text-xs font-semibold whitespace-nowrap" style="color: #d97706">{{ sector.pct }}.0%</span>
            </div>
          </div>
          <span class="text-xs w-8 shrink-0 text-right" style="color: #94a3b8">{{ sector.count }}</span>
        </div>
      </div>
    </div>

    <!-- AI 亏损复盘 -->
    <div class="rounded-xl p-5" style="background: #fff; border: 1px solid #e2e8f0">
      <div class="flex items-center gap-2 mb-4">
        <h4 class="text-sm font-semibold" style="color: #0f172a">AI 亏损复盘</h4>
        <span class="text-xs px-2 py-0.5 rounded-full" style="background: rgba(220,38,38,0.06); color: #dc2626; border: 1px solid rgba(220,38,38,0.15)">亏损仓位</span>
        <span class="text-xs ml-1" style="color: #94a3b8">透明展示AI的亏损，建立信任</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr style="border-bottom: 1px solid #f1f5f9">
              <th class="text-left px-3 py-3 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">股票</th>
              <th class="text-left px-3 py-3 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">行业</th>
              <th class="text-left px-3 py-3 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">交易次数</th>
              <th class="text-left px-3 py-3 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">亏损幅度</th>
              <th class="text-left px-3 py-3 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">亏损金额</th>
              <th class="text-left px-3 py-3 text-xs font-medium whitespace-nowrap" style="color: #94a3b8"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in lossItems" :key="item.code" class="hover:bg-gray-50 transition-colors" style="border-bottom: 1px solid #f8fafc">
              <td class="px-3 py-4">
                <div class="font-semibold text-xs" style="color: #0f172a">{{ item.name }}</div>
                <div class="text-xs" style="color: #94a3b8">{{ item.code }}</div>
              </td>
              <td class="px-3 py-4 text-xs" style="color: #64748b">{{ item.industry }}</td>
              <td class="px-3 py-4 text-xs" style="color: #64748b">{{ item.trades }}</td>
              <td class="px-3 py-4">
                <span class="text-sm font-bold" style="color: #16a34a">{{ item.lossPct }}</span>
              </td>
              <td class="px-3 py-4">
                <span class="text-sm font-bold" style="color: #16a34a">{{ item.lossAmt }}</span>
              </td>
              <td class="px-3 py-4">
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
    </div>
  </div>
</template>
