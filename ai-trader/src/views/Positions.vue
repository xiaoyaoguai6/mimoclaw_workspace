<script setup>
import { ref } from 'vue'

const positions = ref([
  { code: '600519', name: '贵州茅台', qty: 100, cost: 1680.50, current: 1725.00, pnl: '+4,450', pnlPercent: '+2.65%', status: 'profit' },
  { code: '000858', name: '五粮液', qty: 200, cost: 152.30, current: 148.80, pnl: '-700', pnlPercent: '-2.30%', status: 'loss' },
  { code: '601318', name: '中国平安', qty: 300, cost: 48.50, current: 52.10, pnl: '+1,080', pnlPercent: '+7.42%', status: 'profit' },
  { code: '300750', name: '宁德时代', qty: 100, cost: 218.00, current: 225.60, pnl: '+760', pnlPercent: '+3.49%', status: 'profit' },
])
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">交易持仓</h1>
    <p class="page-desc">当前持有的所有股票及其盈亏情况</p>

    <div class="card">
      <table class="data-table">
        <thead>
          <tr>
            <th>代码</th>
            <th>名称</th>
            <th>持仓数量</th>
            <th>成本价</th>
            <th>现价</th>
            <th>盈亏</th>
            <th>盈亏比例</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="pos in positions" :key="pos.code">
            <td class="code">{{ pos.code }}</td>
            <td>{{ pos.name }}</td>
            <td>{{ pos.qty }}</td>
            <td>{{ pos.cost.toFixed(2) }}</td>
            <td>{{ pos.current.toFixed(2) }}</td>
            <td :class="pos.status">{{ pos.pnl }}</td>
            <td :class="pos.status">{{ pos.pnlPercent }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.page-container { padding: 24px; }
.page-title { font-size: 24px; font-weight: 700; margin-bottom: 8px; color: #1a1a2e; }
.page-desc { color: #6b7280; margin-bottom: 24px; }
.card { background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { text-align: left; padding: 12px 16px; border-bottom: 2px solid #e5e7eb; color: #6b7280; font-weight: 600; font-size: 13px; }
.data-table td { padding: 14px 16px; border-bottom: 1px solid #f3f4f6; }
.data-table .code { font-family: monospace; color: #3b82f6; }
.profit { color: #dc2626; font-weight: 600; }
.loss { color: #16a34a; font-weight: 600; }
</style>
