"""
智能选股引擎 — 六脉神剑 + 筹码D值增强 + 热度综合选股
通达信公式转 Python 实现。

数据源: mootdx(通达信TCP) 获取股票列表 + K线
       腾讯财经 获取实时换手率/量比
"""
import time
import json
import threading
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta

import screener_db
from stock_data import tdx_client, tencent_quote

TZ = timezone(timedelta(hours=8))

# 线程本地存储 — 每个线程有自己的 mootdx 客户端(TCP连接不是线程安全的)
_tls = threading.local()


def _get_thread_client():
    """获取当前线程的 mootdx 客户端(首次调用时创建,后续复用,绕过全局缓存)。"""
    if not hasattr(_tls, 'client'):
        import socket
        from mootdx.quotes import Quotes
        _TDX_SERVERS = [
            ('119.97.185.59', 7709), ('124.70.133.119', 7709), ('116.205.183.150', 7709),
            ('123.60.73.44', 7709),  ('116.205.163.254', 7709), ('121.36.225.169', 7709),
        ]
        client = None
        for ip, port in _TDX_SERVERS:
            try:
                with socket.create_connection((ip, port), timeout=3):
                    pass
            except Exception:
                continue
            try:
                client = Quotes.factory(market='std', server=(ip, port))
                break
            except Exception:
                continue
        if client is None:
            try:
                client = Quotes.factory(market='std', bestip=True)
            except Exception:
                client = Quotes.factory(market='std')
        _tls.client = client
    return _tls.client


def _now():
    return datetime.now(TZ).isoformat()


# ── 通达信公式函数库 ─────────────────────────────────────────────────────

def EMA(series, period):
    return series.ewm(span=period, adjust=False).mean()


def SMA(series, period, weight=1):
    return series.ewm(alpha=weight / period, adjust=False).mean()


def MA(series, period):
    return series.rolling(window=period, min_periods=1).mean()


def LLV(series, period):
    return series.rolling(window=period, min_periods=1).min()


def HHV(series, period):
    return series.rolling(window=period, min_periods=1).max()


def REF(series, n):
    return series.shift(n)


def MAX_(a, b):
    return np.maximum(a, b)


def ABS_(series):
    return series.abs()


def WINNER(close, high, low, vol, target_price):
    mask = close <= target_price
    total_vol = vol.sum()
    if total_vol <= 0:
        return 0.0
    return vol[mask].sum() / total_vol


# ── 六脉神剑选股策略 ─────────────────────────────────────────────────────

