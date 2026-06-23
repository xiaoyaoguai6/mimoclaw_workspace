"""Fetch and analyze the live website API and pages."""
import requests
import json
import os
import re
import sys
import io
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

OUT = os.path.dirname(os.path.abspath(__file__))
session = requests.Session()
BASE = "http://8.154.27.225:8088"

# 1. Login page
print("=" * 60)
print("1. LOGIN PAGE")
print("=" * 60)
r = session.get(f"{BASE}/login", timeout=15)
print(f"Status: {r.status_code}, Length: {len(r.text)}")
with open(os.path.join(OUT, "login-source.html"), "w", encoding="utf-8") as f:
    f.write(r.text)
print("Content:")
print(r.text[:2000])
print()

# 2. Try login API
print("=" * 60)
print("2. LOGIN API")
print("=" * 60)
for path in ["/api/login", "/api/auth/login", "/api/user/login"]:
    for payload in [
        {"phone": "18138018452", "password": "qwertyuiop1"},
        {"username": "18138018452", "password": "qwertyuiop1"},
        {"account": "18138018452", "password": "qwertyuiop1"},
    ]:
        try:
            r = session.post(f"{BASE}{path}", json=payload, timeout=10)
            if r.status_code != 404:
                print(f"POST {path} keys={list(payload.keys())}: status={r.status_code}")
                print(f"  Body: {r.text[:500]}")
        except Exception as e:
            pass

# 3. Fetch all pages
print()
print("=" * 60)
print("3. ALL PAGES")
print("=" * 60)
for p in ["/dashboard", "/positions", "/stocks", "/simtrade", "/news", "/reports", "/settings"]:
    try:
        r = session.get(f"{BASE}{p}", timeout=10)
        fname = p.strip("/").replace("/", "_") + ".html"
        with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
            f.write(r.text)
        print(f"GET {p}: status={r.status_code}, len={len(r.text)}")
    except Exception as e:
        print(f"GET {p}: error={e}")

# 4. Probe API endpoints
print()
print("=" * 60)
print("4. API ENDPOINTS")
print("=" * 60)
apis = [
    "/api/user/info", "/api/dashboard", "/api/positions",
    "/api/stocks", "/api/news", "/api/reports",
    "/api/trade/list", "/api/account/info", "/api/market/data",
]
for ep in apis:
    try:
        r = session.get(f"{BASE}{ep}", timeout=8)
        if r.status_code != 404:
            print(f"GET {ep}: status={r.status_code}, len={len(r.text)}")
            if r.status_code == 200:
                print(f"  Preview: {r.text[:200]}")
    except:
        pass

# 5. Cookies
print()
print("=" * 60)
print("5. COOKIES")
print("=" * 60)
for c in session.cookies:
    print(f"Cookie: {c.name}={c.value[:80]}")

# 6. Analyze JS bundles from login page
print()
print("=" * 60)
print("6. JS BUNDLES")
print("=" * 60)
html = open(os.path.join(OUT, "login-source.html"), "r", encoding="utf-8").read()
soup = BeautifulSoup(html, "html.parser")
for s in soup.find_all("script"):
    src = s.get("src", "")
    if src:
        print(f"Script: {src}")
        try:
            full_url = f"{BASE}{src}" if src.startswith("/") else src
            r = session.get(full_url, timeout=10)
            js_name = src.split("/")[-1]
            with open(os.path.join(OUT, js_name), "w", encoding="utf-8") as f:
                f.write(r.text)
            print(f"  Saved: {js_name} ({len(r.text)} chars)")
            # Extract routes
            routes = re.findall(r'path:\s*["\']([^"\']+)["\']', r.text)
            if routes:
                print(f"  Routes found: {routes[:30]}")
            # Extract API endpoints
            api_eps = re.findall(r'["\'](/api/[^"\']+)["\']', r.text)
            if api_eps:
                print(f"  APIs found: {api_eps[:30]}")
        except Exception as e:
            print(f"  Error: {e}")

# 7. Analyze link/css
print()
print("=" * 60)
print("7. CSS/LINKS")
print("=" * 60)
for l in soup.find_all("link"):
    href = l.get("href", "")
    if href:
        print(f"Link: {href}")

print()
print("DONE!")
