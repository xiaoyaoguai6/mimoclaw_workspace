<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '@/api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const initLoading = ref(false)
const status = ref(null)
const results = ref([])

let pollTimer = null

const initProgress = computed(() => {
  if (!status.value?.init) return 0
  const { total, fetched } = status.value.init
  if (!total) return 0
  return Math.round((fetched / total) * 100)
})

const screenProgress = computed(() => {
  if (!status.value) return 0
  const { screen_total, screen_done } = status.value
  if (!screen_total) return 0
  return Math.round((screen_done / screen_total) * 100)
})

const signalLabels = {
  macd: 'MACD', kdj: 'KDJ', rsi: 'RSI',
  lwr: 'LWR威廉', bbi: 'BBI多空', rc: 'RC动量',
}

async function fetchStatus() {
  try {
    status.value = await api.getScreenerStatus()
    // 同步结果
    if (status.value.results?.length) {
      results.value = status.value.results
    }
    return status.value
  } catch (e) {
    console.error('fetch status:', e)
  }
}

async function startInitialize() {
  initLoading.value = true
  try {
    const data = await api.initializeScreener()
    if (data.status === 'already_initialized') {
      ElMessage.info('已经初始化过了')
      initLoading.value = false
    } else if (data.status === 'already_running') {
      ElMessage.info('初始化正在进行中…')
    } else {
      ElMessage.success('初始化已启动,后台获取数据中…')
    }
    startPolling()
  } catch (e) {
    ElMessage.error('初始化失败: ' + e.message)
    initLoading.value = false
  }
}

async function startRefresh() {
  if (!status.value?.init?.initialized) {
    ElMessage.warning('请先完成初始化')
    return
  }
  loading.value = true
  results.value = []
  try {
    const data = await api.refreshScreener()
    if (data.status === 'already_running') {
      ElMessage.info('选股正在进行中…')
    } else if (data.status === 'not_initialized') {
      ElMessage.warning('请先完成初始化')
      loading.value = false
    } else {
      ElMessage.success('选股已启动,后台运行中…')
    }
    startPolling()
  } catch (e) {
    ElMessage.error('选股失败: ' + e.message)
    loading.value = false
  }
}

