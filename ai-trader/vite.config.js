import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      // 腾讯财经行情代理（解决 GBK 编码 + CORS）
      '/api/tencent': {
        target: 'https://qt.gtimg.cn',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/tencent/, ''),
      },
      // 新浪板块代理
      '/api/sina': {
        target: 'https://vip.stock.finance.sina.com.cn',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/sina/, ''),
      },
      // 同花顺热榜代理
      '/api/ths-hot': {
        target: 'https://eq.10jqka.com.cn',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/ths-hot/, ''),
      },
      // 同花顺强势股代理
      '/api/ths-reason': {
        target: 'http://zx.10jqka.com.cn',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/ths-reason/, ''),
      },
      // 原有 API 代理
      '/api': {
        target: 'http://8.154.27.225:8088',
        changeOrigin: true,
      },
    },
  },
})
