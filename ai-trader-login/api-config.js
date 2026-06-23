/**
 * API 配置 - 全局共享
 * 所有 AI 推理走 mimov2.5pro (OpenAI 协议)
 * 股票数据走腾讯/新浪公开行情接口
 */
const API_CONFIG = {
  // ===== mimov2.5pro AI 配置 =====
  AI: {
    BASE_URL: 'https://api.mimov25pro.com/v1',
    API_KEY: 'sk-cbz…fqdm',
    MODEL: 'mimov2.5pro',
    MAX_TOKENS: 2048,
    TEMPERATURE: 0.7,
  },

  // ===== 股票行情数据源 (浏览器可直接调用) =====
  STOCK_SOURCES: {
    // 腾讯财经实时行情 (JSONP)
    TENCENT_RT: 'https://qt.gtimg.cn/q=',
    // 新浪财经实时行情 (JSONP)
    SINA_RT: 'https://hq.sinajs.cn/list=',
    // 腾讯日K线
    TENCENT_KLINE: 'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get',
  },

  // ===== 模拟账户初始配置 =====
  ACCOUNT: {
    INITIAL_CAPITAL: 1000000,   // 初始资金 100万
    NAME: 'AI模拟账户',
  },
};

/**
 * 调用 mimov2.5pro Chat Completion API
 * @param {Array} messages - [{role:'system',content:'...'},{role:'user',content:'...'}]
 * @param {Object} options - {max_tokens, temperature, stream}
 * @returns {Promise<string>} AI 回复文本
 */
async function callAI(messages, options = {}) {
  const { max_tokens = API_CONFIG.AI.MAX_TOKENS, temperature = API_CONFIG.AI.TEMPERATURE, stream = false } = options;

  try {
    const resp = await fetch(`${API_CONFIG.AI.BASE_URL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_CONFIG.AI.API_KEY}`,
      },
      body: JSON.stringify({
        model: API_CONFIG.AI.MODEL,
        messages,
        max_tokens,
        temperature,
        stream,
      }),
    });

    if (!resp.ok) {
      const err = await resp.text();
      console.error('AI API Error:', resp.status, err);
      return `[AI 服务暂不可用: ${resp.status}]`;
    }

    const data = await resp.json();
    return data.choices?.[0]?.message?.content || '[无回复]';
  } catch (e) {
    console.error('AI API 调用失败:', e);
    return '[AI 服务连接失败，请稍后重试]';
  }
}

/**
 * 流式调用 AI (SSE)
 * @param {Array} messages
 * @param {Function} onChunk - 每收到一段文字时回调
 * @param {Function} onDone - 流结束时回调
 */
async function callAIStream(messages, onChunk, onDone) {
  try {
    const resp = await fetch(`${API_CONFIG.AI.BASE_URL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_CONFIG.AI.API_KEY}`,
      },
      body: JSON.stringify({
        model: API_CONFIG.AI.MODEL,
        messages,
        max_tokens: API_CONFIG.AI.MAX_TOKENS,
        temperature: API_CONFIG.AI.TEMPERATURE,
        stream: true,
      }),
    });

    if (!resp.ok) {
      onChunk(`[AI 服务暂不可用: ${resp.status}]`);
      onDone?.();
      return;
    }

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const json = line.slice(6).trim();
          if (json === '[DONE]') { onDone?.(); return; }
          try {
            const parsed = JSON.parse(json);
            const content = parsed.choices?.[0]?.delta?.content;
            if (content) onChunk(content);
          } catch (e) { /* skip */ }
        }
      }
    }
    onDone?.();
  } catch (e) {
    console.error('AI Stream 失败:', e);
    onChunk('[AI 服务连接失败]');
    onDone?.();
  }
}

/**
 * 获取腾讯实时行情
 * @param {string} codes - 股票代码，如 "sh600519,sz000001"
 * @returns {Promise<Array>} 行情数据数组
 */
