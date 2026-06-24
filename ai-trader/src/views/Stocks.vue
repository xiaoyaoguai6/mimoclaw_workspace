<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import { useAppStore } from '@/stores/app'

const store = useAppStore()
const overseasIndices = ref({ us: [], hk: [] })
const industryRanking = ref({ top: [], bottom: [], total: 0 })
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const [overseas, ranking] = await Promise.allSettled([
      api.getOverseasIndices(),
      api.getIndustryRanking(15),
    ])
    if (overseas.status === 'fulfilled') {
      overseasIndices.value.us = overseas.value.filter(i => i.code.startsWith('usr'))
      overseasIndices.value.hk = overseas.value.filter(i => i.code.startsWith('hks'))
    }
    if (ranking.status === 'fulfilled') {
      industryRanking.value = ranking.value
    }
  } catch (e) {
    console.error(e)
  }
  loading.value = false
})
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- 市场状态 -->
    <div class="rounded-2xl p-5 card" :style="{
      background: store.marketStatus.isOpen ? 'var(--color-success-light)' : 'var(--color-warning-light)',
      border: `1px solid ${store.marketStatus.isOpen ? 'rgba(16,185,129,0.2)' : 'rgba(245,158,11,0.2)'}`,
    }">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl flex items-center justify-center" :style="{ background: store.marketStatus.isOpen ? 'rgba(16,185,129,0.15)' : 'rgba(245,158,11,0.15)' }">
          <i :class="store.marketStatus.isOpen ? 'ri-radio-button-line' : 'ri-pause-circle-line'" class="text-lg" :style="{ color: store.marketStatus.isOpen ? 'var(--color-success)' : 'var(--color-warning)' }"></i>
        </div>
        <div>
          <div class="text-sm font-bold" :style="{ color: store.marketStatus.isOpen ? 'var(--color-success)' : 'var(--color-warning)' }">
            {{ store.marketStatus.label }}
          </div>
          <div class="text-xs mt-0.5" :style="{ color: store.marketStatus.isOpen ? 'var(--color-success)' : 'var(--color-warning)', opacity: 0.7 }">
            {{ store.marketStatus.dateLabel }} · {{ store.marketStatus.statusLabel }}
          </div>
        </div>
      </div>
    </div>

    <!-- 指数行情卡片 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <div class="card p-5">
        <div class="flex items-center gap-2 mb-4">
          <span class="w-2 h-2 rounded-full" style="background: var(--color-danger)"></span>
          <span class="text-sm font-bold" style="color: var(--color-text-primary)">国内指数</span>
        </div>
        <div class="space-y-3">
          <div v-for="idx in store.marketIndices" :key="idx.code" class="flex items-center justify-between py-2" style="border-bottom: 1px solid var(--color-border-light)">
            <span class="text-sm" style="color: var(--color-text-secondary)">{{ idx.name }}</span>
            <div class="text-right">
              <span class="text-sm font-bold tabular-nums" style="color: var(--color-text-primary)">{{ idx.value }}</span>
              <span class="text-xs ml-2 tabular-nums font-semibold" :style="{ color: idx.direction === 'up' ? 'var(--color-up)' : 'var(--color-down)' }">
                {{ idx.change }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="card p-5">
        <div class="flex items-center gap-2 mb-4">
          <span class="w-2 h-2 rounded-full" style="background: #3b82f6"></span>
          <span class="text-sm font-bold" style="color: var(--color-text-primary)">美股指数</span>
        </div>
        <div class="space-y-3">
          <div v-for="idx in overseasIndices.us" :key="idx.code" class="flex items-center justify-between py-2" style="border-bottom: 1px solid var(--color-border-light)">
            <span class="text-sm" style="color: var(--color-text-secondary)">{{ idx.name }}</span>
            <div class="text-right">
              <span class="text-sm font-bold tabular-nums" style="color: var(--color-text-primary)">{{ idx.value }}</span>
              <span class="text-xs ml-2 tabular-nums font-semibold" :style="{ color: idx.direction === 'up' ? 'var(--color-up)' : 'var(--color-down)' }">
                {{ idx.change }}
              </span>
            </div>
          </div>
          <div v-if="!overseasIndices.us.length" class="text-xs text-center py-4" style="color: var(--color-text-muted)">加载中…</div>
        </div>
      </div>

      <div class="card p-5">
        <div class="flex items-center gap-2 mb-4">
          <span class="w-2 h-2 rounded-full" style="background: var(--color-warning)"></span>
          <span class="text-sm font-bold" style="color: var(--color-text-primary)">港股指数</span>
        </div>
        <div class="space-y-3">
          <div v-for="idx in overseasIndices.hk" :key="idx.code" class="flex items-center justify-between py-2" style="border-bottom: 1px solid var(--color-border-light)">
            <span class="text-sm" style="color: var(--color-text-secondary)">{{ idx.name }}</span>
            <div class="text-right">
              <span class="text-sm font-bold tabular-nums" style="color: var(--color-text-primary)">{{ idx.value }}</span>
              <span class="text-xs ml-2 tabular-nums font-semibold" :style="{ color: idx.direction === 'up' ? 'var(--color-up)' : 'var(--color-down)' }">
                {{ idx.change }}
              </span>
            </div>
          </div>
          <div v-if="!overseasIndices.hk.length" class="text-xs text-center py-4" style="color: var(--color-text-muted)">加载中…</div>
        </div>
      </div>
    </div>

    <!-- 行业板块排名 -->
    <div class="card p-6">
      <div class="flex items-center justify-between mb-5">
        <div class="flex items-center gap-2">
          <i class="ri-bar-chart-grouped-line text-lg" style="color: var(--color-primary)"></i>
          <h3 class="text-base font-bold" style="color: var(--color-text-primary)">行业板块涨跌排名</h3>
        </div>
        <span class="badge" style="background: var(--color-primary-light); color: var(--color-primary)">共 {{ industryRanking.total }} 个行业</span>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 涨幅 -->
        <div>
          <div class="flex items-center gap-2 mb-4">
            <i class="ri-arrow-up-circle-fill" style="color: var(--color-up)"></i>
            <span class="text-sm font-bold" style="color: var(--color-up)">涨幅 TOP 15</span>
          </div>
          <div class="space-y-2">
            <div
              v-for="r in industryRanking.top"
              :key="r.code"
              class="flex items-center gap-3 py-2.5 px-3 rounded-xl transition-all hover:translate-x-1"
              style="background: var(--color-border-light); border: 1px solid transparent"
            >
              <span class="text-xs font-mono w-6 text-right tabular-nums" style="color: var(--color-text-muted)">{{ r.rank }}</span>
              <span class="text-sm font-semibold flex-1" style="color: var(--color-text-primary)">{{ r.name }}</span>
              <span class="text-xs hidden sm:block" style="color: var(--color-text-muted)">领涨 {{ r.leader }}</span>
              <span class="text-sm font-bold w-20 text-right tabular-nums" style="color: var(--color-up)">
                +{{ r.change_pct }}%
              </span>
            </div>
            <div v-if="!industryRanking.top.length" class="text-xs text-center py-6" style="color: var(--color-text-muted)">
              {{ loading ? '加载中…' : '暂无数据' }}
            </div>
          </div>
        </div>

        <!-- 跌幅 -->
        <div>
          <div class="flex items-center gap-2 mb-4">
            <i class="ri-arrow-down-circle-fill" style="color: var(--color-down)"></i>
            <span class="text-sm font-bold" style="color: var(--color-down)">跌幅 TOP 15</span>
          </div>
          <div class="space-y-2">
            <div
              v-for="r in industryRanking.bottom"
              :key="r.code"
              class="flex items-center gap-3 py-2.5 px-3 rounded-xl transition-all hover:translate-x-1"
              style="background: var(--color-border-light); border: 1px solid transparent"
            >
              <span class="text-xs font-mono w-6 text-right tabular-nums" style="color: var(--color-text-muted)">{{ r.rank }}</span>
              <span class="text-sm font-semibold flex-1" style="color: var(--color-text-primary)">{{ r.name }}</span>
              <span class="text-xs hidden sm:block" style="color: var(--color-text-muted)">领涨 {{ r.leader }}</span>
              <span class="text-sm font-bold w-20 text-right tabular-nums" style="color: var(--color-down)">
                {{ r.change_pct }}%
              </span>
            </div>
            <div v-if="!industryRanking.bottom.length" class="text-xs text-center py-6" style="color: var(--color-text-muted)">
              {{ loading ? '加载中…' : '暂无数据' }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
