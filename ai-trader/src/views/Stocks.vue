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
  <div class="space-y-5">
    <!-- 市场状态 -->
    <div class="rounded-xl p-4" :style="{
      background: store.marketStatus.isOpen ? 'rgba(34,197,94,0.06)' : 'rgba(245,166,35,0.06)',
      border: `1px solid ${store.marketStatus.isOpen ? 'rgba(34,197,94,0.2)' : 'rgba(245,166,35,0.2)'}`,
    }">
      <div class="text-sm font-bold mb-1" :style="{ color: store.marketStatus.isOpen ? '#166534' : '#92400e' }">
        {{ store.marketStatus.label }}（{{ store.marketStatus.dateLabel }}）
      </div>
      <div class="text-xs" :style="{ color: store.marketStatus.isOpen ? '#166534' : '#92400e', opacity: 0.7 }">
        {{ store.marketStatus.statusLabel }}
      </div>
    </div>

    <!-- 指数行情 -->
    <el-card>
      <template #header>
        <span class="font-bold">📈 实时指数行情</span>
      </template>
      <el-row :gutter="24">
        <el-col :span="8">
          <div class="text-xs font-semibold mb-2" style="color: #64748b">国内</div>
          <div v-for="idx in store.marketIndices" :key="idx.code" class="text-xs flex justify-between py-1">
            <span>{{ idx.name }}</span>
            <span :style="{ color: idx.direction === 'up' ? '#dc2626' : '#16a34a' }">
              {{ idx.value }} ({{ idx.change }})
            </span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="text-xs font-semibold mb-2" style="color: #64748b">美股</div>
          <div v-for="idx in overseasIndices.us" :key="idx.code" class="text-xs flex justify-between py-1">
            <span>{{ idx.name }}</span>
            <span :style="{ color: idx.direction === 'up' ? '#dc2626' : '#16a34a' }">
              {{ idx.value }} ({{ idx.change }})
            </span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="text-xs font-semibold mb-2" style="color: #64748b">港股</div>
          <div v-for="idx in overseasIndices.hk" :key="idx.code" class="text-xs flex justify-between py-1">
            <span>{{ idx.name }}</span>
            <span :style="{ color: idx.direction === 'up' ? '#dc2626' : '#16a34a' }">
              {{ idx.value }} ({{ idx.change }})
            </span>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 行业板块排名 -->
    <div class="rounded-xl p-5" style="background: #fff; border: 1px solid #e2e8f0">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-sm font-semibold" style="color: #0f172a">行业板块涨跌排名</h3>
        <span class="text-xs" style="color: #94a3b8">共 {{ industryRanking.total }} 个行业</span>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <!-- 涨幅前15 -->
        <div>
          <div class="text-xs font-semibold mb-3" style="color: #dc2626">涨幅 TOP 15</div>
          <div class="space-y-1.5">
            <div
              v-for="r in industryRanking.top"
              :key="r.code"
              class="flex items-center gap-3 py-2 px-3 rounded-lg transition-all hover:bg-gray-50"
              style="background: #f8fafc; border: 1px solid #f1f5f9"
            >
              <span class="text-xs font-mono w-6 text-right" style="color: #94a3b8">{{ r.rank }}</span>
              <span class="text-xs font-semibold flex-1" style="color: #0f172a">{{ r.name }}</span>
              <span class="text-xs" style="color: #94a3b8">领涨 {{ r.leader }}</span>
              <span class="text-xs font-bold w-16 text-right" style="color: #dc2626">
                +{{ r.change_pct }}%
              </span>
            </div>
            <div v-if="!industryRanking.top.length" class="text-xs text-center py-4" style="color: #94a3b8">
              {{ loading ? '加载中…' : '暂无数据' }}
            </div>
          </div>
        </div>

        <!-- 跌幅前15 -->
        <div>
          <div class="text-xs font-semibold mb-3" style="color: #16a34a">跌幅 TOP 15</div>
          <div class="space-y-1.5">
            <div
              v-for="r in industryRanking.bottom"
              :key="r.code"
              class="flex items-center gap-3 py-2 px-3 rounded-lg transition-all hover:bg-gray-50"
              style="background: #f8fafc; border: 1px solid #f1f5f9"
            >
              <span class="text-xs font-mono w-6 text-right" style="color: #94a3b8">{{ r.rank }}</span>
              <span class="text-xs font-semibold flex-1" style="color: #0f172a">{{ r.name }}</span>
              <span class="text-xs" style="color: #94a3b8">领涨 {{ r.leader }}</span>
              <span class="text-xs font-bold w-16 text-right" style="color: #16a34a">
                {{ r.change_pct }}%
              </span>
            </div>
            <div v-if="!industryRanking.bottom.length" class="text-xs text-center py-4" style="color: #94a3b8">
              {{ loading ? '加载中…' : '暂无数据' }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
