# -*- coding: utf-8 -*-
import sys, os, json, asyncio
sys.stdout.reconfigure(encoding="utf-8")

from playwright.async_api import async_playwright

WP_URL = "https://yange14.sg-host.com"
USER = "243626599@qq.com"
PASS = "8008208820dhc"
PROFILE = os.path.join(os.path.dirname(__file__), "chrome_profile")
savedir = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(savedir, exist_ok=True)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE,
            headless=True,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        page = await browser.new_page()

        # Login
        print("[1] Logging in...")
        await page.goto(f"{WP_URL}/wp-login.php", wait_until="networkidle")
        
        if "wp-admin" not in page.url and "reauth" not in page.url:
            await page.fill("#user_login", USER)
            await page.fill("#user_pass", PASS)
            await page.click("#wp-submit")
            await page.wait_for_timeout(5000)
            await page.screenshot(path=os.path.join(savedir, "20_login.png"))
        
        await page.goto(f"{WP_URL}/wp-admin", wait_until="networkidle")
        print(f"    Admin URL: {page.url}")
        
        if "reauth" in page.url or "login" in page.url:
            print("    Login failed - trying again")
            await page.fill("#user_login", USER)
            await page.fill("#user_pass", PASS)
            await page.click("#wp-submit")
            await page.wait_for_timeout(5000)
            await page.goto(f"{WP_URL}/wp-admin", wait_until="networkidle")
            print(f"    Admin URL: {page.url}")
        
        # Go to Elementor settings
        print("\n[2] Elementor settings...")
        await page.goto(f"{WP_URL}/wp-admin/admin.php?page=elementor-settings", wait_until="networkidle")
        await page.screenshot(path=os.path.join(savedir, "21_elementor_settings.png"))
        print(f"    URL: {page.url}")
        
        # Check if we need to enable Elementor for pages
        if "elementor-settings" in page.url:
            # Check the "General" tab content
            content = await page.content()
            
            # Look for Checkbox to enable Elementor for pages
            # Try clicking through tabs
            tabs = await page.query_selector_all(".elementor-settings-tabs a, .nav-tab-wrapper a, .nav-tab")
            print(f"    Settings tabs: {len(tabs)}")
            for tab in tabs:
                txt = await tab.inner_text()
                href = await tab.get_attribute("href") or ""
                print(f"      Tab: '{txt}' -> {href[:80]}")
        
        # Check existing pages
        print("\n[3] Existing pages...")
        await page.goto(f"{WP_URL}/wp-admin/edit.php?post_type=page", wait_until="networkidle")
        await page.screenshot(path=os.path.join(savedir, "22_pages_list.png"))
        
        rows = await page.query_selector_all("table.wp-list-table tbody tr")
        page_data = []
        for row in rows:
            title_el = await row.query_selector(".page-title a.row-title")
            if title_el:
                title = await title_el.inner_text()
                href = await title_el.get_attribute("href") or ""
                pid = href.split("post=")[-1].split("&")[0] if "post=" in href else "?"
                page_data.append({"id": pid, "title": title})
                if len(page_data) <= 6:
                    print(f"    ID={pid}: {title}")
        print(f"    Total: {len(page_data)} pages")
        
        # Create a NEW page the WordPress way, then open with Elementor
        print("\n[4] Creating new page to test Elementor...")
        await page.goto(f"{WP_URL}/wp-admin/post-new.php?post_type=page", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        # Check if it's Block Editor or Classic
        has_gutenberg = await page.query_selector(".block-editor")
        has_classic = await page.query_selector("#postdivrich")
        print(f"    Block Editor (Gutenberg): {bool(has_gutenberg)}")
        print(f"    Classic Editor: {bool(has_classic)}")
        
        # Fill title
        try:
            if has_gutenberg:
                await page.fill(".editor-post-title__input", "Elementor Learning Test")
            elif has_classic:
                await page.fill("#title", "Elementor Learning Test")
        except:
            print("    Could not fill title")
        
        await page.screenshot(path=os.path.join(savedir, "23_new_page.png"))
        
        # Look for any Elementor-related button
        elementor_links = await page.query_selector_all("a[href*='elementor'], button[class*='elementor'], [id*='elementor']")
        print(f"    Elementor elements: {len(elementor_links)}")
        for el in elementor_links[:5]:
            tag = await el.get_attribute("tagName") or "?"
            txt = await el.inner_text() or ""
            cls = await el.get_attribute("class") or ""
            print(f"      <{tag}> class='{cls[:40]}' text='{txt[:40]}'")
        
        # Try the direct Elementor URL approach
        # Elementor adds a meta box - check
        metaboxes = await page.query_selector_all("#poststuff #post-body #side-sortables .postbox")
        print(f"    Meta boxes: {len(metaboxes)}")
        for mb in metaboxes:
            hdr = await mb.query_selector("h2.hndle, h2.hndle span")
            if hdr:
                txt = await hdr.inner_text()
                print(f"      Meta box: '{txt}'")
            else:
                cls = await mb.get_attribute("class") or ""
                if "elementor" in cls.lower():
                    print(f"      Elementor meta box: class='{cls[:60]}'")
        
        # The issue might be that the page needs to be saved first
        # Let's publish as draft and then open with Elementor
        print("\n[5] Saving draft and opening with Elementor...")
        
        # Find publish button
        publish_btn = await page.query_selector("#save-post, .editor-post-publish-button__button, .editor-post-save-draft")
        if publish_btn:
            await publish_btn.click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path=os.path.join(savedir, "24_saved_draft.png"))
        
        # Get current post ID from URL
        current_url = page.url
        import re
        post_id_match = re.search(r'post=(\d+)', current_url)
        if post_id_match:
            post_id = post_id_match.group(1)
            print(f"    Post ID: {post_id}")
            
            # Direct Elementor URL
            await page.goto(f"{WP_URL}/wp-admin/post.php?post={post_id}&action=elementor", wait_until="networkidle")
            await page.wait_for_timeout(5000)
            await page.screenshot(path=os.path.join(savedir, "25_elementor_direct.png"))
            print(f"    Elementor URL: {page.url}")
            
            if "elementor" in page.url:
                print("    Elementor editor loaded!")
                
                # Wait for Elementor to fully initialize
                await page.wait_for_timeout(8000)
                await page.screenshot(path=os.path.join(savedir, "26_elementor_loaded.png"))
                
                # Test Elementor API
                api_test = await page.evaluate("""
                    async () => {
                        const results = {};
                        
                        results.hasElementorGlobal = typeof elementor !== 'undefined';
                        results.hasDollarE = typeof $e !== 'undefined';
                        
                        if (typeof $e !== 'undefined') {
                            results.runExists = typeof $e.run === 'function';
                        }
                        
                        if (typeof elementor !== 'undefined') {
                            results.hasDocuments = !!elementor.documents;
                            if (elementor.documents) {
                                try {
                                    const doc = elementor.documents.getCurrent();
                                    results.currentDocExists = !!doc;
                                    if (doc) {
                                        results.docTitle = doc.getTitle();
                                        results.hasContainer = !!doc.container;
                                        if (doc.container) {
                                            results.childCount = doc.container.children.length;
                                        }
                                    }
                                } catch(e) {
                                    results.docError = e.message;
                                }
                            }
                        }
                        
                        // Test available commands
                        if (typeof $e !== 'undefined' && $e.commands) {
                            const commands = [];
                            $e.commands.getAll().forEach((cmd, name) => {
                                commands.push(name);
                            });
                            results.availableCommands = commands.filter(c => 
                                c.includes('document/elements') || 
                                c.includes('document/save') ||
                                c.includes('editor')
                            ).slice(0, 20);
                        }
                        
                        return results;
                    }
                """)
                print(f"\n    Elementor API test:")
                print(f"    {json.dumps(api_test, indent=2, default=str)[:2000]}")
                
                # Now create a simple section to test
                print("\n[6] Testing section creation...")
                create_test = await page.evaluate("""
                    async () => {
                        try {
                            const doc = elementor.documents.getCurrent();
                            const container = doc.container;
                            
                            // Create a simple section with one column and heading
                            const sectionData = {
                                elType: 'section',
                                settings: {
                                    background_background: 'classic',
                                    background_color: '#1a1a1a',
                                    padding: { unit: 'px', top: '100', right: '0', bottom: '100', left: '0', isLinked: false },
                                    gap: 'no',
                                    _element_width: 'boxed',
                                    _element_custom_width: { size: 1200, unit: 'px' }
                                },
                                elements: [{
                                    elType: 'column',
                                    settings: {
                                        _column_size: 100,
                                        _inline_size: 100,
                                        content_position: 'center',
                                        padding: { unit: 'px', top: '20', right: '20', bottom: '20', left: '20', isLinked: true }
                                    },
                                    elements: [{
                                        elType: 'widget',
                                        widgetType: 'heading',
                                        settings: {
                                            title: 'Container Motel Buildings',
                                            header_size: 'h1',
                                            align: 'center',
                                            title_color: '#ffffff',
                                            typography_typography: 'custom',
                                            typography_font_family: 'Oswald',
                                            typography_font_size: { size: 56, unit: 'px' },
                                            typography_font_weight: '700'
                                        }
                                    }]
                                }]
                            };
                            
                            const result = await $e.run('document/elements/create', {
                                container: container,
                                model: sectionData,
                                options: { edit: false, raise: false }
                            });
                            
                            return {
                                success: true,
                                resultType: typeof result,
                                hasResult: !!result,
                                childCount: container.children.length
                            };
                        } catch(e) {
                            return {
                                success: false,
                                error: e.message,
                                errorStack: e.stack?.substring(0, 300)
                            };
                        }
                    }
                """)
                print(f"    Create result: {json.dumps(create_test, indent=2, default=str)[:2000]}")
                
                if create_test.get("success"):
                    await page.screenshot(path=os.path.join(savedir, "27_section_created.png"))
                    
                    # Save
                    save_test = await page.evaluate("""
                        async () => {
                            try {
                                await $e.run('document/save/update');
                                return { success: true };
                            } catch(e) {
                                return { success: false, error: e.message };
                            }
                        }
                    """)
                    print(f"    Save result: {save_test}")
        
        await browser.close()
        print("\n[*] Done!")

asyncio.run(main())