async function fetchStockQuote(codes) {
  return new Promise((resolve) => {
    const cbName = '_stockCb_' + Date.now();
    window[cbName] = (data) => {
      delete window[cbName];
      resolve(parseTencentQuote(data));
    };
    const script = document.createElement('script');
    script.src = `${API_CONFIG.STOCK_SOURCES.TENCENT_RT}${codes}&callback=${cbName}`;
    script.onerror = () => { delete window[cbName]; resolve([]); };
    document.head.appendChild(script);
    setTimeout(() => { script.remove(); }, 5000);
  });
}

function parseTencentQuote(raw) {
  if (!raw || typeof raw !== 'object') return [];
  return Object.entries(raw).map(([key, val]) => {
    if (!val || typeof val !== 'string') return null;
    const parts = val.split('~');
    if (parts.length < 45) return null;
    return {
      code: parts[2],
      name: parts[1],
      price: parseFloat(parts[3]) || 0,
      prevClose: parseFloat(parts[4]) || 0,
      open: parseFloat(parts[5]) || 0,
      high: parseFloat(parts[33]) || parseFloat(parts[41]) || 0,
      low: parseFloat(parts[34]) || parseFloat(parts[42]) || 0,
      volume: parseInt(parts[6]) || 0,
      amount: parseFloat(parts[37]) || 0,
      change: parseFloat(parts[31]) || 0,
      changePercent: parseFloat(parts[32]) || 0,
      pe: parseFloat(parts[39]) || 0,
      pb: parseFloat(parts[46]) || 0,
      turnover: parseFloat(parts[38]) || 0,
      marketCap: parseFloat(parts[45]) || 0,
    };
  }).filter(Boolean);
}

/**
 * A股代码转腾讯格式
 * @param {string} code - 6位数字代码 如 "600519"
 * @returns {string} "sh600519" 或 "sz000001"
 */
function toTencentCode(code) {
  code = code.replace(/^(sh|sz|bj)/i, '');
  if (code.startsWith('6') || code.startsWith('9')) return 'sh' + code;
  if (code.startsWith('0') || code.startsWith('3') || code.startsWith('2')) return 'sz' + code;
  if (code.startsWith('4') || code.startsWith('8')) return 'bj' + code;
  return 'sh' + code;
}

/**
 * AI 系统提示词 - 角色设定
 */
const AI_SYSTEM_PROMPTS = {
  // AI 交易员主对话
  trader: `你是"AI交易员"，一个专业的A股模拟交易助手。你的职责：
1. 分析用户持仓、提供买卖建议
2. 解读市场行情和新闻
3. 解释你的交易决策逻辑
4. 风险提示和仓位管理建议

当前账户信息会作为上下文提供给你。回答要专业、简洁、有理有据。
注意：这是模拟交易，不涉及真实资金。所有分析仅供参考，不构成投资建议。`,

  // 4位分析师
  analysts: {
    fundamental: `你是"财报研究员"，专注基本面分析。分析维度：PE/PB/ROE/营收增长/利润率/现金流/行业地位。用数据说话，给出估值判断。回复简短，50字内。`,
    quant: `你是"量化交易员"，专注技术面分析。分析维度：MACD/RSI/布林带/均线/成交量/K线形态/支撑阻力位。给出明确的买卖信号。回复简短，50字内。`,
    capital: `你是"资金分析师"，专注资金面分析。分析维度：主力资金流向/龙虎榜/北向资金/融资融券/大宗交易/换手率。判断多空力量。回复简短，50字内。`,
    industry: `你是"行业研究员"，专注行业和宏观分析。分析维度：行业政策/产业链景气度/竞争格局/市场情绪/板块轮动。给出行业判断。回复简短，50字内。`,
  },

  // 客服
  customerService: `你是"在线客服"，为AI交易员平台提供客户服务。回答关于：
1. 收费标准（年付9886元/半年6886元/季度4886元/月付2886元）
2. 功能介绍
3. 使用帮助
4. 技术支持
回答要热情、专业、简洁。`,

  // 风险评估
  risk: `你是"风险评估AI"，负责分析投资组合风险。评估维度：
1. 仓位集中度
2. 最大回撤风险
3. 止损距离
4. 行业分布
5. 个股相关性
给出风险等级（可控/预警/危险）和具体建议。回复简洁，100字内。`,
};
