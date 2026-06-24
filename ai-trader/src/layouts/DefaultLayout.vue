<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useAppStore } from '@/stores/app'
import AppHeader from '@/components/AppHeader.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AiChatButton from '@/components/AiChatButton.vue'

const store = useAppStore()

let refreshTimer = null

onMounted(() => {
  store.fetchAll()
  refreshTimer = setInterval(() => {
    store.fetchMarketIndices()
    store.fetchAccount()
  }, 15000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<template>
  <div class="min-h-screen" style="background: var(--color-bg-page)">
    <AppHeader />
    <AppSidebar />
    <main
      class="transition-all duration-300"
      style="padding-top: var(--header-height); margin-left: var(--sidebar-width)"
    >
      <div class="p-8 max-w-[1600px] mx-auto">
        <router-view v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </router-view>
      </div>
    </main>
    <AiChatButton />
  </div>
</template>

<style scoped>
@media (max-width: 767px) {
  main {
    margin-left: 0 !important;
  }
}
</style>
