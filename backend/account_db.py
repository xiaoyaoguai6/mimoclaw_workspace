"""
账户/持仓/交易管理 — SQLite 持久化。
管理：账户资产、持仓、交易历史。
实时价格由 stock_data.tencent_quote 提供，PnL 动态计算。
"""
import sqlite3
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "ai_trader.db"
INITIAL_CAPITAL = 1_000_000.0
TZ = timezone(timedelta(hours=8))


def _get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _now():
    return datetime.now(TZ).isoformat()


def init_db():
    """初始化数据库表 + 默认账户。"""
    with _get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS account (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                initial_capital REAL NOT NULL,
                available_cash REAL NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS holdings (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                qty INTEGER NOT NULL,
                cost_avg REAL NOT NULL,
                built_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                name TEXT NOT NULL,
                action TEXT NOT NULL,
                qty INTEGER NOT NULL,
                price REAL NOT NULL,
                amount REAL NOT NULL,
                ts TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS ai_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                name TEXT NOT NULL,
                action TEXT NOT NULL,
                reason TEXT,
                confidence TEXT,
                ts TEXT NOT NULL
            );
        """)
        row = conn.execute("SELECT id FROM account WHERE id=1").fetchone()
        if not row:
            conn.execute(
                "INSERT INTO account (id, initial_capital, available_cash, created_at) VALUES (1, ?, ?, ?)",
                (INITIAL_CAPITAL, INITIAL_CAPITAL, _now())
            )
        conn.commit()


def get_account() -> dict:
    """获取账户基础信息（不含持仓实时数据）。"""
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM account WHERE id=1").fetchone()
        if not row:
            init_db()
            row = conn.execute("SELECT * FROM account WHERE id=1").fetchone()
        return dict(row)


def get_holdings_raw() -> list[dict]:
    """获取持仓原始数据（不含实时价格）。"""
    with _get_conn() as conn:
        rows = conn.execute("SELECT * FROM holdings ORDER BY built_at").fetchall()
        return [dict(r) for r in rows]


def get_holdings_with_quotes() -> list[dict]:
    """获取持仓 + 实时价格 + 盈亏计算。"""
    from stock_data import tencent_quote

    raw = get_holdings_raw()
    if not raw:
        return []

    codes = [h["code"] for h in raw]
    quotes = tencent_quote(codes)

    result = []
    for h in raw:
        q = quotes.get(h["code"], {})
        price = q.get("price", 0)
        cost = h["cost_avg"]
        qty = h["qty"]
        market_value = price * qty
        cost_total = cost * qty
        pnl = (price - cost) * qty
        pnl_pct = ((price - cost) / cost * 100) if cost > 0 else 0
        result.append({
            "code": h["code"],
            "name": h["name"],
            "qty": qty,
            "cost_avg": round(cost, 3),
            "current_price": round(price, 3),
            "cost_total": round(cost_total, 2),
            "market_value": round(market_value, 2),
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl_pct, 2),
            "built_at": h["built_at"],
            "change_pct": q.get("change_pct", 0),
        })
    return result


def get_account_summary() -> dict:
    """获取完整账户摘要（含持仓实时市值、总盈亏）。"""
    from stock_data import tencent_quote

    acct = get_account()
    holdings = get_holdings_with_quotes()

    total_market_value = sum(h["market_value"] for h in holdings)
    total_cost = sum(h["cost_total"] for h in holdings)
    unrealized_pnl = sum(h["pnl"] for h in holdings)
    total_assets = acct["available_cash"] + total_market_value
    initial = acct["initial_capital"]
    total_pnl = total_assets - initial
    total_pnl_pct = (total_pnl / initial * 100) if initial > 0 else 0

    today_pnl = 0
    if holdings:
        codes = [h["code"] for h in holdings]
        quotes = tencent_quote(codes)
        for h in holdings:
            q = quotes.get(h["code"], {})
            last_close = q.get("last_close", h["current_price"])
            today_pnl += (h["current_price"] - last_close) * h["qty"]

    return {
        "initial_capital": round(initial, 2),
        "available_cash": round(acct["available_cash"], 2),
        "total_market_value": round(total_market_value, 2),
        "total_assets": round(total_assets, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round(total_pnl_pct, 2),
        "unrealized_pnl": round(unrealized_pnl, 2),
        "realized_pnl": round(total_pnl - unrealized_pnl, 2),
        "today_pnl": round(today_pnl, 2),
        "position_count": len(holdings),
        "position_usage": round((total_market_value / total_assets * 100) if total_assets > 0 else 0, 1),
        "holdings": holdings,
    }


def execute_trade(code: str, name: str, action: str, qty: int, price: float) -> dict:
    """
    执行交易（买入/卖出）。
    返回: {success, message, account}
    """
    if qty <= 0 or price <= 0:
        return {"success": False, "message": "数量和价格必须大于0"}
    if action not in ("buy", "sell"):
        return {"success": False, "message": "action 必须是 buy 或 sell"}

    amount = qty * price
    ts = _now()

    with _get_conn() as conn:
        acct = conn.execute("SELECT * FROM account WHERE id=1").fetchone()
        if not acct:
            return {"success": False, "message": "账户不存在"}

        holding = conn.execute("SELECT * FROM holdings WHERE code=?", (code,)).fetchone()

        if action == "buy":
            if acct["available_cash"] < amount:
                return {"success": False, "message": f"资金不足，需要 ¥{amount:.2f}，可用 ¥{acct['available_cash']:.2f}"}
            conn.execute("UPDATE account SET available_cash = available_cash - ? WHERE id=1", (amount,))
            if holding:
                old_qty = holding["qty"]
                old_cost = holding["cost_avg"]
                new_qty = old_qty + qty
                new_cost = (old_cost * old_qty + price * qty) / new_qty
                conn.execute(
                    "UPDATE holdings SET qty=?, cost_avg=? WHERE code=?",
                    (new_qty, round(new_cost, 3), code)
                )
            else:
                conn.execute(
                    "INSERT INTO holdings (code, name, qty, cost_avg, built_at) VALUES (?, ?, ?, ?, ?)",
                    (code, name, qty, round(price, 3), ts)
                )
        else:  # sell
            if not holding:
                return {"success": False, "message": f"无持仓 {code}"}
            if holding["qty"] < qty:
                return {"success": False, "message": f"持仓不足，当前 {holding['qty']} 股，尝试卖出 {qty} 股"}
            conn.execute("UPDATE account SET available_cash = available_cash + ? WHERE id=1", (amount,))
            new_qty = holding["qty"] - qty
            if new_qty == 0:
                conn.execute("DELETE FROM holdings WHERE code=?", (code,))
            else:
                conn.execute("UPDATE holdings SET qty=? WHERE code=?", (new_qty, code))

        conn.execute(
            "INSERT INTO trades (code, name, action, qty, price, amount, ts) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (code, name, action, qty, price, amount, ts)
        )
        conn.commit()

    return {"success": True, "message": f"{'买入' if action == 'buy' else '卖出'} {name}({code}) {qty}股 @ ¥{price}", "account": get_account_summary()}


def get_trade_history(limit: int = 100) -> list[dict]:
    """获取交易历史。"""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM trades ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def reset_account(initial_capital: float = INITIAL_CAPITAL) -> dict:
    """重置账户到初始状态。"""
    with _get_conn() as conn:
        conn.execute("DELETE FROM holdings")
        conn.execute("DELETE FROM trades")
        conn.execute("DELETE FROM ai_decisions")
        conn.execute(
            "UPDATE account SET initial_capital=?, available_cash=?, created_at=? WHERE id=1",
            (initial_capital, initial_capital, _now())
        )
        conn.commit()
    return {"success": True, "message": "账户已重置", "account": get_account_summary()}


def add_ai_decision(code: str, name: str, action: str, reason: str, confidence: str) -> dict:
    """记录 AI 决策。"""
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO ai_decisions (code, name, action, reason, confidence, ts) VALUES (?, ?, ?, ?, ?, ?)",
            (code, name, action, reason, confidence, _now())
        )
        conn.commit()
    return {"success": True}


def get_ai_decisions(limit: int = 50) -> list[dict]:
    """获取 AI 决策记录。"""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM ai_decisions ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
