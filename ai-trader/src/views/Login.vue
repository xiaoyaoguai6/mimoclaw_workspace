<script setup>
import { useRouter } from 'vue-router'
import { ref } from 'vue'

const router = useRouter()
const username = ref('')
const password = ref('')
const showPassword = ref(false)

const handleLogin = () => {
  router.push('/dashboard')
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden" style="background: #1a2844">
    <!-- 网格背景 -->
    <div class="absolute inset-0 opacity-10" style="background-image: linear-gradient(rgba(245,166,35,0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(245,166,35,0.15) 1px, transparent 1px); background-size: 60px 60px"></div>

    <!-- 光晕 -->
    <div class="absolute top-1/4 left-1/4 w-96 h-96 rounded-full opacity-10" style="background: radial-gradient(circle, #f5a623 0%, transparent 70%)"></div>
    <div class="absolute bottom-1/4 right-1/4 w-64 h-64 rounded-full opacity-8" style="background: radial-gradient(circle, #1e40af 0%, transparent 70%)"></div>

    <!-- 装饰线条 -->
    <svg class="absolute inset-0 w-full h-full opacity-5 pointer-events-none" preserveAspectRatio="none">
      <polyline points="0,600 200,450 400,500 600,380 800,420 1000,320 1200,360 1440,280" fill="none" stroke="#F5A623" stroke-width="2"/>
      <polyline points="0,650 200,520 400,560 600,440 800,480 1000,380 1200,410 1440,340" fill="none" stroke="#F5A623" stroke-width="1"/>
    </svg>

    <!-- 登录卡片 -->
    <div class="relative z-10 w-full max-w-md mx-4">
      <div
        class="rounded-2xl p-10"
        style="background: rgba(255,255,255,0.09); border: 1px solid rgba(245,166,35,0.25); backdrop-filter: blur(20px); box-shadow: 0 0 60px rgba(245,166,35,0.08), inset 0 1px 0 rgba(255,255,255,0.06)"
      >
        <!-- Logo -->
        <div class="flex flex-col items-center mb-10">
          <div class="w-16 h-16 flex items-center justify-center mb-4">
            <img alt="AI交易员 Logo" class="w-full h-full object-contain" src="@/assets/logo.svg" />
          </div>
          <h1 class="text-2xl font-bold text-white tracking-wide">AI交易员</h1>
          <p class="text-sm mt-2" style="color: rgba(245,166,35,0.8)">由 AI 驱动的模拟炒股体验</p>
          <div class="mt-3 flex items-center gap-2">
            <span class="w-1.5 h-1.5 rounded-full animate-pulse" style="background: #22c55e"></span>
            <span class="text-xs" style="color: rgba(255,255,255,0.4)">系统运行正常 · A股实时行情接入中</span>
          </div>
        </div>

        <!-- 表单 -->
        <el-form @submit.prevent="handleLogin">
          <div class="space-y-5">
            <div>
              <label class="block text-xs font-medium mb-2" style="color: rgba(255,255,255,0.5)">专属账号</label>
              <div class="relative">
                <div class="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                  <i class="ri-user-line text-base" style="color: rgba(245,166,35,0.6)"></i>
                </div>
                <el-input
                  v-model="username"
                  placeholder="请输入主站下发的账号"
                  class="login-input"
                />
              </div>
            </div>

            <div>
              <label class="block text-xs font-medium mb-2" style="color: rgba(255,255,255,0.5)">密码</label>
              <div class="relative">
                <div class="absolute inset-y-0 left-4 flex items-center pointer-events-none z-10">
                  <i class="ri-lock-line text-base" style="color: rgba(245,166,35,0.6)"></i>
                </div>
                <el-input
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="请输入密码"
                  class="login-input"
                />
                <button
                  type="button"
                  class="absolute inset-y-0 right-4 flex items-center"
                  @click="showPassword = !showPassword"
                >
                  <i
                    :class="showPassword ? 'ri-eye-off-line' : 'ri-eye-line'"
                    class="text-base"
                    style="color: rgba(255,255,255,0.3)"
                  ></i>
                </button>
              </div>
            </div>

            <div class="flex justify-between">
              <a class="text-xs cursor-pointer hover:underline" style="color: rgba(245,166,35,0.7)">还没有账号？注册</a>
              <a class="text-xs cursor-pointer hover:underline" style="color: rgba(245,166,35,0.7)">忘记密码？</a>
            </div>

            <el-button
              type="primary"
              class="w-full !py-4 !rounded-xl !font-semibold !text-sm !tracking-wider !border-none"
              style="background: linear-gradient(135deg, #f5a623, #e8941a); color: #0a1628"
              @click="handleLogin"
            >
              <i class="ri-robot-line mr-2"></i>
              进入交易台
            </el-button>
          </div>
        </el-form>

        <!-- 底部 -->
        <div class="mt-8 pt-6" style="border-top: 1px solid rgba(255,255,255,0.06)">
          <p class="text-xs text-center" style="color: rgba(255,255,255,0.25)">
            账号由主站授权下发 · 仅供模拟交易使用 · 不涉及真实资金
          </p>
          <div class="flex items-center justify-center gap-4 mt-4">
            <span class="flex items-center gap-1.5 text-xs" style="color: rgba(255,255,255,0.3)">
              <i class="ri-shield-check-line" style="color: rgba(245,166,35,0.5)"></i>数据加密传输
            </span>
            <span class="flex items-center gap-1.5 text-xs" style="color: rgba(255,255,255,0.3)">
              <i class="ri-time-line" style="color: rgba(245,166,35,0.5)"></i>实时行情驱动
            </span>
            <span class="flex items-center gap-1.5 text-xs" style="color: rgba(255,255,255,0.3)">
              <i class="ri-robot-2-line" style="color: rgba(245,166,35,0.5)"></i>AI全自主决策
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.06) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 0.75rem !important;
  padding-left: 2.75rem !important;
  box-shadow: none !important;
}
.login-input :deep(.el-input__inner) {
  color: #fff !important;
}
.login-input :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.25) !important;
}
.login-input :deep(.el-input__wrapper:hover),
.login-input :deep(.el-input__wrapper.is-focus) {
  border-color: rgba(245, 166, 35, 0.5) !important;
}
</style>
