"""Probe all API endpoints with authentication."""
import requests
import json
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "http://8.154.27.225:8088"

# Login to get token
s = requests.Session()
r = s.post(f"{BASE}/api/user/login", json={"username": "18138018452", "password": "qwertyuiop1"}, timeout=10)
data = r.json()
token = data["data"]["token"]
user = data["data"]["user"]
print(f"Token: {token[:60]}...")
print(f"User: {json.dumps(user, ensure_ascii=False)}")

with open(os.path.join(OUT, "token.txt"), "w") as f:
    f.write(token)

headers = {"Authorization": f"Bearer {token}"}

# Probe all endpoints
apis = [
    "GET /api/user/info",
    "GET /api/user/profile",
    "GET /api/dashboard",
    "GET /api/dashboard/summary",
    "GET /api/dashboard/stats",
    "GET /api/positions",
    "GET /api/position/list",
    "GET /api/position/summary",
    "GET /api/stocks",
    "GET /api/stock/list",
    "GET /api/stock/search",
    "GET /api/stock/hot",
    "GET /api/stock/recommend",
    "GET /api/news",
    "GET /api/news/list",
    "GET /api/news/hot",
    "GET /api/reports",
    "GET /api/report/list",
    "GET /api/report/summary",
    "GET /api/trade",
    "GET /api/trade/list",
    "GET /api/trade/history",
    "GET /api/account",
    "GET /api/account/info",
    "GET /api/account/balance",
    "GET /api/market",
    "GET /api/market/data",
    "GET /api/market/index",
    "GET /api/ai",
    "GET /api/ai/chat",
    "GET /api/ai/history",
    "GET /api/settings",
    "GET /api/settings/profile",
    "GET /api/monitor",
    "GET /api/monitor/list",
    "GET /api/simtrade",
    "GET /api/simtrade/list",
]

print()
print("=" * 60)
print("API ENDPOINTS WITH AUTH")
print("=" * 60)
for api in apis:
    method, path = api.split(" ", 1)
    try:
        r = s.request(method, f"{BASE}{path}", headers=headers, timeout=8)
        if r.status_code != 404:
            print(f"{api}: status={r.status_code}, len={len(r.text)}")
            if r.status_code == 200 and len(r.text) > 2:
                fname = path.replace("/", "_").strip("_") + ".json"
                with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
                    f.write(r.text)
                print(f"  Saved: {fname}")
                print(f"  Preview: {r.text[:300]}")
    except Exception as e:
        print(f"{api}: error={e}")

print()
print("DONE!")
