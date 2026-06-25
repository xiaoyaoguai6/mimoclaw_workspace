/**
 * 股票数据 API 服务
 * 数据源：腾讯财经(指数/行情) + 新浪(板块) + 同花顺(热榜/强势股)
 * 通过 Vite 代理解决 CORS + GBK 编码问题
 */

// ===== 腾讯财经 API =====

/**
 * 通过 Vite 代理获取腾讯行情数据（A股/港股/美股指数）
 * @param {string[]} codes - 腾讯格式代码 ["sh000001", "usDJI", "hkHSI"]
 * @returns {Promise<Array>} 行情数组
 */
export async function fetchTencentQuotes(codes) {
  try {
    const url = `/api/tencent/q=${codes.join(',')}`
    const resp = await fetch(url)
    const buffer = await resp.arrayBuffer()
    // 腾讯 API 返回 GBK 编码
    const decoder = new TextDecoder('gbk')
    const text = decoder.decode(buffer)
    return parseTencentText(text)
  } catch (e) {
    console.error('腾讯行情获取失败:', e)
    return []
  }
}

function parseTencentText(text) {
  const results = []
  for (const line of text.split(';')) {
    const trimmed = line.trim()
    if (!trimmed || !trimmed.includes('=')) continue

    const keyMatch = trimmed.match(/v_(\w+)="/)
    if (!keyMatch) continue

    const key = keyMatch[1]
    const valMatch = trimmed.match(/"([^"]*)"/)
    if (!valMatch) continue

    const parts = valMatch[1].split('~')
    if (parts.length < 35) continue

    results.push({
      key,
      name: parts[1],
      price: parseFloat(parts[3]) || 0,
      lastClose: parseFloat(parts[4]) || 0,
      open: parseFloat(parts[5]) || 0,
      changeAmt: parseFloat(parts[31]) || 0,
      changePct: parseFloat(parts[32]) || 0,
      high: parseFloat(parts[33]) || 0,
      low: parseFloat(parts[34]) || 0,
      volume: parseInt(parts[6]) || 0,
      amount: parseFloat(parts[37]) || 0,
    })
  }
  return results
}

/**
 * 获取全球指数行情（国内 + 美股 + 港股）
 */
export async function fetchGlobalIndices() {
  const codes = [
    // A股指数
    'sh000001', 'sz399001', 'sz399006', 'sh000300', 'sh000016', 'sh000905',
    // 美股指数
    'usDJI', 'usIXIC', 'usINX',
    // 港股指数
    'hkHSI', 'hkHSCEI', 'hkHSCCI',
  ]
  const raw = await fetchTencentQuotes(codes)

  // 分组
  const domestic = raw.filter(r => r.key.startsWith('sh') || r.key.startsWith('sz'))
  const us = raw.filter(r => r.key.startsWith('us'))
  const hk = raw.filter(r => r.key.startsWith('hk'))

  return { domestic, us, hk, all: raw }
}


// ===== 新浪行业板块 API =====

/**
 * 获取新浪行业板块数据
 * @returns {Promise<Array>} 板块列表
 */
export async function fetchSinaSectors() {
  try {
    const resp = await fetch('/api/sina/q/view/newSinaHy.php')
    const buffer = await resp.arrayBuffer()
    const decoder = new TextDecoder('gbk')
    const text = decoder.decode(buffer)

    // 解析 JS 变量赋值格式
    const match = text.match(/\{(.+)\}/s)
    if (!match) return []

    const raw = JSON.parse(`{${match[1]}}`)
    const sectors = []

    for (const [key, val] of Object.entries(raw)) {
      if (typeof val !== 'string') continue
      const parts = val.split(',')
      if (parts.length < 8) continue

      sectors.push({
        id: key,
        name: parts[1] || '',
        count: parseInt(parts[2]) || 0,
        avgPrice: parseFloat(parts[3]) || 0,
        changePct: parseFloat(parts[5]) || 0,
        leaderCode: parts[8] || '',
        leaderChange: parseFloat(parts[9]) || 0,
        leaderPrice: parseFloat(parts[10]) || 0,
        leaderAmtChg: parseFloat(parts[11]) || 0,
        leaderName: parts[12] || '',
      })
    }

    sectors.sort((a, b) => b.changePct - a.changePct)
    return sectors
  } catch (e) {
    console.error('新浪板块数据获取失败:', e)
    return []
  }
}


// ===== 同花顺热榜 API =====

/**
 * 获取同花顺小时热榜
 * @returns {Promise<Array>} 热榜股票列表
 */
export async function fetchTHSHotList() {
  try {
    const resp = await fetch('/api/ths-hot/open/api/hot_list/v1/hot_stock/a/hour/data.txt')
    const data = await resp.json()
    if (data.status_code !== 0) return []

    return (data.data?.stock_list || []).map(item => ({
      order: item.order,
      code: item.code,
      name: item.name,
      rate: parseFloat(item.rate) || 0,
      market: item.market,
      hotRankChg: item.hot_rank_chg || 0,
      conceptTags: item.tag?.concept_tag || [],
      popularityTag: item.tag?.popularity_tag || '',
    }))
  } catch (e) {
    console.error('同花顺热榜获取失败:', e)
    return []
  }
}

/**
 * 获取同花顺当日强势股（含题材归因）
 * @param {string} date - YYYY-MM-DD，默认今天
 * @returns {Promise<Array>} 强势股列表
 */
export async function fetchTHSHotReason(date) {
  if (!date) {
    date = new Date().toISOString().slice(0, 10)
  }
  try {
    const resp = await fetch(
      `/api/ths-reason/event/api/getharden/date/${date}/orderby/date/orderway/desc/charset/GBK/`
    )
    const data = await resp.json()
    if (data.errocode !== 0) return []

    return (data.data || []).map(item => ({
      code: item.code,
      name: item.name,
      reason: item.reason || '',
      close: parseFloat(item.close) || 0,
      changePct: parseFloat(item.zhangfu) || 0,
      turnover: parseFloat(item.huanshou) || 0,
      amount: parseFloat(item.chengjiaoe) || 0,
      netFlow: parseFloat(item.ddejingliang) || 0,
      market: item.market,
    }))
  } catch (e) {
    console.error('同花顺强势股获取失败:', e)
    return []
  }
}


// ===== A股行情（腾讯代理） =====

/**
 * 获取A股个股/指数实时行情
 * @param {string[]} codes - 6位代码 ["600519", "000001"]
 */
export async function fetchAStockQuotes(codes) {
  const prefixed = codes.map(c => {
    if (c.startsWith('6') || c.startsWith('9')) return `sh${c}`
    if (c.startsWith('8')) return `bj${c}`
    return `sz${c}`
  })
  return fetchTencentQuotes(prefixed)
}
