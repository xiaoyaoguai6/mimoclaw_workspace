"""Capture screenshots of all pages via Playwright."""
import os, sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

OUT = os.path.dirname(os.path.abspath(__file__))
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        # 1. Login
        print("[1] Opening login page...")
        page.goto("http://8.154.27.225:8088/login", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        page.screenshot(path=os.path.join(OUT, "screen-login.png"))
        print(f"    Login page loaded: {page.url}")

        # Fill credentials
        username_el = page.query_selector('input[type="text"]')
        pwd_el = page.query_selector('input[type="password"]')
        if username_el:
            username_el.fill("18138018452")
            print("    Username filled")
        if pwd_el:
            pwd_el.fill("qwertyuiop1")
            print("    Password filled")

        page.screenshot(path=os.path.join(OUT, "screen-login-filled.png"))

        # Click submit
        btns = page.query_selector_all("button")
        for btn in btns:
            txt = btn.text_content().strip()
            if txt and len(txt) < 15:
                btn.click()
                print(f"    Clicked button: {txt}")
                break

        time.sleep(4)
        print(f"    After login: {page.url}")
        page.screenshot(path=os.path.join(OUT, "screen-after-login.png"))

        # 2. Visit each page
        pages_list = [
            ("dashboard", "/dashboard"),
            ("positions", "/positions"),
            ("stocks", "/stocks"),
            ("simtrade", "/simtrade"),
            ("news", "/news"),
            ("reports", "/reports"),
            ("settings", "/settings"),
        ]

        for name, path in pages_list:
            try:
                url = "http://8.154.27.225:8088" + path
                print("[2] Navigating to " + name + "...")
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(4)
                page.screenshot(path=os.path.join(OUT, "screen-" + name + ".png"), full_page=True)
                html = page.content()
                with open(os.path.join(OUT, "rendered-" + name + ".html"), "w", encoding="utf-8") as f:
                    f.write(html)
                print("    " + name + " done, html=" + str(len(html)) + " chars")
            except Exception as e:
                print("    " + name + " error: " + str(e))

        # 3. Collect navigation structure from dashboard
        print("[3] Collecting nav structure...")
        try:
            page.goto("http://8.154.27.225:8088/dashboard", wait_until="domcontentloaded", timeout=30000)
            time.sleep(4)
            links = page.query_selector_all("a")
            seen = set()
            for link in links:
                href = link.get_attribute("href") or ""
                text = link.text_content().strip()[:60]
                if href and href not in seen and not href.startswith("http"):
                    seen.add(href)
                    print("    Link: " + text + " -> " + href)

            # Get body text
            body = page.inner_text("body")
            with open(os.path.join(OUT, "dashboard-body.txt"), "w", encoding="utf-8") as f:
                f.write(body)
            print("    Dashboard body text: " + str(len(body)) + " chars")
        except Exception as e:
            print("    Nav error: " + str(e))

        browser.close()
        print("\nAll done!")

if __name__ == "__main__":
    main()
