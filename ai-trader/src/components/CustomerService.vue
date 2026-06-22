<script setup>
import { ref } from 'vue'

const isMinimized = ref(false)
const inputText = ref('')

const messages = [
  { role: 'user', text: '收费标准是什么？', time: '21:11' },
  {
    role: 'bot',
    text: '1:年付9886元（送2000元能量补贴券），充值可以直接抵扣\n2:半年6886元（送1500元能量补贴券），充值可以直接抵扣\n3:季度4886元（送1000元能量补贴券），充值可以直接抵扣\n4:月付2886元',
    time: '09:03',
  },
]

const toggleMinimize = () => {
  isMinimized.value = !isMinimized.value
}
</script>

<template>
  <div class="fixed bottom-0 left-6 z-40" style="width: 360px">
    <!-- 头部 -->
    <div
      class="flex items-center justify-between px-4 py-3 rounded-t-2xl cursor-pointer"
      style="background: linear-gradient(135deg, #f5a623, #d97706)"
      @click="toggleMinimize"
    >
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
          <i class="ri-customer-service-2-line text-lg text-white"></i>
        </div>
        <div>
          <div class="text-sm font-semibold text-white leading-tight">在线客服</div>
          <div class="flex items-center gap-1">
            <span class="w-1.5 h-1.5 rounded-full bg-green-300"></span>
            <span class="text-[10px] text-white/80">在线</span>
          </div>
        </div>
      </div>
      <button class="w-7 h-7 flex items-center justify-center rounded-lg text-white/70 hover:text-white hover:bg-white/10">
        <i :class="isMinimized ? 'ri-arrow-up-s-line' : 'ri-subtract-line'" class="text-sm"></i>
      </button>
    </div>

    <!-- 消息区域 -->
    <Transition name="cs">
      <div v-if="!isMinimized">
        <div class="overflow-y-auto px-3 py-3 space-y-3" style="height: 320px; background: #f4f6f8">
          <div v-for="(msg, i) in messages" :key="i" class="flex" :class="msg.role === 'user' ? 'justify-end' : 'justify-start'">
            <div v-if="msg.role === 'bot'" class="w-7 h-7 rounded-full shrink-0 mr-2 flex items-center justify-center" style="background: linear-gradient(135deg, #f5a623, #d97706)">
              <i class="ri-customer-service-2-line text-xs text-white"></i>
            </div>
            <div class="max-w-[75%]">
              <div
                class="px-3 py-2 text-sm leading-relaxed rounded-xl whitespace-pre-line"
                :class="msg.role === 'user' ? 'rounded-tr-sm' : 'rounded-tl-sm'"
                :style="{
                  background: msg.role === 'user' ? '#d1f0e0' : '#fff',
                  border: msg.role === 'user' ? '1px solid #b7e4cf' : '1px solid #e2e8f0',
                  color: '#1e293b',
                }"
              >
                {{ msg.text }}
              </div>
              <div class="text-[10px] text-slate-400 mt-0.5" :class="msg.role === 'user' ? 'text-right' : 'text-left'">
                {{ msg.time }}
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="px-3 py-2.5 bg-white border-t border-slate-200 rounded-b-2xl">
          <div class="flex gap-2 items-end">
            <textarea
              v-model="inputText"
              placeholder="输入消息..."
              rows="1"
              class="flex-1 resize-none rounded-lg px-3 py-2 text-sm bg-slate-50 border border-slate-200 text-slate-700 placeholder-slate-400 outline-none focus:border-amber-300"
              style="max-height: 80px; font-family: inherit"
            ></textarea>
            <button
              class="w-9 h-9 flex items-center justify-center rounded-lg shrink-0 transition-all disabled:opacity-40"
              style="background: linear-gradient(135deg, #f5a623, #d97706)"
              :disabled="!inputText.trim()"
            >
              <i class="ri-send-plane-fill text-sm text-white"></i>
            </button>
          </div>
          <p class="text-[10px] text-slate-300 text-center mt-1.5">Enter 发送</p>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.cs-enter-active,
.cs-leave-active {
  transition: all 0.3s ease;
}
.cs-enter-from,
.cs-leave-to {
  opacity: 0;
  max-height: 0;
  overflow: hidden;
}
</style>
