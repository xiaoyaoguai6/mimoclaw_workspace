/**
 * 数据存储层 - localStorage 持久化
 * 管理：账户、持仓、交易历史、AI决策、设置
 */
const DataStore = {
  _key: 'ai_trader_',

  _get(key) {
    try { return JSON.parse(localStorage.getItem(this._key + key)); } catch { return null; }
  },
  _set(key, val) {
    localStorage.setItem(this._key + key, JSON.stringify(val));
  },

  // ===== 账户 =====
  getAccount() {
    return this._get('account') || {
      capital: API_CONFIG.ACCOUNT.INITIAL_CAPITAL,
      available: API_CONFIG.ACCOUNT.INITIAL_CAPITAL,
      totalAsset: API_CONFIG.ACCOUNT.INITIAL_CAPITAL,
      positions: [],
      tradeHistory: [],
      aiDecisions: [],
      createdAt: new Date().toISOString(),
      settings: {
        aiEnabled: true,
        sectors: ['科技', '消费', '医药', '新能源', '金融'],
        maxPositionPct: 30,
        stopLossPct: 5,
        takeProfitPct: 15,
        tradeFrequency: 'medium',
      },
    };
  },
  saveAccount(acc) { this._set('account', acc); },

  // ===== 持仓 =====
  getPositions() { return this.getAccount().positions || []; },
  addPosition(pos) {
    const acc = this.getAccount();
    acc.positions.push(pos);
    acc.available -= pos.cost;
    this._recalc(acc);
    this.saveAccount(acc);
    return acc;
  },
  removePosition(code, qty) {
    const acc = this.getAccount();
    const idx = acc.positions.findIndex(p => p.code === code);
    if (idx === -1) return null;
    const pos = acc.positions[idx];
    const sellQty = Math.min(qty, pos.qty);
    const sellAmount = sellQty * pos.currentPrice;
    const pnl = (pos.currentPrice - pos.avgCost) * sellQty;
    const fee = sellAmount * 0.001; // 0.1% 手续费

    // 记录交易
    acc.tradeHistory.unshift({
      date: new Date().toISOString().slice(0, 10),
      time: new Date().toLocaleTimeString('zh-CN', { hour12: false }),
      code: pos.code,
      name: pos.name,
      direction: 'sell',
      qty: sellQty,
      price: pos.currentPrice,
      amount: sellAmount,
      pnl: pnl - fee,
      fee,
      status: 'done',
    });

    pos.qty -= sellQty;
    acc.available += sellAmount - fee;
    if (pos.qty <= 0) acc.positions.splice(idx, 1);

    this._recalc(acc);
    this.saveAccount(acc);
    return { pnl, fee, sellAmount };
  },

  // ===== 买入 =====
  buyStock(code, name, price, qty) {
    const acc = this.getAccount();
    const amount = price * qty;
    const fee = amount * 0.001;
    const totalCost = amount + fee;

    if (totalCost > acc.available) return { error: '可用资金不足' };
    if (qty < 100 || qty % 100 !== 0) return { error: '数量必须为100的整数倍' };

    // 检查是否已有持仓
    let pos = acc.positions.find(p => p.code === code);
    if (pos) {
      const newQty = pos.qty + qty;
      pos.avgCost = (pos.avgCost * pos.qty + price * qty) / newQty;
      pos.qty = newQty;
      pos.currentPrice = price;
    } else {
      acc.positions.push({
        code, name, qty, avgCost: price, currentPrice: price,
        buyDate: new Date().toISOString().slice(0, 10),
      });
    }

    acc.tradeHistory.unshift({
      date: new Date().toISOString().slice(0, 10),
      time: new Date().toLocaleTimeString('zh-CN', { hour12: false }),
      code, name,
      direction: 'buy',
      qty, price,
      amount,
      fee,
      pnl: null,
      status: 'done',
    });

    acc.available -= totalCost;
    this._recalc(acc);
    this.saveAccount(acc);
    return { success: true, amount, fee };
  },

  // ===== 更新持仓市价 =====
  updatePositionPrices(quotes) {
    const acc = this.getAccount();
    quotes.forEach(q => {
      const pos = acc.positions.find(p => p.code === q.code);
      if (pos) pos.currentPrice = q.price;
    });
    this._recalc(acc);
    this.saveAccount(acc);
  },

  // ===== 重算总资产 =====
  _recalc(acc) {
    const posValue = acc.positions.reduce((sum, p) => sum + p.qty * p.currentPrice, 0);
    acc.totalAsset = acc.available + posValue;
    acc.totalPnl = acc.totalAsset - API_CONFIG.ACCOUNT.INITIAL_CAPITAL;
    acc.totalPnlPct = (acc.totalPnl / API_CONFIG.ACCOUNT.INITIAL_CAPITAL * 100);
    acc.posValue = posValue;
    acc.posCount = acc.positions.length;
  },

  // ===== AI 决策记录 =====
  addDecision(decision) {
    const acc = this.getAccount();
    acc.aiDecisions.unshift({
      ...decision,
      time: new Date().toISOString(),
      id: 'd_' + Date.now(),
    });
    if (acc.aiDecisions.length > 100) acc.aiDecisions = acc.aiDecisions.slice(0, 100);
    this.saveAccount(acc);
  },
  getDecisions() { return this.getAccount().aiDecisions || []; },

  // ===== 设置 =====
  getSettings() { return this.getAccount().settings || {}; },
  updateSettings(patch) {
    const acc = this.getAccount();
    acc.settings = { ...acc.settings, ...patch };
    this.saveAccount(acc);
    return acc.settings;
  },

  // ===== 重置 =====
  reset() {
    localStorage.removeItem(this._key + 'account');
  },

  // ===== 导出报表数据 =====
  getReportData() {
    const acc = this.getAccount();
    const trades = acc.tradeHistory || [];
    const sellTrades = trades.filter(t => t.direction === 'sell');
    const totalPnl = sellTrades.reduce((s, t) => s + (t.pnl || 0), 0);
    const totalFee = trades.reduce((s, t) => s + (t.fee || 0), 0);
    const winTrades = sellTrades.filter(t => t.pnl > 0);
    const winRate = sellTrades.length > 0 ? (winTrades.length / sellTrades.length * 100) : 0;

    return {
      totalTrades: trades.length,
      sellTrades: sellTrades.length,
      winRate: winRate.toFixed(1),
      totalPnl,
      totalFee,
      maxDrawdown: 0, // TODO: 需要按日计算
      positions: acc.positions,
      available: acc.available,
      totalAsset: acc.totalAsset,
      totalPnlPct: acc.totalPnlPct,
    };
  },
};

// ===== 自选股列表 =====
const WATCHLIST = [
  { code: '002384', name: '东山精密' },
  { code: '688041', name: '海光信息' },
  { code: '600522', name: '中天科技' },
  { code: '600487', name: '亨通光电' },
  { code: '601138', name: '工业富联' },
  { code: '300750', name: '宁德时代' },
  { code: '002594', name: '比亚迪' },
  { code: '600519', name: '贵州茅台' },
  { code: '000001', name: '平安银行' },
  { code: '601318', name: '中国平安' },
  { code: '600036', name: '招商银行' },
  { code: '000858', name: '五粮液' },
  { code: '300059', name: '东方财富' },
  { code: '002415', name: '海康威视' },
  { code: '603259', name: '药明康德' },
  { code: '688981', name: '中芯国际' },
  { code: '601012', name: '隆基绿能' },
  { code: '300274', name: '阳光电源' },
  { code: '002049', name: '紫光国微' },
  { code: '688599', name: '天合光能' },
];
