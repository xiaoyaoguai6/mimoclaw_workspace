<script setup>
import { ref, computed } from 'vue'
import RiskBanner from '@/components/RiskBanner.vue'

const activeTab = ref('current')
const riskExpanded = ref(true)

const summaryStats = [
  { label: '今日盈亏', value: '+¥0', color: '#dc2626' },
  { label: '累计收益率', value: '+8.44%', color: '#dc2626' },
  { label: '总浮动盈亏', value: '+¥4,047', color: '#dc2626' },
  { label: '浮动盈亏率', value: '+0.40%', color: '#dc2626' },
]

const riskConcentration = [
  { name: '宁德时代', pct: 63, color: '#d97706' },
  { name: '亨通光电', pct: 37, color: '#f59e0b' },
]

const positions = ref([
  {
    code: '600487', name: '亨通光电', shares: '1,200 股', costAvg: '¥116.79', current: '¥120.13',
    costTotal: '¥140,151', marketValue: '¥144,156', pnl: '+¥4,005', pnlPct: '+2.86%',
    tp: '¥123.33 (+2.7%)', sl: '¥109.24 (-9.1%)',
    buildDate: '06/10', buildAgo: '13 天前', aiStatus: '持有中', aiSub: '已止盈 2 档',
    aiStatusColor: '#16a34a',
  },
  {
    code: '300750', name: '宁德时代', shares: '600 股', costAvg: '¥408.91', current: '¥408.98',
    costTotal: '¥245,346', marketValue: '¥245,388', pnl: '+¥42', pnlPct: '+0.02%',
    tp: '¥419.13 (+2.5%)', sl: '¥398.40 (-2.6%)',
    buildDate: '06/22', buildAgo: '昨天建仓', aiStatus: '持有中', aiSub: '',
    aiStatusColor: '#16a34a',
  },
])

const totals = computed(() => {
  return { costTotal: '¥385,497', marketValue: '¥389,544', pnl: '+¥4,047', pnlPct: '+0.40%' }
})

const drawdownMin = { name: '宁德时代', pct: '+0.02%', profit: '盈利 ¥42', status: '持有中' }
</script>

