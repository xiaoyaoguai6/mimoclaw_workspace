<template>
  <div>
    <div class="rounded-xl p-4 mb-4" style="background: rgba(245,166,35,0.06); border: 1px solid rgba(245,166,35,0.2)">
      <div class="text-sm font-bold mb-1" style="color: #92400e">休市中（2026-06-19）</div>
      <div class="text-xs" style="color: #92400e; opacity: 0.7">下个交易日 6/22（周一）</div>
    </div>
    <el-card>
      <template #header>
        <span class="font-bold">📈 上周行情</span>
      </template>
      <el-row :gutter="24">
        <el-col :span="8">
          <div class="text-xs font-semibold mb-2" style="color: #64748b">国内</div>
          <div class="text-xs flex justify-between py-1"><span>上证指数</span><span style="color:#dc2626">4090.48 (+2.60%)</span></div>
          <div class="text-xs flex justify-between py-1"><span>深证成指</span><span style="color:#dc2626">16030.70 (+7.94%)</span></div>
          <div class="text-xs flex justify-between py-1"><span>创业板指</span><span style="color:#dc2626">4252.39 (+11.57%)</span></div>
        </el-col>
        <el-col :span="8">
          <div class="text-xs font-semibold mb-2" style="color: #64748b">美股</div>
          <div class="text-xs flex justify-between py-1"><span>道琼斯</span><span style="color:#dc2626">51564.70 (+0.14%)</span></div>
          <div class="text-xs flex justify-between py-1"><span>纳斯达克</span><span style="color:#dc2626">26517.93 (+1.91%)</span></div>
        </el-col>
        <el-col :span="8">
          <div class="text-xs font-semibold mb-2" style="color: #64748b">港股</div>
          <div class="text-xs flex justify-between py-1"><span>恒生指数</span><span style="color:#dc2626">25606.03 (+0.86%)</span></div>
          <div class="text-xs flex justify-between py-1"><span>恒生中企</span><span style="color:#dc2626">8550.87 (+0.89%)</span></div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>