def run_strategy(df: pd.DataFrame) -> dict:
    if len(df) < 30:
        return {"xg": False}

    C = df["close"]
    H = df["high"]
    L = df["low"]
    V = df["vol"]

    # 1. MACD变种
    M1 = EMA(C, 8) - EMA(C, 13)
    M2 = EMA(M1, 5)
    T3 = (M1 > M2).astype(int)

    # 2. KDJ变种
    K1 = (C - LLV(L, 8)) / (HHV(H, 8) - LLV(L, 8)) * 100
    K2 = SMA(K1, 3, 1)
    K3 = SMA(K2, 3, 1)
    T4 = (K2 > K3).astype(int)

    # 3. RSI
    R1 = REF(C, 1)
    diff = C - R1
    R2 = SMA(MAX_(diff, 0), 5, 1) / SMA(ABS_(diff), 5, 1) * 100
    R3 = SMA(MAX_(diff, 0), 13, 1) / SMA(ABS_(diff), 13, 1) * 100
    T5 = (R2 > R3).astype(int)

    # 4. LWR威廉
    L1 = (-(HHV(H, 13) - C)) / (HHV(H, 13) - LLV(L, 13)) * 100
    L2 = SMA(L1, 3, 1)
    L3 = SMA(L2, 3, 1)
    T6 = (L2 > L3).astype(int)

    # 5. BBI多空均线
    B1 = (MA(C, 3) + MA(C, 6) + MA(C, 12) + MA(C, 24)) / 4
    T7 = (C > B1).astype(int)

    # 6. RC动量指标
    C1 = C - REF(C, 1)
    C2 = 100 * EMA(EMA(C1, 5), 3) / EMA(EMA(ABS_(C1), 5), 3)
    C3 = 100 * EMA(EMA(C1, 13), 8) / EMA(EMA(ABS_(C1), 13), 8)
    T8 = (C2 > C3).astype(int)

    # 六脉共振
    LMGZ = ((T3 & T4 & T5 & T6 & T7 & T8) == 1)

    # 筹码D值
    win_vals = []
    for i in range(len(C)):
        target = C.iloc[i] * 0.9
        start = max(0, i - 20)
        w = WINNER(C.iloc[start:i+1], H.iloc[start:i+1], L.iloc[start:i+1],
                   V.iloc[start:i+1], target)
        win_vals.append(w * 100 * C.iloc[i])
    win_series = pd.Series(win_vals, index=C.index)
    WIN_VAL = MA(win_series, 5)
    D_VAL = win_series.copy()
    D_VAL[WIN_VAL <= 10] = 0
    D_VAL = D_VAL / 2

    # 条件组合
    cond1 = LMGZ & REF(LMGZ, 1).fillna(False)
    cond2 = (D_VAL > 800) & (D_VAL > REF(D_VAL, 1).fillna(0))
    vol_ma5 = MA(V, 5)
    vol_ratio = V / vol_ma5.replace(0, np.nan)
    turnover = df["amount"] / (df["close"] * df["vol"].replace(0, np.nan))
    cond3 = (vol_ratio > 1) & (turnover > 0.03)
    cond3 = cond3.fillna(False)

    all_cond = cond1 & cond2 & cond3
    yesterday_not = ~REF(all_cond, 1).fillna(True)
    xg = yesterday_not & all_cond

    last_idx = len(df) - 1
    return {
        "xg": bool(xg.iloc[last_idx]),
        "lmgz": bool(LMGZ.iloc[last_idx]),
        "cond1": bool(cond1.iloc[last_idx]),
        "cond2": bool(cond2.iloc[last_idx]),
        "cond3": bool(cond3.iloc[last_idx]),
        "d_val": round(float(D_VAL.iloc[last_idx]), 2),
        "signals": {
            "macd": bool(T3.iloc[last_idx]),
            "kdj": bool(T4.iloc[last_idx]),
            "rsi": bool(T5.iloc[last_idx]),
            "lwr": bool(T6.iloc[last_idx]),
            "bbi": bool(T7.iloc[last_idx]),
            "rc": bool(T8.iloc[last_idx]),
        },
    }


# ── 股票列表获取 ──────────────────────────────────────────────────────────

def fetch_all_stocks() -> list[dict]:
    client = _get_thread_client()
    result = []
    for market in [0, 1]:
        try:
            stocks = client.stocks(market=market)
            if stocks is None or len(stocks) == 0:
                continue
            for _, row in stocks.iterrows():
                code = str(row.get("code", "")).zfill(6)
                name = str(row.get("name", "")).strip()
                if not code or not name:
                    continue
                if code.startswith(("60", "00", "30")):
                    if any(k in name for k in ["指数", "ETF", "基金", "债", "回购"]):
                        continue
                    result.append({"code": code, "name": name, "market": market})
        except Exception:
            continue
    return result


def fetch_klines(code: str, count: int = 60) -> list[dict]:
    client = _get_thread_client()
    market = 1 if code.startswith("6") else 0
    try:
        df = client.bars(symbol=code, category=4, offset=count)
        if df is None or len(df) == 0:
            return []
        klines = []
        for _, row in df.iterrows():
            dt = str(row.get("datetime", ""))
            date_str = dt[:10] if len(dt) >= 10 else dt
            klines.append({
                "date": date_str,
                "open": float(row.get("open", 0)),
                "high": float(row.get("high", 0)),
                "low": float(row.get("low", 0)),
                "close": float(row.get("close", 0)),
                "vol": float(row.get("vol", 0)),
                "amount": float(row.get("amount", 0)),
            })
        return klines
    except Exception:
        return []


# ── 后台初始化(首次加载60天数据) ─────────────────────────────────────────

