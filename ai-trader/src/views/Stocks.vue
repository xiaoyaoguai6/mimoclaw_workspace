<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { fetchGlobalIndices, fetchSinaSectors, fetchTHSHotList } from '@/services/stockApi'

// ===== 全球指数 =====
const indices = ref({ domestic: [], us: [], hk: [] })
const indicesLoading = ref(true)

// ===== 行业板块 =====
const sectors = ref([])
const sectorsLoading = ref(true)
const sectorViewMode = ref('top') // top | bottom

// ===== 同花顺热榜 =====
const hotList = ref([])
const hotListLoading = ref(true)

// ===== 刷新定时器 =====
let refreshTimer = null

const indexNameMap = {
  'sh000001': '上证指数', 'sz399001': '深证成指', 'sz399006': '创业板指',
  'sh000300': '沪深300', 'sh000016': '上证50', 'sh000905': '中证500',
  'usDJI': '道琼斯', 'usIXIC': '纳斯达克', 'usINX': '标普500',
  'hkHSI': '恒生指数', 'hkHSCEI': '国企指数', 'hkHSCCI': '红筹指数',
}

function formatPrice(val) {
  if (!val) return '--'
  return val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatChange(pct) {
  if (pct == null) return '--'
  const sign = pct >= 0 ? '+' : ''
  return `${sign}${pct.toFixed(2)}%`
}

function changeColor(pct) {
  if (pct > 0) return '#dc2626'
  if (pct < 0) return '#16a34a'
  return '#6b7280'
}

function formatAmount(val) {
  if (!val) return '--'
  if (val >= 100000000) return (val / 100000000).toFixed(1) + '亿'
  if (val >= 10000) return (val / 10000).toFixed(1) + '万'
  return val.toFixed(0)
}

async function loadAllData() {
  // 并行加载
  const [idxData, sectorData, hotData] = await Promise.all([
    fetchGlobalIndices().catch(() => ({ domestic: [], us: [], hk: [] })),
    fetchSinaSectors().catch(() => []),
    fetchTHSHotList().catch(() => []),
  ])

  indices.value = idxData
  indicesLoading.value = false

  sectors.value = sectorData
  sectorsLoading.value = false

  hotList.value = hotData.slice(0, 20)
  hotListLoading.value = false
}

onMounted(() => {
  loadAllData()
  // 每60秒刷新一次
  refreshTimer = setInterval(loadAllData, 60000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<template>
  <div>
    <!-- 休市横幅 -->
    <div class="rounded-xl p-4 mb-4" style="background: rgba(245,166,35,0.06); border: 1px solid rgba(245,166,35,0.2)">
      <div class="text-sm font-bold mb-1" style="color: #92400e">📊 实时行情数据</div>
      <div class="text-xs" style="color: #92400e; opacity: 0.7">
        数据来源：腾讯财经 + 新浪财经 + 同花顺 · 每分钟自动刷新
      </div>
    </div>

    <!-- 全球指数 -->
    <div class="card-section mb-4">
      <div class="section-header">
        <span class="section-title">📈 全球指数</span>
        <span v-if="indicesLoading" class="loading-tag">加载中...</span>
      </div>

      <div class="index-grid">
        <!-- 国内 -->
        <div class="index-col">
          <div class="index-col-title">🇨🇳 国内</div>
          <div v-if="indicesLoading" class="skeleton-row" v-for="i in 3" :key="i" />
          <div v-else v-for="item in indices.domestic" :key="item.key" class="index-row">
            <span class="index-name">{{ indexNameMap[item.key.replace('v_','')] || item.name }}</span>
            <span class="index-price">{{ formatPrice(item.price) }}</span>
            <span class="index-change" :style="{ color: changeColor(item.changePct) }">
              {{ formatChange(item.changePct) }}
            </span>
          </div>
        </div>

        <!-- 美股 -->
        <div class="index-col">
          <div class="index-col-title">🇺🇸 美股</div>
          <div v-if="indicesLoading" class="skeleton-row" v-for="i in 3" :key="i" />
          <div v-else v-for="item in indices.us" :key="item.key" class="index-row">
            <span class="index-name">{{ indexNameMap[item.key.replace('v_','')] || item.name }}</span>
            <span class="index-price">{{ formatPrice(item.price) }}</span>
            <span class="index-change" :style="{ color: changeColor(item.changePct) }">
              {{ formatChange(item.changePct) }}
            </span>
          </div>
        </div>

        <!-- 港股 -->
        <div class="index-col">
          <div class="index-col-title">🇭🇰 港股</div>
          <div v-if="indicesLoading" class="skeleton-row" v-for="i in 3" :key="i" />
          <div v-else v-for="item in indices.hk" :key="item.key" class="index-row">
            <span class="index-name">{{ indexNameMap[item.key.replace('v_','')] || item.name }}</span>
            <span class="index-price">{{ formatPrice(item.price) }}</span>
            <span class="index-change" :style="{ color: changeColor(item.changePct) }">
              {{ formatChange(item.changePct) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- A股行业板块 -->
    <div class="card-section mb-4">
      <div class="section-header">
        <span class="section-title">🏭 A股行业板块</span>
        <div class="toggle-group">
          <button :class="['toggle-btn', { active: sectorViewMode === 'top' }]" @click="sectorViewMode = 'top'">涨幅榜</button>
          <button :class="['toggle-btn', { active: sectorViewMode === 'bottom' }]" @click="sectorViewMode = 'bottom'">跌幅榜</button>
        </div>
      </div>

      <div v-if="sectorsLoading" class="loading-text">加载中...</div>
      <div v-else class="sector-grid">
        <div
          v-for="(s, idx) in sectorViewMode === 'top'
            ? sectors.slice(0, 15)
            : sectors.slice(-15).reverse()"
          :key="s.id"
          class="sector-item"
        >
          <div class="sector-rank" :class="{ 'top3': idx < 3 }">{{ idx + 1 }}</div>
          <div class="sector-info">
            <div class="sector-name">{{ s.name }}</div>
            <div class="sector-leader">领涨: {{ s.leaderName }}</div>
          </div>
          <div class="sector-change" :style="{ color: changeColor(s.changePct) }">
            {{ formatChange(s.changePct) }}
          </div>
        </div>
      </div>
    </div>

    <!-- 同花顺热榜 -->
    <div class="card-section mb-4">
      <div class="section-header">
        <span class="section-title">🔥 同花顺人气榜</span>
        <span v-if="hotListLoading" class="loading-tag">加载中...</span>
      </div>

      <div v-if="hotListLoading" class="loading-text">加载中...</div>
      <div v-else class="hot-grid">
        <div v-for="item in hotList" :key="item.code" class="hot-item">
          <div class="hot-rank" :class="{ 'top3': item.order <= 3 }">{{ item.order }}</div>
          <div class="hot-info">
            <div class="hot-name">{{ item.name }}</div>
            <div class="hot-code">{{ item.code }}</div>
          </div>
          <div class="hot-tags">
            <span v-for="tag in item.conceptTags.slice(0, 2)" :key="tag" class="hot-tag">{{ tag }}</span>
            <span v-if="item.popularityTag" class="hot-pop-tag">{{ item.popularityTag }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 卡片通用 */
.card-section {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1rem;
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}
.section-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: #0f172a;
}
.loading-tag {
  font-size: 0.75rem;
  color: #94a3b8;
}
.loading-text {
  font-size: 0.75rem;
  color: #94a3b8;
  padding: 1rem 0;
  text-align: center;
}

/* 全球指数 */
.index-grid {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}
.index-col {
  flex: 1;
  min-width: 200px;
}
.index-col-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 0.5rem;
  padding-bottom: 0.375rem;
  border-bottom: 1px solid #f1f5f9;
}
.index-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.375rem 0;
  font-size: 0.75rem;
}
.index-name {
  color: #0f172a;
  flex: 1;
}
.index-price {
  font-weight: 600;
  color: #0f172a;
  margin: 0 0.75rem;
  min-width: 70px;
  text-align: right;
}
.index-change {
  font-weight: 600;
  min-width: 60px;
  text-align: right;
}
.skeleton-row {
  height: 1.5rem;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 0.25rem;
  margin-bottom: 0.375rem;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

/* 切换按钮 */
.toggle-group {
  display: flex;
  gap: 0.125rem;
  padding: 0.125rem;
  background: #f1f5f9;
  border-radius: 0.5rem;
}
.toggle-btn {
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  background: transparent;
  border: none;
  color: #94a3b8;
  transition: all 0.2s;
}
.toggle-btn.active {
  background: #fff;
  color: #0f172a;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

/* 行业板块 */
.sector-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.25rem;
}
.sector-item {
  display: flex;
  align-items: center;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  transition: background 0.15s;
}
.sector-item:hover {
  background: #f8fafc;
}
.sector-rank {
  width: 1.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  flex-shrink: 0;
}
.sector-rank.top3 {
  color: #dc2626;
  font-weight: 700;
}
.sector-info {
  flex: 1;
  margin-left: 0.5rem;
}
.sector-name {
  font-size: 0.75rem;
  font-weight: 600;
  color: #0f172a;
}
.sector-leader {
  font-size: 0.625rem;
  color: #94a3b8;
  margin-top: 0.125rem;
}
.sector-change {
  font-size: 0.75rem;
  font-weight: 700;
  min-width: 50px;
  text-align: right;
}

/* 同花顺热榜 */
.hot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 0.25rem;
}
.hot-item {
  display: flex;
  align-items: center;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  transition: background 0.15s;
}
.hot-item:hover {
  background: #f8fafc;
}
.hot-rank {
  width: 1.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  flex-shrink: 0;
}
.hot-rank.top3 {
  color: #dc2626;
  font-weight: 700;
}
.hot-info {
  margin-left: 0.5rem;
  min-width: 80px;
}
.hot-name {
  font-size: 0.75rem;
  font-weight: 600;
  color: #0f172a;
}
.hot-code {
  font-size: 0.625rem;
  color: #94a3b8;
  font-family: monospace;
}
.hot-tags {
  flex: 1;
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.hot-tag {
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  background: rgba(59, 130, 246, 0.08);
  color: #3b82f6;
}
.hot-pop-tag {
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  background: rgba(245, 166, 35, 0.08);
  color: #d97706;
}
</style>
