<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const store = useAppStore()
const currentTime = ref('')
const showDropdown = ref(false)
let timer = null

const updateTime = () => {
  currentTime.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

const toggleDropdown = () => { showDropdown.value = !showDropdown.value }
const closeDropdown = () => { showDropdown.value = false }
const logout = () => { router.push('/login') }
const goToSettings = () => { showDropdown.value = false; router.push('/settings') }
</script>

<template>
  <header
    class="fixed top-0 left-0 right-0 z-30 flex items-center px-6 glass-dark"
    style="height: var(--header-height); border-bottom: 1px solid rgba(255,255,255,0.06)"
  >
    <!-- 左侧 Logo -->
    <div class="flex items-center gap-3 shrink-0" style="width: var(--sidebar-width)">
      <button
        class="w-9 h-9 flex items-center justify-center rounded-lg cursor-pointer md:hidden transition-colors"
        style="background: rgba(255,255,255,0.06)"
        @click="store.sidebarOpen = !store.sidebarOpen"
      >
        <i class="ri-menu-line text-white"></i>
      </button>
      <div class="w-9 h-9 rounded-xl flex items-center justify-center gradient-primary" style="box-shadow: 0 4px 12px rgba(99,102,241,0.3)">
        <img alt="logo" class="w-6 h-6 object-contain brightness-0 invert" src="@/assets/logo.svg" />
      </div>
      <div class="hidden sm:flex flex-col leading-none">
        <span class="text-white font-bold text-sm tracking-tight">AI 交易员</span>
        <span class="text-[10px] mt-0.5" style="color: rgba(255,255,255,0.3)">Alpha Workshop</span>
      </div>
      <span
        v-if="store.marketStatus.label"
        class="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] ml-1"
        :style="{
          background: store.marketStatus.isOpen ? 'rgba(16,185,129,0.12)' : 'rgba(255,255,255,0.05)',
          color: store.marketStatus.isOpen ? '#34d399' : 'rgba(255,255,255,0.4)',
          border: `1px solid ${store.marketStatus.isOpen ? 'rgba(16,185,129,0.2)' : 'rgba(255,255,255,0.08)'}`,
        }"
      >
        <span class="w-1.5 h-1.5 rounded-full animate-pulse" :style="{ background: store.marketStatus.isOpen ? '#34d399' : '#64748b' }"></span>
        {{ store.marketStatus.label }}
      </span>
    </div>

    <!-- 中间指数 -->
    <div class="flex-1 flex items-center justify-center gap-8 overflow-hidden">
      <div
        v-for="idx in store.marketIndices.slice(0, 3)"
        :key="idx.code"
        class="flex items-center gap-2.5 shrink-0"
      >
        <span class="text-xs font-medium" style="color: rgba(255,255,255,0.5)">{{ idx.name }}</span>
        <span class="text-sm font-bold text-white tabular-nums">{{ idx.value }}</span>
        <span
          class="flex items-center gap-0.5 text-xs font-semibold tabular-nums"
          :style="{ color: idx.direction === 'up' ? 'var(--color-up)' : 'var(--color-down)' }"
        >
          <i :class="idx.direction === 'up' ? 'ri-arrow-up-s-fill' : 'ri-arrow-down-s-fill'"></i>
          {{ idx.change }}
        </span>
      </div>
    </div>

    <!-- 右侧用户 -->
    <div class="flex items-center gap-4 shrink-0" style="width: var(--sidebar-width); justify-content: flex-end">
      <span class="text-xs font-mono hidden lg:block tabular-nums" style="color: rgba(255,255,255,0.4)">{{ currentTime }}</span>
      <div class="relative">
        <div
          class="flex items-center gap-2.5 cursor-pointer p-1 pr-3 rounded-full transition-all hover:bg-white/5"
          @click="toggleDropdown"
        >
          <div
            class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
            style="background: linear-gradient(135deg, #6366f1, #4f46e5); color: #fff"
          >
            {{ store.user.avatar }}
          </div>
          <span class="text-sm text-white hidden sm:block">{{ store.user.phone }}</span>
          <i class="ri-arrow-down-s-line text-xs hidden sm:block" style="color: rgba(255,255,255,0.4)"></i>
        </div>

        <Transition name="dropdown">
          <div
            v-if="showDropdown"
            class="absolute top-full right-0 mt-2 w-48 rounded-2xl shadow-xl border py-2 z-50 glass"
            @click="closeDropdown"
          >
            <div class="px-3 pb-2 mb-1" style="border-bottom: 1px solid var(--color-border-light)">
              <p class="text-sm font-semibold" style="color: var(--color-text-primary)">{{ store.user.phone }}</p>
              <p class="text-xs mt-0.5" style="color: var(--color-text-muted)">UID-390 · 季度会员</p>
            </div>
            <div class="flex items-center gap-2.5 px-4 py-2.5 text-sm cursor-pointer hover:bg-slate-50 rounded-lg mx-1 transition-colors" @click="goToSettings">
              <i class="ri-user-line" style="color: var(--color-text-muted)"></i>个人中心
            </div>
            <div class="flex items-center gap-2.5 px-4 py-2.5 text-sm cursor-pointer hover:bg-slate-50 rounded-lg mx-1 transition-colors" @click="goToSettings">
              <i class="ri-settings-4-line" style="color: var(--color-text-muted)"></i>账户设置
            </div>
            <div class="h-px my-1 mx-3" style="background: var(--color-border-light)"></div>
            <div class="flex items-center gap-2.5 px-4 py-2.5 text-sm cursor-pointer hover:bg-red-50 rounded-lg mx-1 transition-colors" style="color: var(--color-danger)" @click="logout">
              <i class="ri-logout-box-r-line"></i>退出登录
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </header>

  <div v-if="showDropdown" class="fixed inset-0 z-20" @click="closeDropdown"></div>
</template>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.96);
}
</style>
