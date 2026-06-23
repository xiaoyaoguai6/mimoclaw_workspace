<script setup>
import { ref } from 'vue'
import { useAppStore } from '@/stores/app'
import RiskBanner from '@/components/RiskBanner.vue'

const store = useAppStore()

const activeMenu = ref('strategy')

const menuItems = [
  { key: 'basic', icon: 'ri-user-settings-line', label: '基本信息' },
  { key: 'strategy', icon: 'ri-robot-2-line', label: 'AI 策略配置', badge: '已同步' },
  { key: 'strategySelect', icon: 'ri-flask-line', label: 'AI 策略选择' },
  { key: 'security', icon: 'ri-shield-keyhole-line', label: '安全设置' },
  { key: 'notification', icon: 'ri-notification-3-line', label: '通知设置' },
  { key: 'achievement', icon: 'ri-trophy-line', label: '成就展示' },
]

// 策略配置数据
const fundAmount = ref('1000000')
const fundPresets = [
  { label: '¥50万', value: 500000 },
  { label: '¥100万', value: 1000000 },
  { label: '¥500万', value: 5000000 },
  { label: '¥1000万', value: 10000000 },
]

const sectors = [
  { key: 'all', icon: 'ri-layout-grid-line', label: '不限制', selected: true },
  { key: 'tech', icon: 'ri-cpu-line', label: '科技半导体', selected: false },
  { key: 'energy', icon: 'ri-flashlight-line', label: '新能源', selected: false },
  { key: 'consumer', icon: 'ri-shopping-bag-line', label: '消费零售', selected: false },
  { key: 'pharma', icon: 'ri-heart-pulse-line', label: '医药生物', selected: false },
  { key: 'finance', icon: 'ri-bank-line', label: '金融银行', selected: false },
  { key: 'military', icon: 'ri-rocket-line', label: '军工航天', selected: false },
]

const selectedSectors = ref(['all'])

const toggleSector = (key) => {
  if (key === 'all') {
    selectedSectors.value = ['all']
    return
  }
  const idx = selectedSectors.value.indexOf(key)
  if (idx >= 0) {
    selectedSectors.value.splice(idx, 1)
  } else {
    selectedSectors.value = selectedSectors.value.filter(s => s !== 'all')
    selectedSectors.value.push(key)
  }
  if (selectedSectors.value.length === 0) selectedSectors.value = ['all']
}

const riskLevel = ref(50)
const riskLabel = ref('平衡')

const updateRiskLabel = () => {
  if (riskLevel.value < 33) riskLabel.value = '保守'
  else if (riskLevel.value < 66) riskLabel.value = '平衡'
  else riskLabel.value = '激进'
}

const maxPositionPct = ref(20)

const setFund = (v) => {
  fundAmount.value = String(v)
}

const saved = ref(false)
const saveConfig = () => {
  saved.value = true
  setTimeout(() => { saved.value = false }, 2000)
}
</script>

