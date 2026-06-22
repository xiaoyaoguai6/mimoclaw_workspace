import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', layout: 'blank' },
  },
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '总览仪表盘' },
  },
  {
    path: '/news',
    name: 'News',
    component: () => import('@/views/News.vue'),
    meta: { title: '热点新闻' },
  },
  {
    path: '/stocks',
    name: 'Stocks',
    component: () => import('@/views/Stocks.vue'),
    meta: { title: 'AI交易模拟盘' },
  },
  {
    path: '/simtrade',
    name: 'SimTrade',
    component: () => import('@/views/SimTrade.vue'),
    meta: { title: '模拟交易' },
  },
  {
    path: '/positions',
    name: 'Positions',
    component: () => import('@/views/Positions.vue'),
    meta: { title: '交易持仓' },
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/Reports.vue'),
    meta: { title: '交易报表' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { title: '账户设置' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || 'AI交易员'} · 阿尔法工坊`
  next()
})

export default router
