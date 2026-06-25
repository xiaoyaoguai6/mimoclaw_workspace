<script setup>
import { ref } from 'vue'

const username = ref('AI交易员')
const email = ref('trader@example.com')
const riskLevel = ref('medium')
const maxPosition = ref(40)
const stopLoss = ref(5)
const takeProfit = ref(10)

const saved = ref(false)

function save() {
  saved.value = true
  setTimeout(() => { saved.value = false }, 2000)
}
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">账户设置</h1>
    <p class="page-desc">管理你的账户信息和交易参数</p>

    <div class="card">
      <h2 class="section-title">基本信息</h2>
      <div class="form-group">
        <label>用户名</label>
        <input v-model="username" type="text" />
      </div>
      <div class="form-group">
        <label>邮箱</label>
        <input v-model="email" type="email" />
      </div>
    </div>

    <div class="card">
      <h2 class="section-title">风控参数</h2>
      <div class="form-group">
        <label>风险偏好</label>
        <select v-model="riskLevel">
          <option value="low">保守</option>
          <option value="medium">稳健</option>
          <option value="high">激进</option>
        </select>
      </div>
      <div class="form-group">
        <label>单只持仓上限 (%)</label>
        <input v-model.number="maxPosition" type="number" min="1" max="100" />
      </div>
      <div class="form-group">
        <label>止损比例 (%)</label>
        <input v-model.number="stopLoss" type="number" min="1" max="50" />
      </div>
      <div class="form-group">
        <label>止盈比例 (%)</label>
        <input v-model.number="takeProfit" type="number" min="1" max="100" />
      </div>
    </div>

    <button class="save-btn" @click="save">
      {{ saved ? '✅ 已保存' : '保存设置' }}
    </button>
  </div>
</template>

<style scoped>
.page-container { padding: 24px; max-width: 640px; }
.page-title { font-size: 24px; font-weight: 700; margin-bottom: 8px; color: #1a1a2e; }
.page-desc { color: #6b7280; margin-bottom: 24px; }
.card { background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 20px; }
.section-title { font-size: 16px; font-weight: 600; margin-bottom: 20px; color: #1a1a2e; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; font-weight: 500; color: #374151; margin-bottom: 6px; }
.form-group input, .form-group select { width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; outline: none; transition: border-color 0.2s; }
.form-group input:focus, .form-group select:focus { border-color: #3b82f6; }
.save-btn { background: #3b82f6; color: #fff; border: none; padding: 12px 32px; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
.save-btn:hover { background: #2563eb; }
</style>
