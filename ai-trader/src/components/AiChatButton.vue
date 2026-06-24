<script setup>
import { ref, nextTick, onUnmounted } from 'vue'
import api from '@/api'

const isOpen = ref(false)
const inputText = ref('')
const sending = ref(false)
const messagesRef = ref(null)

const messages = ref([
  {
    role: 'bot',
    text: '你好！我是 AI 交易员，可以回答你关于持仓、行情、策略的问题。试试下方的快捷提问吧。',
  },
])

const quickQuestions = ['当前持仓情况', '今日盈亏分析', '帮我分析下茅台', '现在适合建仓吗？']

const toggleChat = () => { isOpen.value = !isOpen.value }
const closeChat = () => { isOpen.value = false }

const askQuestion = (q) => {
  inputText.value = q
  sendMessage()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

const formatText = (text) => {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}

const sendMessage = async () => {
  const text = inputText.value.trim()
  if (!text || sending.value) return

  messages.value.push({ role: 'user', text })
  inputText.value = ''
  sending.value = true
  scrollToBottom()

  // 构建发送给后端的 messages (只传 user/assistant，不含初始 bot 欢迎语)
  const apiMessages = messages.value
    .filter(m => m.role === 'user' || (m.role === 'bot' && m.text !== messages.value[0].text))
    .map(m => ({ role: m.role === 'bot' ? 'assistant' : 'user', content: m.text }))

  // 添加 AI 占位（流式更新）
  const botIdx = messages.value.push({ role: 'bot', text: '' }) - 1
  scrollToBottom()

  try {
    const resp = await api.aiChatStream(apiMessages)
    if (!resp.ok) {
      messages.value[botIdx].text = `[AI 服务暂不可用: ${resp.status}]`
      sending.value = false
      return
    }

    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let fullText = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const payload = line.slice(6)
        if (payload === '[DONE]') continue
        try {
          const obj = JSON.parse(payload)
          if (obj.content) {
            fullText += obj.content
            messages.value[botIdx].text = fullText
            scrollToBottom()
          }
        } catch (e) { /* skip */ }
      }
    }

    if (!fullText) {
      messages.value[botIdx].text = '[无回复，请重试]'
    }
  } catch (e) {
    messages.value[botIdx].text = `[AI 连接失败: ${e.message}]`
  }
  sending.value = false
  scrollToBottom()
}

onUnmounted(() => { isOpen.value = false })
</script>

