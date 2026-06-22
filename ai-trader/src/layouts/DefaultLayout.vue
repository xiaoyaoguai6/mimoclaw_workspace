<script setup>
import { useAppStore } from '@/stores/app'
import AppHeader from '@/components/AppHeader.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AiChatButton from '@/components/AiChatButton.vue'
import CustomerService from '@/components/CustomerService.vue'

const store = useAppStore()
</script>

<template>
  <div class="min-h-screen" style="background: #f0f4f8">
    <AppHeader />
    <AppSidebar />
    <main
      class="transition-all duration-300 pt-14"
      :style="{ marginLeft: '220px' }"
    >
      <div class="p-6">
        <router-view />
      </div>
    </main>
    <AiChatButton />
    <CustomerService />
  </div>
</template>

<style scoped>
@media (max-width: 767px) {
  main {
    margin-left: 0 !important;
  }
}
</style>
