"""
选股数据库 — SQLite 存储股票列表 + 60天K线 + 初始化状态。
主板(60xxxx/00xxxx) + 创业板(30xxxx) + 中小板(002xxx)。
"""
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "screener.db"
TZ = timezone(timedelta(hours=8))

INIT_WINDOW_DAYS = 60


def _get_conn():
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.row_factory = sqlite3.Row
    # WAL 模式: 允许并发读写,不互斥
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def _now():
    return datetime.now(TZ).isoformat()


def init_db():
    """建表。"""
    with _get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS screener_state (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE TABLE IF NOT EXISTS stocks (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                market INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS klines (
                code TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL, high REAL, low REAL, close REAL,
                vol REAL, amount REAL,
                PRIMARY KEY (code, date)
            );

            CREATE INDEX IF NOT EXISTS idx_klines_code ON klines(code);
        """)
        conn.commit()


def get_state(key: str, default=None) -> str:
    with _get_conn() as conn:
        row = conn.execute("SELECT value FROM screener_state WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default


def set_state(key: str, value: str):
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO screener_state (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value)
        )
        conn.commit()


def is_initialized() -> bool:
    return get_state("initialized") == "1"


def get_init_progress() -> dict:
    total = get_state("total_stocks", "0")
    done = get_state("fetched_stocks", "0")
    return {
        "initialized": is_initialized(),
        "total": int(total),
        "fetched": int(done),
        "running": get_state("init_running") == "1",
    }


def clear_all_stocks():
    with _get_conn() as conn:
        conn.execute("DELETE FROM stocks")
        conn.execute("DELETE FROM klines")
        conn.commit()


def upsert_stock(code: str, name: str, market: int):
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO stocks (code, name, market) VALUES (?, ?, ?) "
            "ON CONFLICT(code) DO UPDATE SET name=excluded.name, market=excluded.market",
            (code, name, market)
        )
        conn.commit()


def bulk_upsert_stocks(stocks: list[dict]):
    """批量插入股票列表(单连接单事务,速度快100倍)。"""
    with _get_conn() as conn:
        conn.executemany(
            "INSERT INTO stocks (code, name, market) VALUES (?, ?, ?) "
            "ON CONFLICT(code) DO UPDATE SET name=excluded.name, market=excluded.market",
            [(s["code"], s["name"], s["market"]) for s in stocks]
        )
        conn.commit()


def get_all_stocks() -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute("SELECT * FROM stocks ORDER BY code").fetchall()
        return [dict(r) for r in rows]


def get_stock_count() -> int:
    with _get_conn() as conn:
        row = conn.execute("SELECT COUNT(*) as c FROM stocks").fetchone()
        return row["c"]


def upsert_klines(code: str, klines: list[dict]):
    """批量插入K线(覆盖同日数据,单连接单事务)。"""
    with _get_conn() as conn:
        conn.executemany(
            "INSERT INTO klines (code, date, open, high, low, close, vol, amount) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(code, date) DO UPDATE SET "
            "open=excluded.open, high=excluded.high, low=excluded.low, "
            "close=excluded.close, vol=excluded.vol, amount=excluded.amount",
            [(code, k["date"], k["open"], k["high"], k["low"], k["close"], k["vol"], k["amount"]) for k in klines]
        )
        conn.commit()


def get_klines(code: str, days: int = 60) -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT date, open, high, low, close, vol, amount FROM klines "
            "WHERE code=? ORDER BY date DESC LIMIT ?", (code, days)
        ).fetchall()
        return list(reversed([dict(r) for r in rows]))


def trim_old_klines():
    """只保留最近60天K线。"""
    with _get_conn() as conn:
        conn.execute(
            "DELETE FROM klines WHERE date < "
            "(SELECT MIN(date) FROM (SELECT DISTINCT date FROM klines ORDER BY date DESC LIMIT 60))"
        )
        conn.commit()
