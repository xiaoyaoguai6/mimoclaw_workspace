"""Explore the live website structure."""
import os, json
from playwright.sync_api import sync_playwright

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        # 1. Login page
        page.goto("http://8.154.27.225:8088/login", wait_until="networkidle", timeout=30000)
        page.screenshot(path=os.path.join(OUT_DIR, "01-login.png"))
        print("Login page title:", page.title())

        inputs = page.query_selector_all("input")
        print(f"Input fields found: {len(inputs)}")
        for inp in inputs:
            t = inp.get_attribute("type") or ""
            n = inp.get_attribute("name") or ""
            ph = inp.get_attribute("placeholder") or ""
            print(f"  Input: type={t}, name={n}, placeholder={ph}")

        buttons = page.query_selector_all("button")
        print(f"Buttons found: {len(buttons)}")
        for btn in buttons:
            print(f"  Button: text={btn.text_content().strip()[:80]}")

        # 2. Login
        # Try to fill in credentials
        phone_input = page.query_selector('input[type="text"], input[type="tel"], input[name="phone"], input[name="username"]')
        pwd_input = page.query_selector('input[type="password"]')
        if phone_input and pwd_input:
            phone_input.fill("18138018452")
            pwd_input.fill("qwertyuiop1")
            page.screenshot(path=os.path.join(OUT_DIR, "02-login-filled.png"))
            # Find and click submit
            submit = page.query_selector('button[type="submit"], .login-btn, button:has-text("登录"), button:has-text("Login")')
            if submit:
                submit.click()
                page.wait_for_timeout(3000)
                page.screenshot(path=os.path.join(OUT_DIR, "03-after-login.png"))
                print("After login URL:", page.url)
                print("After login title:", page.title())
            else:
                print("No submit button found")
        else:
            print("Login inputs not found, trying direct navigation")

        # 3. Explore all pages
        pages_to_visit = [
            ("dashboard", "/dashboard"),
            ("positions", "/positions"),
            ("stocks", "/stocks"),
            ("simtrade", "/simtrade"),
            ("news", "/news"),
            ("reports", "/reports"),
            ("settings", "/settings"),
        ]

        for name, path in pages_to_visit:
            try:
                url = f"http://8.154.27.225:8088{path}"
                page.goto(url, wait_until="networkidle", timeout=15000)
                page.screenshot(path=os.path.join(OUT_DIR, f"page-{name}.png"), full_page=True)
                print(f"Page {name}: URL={page.url}, Title={page.title()}")
            except Exception as e:
                print(f"Page {name} error: {e}")

        # 4. Get sidebar/navigation structure
        nav_links = page.query_selector_all("nav a, .sidebar a, .menu a, a[href]")
        print(f"\nNav links found: {len(nav_links)}")
        seen = set()
        for link in nav_links:
            href = link.get_attribute("href") or ""
            text = link.text_content().strip()[:60]
            if href and href not in seen:
                seen.add(href)
                print(f"  Link: {text} -> {href}")

        # 5. Get dashboard page full HTML for analysis
        page.goto("http://8.154.27.225:8088/dashboard", wait_until="networkidle", timeout=15000)
        dashboard_html = page.content()
        with open(os.path.join(OUT_DIR, "dashboard-source.html"), "w", encoding="utf-8") as f:
            f.write(dashboard_html)
        print(f"\nDashboard HTML saved: {len(dashboard_html)} chars")

        # 6. Get positions page full HTML
        page.goto("http://8.154.27.225:8088/positions", wait_until="networkidle", timeout=15000)
        positions_html = page.content()
        with open(os.path.join(OUT_DIR, "positions-source.html"), "w", encoding="utf-8") as f:
            f.write(positions_html)
        print(f"Positions HTML saved: {len(positions_html)} chars")

        browser.close()
        print("\nExploration complete!")

if __name__ == "__main__":
    main()
