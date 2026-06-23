"""
A股数据获取层 — 基于 a-stock-data (simonlin1212/a-stock-data V3.2.4) 提取。
数据源：mootdx(通达信TCP) + 腾讯财经(HTTP) + 东财(HTTP,内置限流) + 百度股市通(HTTP)
所有数据源免费无Key（iwencai除外，本项目未使用）。
"""
import socket
import time
import random
import re
import json
import urllib.request
import uuid
from pathlib import Path

import requests

# ── 全局常量 ────────────────────────────────────────────────────────────
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
DATACENTER_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
REPORT_API = "https://reportapi.eastmoney.com/report/list"
PDF_TPL = "https://pdf.dfcfw.com/pdf/H3_{info_code}_1.pdf"

# ── 东财防封：全局节流 + 会话复用 ──────────────────────────────────────
EM_SESSION = requests.Session()
EM_SESSION.headers.update({"User-Agent": UA})
EM_MIN_INTERVAL = 1.0
_em_last_call = [0.0]


def em_get(url, params=None, headers=None, timeout=15, **kwargs):
    """东财统一请求入口：自动节流 + 复用 session + 默认 UA。"""
    wait = EM_MIN_INTERVAL - (time.time() - _em_last_call[0])
    if wait > 0:
        time.sleep(wait + random.uniform(0.1, 0.5))
    try:
        return EM_SESSION.get(url, params=params, headers=headers, timeout=timeout, **kwargs)
    finally:
        _em_last_call[0] = time.time()


# ── mootdx 客户端（规避 0.11.x BESTIP 空串 bug）─────────────────────────
_TDX_SERVERS = [
    ('119.97.185.59', 7709), ('124.70.133.119', 7709), ('116.205.183.150', 7709),
    ('123.60.73.44', 7709),  ('116.205.163.254', 7709), ('121.36.225.169', 7709),
    ('123.60.70.228', 7709), ('124.71.9.153', 7709),    ('110.41.147.114', 7709),
    ('124.71.187.122', 7709),
]

_tdx_client_cache = None


def _probe(ip, port, timeout=2.0):
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False


def tdx_client(market='std'):
    """创建 mootdx 客户端，规避 0.11.x BESTIP.HQ 空串 bug。"""
    global _tdx_client_cache
    if _tdx_client_cache is not None:
        return _tdx_client_cache
    from mootdx.quotes import Quotes
    for ip, port in _TDX_SERVERS:
        if _probe(ip, port):
            try:
                _tdx_client_cache = Quotes.factory(market=market, server=(ip, port))
                return _tdx_client_cache
            except Exception:
                continue
    try:
        _tdx_client_cache = Quotes.factory(market=market, bestip=True)
        return _tdx_client_cache
    except Exception:
        pass
    try:
        _tdx_client_cache = Quotes.factory(market=market)
        return _tdx_client_cache
    except Exception as e:
        raise RuntimeError(
            "所有 mootdx 服务器均不可达。海外网络通常全部超时（TCP 7709），"
            "请走国内代理或更新 _TDX_SERVERS 列表。原始错误：%s" % e
        )


def get_prefix(code: str) -> str:
    """6位代码 → 市场前缀"""
    if code.startswith(("6", "9")):
        return "sh"
    elif code.startswith("8"):
        return "bj"
    else:
        return "sz"


# ── 1. 行情层 ────────────────────────────────────────────────────────────

def _safe_float(v):
    """安全转 float，非数字返回 0。"""
    try:
        return float(v) if v else 0
    except (ValueError, TypeError):
        return 0


def tencent_quote(codes: list[str]) -> dict[str, dict]:
    """
    批量拉取腾讯财经实时行情。
    codes 支持以下格式:
      - 纯代码: ["688017", "300476", "002463"] → 自动加 sh/sz/bj 前缀
      - 带前缀: ["sh000001", "sz399006"]        → 指数/ETF 需显式指定前缀
    返回 dict 的 key 与传入格式一致（纯代码→纯代码，带前缀→带前缀）。
    """
    prefixed = []
    key_map = {}  # prefixed_code → original_code
    for c in codes:
        c = c.strip()
        if not c:
            continue
        if c[:2] in ("sh", "sz", "bj") and "_" not in c:
            pc = c
        elif len(c) == 6 and c.isdigit():
            if c.startswith(("6", "9")):
                pc = f"sh{c}"
            elif c.startswith("8"):
                pc = f"bj{c}"
            else:
                pc = f"sz{c}"
        else:
            pc = c  # international indices (usDJI, hkHSI, etc.) or other formats
        prefixed.append(pc)
        key_map[pc] = c

    url = "https://qt.gtimg.cn/q=" + ",".join(prefixed)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = resp.read().decode("gbk")
    except Exception:
        return {}

    result = {}
    for line in data.strip().split(";"):
        if not line.strip() or "=" not in line or '"' not in line:
            continue
        raw_key = line.split("=")[0].strip()
        key = raw_key[2:] if raw_key.startswith("v_") else raw_key
        vals = line.split('"')[1].split("~")
        if len(vals) < 53:
            continue
        orig = key_map.get(key, key[2:] if key[:2] in ("sh", "sz", "bj") else key)
        result[orig] = {
            "name":         vals[1],
            "price":        _safe_float(vals[3]),
            "last_close":   _safe_float(vals[4]),
            "open":         _safe_float(vals[5]),
            "change_amt":   _safe_float(vals[31]),
            "change_pct":   _safe_float(vals[32]),
            "high":         _safe_float(vals[33]),
            "low":          _safe_float(vals[34]),
            "amount_wan":   _safe_float(vals[37]),
            "turnover_pct": _safe_float(vals[38]),
            "pe_ttm":       _safe_float(vals[39]),
            "amplitude_pct":_safe_float(vals[43]),
            "mcap_yi":      _safe_float(vals[44]),
            "float_mcap_yi":_safe_float(vals[45]),
            "pb":           _safe_float(vals[46]),
            "limit_up":     _safe_float(vals[47]),
            "limit_down":   _safe_float(vals[48]),
            "vol_ratio":    _safe_float(vals[49]),
            "pe_static":    _safe_float(vals[52]) if len(vals) > 52 else 0,
        }
    return result


