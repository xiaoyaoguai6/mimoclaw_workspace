<script setup>
import { ref, computed, watch } from 'vue'
import RiskBanner from '@/components/RiskBanner.vue'
import { useAppStore } from '@/stores/app'
import api from '@/api'
import { ElMessage } from 'element-plus'

const store = useAppStore()
const tradeType = ref('buy')
const stockCode = ref('')
const stockName = ref('')
const stockInfo = ref(null)
const price = ref('')
const qty = ref('')
const shortcuts = [100, 500, 1000, 5000, 10000]
const searching = ref(false)
const trading = ref(false)

const fmt = (v) => v.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const estAmount = computed(() => {
  const p = parseFloat(price.value) || 0
  const q = parseInt(qty.value) || 0
  return fmt(p * q)
})

const setQty = (v) => { qty.value = String(v) }

async function searchStock() {
  const code = stockCode.value.trim()
  if (code.length !== 6) return
  searching.value = true
  try {
    const q = await api.getStockQuote(code)
    stockInfo.value = q
    stockName.value = q.name
    price.value = String(q.price)
  } catch (e) {
    ElMessage.warning(`未找到股票 ${code}`)
    stockInfo.value = null
    stockName.value = ''
  }
  searching.value = false
}

watch(stockCode, (v) => {
  if (v && v.trim().length === 6) {
    searchStock()
  }
})

async function executeOrder() {
  if (!stockCode.value || !price.value || !qty.value) {
    ElMessage.warning('请输入股票代码、价格和数量')
    return
  }
  if (!stockName.value) {
    ElMessage.warning('请先搜索有效股票代码')
    return
  }
  trading.value = true
  try {
    const result = await store.executeTrade({
      code: stockCode.value.trim(),
      name: stockName.value,
      action: tradeType.value,
      qty: parseInt(qty.value),
      price: parseFloat(price.value),
    })
    ElMessage.success(result.message)
    qty.value = ''
  } catch (e) {
    ElMessage.error(e.message || '交易失败')
  }
  trading.value = false
}
</script>