def _do_initialize():
    """实际初始化逻辑(在后台线程跑)。"""
    try:
        screener_db.init_db()
        if screener_db.is_initialized():
            return

        screener_db.set_state("init_running", "1")
        screener_db.set_state("fetched_stocks", "0")
        screener_db.set_state("init_error", "")
        screener_db.set_state("init_step", "fetching_stock_list")

        stocks = fetch_all_stocks()
        screener_db.set_state("total_stocks", str(len(stocks)))
        screener_db.set_state("init_step", f"got_{len(stocks)}_stocks")

        screener_db.clear_all_stocks()
        screener_db.bulk_upsert_stocks(stocks)

        screener_db.set_state("init_step", "fetching_klines")
        fetched = 0

        def fetch_one(stock):
            klines = fetch_klines(stock["code"], 60)
            if klines:
                screener_db.upsert_klines(stock["code"], klines)
            return stock["code"]

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fetch_one, s): s for s in stocks}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception:
                    pass
                fetched += 1
                # 每10只更新一次进度,减少SQLite写锁竞争
                if fetched % 10 == 0 or fetched == len(stocks):
                    screener_db.set_state("fetched_stocks", str(fetched))

        screener_db.set_state("initialized", "1")
        screener_db.set_state("last_refresh", _now())
    except Exception as e:
        screener_db.set_state("init_error", str(e))
    finally:
        screener_db.set_state("init_running", "0")


def initialize_stock_pool():
    """启动后台初始化线程,立即返回。"""
    if screener_db.get_state("init_running") == "1":
        return {"status": "already_running"}
    if screener_db.is_initialized():
        return {"status": "already_initialized"}

    screener_db.init_db()
    thread = threading.Thread(target=_do_initialize, daemon=True)
    thread.start()
    return {"status": "started"}


# ── 后台选股(刷新当天数据 + 运行策略) ────────────────────────────────────

def _do_refresh_and_screen():
    """实际选股逻辑(在后台线程跑)。"""
    try:
        screener_db.init_db()
        if not screener_db.is_initialized():
            screener_db.set_state("screen_running", "0")
            return

        stocks = screener_db.get_all_stocks()
        screener_db.set_state("screen_running", "1")
        screener_db.set_state("screen_total", str(len(stocks)))
        screener_db.set_state("screen_done", "0")
        screener_db.set_state("screen_error", "")
        screener_db.set_state("screen_results", "")

        results = []
        done = 0

        def process_one(stock):
            code = stock["code"]
            name = stock["name"]
            try:
                new_klines = fetch_klines(code, 2)
                if new_klines:
                    screener_db.upsert_klines(code, new_klines)
                db_klines = screener_db.get_klines(code, 60)
                if len(db_klines) < 30:
                    return None
                df = pd.DataFrame(db_klines)
                result = run_strategy(df)
                if result.get("xg"):
                    return {
                        "code": code,
                        "name": name,
                        "price": float(df.iloc[-1]["close"]),
                        "d_val": result.get("d_val", 0),
                        "signals": result.get("signals", {}),
                        "lmgz": result.get("lmgz", False),
                    }
            except Exception:
                pass
            return None

        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = {executor.submit(process_one, s): s for s in stocks}
            for future in as_completed(futures):
                try:
                    r = future.result()
                    if r:
                        results.append(r)
                except Exception:
                    pass
                done += 1
                if done % 50 == 0 or done == len(stocks):
                    screener_db.set_state("screen_done", str(done))

        results.sort(key=lambda x: x.get("d_val", 0), reverse=True)
        screener_db.set_state("screen_results", json.dumps(results, ensure_ascii=False))
        screener_db.set_state("last_refresh", _now())
    except Exception as e:
        screener_db.set_state("screen_error", str(e))
    finally:
        screener_db.set_state("screen_running", "0")


def refresh_and_screen():
    """启动后台选股线程,立即返回。"""
    if screener_db.get_state("screen_running") == "1":
        return {"status": "already_running"}
    if not screener_db.is_initialized():
        return {"status": "not_initialized"}

    thread = threading.Thread(target=_do_refresh_and_screen, daemon=True)
    thread.start()
    return {"status": "started"}


def get_screen_progress() -> dict:
    """获取选股进度 + 结果。"""
    results_json = screener_db.get_state("screen_results", "")
    results = []
    if results_json:
        try:
            results = json.loads(results_json)
        except json.JSONDecodeError:
            pass

    return {
        "init": screener_db.get_init_progress(),
        "init_step": screener_db.get_state("init_step", ""),
        "init_error": screener_db.get_state("init_error", ""),
        "screen_running": screener_db.get_state("screen_running") == "1",
        "screen_total": int(screener_db.get_state("screen_total", "0")),
        "screen_done": int(screener_db.get_state("screen_done", "0")),
        "screen_error": screener_db.get_state("screen_error", ""),
        "last_refresh": screener_db.get_state("last_refresh"),
        "stock_count": screener_db.get_stock_count(),
        "results": results,
    }
