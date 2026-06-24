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
  <div class="space-y-8 animate-fade-in">
    <!-- 页面标题 -->
    <div>
      <h1 class="text-2xl font-bold" style="color: var(--color-text-primary)">账户设置</h1>
      <p class="text-sm mt-1" style="color: var(--color-text-muted)">管理你的个人信息、AI 策略和偏好</p>
    </div>

    <RiskBanner />

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
      <!-- 左侧边栏 -->
      <div class="lg:col-span-1 space-y-3">
        <!-- 用户资料卡 -->
        <div class="card p-6 text-center">
          <div class="relative inline-block mb-4">
            <div
              class="w-20 h-20 rounded-full flex items-center justify-center text-3xl font-bold mx-auto"
              style="background: linear-gradient(135deg, #6366f1, #4f46e5); color: #fff; border: 3px solid rgba(99, 102, 241,0.2)"
            >{{ store.user.avatar }}</div>
            <div
              class="absolute -bottom-0.5 -right-0.5 w-6 h-6 rounded-full flex items-center justify-center cursor-pointer"
              style="background: #fff; border: 2px solid rgba(99, 102, 241,0.3)"
            >
              <i class="ri-pencil-line text-xs" style="color: #6366f1"></i>
            </div>
          </div>
          <p class="text-base font-bold" style="color: var(--color-text-primary)">{{ store.user.phone }}</p>
          <p class="text-xs mt-1" style="color: var(--color-text-muted)">UID-390</p>
          <div class="flex items-center justify-center gap-1.5 mt-3">
            <span class="w-1.5 h-1.5 rounded-full" style="background: var(--color-success)"></span>
            <span class="text-xs font-medium" style="color: var(--color-success)">账号状态正常</span>
          </div>
        </div>

        <!-- 导航按钮 -->
        <div class="card p-2 space-y-1">
          <button
            v-for="item in menuItems"
            :key="item.key"
            class="w-full flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer transition-all text-left"
            :style="activeMenu === item.key
              ? { background: 'var(--color-primary-light)', color: 'var(--color-primary)' }
              : { background: 'transparent', color: 'var(--color-text-secondary)' }"
            @click="activeMenu = item.key"
          >
            <i :class="item.icon" class="text-base w-5 h-5 flex items-center justify-center" :style="{ color: activeMenu === item.key ? 'var(--color-primary)' : 'var(--color-text-muted)' }"></i>
            <span class="text-sm font-medium">{{ item.label }}</span>
            <span
              v-if="item.badge && activeMenu === item.key"
              class="ml-auto badge"
              style="background: var(--color-primary-light); color: var(--color-primary)"
            >{{ item.badge }}</span>
          </button>
        </div>

        <!-- 账户信息 -->
        <div class="card p-5">
          <h4 class="text-xs font-semibold mb-4 uppercase tracking-wider" style="color: var(--color-text-muted)">账户信息</h4>
          <div class="space-y-3">
            <div>
              <p class="text-xs" style="color: var(--color-text-muted)">账号 ID</p>
              <p class="text-sm font-medium mt-0.5" style="color: var(--color-text-primary)">UID-390</p>
            </div>
            <div class="h-px" style="background: var(--color-border-light)"></div>
            <div>
              <p class="text-xs" style="color: var(--color-text-muted)">用户名</p>
              <p class="text-sm font-medium mt-0.5" style="color: var(--color-text-primary)">user_18138018452</p>
            </div>
            <div class="h-px" style="background: var(--color-border-light)"></div>
            <div>
              <p class="text-xs" style="color: var(--color-text-muted)">来源平台</p>
              <p class="text-sm font-medium mt-0.5" style="color: var(--color-text-primary)">主站授权</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧内容区 -->
      <div class="lg:col-span-3 space-y-6">
        <!-- AI 策略配置 -->
        <template v-if="activeMenu === 'strategy'">
          <!-- 提示横幅 -->
          <div class="card p-5 flex items-start gap-4" style="background: linear-gradient(135deg, rgba(124,58,237,0.05) 0%, rgba(99, 102, 241,0.03) 100%); border-color: rgba(124,58,237,0.15)">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0" style="background: rgba(124,58,237,0.1)">
              <i class="ri-information-line text-lg" style="color: #7c3aed"></i>
            </div>
            <div class="text-sm leading-relaxed flex-1" style="color: var(--color-text-secondary)">
              <div class="font-semibold mb-2" style="color: var(--color-text-primary)">「AI 策略选择」和「AI 策略配置」会相互影响</div>
              <p class="mb-2">选择一个内置策略决定了 AI 的<span class="font-medium" style="color: var(--color-text-primary)">基础风格</span>（选股池 / 调仓节奏 / 风控阈值），而「AI 策略配置」是你<span class="font-medium" style="color: var(--color-text-primary)">在该风格上的个性化覆盖</span>（资金 / 板块 / 风险偏好 / 单仓占比）。</p>
              <p><span class="font-medium" style="color: #7c3aed">切换策略</span> 时可选择「清空旧持仓」从零开始，或「保留旧持仓」延续当前交易和 AI 决策历史；<span class="font-medium" style="color: var(--color-primary)">修改配置</span> 不重启会话，只通知 AI 重新校准。 当前运行策略：<span class="font-semibold" style="color: var(--color-text-primary)">智能体自选</span>。</p>
              <button class="mt-3 inline-flex items-center gap-1 text-sm font-medium cursor-pointer hover:underline" style="color: #7c3aed">
                前往「AI 策略选择」切换内置策略<i class="ri-arrow-right-line text-sm"></i>
              </button>
            </div>
          </div>

          <!-- 策略配置表单 -->
          <div class="card p-8">
            <div class="flex items-center justify-between mb-8">
              <h3 class="text-lg font-bold flex items-center gap-2" style="color: var(--color-text-primary)">
                <i class="ri-robot-2-line" style="color: var(--color-primary)"></i>AI 策略配置
                <span class="badge ml-1" style="background: var(--color-primary-light); color: var(--color-primary); border: 1px solid rgba(99,102,241,0.2)">修改后AI重新校准</span>
              </h3>
              <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg" style="background: var(--color-success-light); border: 1px solid rgba(16,185,129,0.2)">
                <i class="ri-links-line text-xs" style="color: var(--color-success)"></i>
                <span class="text-xs font-medium" style="color: var(--color-success)">已同步</span>
              </div>
            </div>

            <!-- 模拟资金总额 -->
            <div class="mb-8">
              <div class="flex items-center justify-between mb-3">
                <label class="text-sm font-medium" style="color: var(--color-text-secondary)">模拟资金总额</label>
                <span class="text-lg font-bold tabular-nums" style="color: var(--color-primary)">¥{{ Number(fundAmount).toLocaleString() }}</span>
              </div>
              <div class="relative mb-4">
                <span class="absolute inset-y-0 left-4 flex items-center text-base font-bold" style="color: var(--color-primary)">¥</span>
                <input
                  v-model="fundAmount"
                  inputmode="numeric"
                  class="w-full pl-9 pr-4 py-3 rounded-xl text-sm outline-none transition-all"
                  placeholder="输入金额，如 5000000"
                  style="background: var(--color-border-light); border: 2px solid rgba(99, 102, 241,0.3); color: var(--color-text-primary)"
                />
              </div>
              <div class="flex gap-2 flex-wrap mb-4">
                <button
                  v-for="p in fundPresets"
                  :key="p.value"
                  class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer whitespace-nowrap transition-all"
                  :style="Number(fundAmount) === p.value
                    ? { background: 'var(--color-primary-light)', border: '1px solid rgba(99, 102, 241,0.3)', color: 'var(--color-primary)' }
                    : { background: 'var(--color-border-light)', border: '1px solid var(--color-border)', color: 'var(--color-text-secondary)' }"
                  @click="setFund(p.value)"
                >{{ p.label }}</button>
              </div>
              <button class="flex items-center gap-1.5 text-xs cursor-pointer whitespace-nowrap font-medium" style="color: var(--color-danger)">
                <i class="ri-restart-line"></i>重置清仓重来
              </button>
            </div>

            <div class="h-px mb-8" style="background: var(--color-border-light)"></div>

            <!-- 投资板块偏好 -->
            <div class="mb-8">
              <div class="flex items-center justify-between mb-4">
                <label class="text-sm font-medium" style="color: var(--color-text-secondary)">投资板块偏好</label>
                <span class="text-xs" style="color: var(--color-text-muted)">已选 {{ selectedSectors.includes('all') ? '1' : selectedSectors.length }} 个板块</span>
              </div>
              <div class="grid grid-cols-3 gap-3">
                <button
                  v-for="s in sectors"
                  :key="s.key"
                  class="flex items-center gap-2 px-4 py-3 rounded-xl cursor-pointer transition-all"
                  :style="selectedSectors.includes(s.key)
                    ? { background: 'var(--color-primary-light)', border: '1px solid rgba(99, 102, 241,0.3)', color: 'var(--color-primary)' }
                    : { background: 'var(--color-border-light)', border: '1px solid var(--color-border)', color: 'var(--color-text-secondary)' }"
                  @click="toggleSector(s.key)"
                >
                  <i :class="s.icon" class="text-base"></i>
                  <span class="text-xs font-medium">{{ s.label }}</span>
                  <i v-if="selectedSectors.includes(s.key)" class="ri-checkbox-circle-fill text-xs ml-auto" style="color: var(--color-primary)"></i>
                </button>
              </div>
            </div>

            <div class="h-px mb-8" style="background: var(--color-border-light)"></div>

            <!-- 风险偏好 -->
            <div class="mb-8">
              <div class="flex items-center justify-between mb-4">
                <label class="text-sm font-medium" style="color: var(--color-text-secondary)">风险偏好</label>
                <span class="px-4 py-1.5 rounded-full text-sm font-bold" style="background: var(--color-primary-light); color: var(--color-primary); border: 1px solid rgba(99, 102, 241,0.2)">{{ riskLabel }}</span>
              </div>
              <input
                v-model.number="riskLevel"
                min="0" max="100" step="1"
                class="w-full h-2 rounded-full appearance-none cursor-pointer"
                type="range"
                style="accent-color: var(--color-primary)"
                @input="updateRiskLabel"
              />
              <div class="flex justify-between text-xs mt-2" style="color: var(--color-text-muted)">
                <span>保守</span><span>平衡</span><span>激进</span>
              </div>
            </div>

            <!-- 最大单笔仓位占比 -->
            <div class="mb-8">
              <div class="flex items-center justify-between mb-4">
                <label class="text-sm font-medium" style="color: var(--color-text-secondary)">最大单笔仓位占比</label>
                <span class="text-lg font-bold tabular-nums" style="color: var(--color-primary)">{{ maxPositionPct }}%</span>
              </div>
              <input
                v-model.number="maxPositionPct"
                min="5" max="50" step="5"
                class="w-full h-2 rounded-full appearance-none cursor-pointer"
                type="range"
                style="accent-color: var(--color-primary)"
              />
              <div class="flex justify-between text-xs mt-2" style="color: var(--color-text-muted)">
                <span>5%（分散）</span><span>50%（集中）</span>
              </div>
            </div>

            <div class="h-px my-8" style="background: var(--color-border-light)"></div>

            <!-- 保存按钮 -->
            <button
              class="w-full py-4 rounded-xl font-bold text-sm cursor-pointer whitespace-nowrap transition-all duration-200 flex items-center justify-center gap-2 hover:shadow-lg hover:scale-[1.01] active:scale-[0.99]"
              style="background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: #fff"
              @click="saveConfig"
            >
              <i :class="saved ? 'ri-check-line' : 'ri-save-line'"></i>
              {{ saved ? '已保存' : '保存并通知 AI 重新校准' }}
            </button>
          </div>
        </template>

        <!-- 其他菜单占位 -->
        <template v-else>
          <div class="card py-20 text-center">
            <div class="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4" style="background: var(--color-border-light)">
              <i class="ri-settings-3-line text-3xl" style="color: var(--color-text-faint)"></i>
            </div>
            <p class="text-sm" style="color: var(--color-text-muted)">{{ menuItems.find(m => m.key === activeMenu)?.label }}功能开发中…</p>
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
  background: #6366f1;
  cursor: pointer;
  border: 3px solid #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.15);
}
</style>
