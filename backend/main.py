"""
AI交易员 后端 — FastAPI
行情/个股/新闻/研报/账户 全量 REST API。
启动: python main.py  或  uvicorn main:app --reload --port 8000
"""
import os
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import stock_data
import account_db
import ai_service
from fastapi.responses import StreamingResponse

app = FastAPI(title="AI交易员 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TZ = timezone(timedelta(hours=8))

# ── 市场状态 ────────────────────────────────────────────────────────────

INDEX_CODES = {
    "sh000001": "上证指数",
    "sz399001": "深证成指",
    "sz399006": "创业板指",
    "sh000300": "沪深300",
    "sh000016": "上证50",
    "sh000905": "中证500",
}

OVERSEAS_INDEX_CODES = {
    "usDJI": "道琼斯",
    "usIXIC": "纳斯达克",
    "usINX": "标普500",
    "hkHSI": "恒生指数",
    "hkHSCEI": "恒生中企",
}


def _market_status() -> dict:
    now = datetime.now(TZ)
    weekday = now.weekday()  # 0=周一
    hour, minute = now.hour, now.minute
    time_min = hour * 60 + minute

    is_weekday = weekday < 5
    is_trading_time = is_weekday and (
        (9 * 60 + 15 <= time_min <= 11 * 60 + 35) or
        (13 * 60 <= time_min <= 15 * 60)
    )

    if not is_weekday:
        label = "周末休市"
        status_label = "非交易日"
    elif is_trading_time:
        label = "交易中"
        status_label = "AI 运行中"
    elif time_min < 9 * 60 + 15:
        label = "盘前"
        status_label = "AI 待机"
    elif time_min < 13 * 60:
        label = "午间休市"
        status_label = "AI 待机"
    else:
        label = "今日已收盘"
        status_label = "AI 暂停"

    weekdays_zh = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    date_label = f"{now.year}年{now.month}月{now.day}日{weekdays_zh[weekday]}"

    return {
        "isOpen": is_trading_time,
        "label": label,
        "dateLabel": date_label,
        "statusLabel": status_label,
        "currentTime": now.strftime("%H:%M:%S"),
    }


# ── 行情 API ─────────────────────────────────────────────────────────────

@app.get("/api/market/status")
def api_market_status():
    """市场状态：开市/休市/日期。"""
    return _market_status()


@app.get("/api/market/indices")
def api_market_indices():
    """实时指数行情（上证/深证/创业板/沪深300/上证50/中证500）。"""
    quotes = stock_data.tencent_quote(list(INDEX_CODES.keys()))
    result = []
    for code, name in INDEX_CODES.items():
        q = quotes.get(code, {})
        if not q:
            continue
        change = q.get("change_pct", 0)
        result.append({
            "code": code,
            "name": name,
            "value": f"{q.get('price', 0):,.2f}",
            "change": f"{'+' if change >= 0 else ''}{change:.2f}%",
            "change_pct": round(change, 2),
            "direction": "up" if change >= 0 else "down",
            "amount_wan": q.get("amount_wan", 0),
        })
    return result


@app.get("/api/market/overseas-indices")
def api_overseas_indices():
    """海外指数行情（道琼斯/纳斯达克/标普500/恒生/恒生中企）。"""
    quotes = stock_data.tencent_quote(list(OVERSEAS_INDEX_CODES.keys()))
    result = []
    for code, name in OVERSEAS_INDEX_CODES.items():
        q = quotes.get(code, {})
        if not q:
            continue
        change = q.get("change_pct", 0)
        result.append({
            "code": code,
            "name": name,
            "value": f"{q.get('price', 0):,.2f}",
            "change": f"{'+' if change >= 0 else ''}{change:.2f}%",
            "change_pct": round(change, 2),
            "direction": "up" if change >= 0 else "down",
        })
    return result


@app.get("/api/market/industry-ranking")
def api_industry_ranking(top_n: int = Query(20, ge=1, le=100)):
    """行业板块涨跌排名。"""
    return stock_data.industry_comparison(top_n)


# ── 个股 API ─────────────────────────────────────────────────────────────

@app.get("/api/stock/quote/{code}")
def api_stock_quote(code: str):
    """实时个股行情（PE/PB/市值/换手率/涨跌停）。"""
    quotes = stock_data.tencent_quote([code])
    q = quotes.get(code)
    if not q:
        raise HTTPException(404, f"未找到股票 {code}")
    return {"code": code, **q}


@app.get("/api/stock/quotes")
def api_stock_quotes(codes: str = Query(..., description="逗号分隔的股票代码")):
    """批量实时个股行情。"""
    code_list = [c.strip() for c in codes.split(",") if c.strip()]
    return stock_data.tencent_quote_formatted(code_list)


@app.get("/api/stock/kline/{code}")
def api_stock_kline(
    code: str,
    period: str = Query("daily", description="daily/weekly/monthly/5min/15min/30min/60min"),
    count: int = Query(100, ge=1, le=500),
):
    """K线数据。"""
    cat_map = {
        "daily": 4, "weekly": 5, "monthly": 6,
        "1min": 7, "5min": 8, "15min": 9, "30min": 10, "60min": 11,
    }
    category = cat_map.get(period, 4)
    klines = stock_data.mootdx_klines(code, category=category, offset=count)
    return {"code": code, "period": period, "count": len(klines), "klines": klines}


@app.get("/api/stock/info/{code}")
def api_stock_info(code: str):
    """个股基本面信息（行业/总股本/流通股/市值/上市日期）。"""
    info = stock_data.eastmoney_stock_info(code)
    if not info:
        raise HTTPException(404, f"未找到股票 {code}")
    return info


@app.get("/api/stock/news/{code}")
def api_stock_news(code: str, page_size: int = Query(20, ge=1, le=50)):
    """个股新闻。"""
    return stock_data.eastmoney_stock_news(code, page_size)


# ── 新闻 API ─────────────────────────────────────────────────────────────

@app.get("/api/news/global")
def api_global_news(page_size: int = Query(50, ge=1, le=100)):
    """全球财经资讯（7x24）。"""
    return stock_data.eastmoney_global_news(page_size)


# ── 研报 API ─────────────────────────────────────────────────────────────

@app.get("/api/reports/{code}")
def api_reports(code: str, max_pages: int = Query(2, ge=1, le=5)):
    """个股研报列表。"""
    raw = stock_data.eastmoney_reports(code, max_pages)
    result = []
    for r in raw:
        result.append({
            "title": r.get("title", ""),
            "publishDate": (r.get("publishDate") or "")[:10],
            "orgSName": r.get("orgSName", ""),
            "emRatingName": r.get("emRatingName", ""),
            "indvInduName": r.get("indvInduName", ""),
            "predictThisYearEps": r.get("predictThisYearEps"),
            "predictNextYearEps": r.get("predictNextYearEps"),
            "infoCode": r.get("infoCode", ""),
            "pdfUrl": f"https://pdf.dfcfw.com/pdf/H3_{r.get('infoCode', '')}_1.pdf" if r.get("infoCode") else "",
        })
    return result


@app.get("/api/reports/industry/list")
def api_industry_reports(max_pages: int = Query(1, ge=1, le=5)):
    """行业研报列表。"""
    raw = stock_data.eastmoney_industry_reports("*", max_pages)
    result = []
    for r in raw:
        result.append({
            "title": r.get("title", ""),
            "publishDate": (r.get("publishDate") or "")[:10],
            "industryName": r.get("industryName", ""),
            "orgSName": r.get("orgSName", ""),
            "emRatingName": r.get("emRatingName", ""),
            "infoCode": r.get("infoCode", ""),
            "pdfUrl": f"https://pdf.dfcfw.com/pdf/H3_{r.get('infoCode', '')}_1.pdf" if r.get("infoCode") else "",
        })
    return result


# ── 账户 API ─────────────────────────────────────────────────────────────

class TradeRequest(BaseModel):
    code: str
    name: str
    action: str  # buy / sell
    qty: int
    price: float


@app.on_event("startup")
def startup():
    account_db.init_db()


@app.get("/api/account")
def api_account():
    """账户摘要（含持仓实时市值、总盈亏）。"""
    return account_db.get_account_summary()


@app.get("/api/account/holdings")
def api_holdings():
    """持仓列表（含实时价格）。"""
    return account_db.get_holdings_with_quotes()


@app.get("/api/account/history")
def api_trade_history(limit: int = Query(100, ge=1, le=500)):
    """交易历史。"""
    return account_db.get_trade_history(limit)


@app.post("/api/account/trade")
def api_trade(req: TradeRequest):
    """执行交易（买入/卖出）。"""
    result = account_db.execute_trade(req.code, req.name, req.action, req.qty, req.price)
    if not result["success"]:
        raise HTTPException(400, result["message"])
    return result


@app.post("/api/account/reset")
def api_reset():
    """重置账户。"""
    return account_db.reset_account()


@app.get("/api/account/decisions")
def api_ai_decisions(limit: int = Query(50, ge=1, le=200)):
    """AI 决策记录。"""
    return account_db.get_ai_decisions(limit)


# ── AI 对话 API ──────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str  # user / assistant
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


def _build_account_context() -> str:
    """构建当前账户实时上下文，注入 AI 对话。"""
    try:
        acct = account_db.get_account_summary()
        holdings = acct.get("holdings", [])
        holdings_str = "；".join(
            f"{h['name']}({h['code']}) {h['qty']}股 成本¥{h['cost_avg']} 现价¥{h['current_price']} 盈亏{h['pnl_pct']}%"
            for h in holdings
        ) if holdings else "空仓"
        return (
            f"总资产: ¥{acct['total_assets']:,.2f}\n"
            f"可用资金: ¥{acct['available_cash']:,.2f}\n"
            f"持仓市值: ¥{acct['total_market_value']:,.2f}\n"
            f"持仓: {holdings_str}\n"
            f"累计盈亏: ¥{acct['total_pnl']:,.2f} ({acct['total_pnl_pct']}%)\n"
            f"今日盈亏: ¥{acct['today_pnl']:,.2f}"
        )
    except Exception:
        return ""


@app.post("/api/ai/chat")
def api_ai_chat(req: ChatRequest):
    """非流式 AI 对话。"""
    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    context = _build_account_context()
    reply = ai_service.ai_chat(messages, context)
    return {"reply": reply}


@app.post("/api/ai/chat/stream")
def api_ai_chat_stream(req: ChatRequest):
    """流式 AI 对话 (SSE)。"""
    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    context = _build_account_context()
    return StreamingResponse(
        ai_service.ai_chat_stream(messages, context),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── 启动 ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
