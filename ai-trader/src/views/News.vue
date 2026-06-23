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
</script>

<template>
  <div>
    <RiskBanner />

    <!-- 主 Tab -->
    <div class="flex gap-2 mb-4">
      <el-button
        :type="activeMainTab === 'hot' ? 'primary' : ''"
        :class="activeMainTab === 'hot' ? '' : '!bg-white !border !border-gray-200 !text-gray-500'"
        @click="activeMainTab = 'hot'"
      >热榜新闻</el-button>
      <el-button
        :type="activeMainTab === 'monitor' ? 'primary' : ''"
        :class="activeMainTab === 'monitor' ? '' : '!bg-white !border !border-gray-200 !text-gray-500'"
        @click="activeMainTab = 'monitor'"
      >利好监控</el-button>
    </div>

    <!-- 热榜新闻 -->
    <div v-if="activeMainTab === 'hot'">
      <!-- 级别筛选 -->
      <div class="flex gap-2 mb-4">
        <el-button
          v-for="l in ['全部', '重大', '一般']"
          :key="l"
          size="small"
          :type="activeLevel === l ? 'primary' : ''"
          :plain="activeLevel !== l"
          @click="activeLevel = l"
        >{{ l }}</el-button>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="text-center py-10">
        <el-icon class="is-loading" :size="24"><i class="ri-loader-4-line"></i></el-icon>
        <p class="text-sm mt-2" style="color: #94a3b8">加载实时新闻中…</p>
      </div>

      <!-- 新闻列表 -->
      <div v-else-if="filteredNews.length" class="space-y-3">
        <div
          v-for="n in filteredNews"
          :key="n.rank"
          class="flex gap-4 p-4 rounded-xl cursor-pointer transition-all duration-200 hover:shadow-md hover:-translate-y-0.5"
          style="background: #fff; border: 1px solid #e2e8f0"
        >
          <div
            class="w-7 h-7 rounded-md flex items-center justify-center text-xs font-bold shrink-0"
            :style="{ background: n.rank <= 3 ? 'rgba(220,38,38,0.1)' : '#f1f5f9', color: n.rank <= 3 ? '#dc2626' : '#64748b' }"
          >
            {{ n.rank }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <el-tag
                :type="n.level === '重大' ? 'danger' : 'info'"
                size="small"
                effect="plain"
              >{{ n.level }}</el-tag>
              <span class="text-xs" style="color: #94a3b8">{{ n.time }}</span>
            </div>
            <div class="text-sm font-medium leading-relaxed" style="color: #0f172a">{{ n.title }}</div>
            <div v-if="n.impact" class="mt-2 p-3 rounded-md text-xs leading-relaxed" style="background: #f8fafc; color: #64748b">{{ n.impact }}</div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="text-center py-10">
        <i class="ri-newspaper-line text-3xl" style="color: #cbd5e1"></i>
        <p class="text-sm mt-3" style="color: #94a3b8">暂无新闻数据</p>
      </div>
    </div>

    <!-- 利好监控 -->
    <div v-if="activeMainTab === 'monitor'">
      <div class="flex gap-2 mb-4">
        <el-button v-for="t in ['近6小时', '近24小时', '近3日']" :key="t" size="small" plain>{{ t }}</el-button>
      </div>
      <el-empty description="利好监控功能开发中…" />
    </div>
  </div>
</template>
