<script setup>
import { ref, computed, onMounted } from 'vue'
import RiskBanner from '@/components/RiskBanner.vue'
import api from '@/api'

const activeMainTab = ref('hot')
const activeLevel = ref('全部')
const loading = ref(false)

const news = ref([])

onMounted(async () => {
  loading.value = true
  try {
    news.value = await api.getGlobalNews(50)
  } catch (e) {
    console.error('fetch news:', e)
  }
  loading.value = false
})

const filteredNews = computed(() => {
  return news.value.map((n, i) => ({
    rank: i + 1,
    level: i < 5 ? '重大' : '一般',
    time: n.time,
    title: n.title,
    impact: n.summary,
  })).filter(n => activeLevel.value === '全部' || activeLevel.value === n.level)
})

const headline = computed(() => filteredNews.value[0] || null)
const restNews = computed(() => filteredNews.value.slice(1))
</script>

<template>
  <div class="space-y-8 animate-fade-in">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold" style="color: var(--color-text-primary)">热点新闻</h1>
        <p class="text-sm mt-1" style="color: var(--color-text-muted)">7×24 全球财经资讯 · 东方财富直连</p>
      </div>
      <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg card">
        <span class="w-2 h-2 rounded-full animate-pulse" style="background: var(--color-success)"></span>
        <span class="text-xs font-medium" style="color: var(--color-success)">实时更新</span>
      </div>
    </div>

    <RiskBanner />

    <!-- 主 Tab -->
    <div class="flex gap-2">
      <button
        class="px-5 py-2.5 rounded-xl text-sm font-medium cursor-pointer transition-all"
        :style="activeMainTab === 'hot'
          ? { background: 'var(--color-primary)', color: '#fff', boxShadow: '0 4px 12px rgba(99,102,241,0.25)' }
          : { background: 'var(--color-bg-card)', color: 'var(--color-text-secondary)', border: '1px solid var(--color-border)' }"
        @click="activeMainTab = 'hot'"
      >
        <i class="ri-fire-line mr-1.5"></i>热榜新闻
      </button>
      <button
        class="px-5 py-2.5 rounded-xl text-sm font-medium cursor-pointer transition-all"
        :style="activeMainTab === 'monitor'
          ? { background: 'var(--color-primary)', color: '#fff', boxShadow: '0 4px 12px rgba(99,102,241,0.25)' }
          : { background: 'var(--color-bg-card)', color: 'var(--color-text-secondary)', border: '1px solid var(--color-border)' }"
        @click="activeMainTab = 'monitor'"
      >
        <i class="ri-radar-line mr-1.5"></i>利好监控
      </button>
    </div>

    <!-- 热榜新闻 -->
    <div v-if="activeMainTab === 'hot'">
      <!-- 级别筛选 -->
      <div class="flex gap-2 mb-6">
        <button
          v-for="l in ['全部', '重大', '一般']"
          :key="l"
          class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer transition-all"
          :style="activeLevel === l
            ? { background: 'var(--color-primary-light)', color: 'var(--color-primary)', border: '1px solid rgba(99,102,241,0.2)' }
            : { background: 'var(--color-bg-card)', color: 'var(--color-text-muted)', border: '1px solid var(--color-border)' }"
          @click="activeLevel = l"
        >{{ l }}</button>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="card py-20 text-center">
        <div class="w-12 h-12 rounded-full mx-auto mb-4 flex items-center justify-center animate-spin" style="border: 3px solid var(--color-border-light); border-top-color: var(--color-primary)">
          <i class="ri-loader-4-line text-xl" style="color: var(--color-primary)"></i>
        </div>
        <p class="text-sm" style="color: var(--color-text-muted)">加载实时新闻中…</p>
      </div>

      <template v-else-if="filteredNews.length">
        <!-- 头条新闻 -->
        <div v-if="headline" class="card card-hover p-6 mb-6 cursor-pointer relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1 h-full" style="background: linear-gradient(180deg, var(--color-primary), var(--color-accent))"></div>
          <div class="flex items-center gap-3 mb-3">
            <span class="badge" style="background: var(--color-primary); color: #fff">头条</span>
            <span class="badge" :style="{
              background: headline.level === '重大' ? 'var(--color-danger-light)' : 'var(--color-border-light)',
              color: headline.level === '重大' ? 'var(--color-danger)' : 'var(--color-text-secondary)',
            }">{{ headline.level }}</span>
            <span class="text-xs tabular-nums ml-auto" style="color: var(--color-text-muted)">{{ headline.time }}</span>
          </div>
          <h2 class="text-lg font-bold leading-relaxed mb-3" style="color: var(--color-text-primary)">{{ headline.title }}</h2>
          <p v-if="headline.impact" class="text-sm leading-relaxed" style="color: var(--color-text-secondary)">{{ headline.impact }}</p>
        </div>

        <!-- 新闻列表 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div
            v-for="n in restNews"
            :key="n.rank"
            class="card card-hover p-5 cursor-pointer"
          >
            <div class="flex items-start gap-3">
              <div
                class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 mt-0.5"
                :style="{
                  background: n.rank <= 3 ? 'var(--color-danger-light)' : 'var(--color-border-light)',
                  color: n.rank <= 3 ? 'var(--color-danger)' : 'var(--color-text-muted)',
                }"
              >
                {{ n.rank }}
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-2">
                  <span class="badge" :style="{
                    background: n.level === '重大' ? 'var(--color-danger-light)' : 'var(--color-border-light)',
                    color: n.level === '重大' ? 'var(--color-danger)' : 'var(--color-text-secondary)',
                  }">{{ n.level }}</span>
                  <span class="text-xs tabular-nums" style="color: var(--color-text-muted)">{{ n.time }}</span>
                </div>
                <p class="text-sm font-semibold leading-relaxed mb-2" style="color: var(--color-text-primary)">{{ n.title }}</p>
                <p v-if="n.impact" class="text-xs leading-relaxed line-clamp-2" style="color: var(--color-text-muted)">{{ n.impact }}</p>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- 空状态 -->
      <div v-else class="card py-20 text-center">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4" style="background: var(--color-border-light)">
          <i class="ri-newspaper-line text-3xl" style="color: var(--color-text-faint)"></i>
        </div>
        <p class="text-sm" style="color: var(--color-text-muted)">暂无新闻数据</p>
      </div>
    </div>

    <!-- 利好监控 -->
    <div v-if="activeMainTab === 'monitor'">
      <div class="flex gap-2 mb-6">
        <button v-for="t in ['近6小时', '近24小时', '近3日']" :key="t" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background: var(--color-bg-card); border: 1px solid var(--color-border); color: var(--color-text-secondary)">{{ t }}</button>
      </div>
      <div class="card py-20 text-center">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4" style="background: var(--color-border-light)">
          <i class="ri-radar-line text-3xl" style="color: var(--color-text-faint)"></i>
        </div>
        <p class="text-sm" style="color: var(--color-text-muted)">利好监控功能开发中…</p>
      </div>
    </div>
  </div>
</template>
