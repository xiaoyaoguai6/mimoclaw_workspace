<script setup>
import { ref } from 'vue'

const isOpen = ref(false)
const isPaused = ref(false)
const inputText = ref('')
const messages = ref([
  {
    role: 'bot',
    text: '你好！我是 AI 交易员，今日为休市日，我处于待命状态。你可以点击上方快捷按钮或直接输入问题。',
  },
])

const quickQuestions = ['今日买了什么', '当前仓位怎样', '最新决策原因', '明日策略']

const toggleChat = () => {
  isOpen.value = !isOpen.value
}

const closeChat = () => {
  isOpen.value = false
}

const togglePause = () => {
  isPaused.value = !isPaused.value
}

const askQuestion = (q) => {
  inputText.value = q
}

const sendMessage = () => {
  const text = inputText.value.trim()
  if (!text) return

  messages.value.push({ role: 'user', text })
  inputText.value = ''

  setTimeout(() => {
    messages.value.push({ role: 'bot', text: '收到，正在分析中…' })
  }, 800)
}
</script>

<template>
  <!-- 触发按钮 -->
  <button
    v-show="!isOpen"
    class="fixed bottom-6 right-6 z-50 relative h-14 rounded-full cursor-pointer flex items-center gap-3 pl-3 pr-5 transition-transform duration-200 hover:scale-[1.03] active:scale-95"
    style="background: linear-gradient(135deg, rgb(30,50,84), rgb(45,78,120)); border: 2px solid rgba(245,166,35,0.45); box-shadow: 0 8px 32px rgba(0,0,0,0.25)"
    @click="toggleChat"
  >
    <span class="absolute inset-0 rounded-full animate-ping" style="background: rgba(34,197,94,0.1); animation-duration: 2.5s"></span>
    <img alt="AI" class="w-8 h-8 object-contain relative z-10 shrink-0" src="@/assets/logo.svg" />
    <span class="relative z-10 text-sm font-semibold text-white whitespace-nowrap">AI 交易员，点击对话</span>
    <div class="absolute bottom-0.5 right-0.5 w-3.5 h-3.5 rounded-full" style="background: #22c55e; border: 2px solid #fff"></div>
  </button>

  <!-- 对话框 -->
  <Transition name="chat">
    <div
      v-if="isOpen"
      class="fixed bottom-20 right-6 z-50 w-[420px] max-h-[75vh] rounded-2xl flex flex-col"
      style="background: #fff; box-shadow: 0 8px 40px rgba(0,0,0,0.2); border: 1px solid #e2e8f0"
    >
      <!-- 头部 -->
      <div class="flex items-center justify-between px-5 py-4" style="border-bottom: 1px solid #f1f5f9">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full flex items-center justify-center" style="background: linear-gradient(135deg, #f5a623, #e8941a)">
            <i class="ri-robot-2-line text-white text-lg"></i>
          </div>
          <div>
            <div class="text-sm font-semibold" style="color: #0f172a">AI 交易员</div>
            <div class="flex items-center gap-1">
              <span class="w-1.5 h-1.5 rounded-full" style="background: #22c55e"></span>
              <span class="text-xs" style="color: #22c55e">在线</span>
            </div>
          </div>
        </div>
        <div class="flex gap-1">
          <button
            class="w-8 h-8 rounded-lg flex items-center justify-center transition-colors"
            style="color: #94a3b8"
            @click="togglePause"
          >
            <i :class="isPaused ? 'ri-play-line' : 'ri-pause-line'"></i>
          </button>
          <button
            class="w-8 h-8 rounded-lg flex items-center justify-center transition-colors"
            style="color: #94a3b8"
            @click="closeChat"
          >
            <i class="ri-close-line"></i>
          </button>
        </div>
      </div>

      <!-- 快捷问题 -->
      <div class="flex gap-2 px-5 py-3 overflow-x-auto" style="border-bottom: 1px solid #f1f5f9">
        <button
          v-for="q in quickQuestions"
          :key="q"
          class="px-3 py-1.5 rounded-full text-xs whitespace-nowrap transition-all"
          style="background: #f8fafc; border: 1px solid #e2e8f0; color: #64748b"
          @click="askQuestion(q)"
        >
          {{ q }}
        </button>
      </div>

      <!-- 消息列表 -->
      <div class="flex-1 overflow-y-auto px-5 py-4 flex flex-col gap-3" style="max-height: 400px">
        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="flex gap-3"
          :class="msg.role === 'user' ? 'justify-end' : ''"
        >
          <div
            v-if="msg.role === 'bot'"
            class="w-8 h-8 rounded-full flex items-center justify-center shrink-0"
            style="background: linear-gradient(135deg, #f5a623, #e8941a)"
          >
            <i class="ri-robot-2-line text-white text-sm"></i>
          </div>
          <div
            class="max-w-[80%] px-4 py-2.5 text-sm leading-relaxed rounded-2xl"
            :class="msg.role === 'user' ? 'rounded-br-md' : 'rounded-bl-md'"
            :style="{
              background: msg.role === 'user' ? 'rgba(245,166,35,0.1)' : '#f8fafc',
              color: '#0f172a',
              border: msg.role === 'bot' ? '1px solid #f1f5f9' : 'none',
            }"
          >
            {{ msg.text }}
          </div>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="px-5 py-4" style="border-top: 1px solid #f1f5f9">
        <div class="flex gap-2 items-end">
          <textarea
            v-model="inputText"
            placeholder="输入消息..."
            rows="1"
            class="flex-1 resize-none rounded-lg px-3 py-2 text-sm outline-none"
            style="background: #f8fafc; border: 1px solid #e2e8f0; color: #0f172a; max-height: 80px; font-family: inherit"
            @keydown.enter.exact.prevent="sendMessage"
          ></textarea>
          <button
            class="w-9 h-9 rounded-lg flex items-center justify-center shrink-0 transition-transform hover:scale-105"
            style="background: linear-gradient(135deg, #f5a623, #e8941a)"
            @click="sendMessage"
          >
            <i class="ri-send-plane-fill text-white text-sm"></i>
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.chat-enter-active,
.chat-leave-active {
  transition: all 0.3s ease;
}
.chat-enter-from,
.chat-leave-to {
  opacity: 0;
  transform: translateY(1rem);
}

@media (max-width: 767px) {
  .fixed.bottom-20.right-6 {
    left: 0.5rem;
    right: 0.5rem;
    width: auto;
    bottom: 5rem;
  }
}
</style>