function startPolling() {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = setInterval(async () => {
    const s = await fetchStatus()
    if (!s) return

    // 初始化完成检测
    if (initLoading.value && !s.init.running) {
      if (s.init.initialized) {
        initLoading.value = false
        ElMessage.success(`初始化完成,共 ${s.init.total} 只股票`)
        stopPolling()
      } else if (s.init_error) {
        initLoading.value = false
        ElMessage.error('初始化失败: ' + s.init_error)
        stopPolling()
      }
    }

    // 选股完成检测
    if (loading.value && !s.screen_running) {
      loading.value = false
      if (s.screen_error) {
        ElMessage.error('选股失败: ' + s.screen_error)
      } else if (s.results?.length) {
        ElMessage.success(`选股完成,共选出 ${s.results.length} 只股票`)
      } else {
        ElMessage.info('选股完成,今日无符合条件的股票')
      }
      stopPolling()
    }
  }, 1500)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

onMounted(() => { fetchStatus() })
onUnmounted(() => { stopPolling() })
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold" style="color: var(--color-text-primary)">智能选股</h1>
        <p class="text-sm mt-1" style="color: var(--color-text-muted)">六脉神剑 + 筹码D值增强 + 热度综合选股</p>
      </div>
      <button
        class="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold cursor-pointer transition-all hover:shadow-lg hover:scale-105 active:scale-95"
        style="background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark)); color: #fff"
        :disabled="loading || initLoading"
        @click="startRefresh"
      >
        <i :class="loading ? 'ri-loader-4-line animate-spin' : 'ri-refresh-line'" class="text-base"></i>
        {{ loading ? '选股中…' : '刷新选股' }}
      </button>
    </div>

    <!-- 策略说明卡片 -->
    <div class="card p-5">
      <div class="flex items-center gap-2 mb-4">
        <i class="ri-sword-line text-lg" style="color: var(--color-primary)"></i>
        <h3 class="text-sm font-bold" style="color: var(--color-text-primary)">选股策略说明</h3>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="p-4 rounded-xl" style="background: var(--color-border-light)">
          <p class="text-xs font-bold mb-2" style="color: var(--color-primary)">六脉神剑共振</p>
          <p class="text-xs leading-relaxed" style="color: var(--color-text-muted)">MACD变种 + KDJ变种 + RSI + LWR威廉 + BBI多空 + RC动量,六指标同时共振</p>
        </div>
        <div class="p-4 rounded-xl" style="background: var(--color-border-light)">
          <p class="text-xs font-bold mb-2" style="color: var(--color-primary)">筹码D值增强</p>
          <p class="text-xs leading-relaxed" style="color: var(--color-text-muted)">WINNER获利盘估算,D值>800且递增,筹码集中度筛选</p>
        </div>
        <div class="p-4 rounded-xl" style="background: var(--color-border-light)">
          <p class="text-xs font-bold mb-2" style="color: var(--color-primary)">热度综合</p>
          <p class="text-xs leading-relaxed" style="color: var(--color-text-muted)">换手率>3% 且 量比>1,活跃度筛选,首次共振触发</p>
        </div>
      </div>
    </div>

    <!-- 初始化状态 -->
    <div v-if="status && !status.init.initialized && !initLoading" class="card p-8 text-center">
      <div class="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4" style="background: var(--color-primary-light)">
        <i class="ri-database-2-line text-3xl" style="color: var(--color-primary)"></i>
      </div>
      <h3 class="text-base font-bold mb-2" style="color: var(--color-text-primary)">首次使用需要初始化</h3>
      <p class="text-sm mb-6" style="color: var(--color-text-muted)">将获取主板+创业板所有股票的最近60天K线数据到本地数据库</p>
      <button
        class="px-6 py-3 rounded-xl text-sm font-bold cursor-pointer transition-all hover:shadow-lg hover:scale-105"
        style="background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark)); color: #fff"
        @click="startInitialize"
      >
        <i class="ri-download-cloud-2-line mr-2"></i>开始初始化
      </button>
    </div>

    <!-- 初始化进度 -->
    <div v-if="initLoading" class="card p-8">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-10 h-10 rounded-xl flex items-center justify-center animate-spin" style="border: 3px solid var(--color-border-light); border-top-color: var(--color-primary)">
          <i class="ri-loader-4-line" style="color: var(--color-primary)"></i>
        </div>
        <div>
          <h3 class="text-base font-bold" style="color: var(--color-text-primary)">正在获取股票数据…</h3>
          <p class="text-xs mt-0.5" style="color: var(--color-text-muted)">从通达信服务器下载60天K线</p>
        </div>
      </div>
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs" style="color: var(--color-text-muted)">{{ status?.init?.fetched || 0 }} / {{ status?.init?.total || 0 }} 只股票</span>
        <span class="text-sm font-bold tabular-nums" style="color: var(--color-primary)">{{ initProgress }}%</span>
      </div>
      <div class="h-2.5 rounded-full overflow-hidden" style="background: var(--color-border-light)">
        <div class="h-full rounded-full transition-all duration-500" :style="{ width: initProgress + '%', background: 'linear-gradient(90deg, var(--color-primary), var(--color-accent))' }"></div>
      </div>
    </div>

    <!-- 选股 Loading -->
    <div v-if="loading" class="card p-12 text-center">
      <div class="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center animate-spin" style="border: 3px solid var(--color-border-light); border-top-color: var(--color-primary)">
        <i class="ri-radar-line text-2xl" style="color: var(--color-primary)"></i>
      </div>
      <h3 class="text-base font-bold mb-2" style="color: var(--color-text-primary)">正在智能选股…</h3>
      <p class="text-sm" style="color: var(--color-text-muted)">获取当天行情 + 运行六脉神剑策略</p>
      <div v-if="screenProgress > 0" class="max-w-sm mx-auto mt-5">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs tabular-nums" style="color: var(--color-text-muted)">{{ status?.screen_done || 0 }} / {{ status?.screen_total || 0 }}</span>
          <span class="text-sm font-bold tabular-nums" style="color: var(--color-primary)">{{ screenProgress }}%</span>
        </div>
        <div class="h-2 rounded-full overflow-hidden" style="background: var(--color-border-light)">
          <div class="h-full rounded-full transition-all duration-500" :style="{ width: screenProgress + '%', background: 'var(--color-primary)' }"></div>
        </div>
      </div>
    </div>

    <!-- 选股结果 -->
    <div v-if="!loading && !initLoading && results.length" class="space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-base font-bold" style="color: var(--color-text-primary)">
          选股结果 <span class="badge ml-2" style="background: var(--color-primary-light); color: var(--color-primary)">{{ results.length }} 只</span>
        </h3>
        <span class="text-xs" style="color: var(--color-text-muted)" v-if="status?.last_refresh">
          最后刷新: {{ new Date(status.last_refresh).toLocaleString('zh-CN') }}
        </span>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div
          v-for="stock in results"
          :key="stock.code"
          class="card card-hover p-5"
        >
          <div class="flex items-start justify-between mb-4">
            <div>
              <div class="flex items-center gap-2">
                <span class="text-base font-bold" style="color: var(--color-text-primary)">{{ stock.name }}</span>
                <span class="text-xs font-mono" style="color: var(--color-text-muted)">{{ stock.code }}</span>
              </div>
              <div class="text-lg font-bold mt-1 tabular-nums" style="color: var(--color-text-primary)">¥{{ stock.price?.toFixed(2) }}</div>
            </div>
            <div class="text-right">
              <p class="text-xs" style="color: var(--color-text-muted)">筹码D值</p>
              <p class="text-xl font-black tabular-nums" style="color: var(--color-primary)">{{ stock.d_val }}</p>
            </div>
          </div>

          <div class="flex flex-wrap gap-1.5 mb-3">
            <span
              v-for="(active, key) in stock.signals"
              :key="key"
              class="badge"
              :style="{
                background: active ? 'var(--color-success-light)' : 'var(--color-border-light)',
                color: active ? 'var(--color-success)' : 'var(--color-text-faint)',
                opacity: active ? 1 : 0.5,
              }"
            >
              <i :class="active ? 'ri-check-line' : 'ri-close-line'"></i>{{ signalLabels[key] }}
            </span>
          </div>

          <div v-if="stock.lmgz" class="flex items-center gap-2 px-3 py-2 rounded-lg" style="background: var(--color-primary-light)">
            <i class="ri-sword-fill" style="color: var(--color-primary)"></i>
            <span class="text-xs font-bold" style="color: var(--color-primary)">六脉共振触发</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && !initLoading && status?.init?.initialized && !results.length" class="card py-16 text-center">
      <div class="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4" style="background: var(--color-border-light)">
        <i class="ri-radar-line text-3xl" style="color: var(--color-text-faint)"></i>
      </div>
      <p class="text-sm" style="color: var(--color-text-muted)">点击右上角"刷新选股"开始筛选</p>
    </div>
  </div>
</template>