<template>
  <div class="animate-fade-in">
    <RiskBanner />
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 下单面板 -->
      <div class="card p-6">
        <div class="flex items-center gap-2 mb-5">
          <i class="ri-swap-line text-lg" style="color: var(--color-primary)"></i>
          <h3 class="text-base font-bold" style="color: var(--color-text-primary)">模拟交易下单</h3>
        </div>

        <el-input
          v-model="stockCode"
          placeholder="输入6位股票代码（如 600519）"
          prefix-icon="ri-search-line"
          class="mb-4"
          :loading="searching"
        />

        <!-- 股票信息卡片 -->
        <div v-if="stockInfo" class="mb-5 p-4 rounded-xl" style="background: var(--color-border-light); border: 1px solid var(--color-border)">
          <div class="flex items-center justify-between mb-3">
            <div>
              <span class="font-bold text-base" style="color: var(--color-text-primary)">{{ stockInfo.name }}</span>
              <span class="text-xs ml-2 font-mono" style="color: var(--color-text-muted)">{{ stockCode }}</span>
            </div>
            <div class="text-right">
              <div class="text-xl font-bold tabular-nums" :style="{ color: stockInfo.change_pct >= 0 ? 'var(--color-up)' : 'var(--color-down)' }">
                ¥{{ stockInfo.price }}
              </div>
              <div class="text-xs tabular-nums" :style="{ color: stockInfo.change_pct >= 0 ? 'var(--color-up)' : 'var(--color-down)' }">
                {{ stockInfo.change_pct >= 0 ? '+' : '' }}{{ stockInfo.change_pct }}%
              </div>
            </div>
          </div>
          <div class="grid grid-cols-4 gap-3 pt-3" style="border-top: 1px solid var(--color-border)">
            <div>
              <p class="text-xs" style="color: var(--color-text-muted)">PE(TTM)</p>
              <p class="text-sm font-bold mt-0.5 tabular-nums" style="color: var(--color-text-primary)">{{ stockInfo.pe_ttm }}</p>
            </div>
            <div>
              <p class="text-xs" style="color: var(--color-text-muted)">PB</p>
              <p class="text-sm font-bold mt-0.5 tabular-nums" style="color: var(--color-text-primary)">{{ stockInfo.pb }}</p>
            </div>
            <div>
              <p class="text-xs" style="color: var(--color-text-muted)">市值</p>
              <p class="text-sm font-bold mt-0.5 tabular-nums" style="color: var(--color-text-primary)">{{ stockInfo.mcap_yi }}亿</p>
            </div>
            <div>
              <p class="text-xs" style="color: var(--color-text-muted)">换手</p>
              <p class="text-sm font-bold mt-0.5 tabular-nums" style="color: var(--color-text-primary)">{{ stockInfo.turnover_pct }}%</p>
            </div>
          </div>
        </div>

        <!-- 买卖切换 -->
        <div class="grid grid-cols-2 gap-2 mb-5">
          <button
            class="py-3 rounded-xl text-sm font-bold cursor-pointer transition-all"
            :style="tradeType === 'buy'
              ? { background: 'var(--color-up)', color: '#fff', boxShadow: '0 4px 12px rgba(239,68,68,0.25)' }
              : { background: 'var(--color-border-light)', color: 'var(--color-text-muted)', border: '1px solid var(--color-border)' }"
            @click="tradeType = 'buy'"
          >买入</button>
          <button
            class="py-3 rounded-xl text-sm font-bold cursor-pointer transition-all"
            :style="tradeType === 'sell'
              ? { background: 'var(--color-down)', color: '#fff', boxShadow: '0 4px 12px rgba(16,185,129,0.25)' }
              : { background: 'var(--color-border-light)', color: 'var(--color-text-muted)', border: '1px solid var(--color-border)' }"
            @click="tradeType = 'sell'"
          >卖出</button>
        </div>

        <div class="grid grid-cols-2 gap-4 mb-5">
          <div>
            <label class="text-xs font-medium mb-2 block" style="color: var(--color-text-secondary)">价格</label>
            <el-input v-model="price" placeholder="价格" />
          </div>
          <div>
            <label class="text-xs font-medium mb-2 block" style="color: var(--color-text-secondary)">数量</label>
            <el-input v-model="qty" placeholder="输入股数" />
          </div>
        </div>

        <div class="flex gap-2 mb-5">
          <button
            v-for="s in shortcuts"
            :key="s"
            class="px-3 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition-all"
            style="background: var(--color-border-light); color: var(--color-text-secondary)"
            @click="setQty(s)"
          >{{ s }}</button>
        </div>

        <div class="flex justify-between text-xs mb-5 pb-4" style="color: var(--color-text-muted); border-bottom: 1px solid var(--color-border-light)">
          <span>预估金额：<strong class="text-sm tabular-nums" style="color: var(--color-text-primary)">¥{{ estAmount }}</strong></span>
          <span>可用资金：<strong class="text-sm tabular-nums" style="color: var(--color-text-primary)">¥{{ fmt(store.account.available_cash) }}</strong></span>
        </div>

        <button
          class="w-full py-4 rounded-xl font-bold text-base cursor-pointer transition-all hover:shadow-lg"
          :style="tradeType === 'buy'
            ? { background: 'var(--color-up)', color: '#fff' }
            : { background: 'var(--color-down)', color: '#fff' }"
          :disabled="trading"
          @click="executeOrder"
        >
          <i :class="trading ? 'ri-loader-4-line animate-spin' : 'ri-check-line'" class="mr-2"></i>
          {{ trading ? '处理中…' : (tradeType === 'buy' ? '确认买入' : '确认卖出') }}
        </button>
      </div>

      <!-- 持仓明细 -->
      <div class="card p-6">
        <div class="flex items-center gap-2 mb-5">
          <i class="ri-briefcase-line text-lg" style="color: var(--color-primary)"></i>
          <h3 class="text-base font-bold" style="color: var(--color-text-primary)">持仓明细</h3>
          <span class="badge ml-auto" style="background: var(--color-primary-light); color: var(--color-primary)">{{ store.holdings.length }} 只</span>
        </div>
        <div v-if="store.holdings.length" class="space-y-3">
          <div
            v-for="h in store.holdings"
            :key="h.code"
            class="flex items-center justify-between p-4 rounded-xl cursor-pointer transition-all hover:shadow-md"
            style="background: var(--color-border-light); border: 1px solid var(--color-border)"
            @click="stockCode = h.code"
          >
            <div>
              <div class="font-semibold text-sm" style="color: var(--color-text-primary)">{{ h.name }}</div>
              <div class="text-xs mt-0.5" style="color: var(--color-text-muted)">{{ h.code }} · {{ h.qty.toLocaleString() }}股</div>
            </div>
            <div class="text-right">
              <div class="text-base font-bold tabular-nums" style="color: var(--color-text-primary)">¥{{ h.current_price }}</div>
              <div class="text-xs tabular-nums" :style="{ color: h.pnl >= 0 ? 'var(--color-up)' : 'var(--color-down)' }">
                {{ h.pnl >= 0 ? '+' : '' }}{{ h.pnl_pct }}%
              </div>
            </div>
          </div>
        </div>
        <div v-else class="py-16 text-center">
          <div class="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4" style="background: var(--color-border-light)">
            <i class="ri-inbox-line text-3xl" style="color: var(--color-text-faint)"></i>
          </div>
          <p class="text-sm" style="color: var(--color-text-muted)">暂无持仓</p>
        </div>
      </div>
    </div>
  </div>
</template>
