<script setup>
import { ref, computed } from 'vue'
import RiskBanner from '@/components/RiskBanner.vue'

const tradeType = ref('buy')
const price = ref('25.68')
const qty = ref('')
const shortcuts = [100, 500, 1000, 5000, 10000]

const estAmount = computed(() => {
  const p = parseFloat(price.value) || 0
  const q = parseInt(qty.value) || 0
  return (p * q).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
})

const setQty = (v) => { qty.value = String(v) }
</script>

<template>
  <div>
    <RiskBanner />
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header><span class="font-bold">模拟交易下单</span></template>
          <el-input placeholder="搜索股票代码或名称..." prefix-icon="ri-search-line" class="mb-4" />
          <el-radio-group v-model="tradeType" class="mb-4 w-full">
            <el-radio-button value="buy" class="flex-1">买入</el-radio-button>
            <el-radio-button value="sell" class="flex-1">卖出</el-radio-button>
          </el-radio-group>
          <el-form label-width="60px">
            <el-form-item label="价格"><el-input v-model="price" /></el-form-item>
            <el-form-item label="数量"><el-input v-model="qty" placeholder="输入股数" /></el-form-item>
          </el-form>
          <div class="flex gap-2 mb-4">
            <el-button v-for="s in shortcuts" :key="s" size="small" @click="setQty(s)">{{ s }}</el-button>
          </div>
          <div class="flex justify-between text-xs text-gray-400 mb-4">
            <span>预估金额：<strong class="text-gray-800">¥{{ estAmount }}</strong></span>
            <span>可用资金：<strong class="text-gray-800">¥1,000,000</strong></span>
          </div>
          <el-button type="danger" class="w-full" size="large">{{ tradeType === 'buy' ? '买入' : '卖出' }}</el-button>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span class="font-bold">盘口数据</span></template>
          <div class="text-xs space-y-1">
            <div v-for="i in 5" :key="'s'+i" class="flex justify-between"><span style="color:#94a3b8">卖{{ 6-i }}</span><span>{{ (25.70 + (5-i)*0.02).toFixed(2) }}</span><span>{{ [450,320,180,250,120][i-1] }}</span></div>
            <div class="border-t border-b py-1 my-1 flex justify-between font-bold"><span>最新</span><span style="color:#dc2626">25.68</span><span style="color:#dc2626">+1.83%</span></div>
            <div v-for="i in 5" :key="'b'+i" class="flex justify-between"><span style="color:#94a3b8">买{{ i }}</span><span>{{ (25.66 - (i-1)*0.02).toFixed(2) }}</span><span>{{ [380,210,160,290,140][i-1] }}</span></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
