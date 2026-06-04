# -*- coding: utf-8 -*-
import sys, os, json, asyncio
sys.stdout.reconfigure(encoding="utf-8")

from playwright.async_api import async_playwright

WP_URL = "https://yange14.sg-host.com"
USER = "243626599@qq.com"
PASS = "8008208820dhc"
PROFILE = os.path.join(os.path.dirname(__file__), "chrome_profile")
os.makedirs(PROFILE, exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), "screenshots"), exist_ok=True)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE,
            headless=True,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        page = await browser.new_page()
        savedir = os.path.join(os.path.dirname(__file__), "screenshots")

        # Step 1: Login
        print("[1] Navigating to login...")
        await page.goto(f"{WP_URL}/wp-login.php", wait_until="networkidle")
        await page.screenshot(path=os.path.join(savedir, "01_login_page.png"))
        
        if "wp-admin" not in page.url:
            await page.fill("#user_login", USER)
            await page.fill("#user_pass", PASS)
            await page.click("#wp-submit")
            await page.wait_for_timeout(5000)
        
        await page.screenshot(path=os.path.join(savedir, "02_after_login.png"))
        print(f"    URL: {page.url}")

        if "wp-admin" in page.url:
            print("    Login OK!")
        else:
            print(f"    Login failed, trying another way...")
            await page.goto(f"{WP_URL}/wp-admin", wait_until="networkidle")
            await page.screenshot(path=os.path.join(savedir, "02b_admin_attempt.png"))
            print(f"    URL: {page.url}")
        
        # Step 2: Check plugins
        print("\n[2] Checking plugins...")
        await page.goto(f"{WP_URL}/wp-admin/plugins.php", wait_until="networkidle")
        await page.screenshot(path=os.path.join(savedir, "03_plugins.png"))
        content = await page.content()
        
        # Parse plugin status
        if "elementor/elementor.php" in content:
            print("    Elementor plugin found!")
        else:
            # Search for elementor
            elementor_active = "elementor" in content.lower()
            print(f"    Elementor in content: {elementor_active}")
        
        # Step 3: List pages  
        print("\n[3] Checking existing pages...")
        await page.goto(f"{WP_URL}/wp-admin/edit.php?post_type=page", wait_until="networkidle")
        await page.screenshot(path=os.path.join(savedir, "04_pages.png"))
        title = await page.title()
        print(f"    Page title: {title}")
        
        # Get page list
        page_rows = await page.query_selector_all("table.wp-list-table tbody tr")
        print(f"    Existing pages: {len(page_rows)}")
        for row in page_rows[:10]:
            title_el = await row.query_selector(".page-title a.row-title")
            if title_el:
                print(f"      - {await title_el.inner_text()}")
        
        # Step 4: Try Elementor editor
        print("\n[4] Trying to open Elementor editor...")
        await page.goto(f"{WP_URL}/wp-admin/post-new.php?post_type=page", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        # Look for Elementor button
        edit_btns = await page.query_selector_all("#elementor-switch-mode-button, .elementor-button, a[href*='elementor']")
        print(f"    Elementor-related buttons: {len(edit_btns)}")
        
        for i, btn in enumerate(edit_btns[:3]):
            txt = await btn.inner_text()
            href = await btn.get_attribute("href")
            print(f"      Button {i}: text='{txt}' href='{href}'")
        
        # Try clicking "Edit with Elementor"
        e_btn = await page.query_selector("#elementor-switch-mode-button")
        if e_btn:
            btn_text = await e_btn.inner_text()
            print(f"    Clicking: {btn_text}")
            await e_btn.click()
            await page.wait_for_timeout(5000)
            await page.screenshot(path=os.path.join(savedir, "05_elementor_editor.png"))
            print(f"    Editor URL: {page.url}")
            
            # If we're in Elementor editor, explore the interface
            if "elementor" in page.url:
                print("\n[5] Exploring Elementor editor interface...")
                await page.wait_for_timeout(3000)
                await page.screenshot(path=os.path.join(savedir, "06_elementor_interface.png"))
                
                # Try executing $e commands
                try:
                    result = await page.evaluate("""
                        () => {
                            if (typeof elementor !== 'undefined') {
                                return {
                                    hasElementor: true,
                                    hasRun: typeof $e !== 'undefined' && typeof $e.run === 'function',
                                    widgets: Object.keys(elementor.widgets || {}).length,
                                    docLoaded: elementor.documents ? true : false
                                };
                            }
                            return { hasElementor: false };
                        }
                    """)
                    print(f"    Elementor state: {json.dumps(result, indent=2)}")
                except Exception as ex:
                    print(f"    Error evaluating: {ex}")
        else:
            print("    No Elementor switch button found")
        
        # Save cookies
        cookies = await browser.cookies()
        with open(os.path.join(os.path.dirname(__file__), "wp_cookies.json"), "w") as f:
            json.dump(cookies, f)
        print(f"\n[*] Cookies saved: {len(cookies)} cookies")
        
        await browser.close()
        print("[*] Done!")

asyncio.run(main())
