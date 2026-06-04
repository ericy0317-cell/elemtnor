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
        await page.goto(f"{WP_URL}/wp-admin", wait_until="domcontentloaded")
        print(f"    Admin: {page.url[:80]}")

        # Check one existing Container Motel page in Elementor
        print("\n[2] Opening existing page ID=298 with Elementor...")
        await page.goto(f"{WP_URL}/wp-admin/post.php?post=298&action=elementor", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)
        
        url = page.url
        print(f"    URL: {url[:100]}")
        await page.screenshot(path=os.path.join(savedir, "30_elementor_page298.png"))
        
        if "elementor" in url:
            print("    Elementor editor loaded!")
            await page.wait_for_timeout(10000)  # Wait for editor to fully initialize
            await page.screenshot(path=os.path.join(savedir, "31_elementor_ready.png"))
            
            # Get elementor state
            state = await page.evaluate("""
                () => {
                    const info = {
                        hasElementor: typeof elementor !== 'undefined',
                        hasDollarE: typeof $e !== 'undefined',
                        hasRun: typeof $e !== 'undefined' && typeof $e.run === 'function'
                    };
                    
                    if (typeof elementor !== 'undefined' && elementor.documents) {
                        try {
                            const doc = elementor.documents.getCurrent();
                            if (doc) {
                                info.docTitle = doc.getTitle();
                                info.hasContainer = !!doc.container;
                                if (doc.container) {
                                    info.childCount = doc.container.children.length;
                                    info.innerHeight = doc.container.view.$el ? true : false;
                                }
                                // Try to get more details
                                info.sections = [];
                                if (doc.container && doc.container.children) {
                                    for (let i = 0; i < doc.container.children.length; i++) {
                                        const child = doc.container.children[i];
                                        if (child && child.model) {
                                            info.sections.push({
                                                index: i,
                                                elType: child.model.get('elType'),
                                                widgetType: child.model.get('widgetType')
                                            });
                                        }
                                    }
                                }
                            }
                        } catch(e) {
                            info.docError = e.message;
                        }
                    }
                    
                    return info;
                }
            """)
            print(f"\n    Elementor state:")
            print(f"    {json.dumps(state, indent=2, default=str)[:2000]}")
            
            if state.get("hasDollarE"):
                # Test $e.run with a simple operation
                print("\n[3] Testing $e.run('document/elements/create')...")
                test_result = await page.evaluate("""
                    async () => {
                        try {
                            // Check if there are already sections
                            const doc = elementor.documents.getCurrent();
                            const container = doc.container;
                            const existingCount = container.children.length;
                            
                            // Create a simple section
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
                                        content_position: 'center'
                                    },
                                    elements: [{
                                        elType: 'widget',
                                        widgetType: 'heading',
                                        settings: {
                                            title: 'Test Section',
                                            header_size: 'h2',
                                            align: 'center',
                                            title_color: '#ffffff',
                                            typography_typography: 'custom',
                                            typography_font_family: 'Oswald',
                                            typography_font_size: { size: 40, unit: 'px' },
                                            typography_font_weight: '600'
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
                                existingCount: existingCount,
                                newCount: container.children.length,
                                resultType: typeof result,
                                result: result ? 'truthy' : 'falsy/null'
                            };
                        } catch(e) {
                            return {
                                success: false,
                                error: e.message,
                                stack: e.stack?.substring(0, 500)
                            };
                        }
                    }
                """)
                print(f"    {json.dumps(test_result, indent=2, default=str)[:2000]}")
                
                if test_result.get("success"):
                    await page.screenshot(path=os.path.join(savedir, "32_section_created.png"))
                    
                    # Now try to save
                    print("\n[4] Testing save...")
                    save_result = await page.evaluate("""
                        async () => {
                            try {
                                await $e.run('document/save/update');
                                return { success: true };
                            } catch(e) {
                                return { success: false, error: e.message };
                            }
                        }
                    """)
                    print(f"    {json.dumps(save_result)}")
                    
                    # Try adding a text widget
                    print("\n[5] Testing text widget...")
                    txt_result = await page.evaluate("""
                        async () => {
                            try {
                                const doc = elementor.documents.getCurrent();
                                const firstSection = doc.container.children[0];
                                const firstCol = firstSection.children[0];
                                
                                const textWidget = {
                                    elType: 'widget',
                                    widgetType: 'text-editor',
                                    settings: {
                                        editor: '<p>This is a test paragraph to verify text widget works.</p>',
                                        align: 'center',
                                        text_color: '#aaaaaa',
                                        typography_typography: 'custom',
                                        typography_font_family: 'Inter',
                                        typography_font_size: { size: 16, unit: 'px' }
                                    }
                                };
                                
                                await $e.run('document/elements/create', {
                                    container: firstCol,
                                    model: textWidget,
                                    options: { edit: false, raise: false }
                                });
                                
                                return { success: true, childCount: firstCol.children.length };
                            } catch(e) {
                                return { success: false, error: e.message };
                            }
                        }
                    """)
                    print(f"    {json.dumps(txt_result)}")
                    
                    # Try image widget
                    print("\n[6] Testing image widget...")
                    img_result = await page.evaluate("""
                        async () => {
                            try {
                                const doc = elementor.documents.getCurrent();
                                const firstSection = doc.container.children[0];
                                const firstCol = firstSection.children[0];
                                
                                const imgWidget = {
                                    elType: 'widget',
                                    widgetType: 'image',
                                    settings: {
                                        image: { url: 'https://yange14.sg-host.com/wp-content/uploads/2025/01/1.banner.jpg', id: '' },
                                        image_size: 'full',
                                        align: 'center',
                                        width: { size: 100, unit: '%' }
                                    }
                                };
                                
                                await $e.run('document/elements/create', {
                                    container: firstCol,
                                    model: imgWidget,
                                    options: { edit: false, raise: false }
                                });
                                
                                return { success: true, childCount: firstCol.children.length };
                            } catch(e) {
                                return { success: false, error: e.message };
                            }
                        }
                    """)
                    print(f"    {json.dumps(img_result)}")
                    
                    # Try button widget
                    print("\n[7] Testing button widget...")
                    btn_result = await page.evaluate("""
                        async () => {
                            try {
                                const doc = elementor.documents.getCurrent();
                                const firstSection = doc.container.children[0];
                                const firstCol = firstSection.children[0];
                                
                                const btnWidget = {
                                    elType: 'widget',
                                    widgetType: 'button',
                                    settings: {
                                        text: 'LEARN MORE',
                                        link: { url: '#' },
                                        align: 'center',
                                        button_size: 'md',
                                        background_color: '#E87C2A',
                                        button_text_color: '#ffffff',
                                        border_border: 'solid',
                                        border_color: '#E87C2A',
                                        border_width: { unit: 'px', top: '2', right: '2', bottom: '2', left: '2', isLinked: true },
                                        padding: { unit: 'px', top: '16', right: '36', bottom: '16', left: '36', isLinked: false },
                                        hover_background_color: '#c96820',
                                        hover_color: '#ffffff'
                                    }
                                };
                                
                                await $e.run('document/elements/create', {
                                    container: firstCol,
                                    model: btnWidget,
                                    options: { edit: false, raise: false }
                                });
                                
                                return { success: true, childCount: firstCol.children.length };
                            } catch(e) {
                                return { success: false, error: e.message };
                            }
                        }
                    """)
                    print(f"    {json.dumps(btn_result)}")
                    
                    await page.screenshot(path=os.path.join(savedir, "33_all_widgets.png"))
                    
                    # Test divider/counter/toggle
                    print("\n[8] Testing divider widget...")
                    div_result = await page.evaluate("""
                        async () => {
                            try {
                                const doc = elementor.documents.getCurrent();
                                const firstSection = doc.container.children[0];
                                const firstCol = firstSection.children[0];
                                
                                await $e.run('document/elements/create', {
                                    container: firstCol,
                                    model: { elType: 'widget', widgetType: 'divider', settings: {} },
                                    options: { edit: false, raise: false }
                                });
                                
                                return { success: true };
                            } catch(e) {
                                return { success: false, error: e.message };
                            }
                        }
                    """)
                    print(f"    {json.dumps(div_result)}")
                    
                    print("\n[9] Testing counter widget...")
                    counter_result = await page.evaluate("""
                        async () => {
                            try {
                                const doc = elementor.documents.getCurrent();
                                const firstSection = doc.container.children[0];
                                const firstCol = firstSection.children[0];
                                
                                await $e.run('document/elements/create', {
                                    container: firstCol,
                                    model: { elType: 'widget', widgetType: 'counter', settings: {} },
                                    options: { edit: false, raise: false }
                                });
                                
                                return { success: true };
                            } catch(e) {
                                return { success: false, error: e.message };
                            }
                        }
                    """)
                    print(f"    {json.dumps(counter_result)}")
                    
                    print("\n[10] Testing toggle (FAQ) widget...")
                    toggle_result = await page.evaluate("""
                        async () => {
                            try {
                                const doc = elementor.documents.getCurrent();
                                const firstSection = doc.container.children[0];
                                const firstCol = firstSection.children[0];
                                
                                await $e.run('document/elements/create', {
                                    container: firstCol,
                                    model: { elType: 'widget', widgetType: 'toggle', settings: {} },
                                    options: { edit: false, raise: false }
                                });
                                
                                return { success: true };
                            } catch(e) {
                                return { success: false, error: e.message };
                            }
                        }
                    """)
                    print(f"    {json.dumps(toggle_result)}")
                    
                    await page.screenshot(path=os.path.join(savedir, "34_all_done.png"))
                    
                    # Final save
                    print("\n[11] Saving all changes...")
                    final_save = await page.evaluate("""
                        async () => {
                            try {
                                await $e.run('document/save/update');
                                return { success: true };
                            } catch(e) {
                                return { success: false, error: e.message };
                            }
                        }
                    """)
                    print(f"    {json.dumps(final_save)}")
        else:
            print("    Elementor editor did NOT load")
            await page.screenshot(path=os.path.join(savedir, "35_elementor_failed.png"))
            html_preview = await page.content()
            print(f"    Page snippet: {html_preview[:500]}")
        
        await browser.close()
        print("\n[*] Done! Check screenshots folder.")

asyncio.run(main())
