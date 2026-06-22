<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import BlankLayout from '@/layouts/BlankLayout.vue'

const route = useRoute()
const layout = computed(() => {
  return route.meta.layout === 'blank' ? BlankLayout : DefaultLayout
})
</script>

<template>
  <component :is="layout">
    <router-view />
  </component>
</template>
