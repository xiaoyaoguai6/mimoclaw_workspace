<script setup>
import { ref } from 'vue'

const reports = ref([
  { date: '2025-06-24', trades: 3, pnl: '+2,150', winRate: '66.7%', detail: '止盈2笔 止损1笔' },
  { date: '2025-06-23', trades: 5, pnl: '-860', winRate: '40.0%', detail: '止盈2笔 止损3笔' },
  { date: '2025-06-22', trades: 2, pnl: '+3,400', winRate: '100%', detail: '止盈2笔' },
  { date: '2025-06-21', trades: 4, pnl: '+1,200', winRate: '75.0%', detail: '止盈3笔 止损1笔' },
  { date: '2025-06-20', trades: 1, pnl: '-500', winRate: '0%', detail: '止损1笔' },
])
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">交易报表</h1>
    <p class="page-desc">每日交易统计与绩效分析</p>

    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-label">总交易次数</div>
        <div class="stat-value">15</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">胜率</div>
        <div class="stat-value highlight">60.0%</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">累计盈亏</div>
        <div class="stat-value profit">+5,390</div>
      </div>
    </div>

    <div class="card">
      <table class="data-table">
        <thead>
          <tr>
            <th>日期</th>
            <th>交易次数</th>
            <th>当日盈亏</th>
            <th>胜率</th>
            <th>详情</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in reports" :key="r.date">
            <td>{{ r.date }}</td>
            <td>{{ r.trades }}</td>
            <td :class="r.pnl.startsWith('+') ? 'profit' : 'loss'">{{ r.pnl }}</td>
            <td>{{ r.winRate }}</td>
            <td class="detail">{{ r.detail }}</td>
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
.stats-row { display: flex; gap: 16px; margin-bottom: 24px; }
.stat-card { background: #fff; border-radius: 12px; padding: 20px 24px; flex: 1; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.stat-label { font-size: 13px; color: #6b7280; margin-bottom: 4px; }
.stat-value { font-size: 28px; font-weight: 700; color: #1a1a2e; }
.stat-value.highlight { color: #3b82f6; }
.stat-value.profit { color: #dc2626; }
.card { background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { text-align: left; padding: 12px 16px; border-bottom: 2px solid #e5e7eb; color: #6b7280; font-weight: 600; font-size: 13px; }
.data-table td { padding: 14px 16px; border-bottom: 1px solid #f3f4f6; }
.profit { color: #dc2626; font-weight: 600; }
.loss { color: #16a34a; font-weight: 600; }
.detail { color: #6b7280; font-size: 13px; }
</style>
