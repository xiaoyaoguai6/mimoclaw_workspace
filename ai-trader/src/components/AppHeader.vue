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

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

const closeDropdown = () => {
  showDropdown.value = false
}

const logout = () => {
  router.push('/login')
}

const goToSettings = () => {
  showDropdown.value = false
  router.push('/settings')
}
</script>

<template>
  <header class="fixed top-0 left-0 right-0 z-30 flex items-center px-5 h-14" style="background: rgb(30, 50, 84); border-bottom: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(16px)">
    <!-- 左侧 Logo -->
    <div class="flex items-center gap-3 w-56 shrink-0">
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg cursor-pointer md:hidden"
        style="background: rgba(255,255,255,0.08)"
        @click="store.sidebarOpen = !store.sidebarOpen"
      >
        <i class="ri-menu-line text-white"></i>
      </button>
      <img alt="logo" class="w-7 h-7 object-contain" src="@/assets/logo.svg" />
      <span class="text-white font-bold text-sm tracking-wide">AI交易员</span>
      <span
        class="hidden sm:flex items-center gap-1 px-2 py-0.5 rounded-full text-xs"
        style="background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.3); border: 1px solid rgba(255,255,255,0.08)"
      >
        <span class="w-1.5 h-1.5 rounded-full" style="background: #64748b"></span>
        {{ store.marketStatus.label }}
      </span>
    </div>

    <!-- 中间指数 -->
    <div class="flex-1 flex items-center justify-center gap-6">
      <div
        v-for="idx in store.marketIndices"
        :key="idx.name"
        class="flex items-center gap-2"
      >
        <span class="text-xs font-medium" style="color: rgba(255,255,255,0.6)">{{ idx.name }}</span>
        <span class="text-sm font-bold text-white">{{ idx.value }}</span>
        <span
          class="flex items-center gap-0.5 text-xs font-semibold"
          :style="{ color: idx.direction === 'up' ? '#dc2626' : '#16a34a' }"
        >
          <i :class="idx.direction === 'up' ? 'ri-arrow-up-s-fill' : 'ri-arrow-down-s-fill'"></i>
          {{ idx.change }}
        </span>
      </div>
    </div>

    <!-- 右侧用户 -->
    <div class="flex items-center gap-3 w-56 justify-end shrink-0">
      <span class="text-xs font-mono hidden lg:block" style="color: rgba(255,255,255,0.5)">{{ currentTime }}</span>
      <div class="relative">
        <div
          class="flex items-center gap-2 cursor-pointer group"
          @click="toggleDropdown"
        >
          <div
            class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold"
            style="background: linear-gradient(135deg, #f5a623, #e8941a); color: #0a1628"
          >
            {{ store.user.avatar }}
          </div>
          <span class="text-sm text-white hidden sm:block">{{ store.user.phone }}</span>
          <i class="ri-arrow-down-s-line text-xs hidden sm:block" style="color: rgba(255,255,255,0.45)"></i>
        </div>

        <!-- 下拉菜单 -->
        <Transition name="dropdown">
          <div
            v-if="showDropdown"
            class="absolute top-full right-0 mt-2 w-40 rounded-xl shadow-lg border py-1 z-50"
            style="background: #fff; border-color: #e2e8f0"
            @click="closeDropdown"
          >
            <div
              class="flex items-center gap-2 px-4 py-2.5 text-sm cursor-pointer hover:bg-gray-50 transition-colors"
              @click="goToSettings"
            >
              <i class="ri-user-line" style="color: #64748b"></i>
              个人中心
            </div>
            <div
              class="flex items-center gap-2 px-4 py-2.5 text-sm cursor-pointer hover:bg-gray-50 transition-colors"
              @click="goToSettings"
            >
              <i class="ri-settings-4-line" style="color: #64748b"></i>
              账户设置
            </div>
            <div class="border-t my-1" style="border-color: #f1f5f9"></div>
            <div
              class="flex items-center gap-2 px-4 py-2.5 text-sm cursor-pointer hover:bg-red-50 transition-colors"
              style="color: #dc2626"
              @click="logout"
            >
              <i class="ri-logout-box-r-line"></i>
              退出登录
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </header>

  <!-- 点击外部关闭下拉 -->
  <div
    v-if="showDropdown"
    class="fixed inset-0 z-20"
    @click="closeDropdown"
  ></div>
</template>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
