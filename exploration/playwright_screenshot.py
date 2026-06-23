"""Use Playwright to navigate and screenshot the live website."""
import os
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

OUT = os.path.dirname(os.path.abspath(__file__))

from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        # 1. Go to login page
        print("Opening login page...")
        page.goto("http://8.154.27.225:8088/", wait_until="networkidle", timeout=30000)
        time.sleep(2)
        page.screenshot(path=os.path.join(OUT, "screen-login.png"))
        print(f"Login page: {page.url}")

        # 2. Fill in credentials and login
        print("Logging in...")
        # Find username input
        username_input = page.query_selector('input[placeholder*="account"], input[placeholder*="phone"], input[placeholder*="user"], input[name="username"], input[type="text"]')
        if username_input:
            username_input.fill("18138018452")
            print("  Username filled")

        # Find password input
        pwd_input = page.query_selector('input[type="password"]')
        if pwd_input:
            pwd_input.fill("qwertyuiop1")
            print("  Password filled")

        page.screenshot(path=os.path.join(OUT, "screen-login-filled.png"))

        # Click login button
        login_btn = page.query_selector('button[type="submit"], button:has-text("login"), button:has-text("Login"), button:has-text("sign"), .login-btn')
        if not login_btn:
            # Try finding any button
            buttons = page.query_selector_all("button")
            print(f"  Found {len(buttons)} buttons")
            for btn in buttons:
                text = btn.text_content().strip()
                print(f"    Button: {text[:50]}")
                if len(text) < 20 and text:
                    login_btn = btn
                    break

        if login_btn:
            login_btn.click()
            print("  Login button clicked")
            time.sleep(3)
            page.wait_for_load_state("networkidle", timeout=10000)

        page.screenshot(path=os.path.join(OUT, "screen-after-login.png"))
        print(f"After login URL: {page.url}")

        # 3. Visit all pages and take screenshots
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
                print(f"Navigating to {name}...")
                page.goto(url, wait_until="networkidle", timeout=15000)
                time.sleep(1)
                page.screenshot(path=os.path.join(OUT, f"screen-{name}.png"), full_page=True)

                # Also save the rendered HTML
                html = page.content()
                with open(os.path.join(OUT, f"rendered-{name}.html"), "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"  {name}: URL={page.url}, HTML={len(html)} chars")
            except Exception as e:
                print(f"  {name}: error={e}")

        # 4. Get page structure info
        print("\nCollecting page structure...")
        page.goto("http://8.154.27.225:8088/dashboard", wait_until="networkidle", timeout=15000)
        time.sleep(1)

        # Get sidebar links
        links = page.query_selector_all("a[href], nav a, .sidebar a")
        print(f"Links found: {len(links)}")
        seen = set()
        for link in links:
            href = link.get_attribute("href") or ""
            text = link.text_content().strip()[:60]
            if href and href not in seen and not href.startswith("http"):
                seen.add(href)
                print(f"  Link: {text} -> {href}")

        # Get all visible text on dashboard
        body_text = page.inner_text("body")
        with open(os.path.join(OUT, "dashboard-text.txt"), "w", encoding="utf-8") as f:
            f.write(body_text)
        print(f"\nDashboard text length: {len(body_text)} chars")

        browser.close()
        print("\nAll screenshots captured!")

if __name__ == "__main__":
    main()
