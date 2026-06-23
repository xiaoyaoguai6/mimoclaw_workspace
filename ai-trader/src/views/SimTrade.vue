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
  <div>
    <RiskBanner />
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header><span class="font-bold">模拟交易下单</span></template>
          <el-input
            v-model="stockCode"
            placeholder="输入6位股票代码（如 600519）"
            prefix-icon="ri-search-line"
            class="mb-2"
            :loading="searching"
          />
          <div v-if="stockInfo" class="mb-4 p-3 rounded-lg" style="background: #f8fafc; border: 1px solid #f1f5f9">
            <div class="flex items-center justify-between">
              <div>
                <span class="font-bold text-sm">{{ stockInfo.name }}</span>
                <span class="text-xs ml-2" style="color: #94a3b8">{{ stockCode }}</span>
              </div>
              <div class="text-right">
                <div class="text-lg font-bold" :style="{ color: stockInfo.change_pct >= 0 ? '#dc2626' : '#16a34a' }">
                  ¥{{ stockInfo.price }}
                </div>
                <div class="text-xs" :style="{ color: stockInfo.change_pct >= 0 ? '#dc2626' : '#16a34a' }">
                  {{ stockInfo.change_pct >= 0 ? '+' : '' }}{{ stockInfo.change_pct }}%
                </div>
              </div>
            </div>
            <div class="grid grid-cols-4 gap-2 mt-2 text-xs" style="color: #64748b">
              <div>PE <strong>{{ stockInfo.pe_ttm }}</strong></div>
              <div>PB <strong>{{ stockInfo.pb }}</strong></div>
              <div>市值 <strong>{{ stockInfo.mcap_yi }}亿</strong></div>
              <div>换手 <strong>{{ stockInfo.turnover_pct }}%</strong></div>
            </div>
          </div>
          <el-radio-group v-model="tradeType" class="mb-4 w-full">
            <el-radio-button value="buy" class="flex-1">买入</el-radio-button>
            <el-radio-button value="sell" class="flex-1">卖出</el-radio-button>
          </el-radio-group>
          <el-form label-width="60px">
            <el-form-item label="价格"><el-input v-model="price" placeholder="价格" /></el-form-item>
            <el-form-item label="数量"><el-input v-model="qty" placeholder="输入股数" /></el-form-item>
          </el-form>
          <div class="flex gap-2 mb-4">
            <el-button v-for="s in shortcuts" :key="s" size="small" @click="setQty(s)">{{ s }}</el-button>
          </div>
          <div class="flex justify-between text-xs text-gray-400 mb-4">
            <span>预估金额：<strong class="text-gray-800">¥{{ estAmount }}</strong></span>
            <span>可用资金：<strong class="text-gray-800">¥{{ fmt(store.account.available_cash) }}</strong></span>
          </div>
          <el-button
            :type="tradeType === 'buy' ? 'danger' : 'success'"
            class="w-full"
            size="large"
            :loading="trading"
            @click="executeOrder"
          >{{ tradeType === 'buy' ? '买入' : '卖出' }}</el-button>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span class="font-bold">持仓明细</span></template>
          <div v-if="store.holdings.length" class="space-y-2">
            <div
              v-for="h in store.holdings"
              :key="h.code"
              class="flex items-center justify-between p-3 rounded-lg cursor-pointer hover:bg-gray-50 transition-all"
              style="background: #f8fafc; border: 1px solid #f1f5f9"
              @click="stockCode = h.code"
            >
              <div>
                <div class="font-semibold text-sm">{{ h.name }}</div>
                <div class="text-xs" style="color: #94a3b8">{{ h.code }} · {{ h.qty }}股</div>
              </div>
              <div class="text-right">
                <div class="text-sm font-bold">¥{{ h.current_price }}</div>
                <div class="text-xs" :style="{ color: h.pnl >= 0 ? '#dc2626' : '#16a34a' }">
                  {{ h.pnl >= 0 ? '+' : '' }}{{ h.pnl_pct }}%
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8">
            <i class="ri-inbox-line text-2xl" style="color: #cbd5e1"></i>
            <p class="text-sm mt-2" style="color: #94a3b8">暂无持仓</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