def tencent_quote_formatted(codes: list[str]) -> list[dict]:
    """tencent_quote 的列表版本，每条带上 code 字段，方便前端直接用。"""
    raw = tencent_quote(codes)
    result = []
    for code, q in raw.items():
        item = {"code": code, **q}
        result.append(item)
    return result


def mootdx_klines(symbol: str, category: int = 4, offset: int = 100) -> list[dict]:
    """
    mootdx K线数据。
    category: 4=日线, 5=周线, 6=月线, 7=1分钟, 8=5分钟, 9=15分钟, 10=30分钟, 11=60分钟
    返回: [{datetime, open, close, high, low, vol, amount}]
    """
    try:
        client = tdx_client()
        market = 1 if symbol.startswith("6") else 0
        df = client.bars(symbol=symbol, category=category, offset=offset)
        if df is None or len(df) == 0:
            return []
        rows = []
        for _, row in df.iterrows():
            rows.append({
                "datetime": str(row.get("datetime", "")),
                "open":     float(row.get("open", 0)),
                "close":    float(row.get("close", 0)),
                "high":     float(row.get("high", 0)),
                "low":      float(row.get("low", 0)),
                "vol":      float(row.get("vol", 0)),
                "amount":   float(row.get("amount", 0)),
            })
        return rows
    except Exception:
        return []


def baidu_kline_with_ma(code: str, start_time: str = "") -> dict:
    """百度股市通K线 — 返回时自带 ma5/ma10/ma20 均价"""
    url = "https://finance.pae.baidu.com/selfselect/getstockquotation"
    params = {
        "all": "1", "isIndex": "false", "isBk": "false", "isBlock": "false",
        "isFutures": "false", "isStock": "true", "newFormat": "1",
        "group": "quotation_kline_ab", "finClientType": "pc",
        "code": code, "start_time": start_time, "ktype": "1",
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/vnd.finance-web.v1+json",
        "Origin": "https://gushitong.baidu.com",
        "Referer": "https://gushitong.baidu.com/",
    }
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        d = r.json()
        result = d.get("Result", {})
        md = result.get("newMarketData", {})
        keys = md.get("keys", [])
        rows = md.get("marketData", "").split(";")
        return {"keys": keys, "rows": rows}
    except Exception:
        return {"keys": [], "rows": []}


# ── 2. 研报层 ────────────────────────────────────────────────────────────

def eastmoney_reports(code: str, max_pages: int = 3) -> list[dict]:
    """拉取指定股票的研报列表"""
    all_records = []
    for page in range(1, max_pages + 1):
        params = {
            "industryCode": "*", "pageSize": "50", "industry": "*",
            "rating": "*", "ratingChange": "*",
            "beginTime": "2024-01-01", "endTime": "2030-01-01",
            "pageNo": str(page), "fields": "", "qType": "0",
            "orgCode": "", "code": code, "rcode": "",
            "p": str(page), "pageNum": str(page), "pageNumber": str(page),
        }
        try:
            r = em_get(REPORT_API, params=params,
                       headers={"Referer": "https://data.eastmoney.com/"}, timeout=30)
            d = r.json()
            rows = d.get("data") or []
            if not rows:
                break
            all_records.extend(rows)
            if page >= (d.get("TotalPage", 1) or 1):
                break
        except Exception:
            break
    return all_records


def eastmoney_industry_reports(industry_code: str = "*", max_pages: int = 2,
                               begin: str = "2024-01-01") -> list[dict]:
    """拉取行业研报列表（qType=1）。"""
    all_records = []
    for page in range(1, max_pages + 1):
        params = {
            "industryCode": industry_code, "pageSize": "50", "industry": "*",
            "rating": "*", "ratingChange": "*",
            "beginTime": begin, "endTime": "2030-01-01",
            "pageNo": str(page), "fields": "", "qType": "1",
        }
        try:
            r = em_get(REPORT_API, params=params,
                       headers={"Referer": "https://data.eastmoney.com/"}, timeout=30)
            d = r.json()
            rows = d.get("data") or []
            if not rows:
                break
            all_records.extend(rows)
            if page >= (d.get("TotalPage", 1) or 1):
                break
        except Exception:
            break
    return all_records


