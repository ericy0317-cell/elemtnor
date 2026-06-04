# -*- coding: utf-8 -*-
"""Build Section 1 - Hero Banner for Container Motel page (fixed version)"""
import sys, os, json, asyncio
sys.stdout.reconfigure(encoding="utf-8")

from playwright.async_api import async_playwright

WP_URL = "https://yange14.sg-host.com"
USER = "243626599@qq.com"
PASS = "8008208820dhc"
BASE = os.path.dirname(os.path.abspath(__file__))
PROFILE = os.path.join(BASE, "chrome_profile")
savedir = os.path.join(BASE, "screenshots")
os.makedirs(savedir, exist_ok=True)

D = {
    "primary": "#E87C2A", "primary_dark": "#c96820",
    "dark_bg": "#0d0d0d", "dark_1": "#1a1a1a", "dark_2": "#222222",
    "dark_3": "#2a2a2a",
    "white": "#ffffff", "text_main": "#e8e8e8", "text_sub": "#aaaaaa",
    "border": "#3a3a3a", "overlay": "rgba(0,0,0,0.62)",
    "font_h": "Oswald", "font_b": "Inter",
}

BANNER_ID = 27

async def run_js(page, code, name=""):
    try:
        r = await page.evaluate(code)
        ok_str = "OK" if r.get("ok") else "FAIL"
        print(f"  [{ok_str}] {name}: {json.dumps(r, ensure_ascii=False)[:200]}")
        return r
    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
        return {"ok": False, "error": str(e)}

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE, headless=True, channel="chrome",
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        page = await browser.new_page()
        page.set_default_timeout(45000)

        print("=" * 60)
        print("STEP 1: Login to WordPress")
        print("=" * 60)
        await page.goto(f"{WP_URL}/wp-login.php", wait_until="networkidle")
        if "wp-admin" not in page.url:
            await page.fill("#user_login", USER)
            await page.fill("#user_pass", PASS)
            await page.click("#wp-submit")
            await page.wait_for_timeout(5000)
        await page.goto(f"{WP_URL}/wp-admin", wait_until="domcontentloaded")
        print(f"  Admin URL: {page.url[:80]}")

        print("\n" + "=" * 60)
        print("STEP 2: Open Page in Elementor Editor")
        print("=" * 60)
        await page.goto(f"{WP_URL}/wp-admin/post.php?post=298&action=elementor",
                        wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(8000)

        if "elementor" not in page.url:
            print(f"  FAIL - Not Elementor. URL: {page.url[:100]}")
            await page.screenshot(path=os.path.join(savedir, "error_not_loaded.png"))
            await browser.close()
            return
        print("  Elementor loaded!")
        await page.screenshot(path=os.path.join(savedir, "00_editor_loaded.png"))

        # Clear existing content
        print("\n" + "=" * 60)
        print("STEP 3: Clear existing sections")
        print("=" * 60)
        await run_js(page, """
            async () => {
                try {
                    const doc = elementor.documents.getCurrent();
                    const c = doc.container;
                    while (c.children.length > 0) {
                        await $e.run("document/elements/delete", { container: c.children[0] });
                    }
                    return { ok: true, remaining: c.children.length };
                } catch(e) { return { ok: false, error: e.message }; }
            }
        """, "Clear all")
        await page.screenshot(path=os.path.join(savedir, "01_cleared.png"))

        # Build hero section
        print("\n" + "=" * 60)
        print("STEP 4: Build Hero Section")
        print("=" * 60)

        hero_data = {
            "elType": "section",
            "settings": {
                "background_background": "classic",
                "background_color": D["dark_1"],
                "background_image": {"url": f"{WP_URL}/wp-content/uploads/2025/01/1.banner.jpg", "id": BANNER_ID},
                "background_position": "center center",
                "background_size": "cover",
                "background_repeat": "no-repeat",
                "background_overlay_background": "classic",
                "background_overlay_color": "rgba(0,0,0,0.62)",
                "min_height": {"size": 680, "unit": "px"},
                "content_position": "middle",
                "padding": {"unit": "px", "top": "180", "right": "40", "bottom": "140", "left": "40", "isLinked": False},
                "gap": "no",
                "_element_width": "full",
            },
            "elements": [
                {
                    "elType": "column",
                    "settings": {
                        "_column_size": 100,
                        "_inline_size": 100,
                        "content_position": "center",
                        "padding": {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": True},
                    },
                    "elements": [
                        # Eyebrow label
                        {
                            "elType": "widget",
                            "widgetType": "heading",
                            "settings": {
                                "title": "ZN PREFAB SOLUTIONS",
                                "header_size": "span",
                                "align": "left",
                                "title_color": D["primary"],
                                "typography_typography": "custom",
                                "typography_font_family": "Inter",
                                "typography_font_size": {"size": 13, "unit": "px"},
                                "typography_font_weight": "500",
                                "typography_text_transform": "uppercase",
                                "typography_letter_spacing": {"size": 4, "unit": "px"},
                                "typography_line_height": {"size": 1, "unit": "em"},
                                "border_border": "solid",
                                "border_color": "rgba(232,124,42,0.35)",
                                "border_width": {"unit": "px", "top": "1", "right": "1", "bottom": "1", "left": "1", "isLinked": True},
                                "border_radius": {"unit": "px", "top": "4", "right": "4", "bottom": "4", "left": "4", "isLinked": True},
                                "padding": {"unit": "px", "top": "6", "right": "20", "bottom": "6", "left": "20", "isLinked": False},
                                "margin": {"unit": "px", "top": "0", "right": "0", "bottom": "18", "left": "0", "isLinked": False},
                            }
                        },
                        # Main title with orange "Motel"
                        {
                            "elType": "widget",
                            "widgetType": "heading",
                            "settings": {
                                "title": 'Container <span style="color:#E87C2A;">Motel</span> Buildings',
                                "header_size": "h1",
                                "align": "left",
                                "title_color": D["white"],
                                "typography_typography": "custom",
                                "typography_font_family": "Oswald",
                                "typography_font_size": {"size": 62, "unit": "px"},
                                "typography_font_weight": "700",
                                "typography_text_transform": "uppercase",
                                "typography_letter_spacing": {"size": 2, "unit": "px"},
                                "typography_line_height": {"size": 1.1, "unit": "em"},
                                "margin": {"unit": "px", "top": "0", "right": "0", "bottom": "20", "left": "0", "isLinked": False},
                            }
                        },
                        # Description text
                        {
                            "elType": "widget",
                            "widgetType": "text-editor",
                            "settings": {
                                "editor": "Factory-built container motel units designed for fast deployment across remote sites, highways, and hospitality destinations. Durable, customizable, and cost-efficient modular solutions.",
                                "align": "left",
                                "text_color": "rgba(255,255,255,0.82)",
                                "typography_typography": "custom",
                                "typography_font_family": "Inter",
                                "typography_font_size": {"size": 18, "unit": "px"},
                                "typography_font_weight": "400",
                                "typography_line_height": {"size": 1.8, "unit": "em"},
                                "margin": {"unit": "px", "top": "0", "right": "0", "bottom": "30", "left": "0", "isLinked": False},
                            }
                        },
                        # Inner section for buttons
                        {
                            "elType": "section",
                            "settings": {
                                "gap": "no",
                                "_element_width": "boxed",
                                "_element_custom_width": {"size": 520, "unit": "px"},
                                "padding": {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": True},
                                "margin": {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": False},
                                "background_background": "",
                            },
                            "elements": [
                                {
                                    "elType": "column",
                                    "settings": {
                                        "_column_size": 50,
                                        "_inline_size": 50,
                                        "content_position": "center",
                                        "padding": {"unit": "px", "top": "5", "right": "8", "bottom": "5", "left": "0", "isLinked": False},
                                    },
                                    "elements": [
                                        {
                                            "elType": "widget",
                                            "widgetType": "button",
                                            "settings": {
                                                "text": "Get A Free Quote \u203a",
                                                "link": {"url": "#"},
                                                "align": "left",
                                                "button_size": "custom",
                                                "background_color": D["primary"],
                                                "button_text_color": D["white"],
                                                "border_border": "solid",
                                                "border_color": D["primary"],
                                                "border_width": {"unit": "px", "top": "2", "right": "2", "bottom": "2", "left": "2", "isLinked": True},
                                                "border_radius": {"unit": "px", "top": "4", "right": "4", "bottom": "4", "left": "4", "isLinked": True},
                                                "padding": {"unit": "px", "top": "14", "right": "32", "bottom": "14", "left": "32", "isLinked": False},
                                                "typography_typography": "custom",
                                                "typography_font_family": "Inter",
                                                "typography_font_size": {"size": 14, "unit": "px"},
                                                "typography_font_weight": "600",
                                                "typography_text_transform": "uppercase",
                                                "typography_letter_spacing": {"size": 2, "unit": "px"},
                                                "hover_background_color": D["primary_dark"],
                                                "hover_color": D["white"],
                                                "hover_border_color": D["primary_dark"],
                                            }
                                        }
                                    ]
                                },
                                {
                                    "elType": "column",
                                    "settings": {
                                        "_column_size": 50,
                                        "_inline_size": 50,
                                        "content_position": "center",
                                        "padding": {"unit": "px", "top": "5", "right": "0", "bottom": "5", "left": "8", "isLinked": False},
                                    },
                                    "elements": [
                                        {
                                            "elType": "widget",
                                            "widgetType": "button",
                                            "settings": {
                                                "text": "View Brochure",
                                                "link": {"url": "#"},
                                                "align": "left",
                                                "button_size": "custom",
                                                "background_color": "rgba(0,0,0,0)",
                                                "button_text_color": D["primary"],
                                                "border_border": "solid",
                                                "border_color": D["primary"],
                                                "border_width": {"unit": "px", "top": "2", "right": "2", "bottom": "2", "left": "2", "isLinked": True},
                                                "border_radius": {"unit": "px", "top": "4", "right": "4", "bottom": "4", "left": "4", "isLinked": True},
                                                "padding": {"unit": "px", "top": "14", "right": "32", "bottom": "14", "left": "32", "isLinked": False},
                                                "typography_typography": "custom",
                                                "typography_font_family": "Inter",
                                                "typography_font_size": {"size": 14, "unit": "px"},
                                                "typography_font_weight": "600",
                                                "typography_text_transform": "uppercase",
                                                "typography_letter_spacing": {"size": 2, "unit": "px"},
                                                "hover_background_color": D["primary"],
                                                "hover_color": D["white"],
                                                "hover_border_color": D["primary"],
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        result = await run_js(page, f"""
            async () => {{
                try {{
                    const doc = elementor.documents.getCurrent();
                    const c = doc.container;
                    const d = {json.dumps(hero_data)};
                    await $e.run("document/elements/create", {{
                        container: c,
                        model: d,
                        options: {{ edit: false, raise: false }}
                    }});
                    return {{ ok: true, childCount: c.children.length }};
                }} catch(e) {{
                    return {{ ok: false, error: e.message, stack: e.stack?.substring(0,300) }};
                }}
            }}
        """, "Create Hero Section")

        await page.screenshot(path=os.path.join(savedir, "02_hero_built.png"))
        await page.wait_for_timeout(2000)

        # Save
        print("\n" + "=" * 60)
        print("STEP 5: Save and Publish")
        print("=" * 60)
        await run_js(page, """
            async () => {
                try {
                    await $e.run("document/save/update");
                    await $e.run("document/save/publish");
                    return { ok: true };
                } catch(e) { return { ok: false, error: e.message }; }
            }
        """, "Save & Publish")

        await page.wait_for_timeout(3000)

        # Check frontend
        print("\n" + "=" * 60)
        print("STEP 6: Check Frontend")
        print("=" * 60)
        await page.goto(f"{WP_URL}/?page_id=298&t={int(asyncio.get_event_loop().time())}",
                        wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path=os.path.join(savedir, "03_frontend.png"), full_page=True)
        print(f"  Frontend screenshot saved")

        print("\n" + "=" * 60)
        print("DONE!")
        print(f"Screenshots in: {savedir}")
        print("=" * 60)

        await browser.close()

asyncio.run(main())
