<script setup>
import { ref } from 'vue'
import RiskBanner from '@/components/RiskBanner.vue'

const activeMainTab = ref('hot')
const activeSource = ref('all')
const activeLevel = ref('all')

const sources = ['全部', '今日头条', '财联社', '微博', '知乎', '澎湃', '凤凰财经', '华尔街见闻']

const news = [
  { rank: 1, level: '一般', time: '06/19 21:31', title: '多伦多股市指数开盘下跌74.46点（或0.21%），报34,894.80点。', impact: '多伦多股市开盘小幅下跌，属于常规市场波动，反映短期投资者情绪偏弱。' },
  { rank: 2, level: '重大', time: '06/19 21:27', title: '以色列国防军发言人：只要以色列公民仍面临真主党的威胁，以军就将继续驻扎在"缓冲区"内。', impact: '以色列继续驻扎缓冲区表明地缘紧张局势持续，可能推升避险资产需求。' },
  { rank: 3, level: '一般', time: '06/19 21:19', title: '以色列军方发言人：我们尊重各项协议，并根据以色列领导层的指示行事。', impact: '以色列回应尊重协议并听从高层指示，态度审慎但未排除军事选项。' },
  { rank: 4, level: '重大', time: '06/19 21:15', title: '以色列国防军发言人：总参谋长向北部军区下达的指示未作改变。', impact: '以军总参谋长已指示将所有作战能力提供给前线部队，军事准备升级。' },
  { rank: 5, level: '重大', time: '06/19 21:14', title: '以色列国防军发言人：军队打击了100多个真主党目标。', impact: '以军大规模打击真主党目标且声明将继续行动，表明冲突烈度升级。' },
  { rank: 6, level: '一般', time: '06/19 21:12', title: '英国政府延长许可，允许公司继续与卢克石油国际有限公司开展业务。', impact: '英国延长许可使得相关公司能够继续与卢克石油国际开展业务。' },
]
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
      <!-- 来源筛选 -->
      <div class="flex gap-1 mb-4 flex-wrap">
        <el-button
          v-for="s in sources"
          :key="s"
          size="small"
          :type="activeSource === s ? 'primary' : ''"
          :plain="activeSource !== s"
          @click="activeSource = s"
        >{{ s }}</el-button>
      </div>

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

      <!-- 新闻列表 -->
      <div class="space-y-3">
        <div
          v-for="n in news"
          :key="n.rank"
          v-show="activeLevel === '全部' || activeLevel === n.level"
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
            <div class="mt-2 p-3 rounded-md text-xs leading-relaxed" style="background: #f8fafc; color: #64748b">{{ n.impact }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 利好监控 -->
    <div v-if="activeMainTab === 'monitor'">
      <div class="flex gap-2 mb-4">
        <el-button v-for="t in ['近6小时', '近24小时', '近3日']" :key="t" size="small" plain>{{ t }}</el-button>
      </div>
      <el-empty description="利好监控数据加载中..." />
    </div>
  </div>
</template>
