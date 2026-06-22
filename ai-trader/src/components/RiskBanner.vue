<script setup>
import { ref } from 'vue'

const expanded = ref(true)

const risks = [
  '本功能为模拟交易，使用虚拟资金，不涉及真实资金交易，仅供学习参考',
  '行情数据可能存在延迟，成交价格和时机仅供参考，不代表真实市场执行情况',
  '模拟盈利不代表实盘交易能力，历史绩效不构成未来收益保证',
  '投资有风险，入市需谨慎，请勿将模拟结果作为真实投资决策依据',
]
</script>

<template>
  <div class="rounded-xl mb-5 overflow-hidden" style="background: rgba(245,166,35,0.06); border: 1px solid rgba(245,166,35,0.2)">
    <button
      class="w-full flex items-center justify-between px-4 py-3 cursor-pointer"
      @click="expanded = !expanded"
    >
      <div class="flex items-center gap-2">
        <i class="ri-shield-flash-line text-sm" style="color: #d97706"></i>
        <span class="text-xs font-semibold" style="color: #d97706">风险提示</span>
        <span class="text-xs px-2 py-0.5 rounded-full" style="background: rgba(245,166,35,0.1); color: #d97706; border: 1px solid rgba(245,166,35,0.2)">模拟交易</span>
      </div>
      <i
        class="ri-arrow-up-s-line text-sm transition-transform duration-200"
        :style="{ color: '#d97706', transform: expanded ? 'rotate(0deg)' : 'rotate(180deg)' }"
      ></i>
    </button>
    <Transition name="expand">
      <div v-if="expanded" class="px-4 pb-3 grid grid-cols-1 sm:grid-cols-2 gap-2">
        <div v-for="(risk, i) in risks" :key="i" class="flex items-start gap-2">
          <span class="text-xs mt-0.5 shrink-0" style="color: #d97706">·</span>
          <p class="text-xs leading-relaxed" style="color: #64748b">{{ risk }}</p>
        </div>
      </div>
    </Transition>
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
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}
</style>
