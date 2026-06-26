/**
 * API 客户端 — 所有后端接口调用
 * 后端: Python FastAPI (localhost:8000)
 */

const BASE = '/api'

async function request(path, options = {}) {
  const url = `${BASE}${path}`
  const resp = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }))
    throw new Error(err.detail || `HTTP ${resp.status}`)
  }
  return resp.json()
}

export const api = {
  // ── 行情 ──
  getMarketStatus() {
    return request('/market/status')
  },
  getMarketIndices() {
    return request('/market/indices')
  },
  getOverseasIndices() {
    return request('/market/overseas-indices')
  },
  getIndustryRanking(topN = 20) {
    return request(`/market/industry-ranking?top_n=${topN}`)
  },

  // ── 个股 ──
  getStockQuote(code) {
    return request(`/stock/quote/${code}`)
  },
  getStockQuotes(codes) {
    return request(`/stock/quotes?codes=${codes.join(',')}`)
  },
  getStockKline(code, period = 'daily', count = 100) {
    return request(`/stock/kline/${code}?period=${period}&count=${count}`)
  },
  getStockInfo(code) {
    return request(`/stock/info/${code}`)
  },
  getStockNews(code, pageSize = 20) {
    return request(`/stock/news/${code}?page_size=${pageSize}`)
  },

  // ── 新闻 ──
  getGlobalNews(pageSize = 50) {
    return request(`/news/global?page_size=${pageSize}`)
  },

  // ── 研报 ──
  getReports(code, maxPages = 2) {
    return request(`/reports/${code}?max_pages=${maxPages}`)
  },
  getIndustryReports(maxPages = 1) {
    return request(`/reports/industry/list?max_pages=${maxPages}`)
  },

  // ── 账户 ──
  getAccount() {
    return request('/account')
  },
  getHoldings() {
    return request('/account/holdings')
  },
  getTradeHistory(limit = 100) {
    return request(`/account/history?limit=${limit}`)
  },
  executeTrade({ code, name, action, qty, price }) {
    return request('/account/trade', {
      method: 'POST',
      body: JSON.stringify({ code, name, action, qty, price }),
    })
  },
  resetAccount() {
    return request('/account/reset', { method: 'POST' })
  },
  getAiDecisions(limit = 50) {
    return request(`/account/decisions?limit=${limit}`)
  },

  // ── AI 对话 ──
  async aiChat(messages) {
    const resp = await fetch(`${BASE}/ai/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages }),
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    return resp.json()
  },

  aiChatStream(messages) {
    // 返回可读流，调用方用 reader 读取 SSE
    return fetch(`${BASE}/ai/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages }),
    })
  },

  // ── 智能选股 ──
  getScreenerStatus() {
    return request('/screener/status')
  },
  initializeScreener() {
    return request('/screener/initialize', { method: 'POST' })
  },
  refreshScreener() {
    return request('/screener/refresh', { method: 'POST' })
  },
  getScreenerResults() {
    return request('/screener/results')
  },
}

export default api