<template>
  <div class="flex flex-col">
    <RiskBanner />

    <div class="flex items-center justify-between mb-5">
      <div></div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-5 items-start">
      <!-- 左侧边栏 -->
      <div class="lg:col-span-1 space-y-2">
        <!-- 用户资料卡 -->
        <div class="rounded-xl p-5 text-center mb-3" style="background: #fff; border: 1px solid #e2e8f0">
          <div class="relative inline-block mb-3">
            <div
              class="w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold mx-auto"
              style="background: linear-gradient(135deg, #f5a623, #e8941a); color: #0a1628; border: 3px solid rgba(245,166,35,0.2)"
            >{{ store.user.avatar }}</div>
            <div
              class="absolute -bottom-0.5 -right-0.5 w-5 h-5 rounded-full flex items-center justify-center cursor-pointer"
              style="background: #fff; border: 2px solid rgba(245,166,35,0.3)"
            >
              <i class="ri-pencil-line text-xs" style="color: #d97706"></i>
            </div>
          </div>
          <p class="text-sm font-bold" style="color: #0f172a">{{ store.user.phone }}</p>
          <p class="text-xs mt-0.5" style="color: #94a3b8">UID-390</p>
          <div class="flex items-center justify-center gap-1.5 mt-2">
            <span class="w-1.5 h-1.5 rounded-full" style="background: #22c55e"></span>
            <span class="text-xs" style="color: #16a34a">账号状态正常</span>
          </div>
        </div>

        <!-- 导航按钮 -->
        <button
          v-for="item in menuItems"
          :key="item.key"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer transition-all text-left"
          :style="activeMenu === item.key
            ? { background: 'rgba(245,166,35,0.08)', border: '1px solid rgba(245,166,35,0.25)', color: '#d97706' }
            : { background: '#fff', border: '1px solid #e2e8f0', color: '#334155' }"
          @click="activeMenu = item.key"
        >
          <i :class="item.icon" class="text-base w-5 h-5 flex items-center justify-center" :style="{ color: activeMenu === item.key ? '#d97706' : '#94a3b8' }"></i>
          <span class="text-sm font-medium">{{ item.label }}</span>
          <span
            v-if="item.badge && activeMenu === item.key"
            class="ml-auto text-xs px-1.5 py-0.5 rounded-full"
            style="background: rgba(245,166,35,0.12); color: #d97706; font-size: 10px"
          >{{ item.badge }}</span>
        </button>

        <!-- 账户信息 -->
        <div class="rounded-xl p-4 mt-3" style="background: #f8fafc; border: 1px solid #f1f5f9">
          <h4 class="text-xs font-semibold mb-3" style="color: #94a3b8">账户信息</h4>
          <div class="py-1.5" style="border-bottom: 1px solid #f1f5f9">
            <p class="text-xs" style="color: #94a3b8">账号 ID</p>
            <p class="text-xs font-medium mt-0.5" style="color: #334155">UID-390</p>
          </div>
          <div class="py-1.5" style="border-bottom: 1px solid #f1f5f9">
            <p class="text-xs" style="color: #94a3b8">用户名</p>
            <p class="text-xs font-medium mt-0.5" style="color: #334155">user_18138018452</p>
          </div>
          <div class="py-1.5">
            <p class="text-xs" style="color: #94a3b8">来源平台</p>
            <p class="text-xs font-medium mt-0.5" style="color: #334155">主站授权</p>
          </div>
        </div>
      </div>

      <!-- 右侧内容区 -->
      <div class="lg:col-span-3 space-y-4">
        <!-- AI 策略配置 -->
        <template v-if="activeMenu === 'strategy'">
          <!-- 提示横幅 -->
          <div class="rounded-xl p-4 flex items-start gap-3" style="background: linear-gradient(135deg, rgba(124,58,237,0.06) 0%, rgba(245,166,35,0.04) 100%); border: 1px solid rgba(124,58,237,0.18)">
            <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style="background: rgba(124,58,237,0.12)">
              <i class="ri-information-line text-base" style="color: #7c3aed"></i>
            </div>
            <div class="text-xs leading-relaxed flex-1" style="color: #475569">
              <div class="font-semibold mb-1" style="color: #0f172a">「AI 策略选择」和「AI 策略配置」会相互影响</div>
              <p>选择一个内置策略决定了 AI 的<span class="font-medium" style="color: #0f172a">基础风格</span>（选股池 / 调仓节奏 / 风控阈值），而「AI 策略配置」是你<span class="font-medium" style="color: #0f172a">在该风格上的个性化覆盖</span>（资金 / 板块 / 风险偏好 / 单仓占比）。</p>
              <p class="mt-1"><span class="font-medium" style="color: #7c3aed">切换策略</span> 时可选择「清空旧持仓」从零开始，或「保留旧持仓」延续当前交易和 AI 决策历史；<span class="font-medium" style="color: #d97706">修改配置</span> 不重启会话，只通知 AI 重新校准。 当前运行策略：<span class="font-semibold" style="color: #0f172a">智能体自选</span>。</p>
              <button class="mt-2 inline-flex items-center gap-1 text-xs font-medium cursor-pointer hover:underline" style="color: #7c3aed">
                前往「AI 策略选择」切换内置策略<i class="ri-arrow-right-line text-xs"></i>
              </button>
            </div>
          </div>

          <!-- 策略配置表单 -->
          <div class="rounded-xl p-6" style="background: #fff; border: 1px solid #e2e8f0">
            <div class="flex items-center justify-between mb-5">
              <h3 class="text-sm font-semibold flex items-center gap-2" style="color: #0f172a">
                <i class="ri-robot-2-line" style="color: #d97706"></i>AI 策略配置
                <span class="text-xs px-2 py-0.5 rounded-full ml-1" style="background: rgba(245,166,35,0.08); color: #d97706; border: 1px solid rgba(245,166,35,0.2)">修改后AI重新校准</span>
              </h3>
              <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg" style="background: rgba(34,197,94,0.07); border: 1px solid rgba(34,197,94,0.2)">
                <i class="ri-links-line text-xs" style="color: #16a34a"></i>
                <span class="text-xs" style="color: #16a34a">已同步初始化配置</span>
              </div>
            </div>

            <!-- 模拟资金总额 -->
            <div class="mb-6">
              <div class="flex items-center justify-between mb-2">
                <label class="text-xs font-medium" style="color: #64748b">模拟资金总额</label>
                <span class="text-base font-bold" style="color: #d97706">¥{{ Number(fundAmount).toLocaleString() }}</span>
              </div>
              <div class="relative mb-3">
                <span class="absolute inset-y-0 left-3 flex items-center text-sm font-bold" style="color: rgba(217,119,6,0.7)">¥</span>
                <input
                  v-model="fundAmount"
                  inputmode="numeric"
                  class="w-full pl-7 pr-4 py-2.5 rounded-lg text-sm outline-none transition-all"
                  placeholder="输入金额，如 5000000"
                  style="background: #f1f5f9; border: 2px solid rgba(245,166,35,0.4); color: #0f172a"
                />
              </div>
              <div class="flex gap-2 flex-wrap mb-3">
                <button
                  v-for="p in fundPresets"
                  :key="p.value"
                  class="px-3 py-1.5 rounded-lg text-xs font-medium cursor-pointer whitespace-nowrap transition-all"
                  :style="Number(fundAmount) === p.value
                    ? { background: 'rgba(245,166,35,0.1)', border: '1px solid rgba(245,166,35,0.4)', color: '#d97706' }
                    : { background: '#f8fafc', border: '1px solid #e2e8f0', color: '#64748b' }"
                  @click="setFund(p.value)"
                >{{ p.label }}</button>
              </div>
              <button class="flex items-center gap-1.5 text-xs cursor-pointer whitespace-nowrap" style="color: #dc2626">
                <i class="ri-restart-line"></i>重置清仓重来
              </button>
            </div>

            <div class="h-px mb-6" style="background: #f1f5f9"></div>

            <!-- 投资板块偏好 -->
            <div class="mb-6">
              <div class="flex items-center justify-between mb-3">
                <label class="block text-xs font-medium" style="color: #64748b">投资板块偏好</label>
                <span class="text-xs" style="color: #94a3b8">已选 {{ selectedSectors.includes('all') ? '1' : selectedSectors.length }} 个板块</span>
              </div>
              <div class="grid grid-cols-3 gap-2">
                <button
                  v-for="s in sectors"
                  :key="s.key"
                  class="flex items-center gap-2 px-3 py-2.5 rounded-xl cursor-pointer transition-all hover:bg-orange-50"
                  :style="selectedSectors.includes(s.key)
                    ? { background: 'rgba(245,166,35,0.08)', border: '1px solid rgba(245,166,35,0.3)', color: '#d97706' }
                    : { background: '#f8fafc', border: '1px solid #e2e8f0', color: '#64748b' }"
                  @click="toggleSector(s.key)"
                >
                  <i :class="s.icon" class="text-sm"></i>
                  <span class="text-xs font-medium">{{ s.label }}</span>
                  <i v-if="selectedSectors.includes(s.key)" class="ri-checkbox-circle-fill text-xs ml-auto" style="color: #d97706"></i>
                </button>
              </div>
            </div>

            <div class="h-px mb-6" style="background: #f1f5f9"></div>

            <!-- 风险偏好 -->
            <div class="mb-6">
              <div class="flex items-center justify-between mb-3">
                <label class="text-xs font-medium" style="color: #64748b">风险偏好</label>
                <span class="px-3 py-1 rounded-full text-sm font-bold" style="background: rgba(217,119,6,0.063); color: #d97706; border: 1px solid rgba(217,119,6,0.19)">{{ riskLabel }}</span>
              </div>
              <input
                v-model.number="riskLevel"
                min="0" max="100" step="1"
                class="w-full h-1.5 rounded-full appearance-none cursor-pointer"
                type="range"
                style="accent-color: #d97706"
                @input="updateRiskLabel"
              />
              <div class="flex justify-between text-xs mt-1" style="color: #cbd5e1">
                <span>保守</span><span>平衡</span><span>激进</span>
              </div>
            </div>

            <!-- 最大单笔仓位占比 -->
            <div>
              <div class="flex items-center justify-between mb-3">
                <label class="text-xs font-medium" style="color: #64748b">最大单笔仓位占比</label>
                <span class="text-base font-bold" style="color: #d97706">{{ maxPositionPct }}%</span>
              </div>
              <input
                v-model.number="maxPositionPct"
                min="5" max="50" step="5"
                class="w-full h-1.5 rounded-full appearance-none cursor-pointer"
                type="range"
                style="accent-color: #f5a623"
              />
              <div class="flex justify-between text-xs mt-1" style="color: #cbd5e1">
                <span>5%（分散）</span><span>50%（集中）</span>
              </div>
            </div>

            <div class="h-px my-5" style="background: #f1f5f9"></div>

            <!-- 保存按钮 -->
            <button
              class="w-full py-3.5 rounded-xl font-semibold text-sm cursor-pointer whitespace-nowrap transition-all duration-200 flex items-center justify-center gap-2"
              style="background: linear-gradient(135deg, #f5a623 0%, #e8941a 100%); color: #0a1628"
              @click="saveConfig"
            >
              <i :class="saved ? 'ri-check-line' : 'ri-save-line'"></i>
              {{ saved ? '已保存' : '保存并通知 AI 重新校准' }}
            </button>
          </div>
        </template>

        <!-- 其他菜单占位 -->
        <template v-else>
          <div class="rounded-xl p-10 text-center" style="background: #fff; border: 1px solid #e2e8f0">
            <i class="ri-settings-3-line text-3xl" style="color: #cbd5e1"></i>
            <p class="text-sm mt-3" style="color: #94a3b8">{{ menuItems.find(m => m.key === activeMenu)?.label }}功能开发中...</p>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
input[type="range"] {
  -webkit-appearance: none;
  appearance: none;
  height: 6px;
  border-radius: 999px;
  background: #e2e8f0;
  outline: none;
}
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #f5a623;
  cursor: pointer;
  border: 3px solid #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.15);
}
</style>