# ── 3. 信号层 ────────────────────────────────────────────────────────────

def industry_comparison(top_n: int = 20) -> dict:
    """全行业涨跌幅排名（东财行业板块，~100 个行业）。"""
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1", "pz": "100", "po": "1", "np": "1",
        "fltt": "2", "invt": "2",
        "fs": "m:90+t:2",
        "fields": "f2,f3,f4,f12,f13,f14,f104,f105,f128,f136,f140,f141,f207",
    }
    headers = {"User-Agent": UA}
    try:
        r = em_get(url, params=params, headers=headers, timeout=15)
        d = r.json()
        items = d.get("data", {}).get("diff", [])
        if not items:
            return {"top": [], "bottom": [], "total": 0}
        rows = []
        for i, item in enumerate(items):
            rows.append({
                "rank": i + 1,
                "name": item.get("f14", ""),
                "change_pct": item.get("f3", 0),
                "code": item.get("f12", ""),
                "up_count": item.get("f104", 0),
                "down_count": item.get("f105", 0),
                "leader": item.get("f140", ""),
                "leader_change": item.get("f136", 0),
            })
        return {
            "top": rows[:top_n],
            "bottom": list(reversed(rows[-top_n:])),
            "total": len(rows),
        }
    except Exception:
        return {"top": [], "bottom": [], "total": 0}


# ── 5. 新闻层 ────────────────────────────────────────────────────────────

def eastmoney_stock_news(code: str, page_size: int = 20) -> list[dict]:
    """东财个股新闻（JSONP 接口）。返回: [{title, content, time, source, url}]"""
    cb = "jQuery_news"
    url = "https://search-api-web.eastmoney.com/search/jsonp"
    inner_params = json.dumps({
        "uid": "",
        "keyword": code,
        "type": ["cmsArticleWebOld"],
        "client": "web",
        "clientType": "web",
        "clientVersion": "curr",
        "param": {"cmsArticleWebOld": {"searchScope": "default", "sort": "default",
                  "pageIndex": 1, "pageSize": page_size, "preTag": "", "postTag": ""}},
    }, separators=(',', ':'))
    params = {"cb": cb, "param": inner_params}
    headers = {"User-Agent": UA, "Referer": "https://so.eastmoney.com/"}
    try:
        r = em_get(url, params=params, headers=headers, timeout=15)
        text = r.text
        json_str = text[text.index("(") + 1: text.rindex(")")]
        d = json.loads(json_str)
        rows = []
        articles = d.get("result", {}).get("cmsArticleWebOld", []) or []
        for a in articles:
            rows.append({
                "title": re.sub(r'<[^>]+>', '', a.get("title", "")),
                "content": re.sub(r'<[^>]+>', '', a.get("content", ""))[:200],
                "time": a.get("date", ""),
                "source": a.get("mediaName", ""),
                "url": a.get("url", ""),
            })
        return rows
    except Exception:
        return []


def eastmoney_global_news(page_size: int = 50) -> list[dict]:
    """东方财富全球财经资讯（7x24 滚动）。返回: [{title, summary, time}]"""
    url = "https://np-weblist.eastmoney.com/comm/web/getFastNewsList"
    params = {
        "client": "web", "biz": "web_724",
        "fastColumn": "102", "sortEnd": "",
        "pageSize": str(page_size),
        "req_trace": str(uuid.uuid4()),
    }
    headers = {"User-Agent": UA, "Referer": "https://kuaixun.eastmoney.com/"}
    try:
        r = em_get(url, params=params, headers=headers, timeout=10)
        d = r.json()
        rows = []
        for item in d.get("data", {}).get("fastNewsList", []):
            rows.append({
                "title": item.get("title", ""),
                "summary": item.get("summary", "")[:200],
                "time": item.get("showTime", ""),
            })
        return rows
    except Exception:
        return []


# ── 6. 基础数据层 ────────────────────────────────────────────────────────

def eastmoney_stock_info(code: str) -> dict:
    """东财个股基本面信息。"""
    market_code = 1 if code.startswith("6") else 0
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "fltt": "2", "invt": "2",
        "fields": "f57,f58,f84,f85,f127,f116,f117,f189,f43",
        "secid": f"{market_code}.{code}",
    }
    headers = {"User-Agent": UA}
    try:
        r = em_get(url, params=params, headers=headers, timeout=10)
        d = r.json().get("data", {})
        return {
            "code": d.get("f57", ""),
            "name": d.get("f58", ""),
            "industry": d.get("f127", ""),
            "total_shares": d.get("f84", 0),
            "float_shares": d.get("f85", 0),
            "mcap": d.get("f116", 0),
            "float_mcap": d.get("f117", 0),
            "list_date": d.get("f189", ""),
        }
    except Exception:
        return {}
