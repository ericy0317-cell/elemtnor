# -*- coding: utf-8 -*-
import sys, os, json, asyncio
sys.stdout.reconfigure(encoding="utf-8")

from playwright.async_api import async_playwright

WP_URL = "https://yange14.sg-host.com"
PROFILE = os.path.join(os.path.dirname(__file__), "chrome_profile")
savedir = os.path.join(os.path.dirname(__file__), "screenshots")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE,
            headless=True,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        page = await browser.new_page()

        # Step 1: Go to admin
        await page.goto(f"{WP_URL}/wp-admin", wait_until="networkidle")
        print(f"Admin URL: {page.url}")

        # Step 2: Check Elementor settings
        print("\n[1] Checking Elementor settings...")
        await page.goto(f"{WP_URL}/wp-admin/admin.php?page=elementor-settings", wait_until="networkidle")
        await page.screenshot(path=os.path.join(savedir, "10_elementor_settings.png"))
        print(f"    Settings URL: {page.url}")
        
        # Check what post types Elementor is active for
        content = await page.content()
        if "post" in content.lower():
            print("    Post/page settings found")
        
        # Step 3: Check existing Container Motel page
        print("\n[2] Checking existing Container Motel pages...")
        await page.goto(f"{WP_URL}/wp-admin/edit.php?post_type=page&s=Container+Motel", wait_until="networkidle")
        await page.screenshot(path=os.path.join(savedir, "11_container_pages.png"))
        
        # Get all page links
        links = await page.query_selector_all("table.wp-list-table tbody tr td.title a.row-title")
        print(f"    Found {len(links)} pages")
        
        page_ids = []
        for link in links[:5]:
            href = await link.get_attribute("href")
            pid = href.split("post=")[-1] if "post=" in href else "?"
            title = await link.inner_text()
            print(f"    ID={pid}: {title}")
            page_ids.append(pid)
        
        # Step 4: Open the first page and check for Elementor data
        if page_ids:
            pid = page_ids[0]
            print(f"\n[3] Checking page ID={pid}...")
            await page.goto(f"{WP_URL}/wp-admin/post.php?post={pid}&action=elementor", wait_until="networkidle")
            await page.wait_for_timeout(3000)
            await page.screenshot(path=os.path.join(savedir, "12_elementor_editor_page.png"))
            print(f"    URL: {page.url}")
            
            # Check if Elementor loaded
            has_elementor = "elementor" in page.url
            print(f"    Elementor editor: {has_elementor}")
            
            if has_elementor:
                await page.wait_for_timeout(5000)
                await page.screenshot(path=os.path.join(savedir, "13_elementor_editor_loaded.png"))
                
                # Try to get Elementor data
                try:
                    elementor_data = await page.evaluate("""
                        () => {
                            const doc = elementor && elementor.documents;
                            if (!doc) return { error: 'no elementor.documents' };
                            const currentDoc = doc.getCurrent();
                            if (!currentDoc) return { error: 'no current document' };
                            const container = currentDoc.container;
                            if (!container) return { error: 'no container' };
                            
                            const children = container.children;
                            const sections = [];
                            for (let i = 0; i < children.length; i++) {
                                const child = children[i];
                                const model = child.model;
                                sections.push({
                                    index: i,
                                    elType: model.get('elType'),
                                    widgetType: model.get('widgetType'),
                                    settings: model.get('settings'),
                                    childCount: child.children ? child.children.length : 0
                                });
                            }
                            return {
                                docTitle: currentDoc.getTitle(),
                                sectionCount: sections.length,
                                sections: sections
                            };
                        }
                    """)
                    print(f"\n    Elementor page data:")
                    print(f"    {json.dumps(elementor_data, indent=2, default=str)[:3000]}")
                except Exception as ex:
                    print(f"    Error reading Elementor: {ex}")
                    
                    # Try simpler approach
                    try:
                        has_e = await page.evaluate("typeof elementor !== 'undefined'")
                        print(f"    elementor exists: {has_e}")
                        has_erun = await page.evaluate("typeof $e !== 'undefined'")
                        print(f"    $e exists: {has_erun}")
                    except Exception as ex2:
                        print(f"    Also failed: {ex2}")
        
        # Step 5: Check how to enable Elementor for pages
        print("\n[4] Checking Elementor post type settings...")
        await page.goto(f"{WP_URL}/wp-admin/admin.php?page=elementor-settings#tab-general", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(savedir, "14_elementor_general_settings.png"))
        
        # Look for post type checkbox
        ct = await page.content()
        if 'page' in ct:
            print("    Page type appears in settings")
        if 'checkbox' in ct:
            print("    Checkboxes found in settings")
        
        # Step 6: Try creating a page via Elementor directly
        print("\n[5] Creating a new test page with Elementor...")
        await page.goto(f"{WP_URL}/wp-admin/post-new.php?post_type=page", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        # Fill title
        title_input = await page.query_selector("#title, .editor-post-title__input, h1.wp-block-post-title")
        if title_input:
            await title_input.click()
            await title_input.fill("Elementor Test Page - DO NOT PUBLISH")
            print("    Title filled")
        await page.screenshot(path=os.path.join(savedir, "15_new_page.png"))
        
        # Look for "Edit with Elementor" button - maybe it's behind a screen option
        button_selectors = [
            "#elementor-switch-mode-button",
            "a.elementor-button",
            "a[href*='action=elementor']",
            ".elementor-button-wrapper a",
            "#elementor-go-to-edit-link",
            "a.elementor-edit-link",
            ".elementor-switch-mode-off",
            "button[data-event='switchMode']"
        ]
        
        for selector in button_selectors:
            btn = await page.query_selector(selector)
            if btn:
                txt = await btn.inner_text()
                print(f"    Found button: selector='{selector}' text='{txt}'")
                break
        else:
            print("    No Elementor switch button found with any selector")
            
            # Maybe it's in the Gutenberg editor and Elementor adds a panel
            panel_items = await page.query_selector_all(".edit-post-header-toolbar button, .interface-interface-skeleton__header button")
            print(f"    Header buttons: {len(panel_items)}")
            
            # Check if there's an Elementor panel
            e_panels = await page.query_selector_all("[aria-label*='Elementor'], [class*='elementor'], .elementor-panel")
            print(f"    Elementor panel elements: {len(e_panels)}")
        
        await browser.close()
        print("\n[*] Done!")

asyncio.run(main())