<template>
  <!-- 触发按钮 — 永远在右下角 -->
  <Transition name="fab">
    <button
      v-show="!isOpen"
      class="fixed bottom-6 right-6 z-50 h-14 px-5 rounded-full cursor-pointer flex items-center gap-3 transition-all hover:scale-105 active:scale-95"
      style="background: linear-gradient(135deg, #6366f1, #4f46e5); box-shadow: 0 8px 32px rgba(99,102,241,0.35)"
      @click="toggleChat"
    >
      <span class="absolute inset-0 rounded-full animate-ping opacity-30" style="background: #6366f1; animation-duration: 3s"></span>
      <div class="w-9 h-9 rounded-full flex items-center justify-center shrink-0 relative z-10" style="background: rgba(255,255,255,0.2)">
        <i class="ri-robot-2-line text-xl text-white"></i>
      </div>
      <span class="relative z-10 text-sm font-bold text-white whitespace-nowrap">AI 交易员</span>
      <div class="absolute bottom-1 right-1 w-3.5 h-3.5 rounded-full" style="background: #34d399; border: 2px solid #4f46e5"></div>
    </button>
  </Transition>

  <!-- 对话框 -->
  <Transition name="chat">
    <div
      v-if="isOpen"
      class="fixed bottom-6 right-6 z-50 w-[420px] max-w-[calc(100vw-3rem)] rounded-2xl flex flex-col overflow-hidden"
      style="background: var(--color-bg-card); box-shadow: 0 24px 64px rgba(15,23,42,0.2); border: 1px solid var(--color-border); max-height: 75vh"
    >
      <!-- 头部 -->
      <div class="flex items-center justify-between px-5 py-4" style="background: linear-gradient(135deg, #6366f1, #4f46e5)">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center" style="background: rgba(255,255,255,0.2)">
            <i class="ri-robot-2-line text-white text-lg"></i>
          </div>
          <div>
            <div class="text-sm font-bold text-white">AI 交易员</div>
            <div class="flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full animate-pulse" style="background: #34d399"></span>
              <span class="text-xs text-white/80">在线 · 接入 mimov2.5pro</span>
            </div>
          </div>
        </div>
        <button
          class="w-8 h-8 rounded-lg flex items-center justify-center transition-colors hover:bg-white/10"
          @click="closeChat"
        >
          <i class="ri-close-line text-white"></i>
        </button>
      </div>

      <!-- 快捷问题 -->
      <div class="flex gap-2 px-5 py-3 overflow-x-auto" style="border-bottom: 1px solid var(--color-border-light)">
        <button
          v-for="q in quickQuestions"
          :key="q"
          class="px-3 py-1.5 rounded-full text-xs whitespace-nowrap transition-all shrink-0"
          style="background: var(--color-primary-light); border: 1px solid rgba(99,102,241,0.15); color: var(--color-primary)"
          :disabled="sending"
          @click="askQuestion(q)"
        >{{ q }}</button>
      </div>

      <!-- 消息列表 -->
      <div ref="messagesRef" class="flex-1 overflow-y-auto px-5 py-4 flex flex-col gap-4" style="min-height: 280px; max-height: 400px">
        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="flex gap-2.5"
          :class="msg.role === 'user' ? 'justify-end' : ''"
        >
          <div
            v-if="msg.role === 'bot'"
            class="w-8 h-8 rounded-xl flex items-center justify-center shrink-0"
            style="background: linear-gradient(135deg, #6366f1, #4f46e5)"
          >
            <i class="ri-robot-2-line text-white text-sm"></i>
          </div>
          <div
            class="max-w-[80%] px-4 py-2.5 text-sm leading-relaxed rounded-2xl"
            :class="msg.role === 'user' ? 'rounded-br-md' : 'rounded-bl-md'"
            :style="{
              background: msg.role === 'user' ? 'var(--color-primary)' : 'var(--color-border-light)',
              color: msg.role === 'user' ? '#fff' : 'var(--color-text-primary)',
            }"
          >
            <span v-if="msg.role === 'bot' && !msg.text" class="typing-dots">思考中</span>
            <span v-else v-html="formatText(msg.text)"></span>
          </div>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="px-5 py-4" style="border-top: 1px solid var(--color-border-light)">
        <div class="flex gap-2 items-end">
          <textarea
            v-model="inputText"
            placeholder="输入消息..."
            rows="1"
            class="flex-1 resize-none rounded-xl px-3.5 py-2.5 text-sm outline-none transition-all"
            style="background: var(--color-border-light); border: 1px solid var(--color-border); color: var(--color-text-primary); max-height: 80px; font-family: inherit"
            @keydown.enter.exact.prevent="sendMessage"
          ></textarea>
          <button
            class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 transition-all hover:scale-105 disabled:opacity-40"
            style="background: linear-gradient(135deg, #6366f1, #4f46e5)"
            :disabled="!inputText.trim() || sending"
            @click="sendMessage"
          >
            <i :class="sending ? 'ri-loader-4-line animate-spin' : 'ri-send-plane-fill'" class="text-white text-sm"></i>
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.chat-enter-active,
.chat-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.chat-enter-from,
.chat-leave-to {
  opacity: 0;
  transform: translateY(1rem) scale(0.96);
}

.fab-enter-active,
.fab-leave-active {
  transition: all 0.25s ease;
}
.fab-enter-from,
.fab-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

.typing-dots::after {
  content: '...';
  animation: dots 1.4s infinite;
}
@keyframes dots {
  0%, 20% { content: '.'; }
  40% { content: '..'; }
  60%, 100% { content: '...'; }
}

@media (max-width: 767px) {
  .fixed.bottom-6.right-6 {
    left: 1rem;
    right: 1rem;
    width: auto;
  }
}
</style>