<template>
  <div class="max-w-screen-xl">
    <RiskBanner />

    <!-- 顶部统计 -->
    <div class="flex items-center justify-between mb-5">
      <div></div>
      <div class="flex items-center gap-3">
        <div v-for="stat in summaryStats" :key="stat.label" class="text-right" :class="stat !== summaryStats[summaryStats.length - 1] ? 'pr-3' : ''" :style="stat !== summaryStats[summaryStats.length - 1] ? { borderRight: '1px solid #e2e8f0' } : {}">
          <p class="text-xs" style="color: #94a3b8">{{ stat.label }}</p>
          <p class="text-lg font-bold" :style="{ color: stat.color }">{{ stat.value }}</p>
        </div>
      </div>
    </div>

    <!-- 整体风险评估 -->
    <div class="rounded-xl mb-5 overflow-hidden" style="background: #fff; border: 1px solid #e2e8f0">
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
            <p class="text-xs" style="color: #94a3b8">基于当前 2 只持仓的综合风险分析</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <span class="px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap" style="background: rgba(220,38,38,0.08); color: #dc2626; border: 1px solid rgba(220,38,38,0.2)">
            <i class="ri-alarm-warning-line mr-1"></i>高风险
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
                <div v-for="item in riskConcentration" :key="item.name">
                  <div class="flex items-center justify-between mb-0.5">
                    <span class="text-xs" style="color: #64748b">{{ item.name }}</span>
                    <span class="text-xs font-semibold" :style="{ color: item.pct > 50 ? '#d97706' : '#334155' }">{{ item.pct }}.0%</span>
                  </div>
                  <div class="h-1.5 rounded-full" style="background: #e2e8f0">
                    <div class="h-full rounded-full" :style="{ width: item.pct + '%', background: item.color }"></div>
                  </div>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-2 pt-2" style="border-top: 1px solid #e2e8f0">
                <div>
                  <p class="text-xs" style="color: #94a3b8">最大单仓</p>
                  <p class="text-sm font-bold mt-0.5" style="color: #dc2626">63.0%</p>
                </div>
                <div>
                  <p class="text-xs" style="color: #94a3b8">前2仓合计</p>
                  <p class="text-sm font-bold mt-0.5" style="color: #d97706">100.0%</p>
                </div>
              </div>
              <div class="mt-2 flex items-start gap-1.5 px-2 py-1.5 rounded-lg" style="background: rgba(245,166,35,0.06)">
                <i class="ri-alert-line text-xs mt-0.5 shrink-0" style="color: #d97706"></i>
                <p class="text-xs leading-relaxed" style="color: #92400e">宁德时代占比偏高，建议适当分散</p>
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
                  <div class="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full border-2 border-white" style="left: 0.17%; background: #22c55e; margin-top: 4px"></div>
                </div>
              </div>
              <div class="text-center mb-3">
                <p class="text-2xl font-bold" style="color: #dc2626">+0.02%</p>
                <p class="text-xs mt-0.5" style="color: #94a3b8">最小单仓盈亏率（当前无浮亏持仓）</p>
              </div>
              <div class="rounded-lg p-2.5" style="background: #f8fafc; border: 1px solid #f1f5f9">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-semibold" style="color: #334155">{{ drawdownMin.name }}</span>
                  <span class="text-xs font-semibold" style="color: #dc2626">{{ drawdownMin.pct }}</span>
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
                <span class="text-xs font-semibold" style="color: #334155">止损距离</span>
              </div>
              <div class="space-y-3 mb-3">
                <div>
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-xs" style="color: #64748b">宁德时代</span>
                    <div class="flex items-center gap-1.5">
                      <span class="text-xs font-semibold" style="color: #dc2626">距止损 2.6%</span>
                      <span class="w-1.5 h-1.5 rounded-full animate-pulse" style="background: #dc2626"></span>
                    </div>
                  </div>
                  <div class="flex items-center gap-1 text-xs" style="color: #94a3b8">
                    <span>现价 ¥408.98</span><span>→</span><span style="color: #dc2626">止损 ¥398.40</span>
                  </div>
                  <div class="mt-1 px-2 py-1 rounded text-xs" style="background: rgba(220,38,38,0.06); color: #dc2626">
                    <i class="ri-alarm-warning-line mr-1"></i>临近止损线，AI 正在监控
                  </div>
                </div>
                <div>
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-xs" style="color: #64748b">亨通光电</span>
                    <div class="flex items-center gap-1.5">
                      <span class="text-xs font-semibold" style="color: #16a34a">距止损 9.1%</span>
                    </div>
                  </div>
                  <div class="flex items-center gap-1 text-xs" style="color: #94a3b8">
                    <span>现价 ¥120.13</span><span>→</span><span style="color: #dc2626">止损 ¥109.24</span>
                  </div>
                </div>
              </div>
              <div class="pt-2 flex items-center justify-between" style="border-top: 1px solid #e2e8f0">
                <div class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full" style="background: #22c55e"></span><span class="text-xs" style="color: #94a3b8">安全区 &gt;6%</span></div>
                <div class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full" style="background: #d97706"></span><span class="text-xs" style="color: #94a3b8">预警区 3-6%</span></div>
                <div class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full" style="background: #dc2626"></span><span class="text-xs" style="color: #94a3b8">危险区 &lt;3%</span></div>
              </div>
            </div>
          </div>

          <!-- AI 风险建议 -->
          <div class="mt-4 flex items-start gap-3 px-4 py-3 rounded-xl" style="background: rgba(245,166,35,0.04); border: 1px solid rgba(245,166,35,0.15)">
            <div class="w-6 h-6 flex items-center justify-center rounded-full shrink-0 mt-0.5" style="background: rgba(245,166,35,0.12)">
              <i class="ri-robot-line text-xs" style="color: #d97706"></i>
            </div>
            <div>
              <p class="text-xs font-semibold mb-0.5" style="color: #d97706">AI 风险建议</p>
              <p class="text-xs leading-relaxed" style="color: #64748b">
                当前组合整体风险<span class="font-semibold mx-1" style="color: #dc2626">高风险</span>。建议降低 宁德时代 仓位至 15% 以内以提升分散度；各持仓盈亏状态正常；止损机制运行中，如触发将自动执行。
              </p>
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
      <div class="overflow-x-auto">
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
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">风控阶段</th>
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">AI建仓时间</th>
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">AI状态</th>
              <th class="text-left px-4 py-3.5 text-xs font-medium whitespace-nowrap" style="color: #94a3b8">操作</th>
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
                <span class="font-semibold whitespace-nowrap" style="color: #dc2626">{{ pos.pnl }}</span>
              </td>
              <td class="px-4 py-4">
                <span class="font-semibold whitespace-nowrap" style="color: #dc2626">{{ pos.pnlPct }}</span>
              </td>
              <td class="px-4 py-4">
                <div class="flex flex-col gap-1">
                  <span class="text-[10px] px-1.5 py-0.5 rounded font-medium whitespace-nowrap" style="background: rgba(22,163,74,0.08); color: #16a34a">TP {{ pos.tp }}</span>
                  <span class="text-[10px] px-1.5 py-0.5 rounded font-medium whitespace-nowrap" style="background: rgba(220,38,38,0.08); color: #dc2626">SL {{ pos.sl }}</span>
                </div>
              </td>
              <td class="px-4 py-4 text-xs" style="color: #64748b">
                <div class="leading-tight">
                  <div class="whitespace-nowrap">{{ pos.buildDate }}</div>
                  <div class="text-[11px] mt-0.5 whitespace-nowrap" style="color: #94a3b8">{{ pos.buildAgo }}</div>
                </div>
              </td>
              <td class="px-4 py-4">
                <div class="flex flex-col items-start gap-1">
                  <span class="px-2.5 py-1 rounded-full text-xs font-medium whitespace-nowrap" style="background: rgba(22,163,74,0.08); color: #16a34a; border: 1px solid rgba(22,163,74,0.15)">{{ pos.aiStatus }}</span>
                  <span v-if="pos.aiSub" class="text-[10px] whitespace-nowrap" style="color: #94a3b8">{{ pos.aiSub }}</span>
                </div>
              </td>
              <td class="px-4 py-4">
                <div class="flex items-center gap-1.5 whitespace-nowrap">
                  <button class="px-3 py-1.5 rounded-lg text-xs font-medium cursor-pointer whitespace-nowrap transition-all hover:bg-orange-50" style="background: rgba(245,166,35,0.06); border: 1px solid rgba(245,166,35,0.2); color: #d97706">
                    <i class="ri-route-line mr-1"></i>决策过程
                  </button>
                  <button class="px-2.5 py-1.5 rounded-lg text-xs font-medium cursor-pointer whitespace-nowrap transition-all hover:bg-slate-50" style="background: #f8fafc; border: 1px solid #e2e8f0; color: #475569">
                    <i class="ri-arrow-up-circle-line mr-0.5"></i>买入明细
                  </button>
                  <button class="px-2.5 py-1.5 rounded-lg text-xs font-medium cursor-pointer whitespace-nowrap transition-all hover:bg-slate-50" style="background: #f8fafc; border: 1px solid #e2e8f0; color: #475569">
                    <i class="ri-arrow-down-circle-line mr-0.5"></i>卖出明细
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr style="border-top: 1px solid #f1f5f9; background: #fafbfc">
              <td colspan="4" class="px-4 py-3.5 text-sm font-bold" style="color: #0f172a">合计</td>
              <td class="px-4 py-3.5 text-sm font-bold whitespace-nowrap" style="color: #64748b">{{ totals.costTotal }}</td>
              <td class="px-4 py-3.5 text-sm font-bold whitespace-nowrap" style="color: #334155">{{ totals.marketValue }}</td>
              <td class="px-4 py-3.5"><span class="font-bold text-sm whitespace-nowrap" style="color: #dc2626">{{ totals.pnl }}</span></td>
              <td class="px-4 py-3.5"><span class="font-bold text-sm whitespace-nowrap" style="color: #dc2626">{{ totals.pnlPct }}</span></td>
              <td colspan="4"></td>
            </tr>
          </tfoot>
        </table>
      </div>
      <div class="px-4 py-3 flex items-center gap-2" style="border-top: 1px solid #f1f5f9; background: #fafbfc">
        <i class="ri-information-line text-xs" style="color: #d97706"></i>
        <span class="text-xs" style="color: #64748b">所有交易由AI自主执行，点击查看「决策过程」了解完整的AI分析与决策逻辑</span>
      </div>
    </div>

    <!-- 历史交易（占位） -->
    <div v-else class="rounded-xl p-10 text-center" style="background: #fff; border: 1px solid #e2e8f0">
      <i class="ri-history-line text-3xl" style="color: #cbd5e1"></i>
      <p class="text-sm mt-3" style="color: #94a3b8">暂无历史交易记录</p>
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
