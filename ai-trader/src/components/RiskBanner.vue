<script setup>
import { ref } from 'vue'

const expanded = ref(false)

const risks = [
  '本功能为模拟交易，使用虚拟资金，不涉及真实资金交易，仅供学习参考',
  '行情数据可能存在延迟，成交价格和时机仅供参考，不代表真实市场执行情况',
  '模拟盈利不代表实盘交易能力，历史绩效不构成未来收益保证',
  '投资有风险，入市需谨慎，请勿将模拟结果作为真实投资决策依据',
]
</script>

<template>
  <div class="rounded-2xl mb-6 overflow-hidden card">
    <button
      class="w-full flex items-center justify-between px-5 py-3 cursor-pointer transition-colors hover:bg-slate-50"
      @click="expanded = !expanded"
    >
      <div class="flex items-center gap-2.5">
        <div class="w-7 h-7 rounded-lg flex items-center justify-center" style="background: var(--color-warning-light)">
          <i class="ri-shield-flash-line text-sm" style="color: var(--color-warning)"></i>
        </div>
        <span class="text-sm font-semibold" style="color: var(--color-text-secondary)">风险提示</span>
        <span class="badge" style="background: var(--color-warning-light); color: var(--color-warning)">模拟交易</span>
      </div>
      <i
        class="ri-arrow-up-s-line text-base transition-transform duration-200"
        :style="{ color: 'var(--color-text-muted)', transform: expanded ? 'rotate(0deg)' : 'rotate(180deg)' }"
      ></i>
    </button>
    <Transition name="expand">
      <div v-if="expanded" class="px-5 pb-4 grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        <div v-for="(risk, i) in risks" :key="i" class="flex items-start gap-2.5">
          <div class="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0" style="background: var(--color-warning)"></div>
          <p class="text-xs leading-relaxed" style="color: var(--color-text-muted)">{{ risk }}</p>
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
}
</style>
