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

D = {
    "primary": "#E87C2A", "primary_dark": "#c96820",
    "dark_bg": "#0d0d0d", "dark_1": "#1a1a1a", "dark_2": "#222222", "dark_3": "#2a2a2a",
    "white": "#ffffff", "text_sub": "#aaaaaa", "overlay": "rgba(0,0,0,0.62)",
    "font_h": "Oswald", "font_b": "Inter",
}

IMAGES = {
    "1.banner.jpg": 27, "2.jpg": 262,
    "4.Modular-Motel-Buildings.jpg": 263, "4.Portable-Motel.jpg": 264,
    "4.Prefab-Motel.jpg": 265, "4.Shipping-Container-Motel.jpg": 266,
    "5.Double Occupancy Motel Room.jpg": 267, "5.Family-Motel-Unit.jpg": 268,
    "5.Luxury-Modular-Motel-Suite.jpg": 269, "5.Single-Room-Layout.jpg": 270,
}

async def e_run(page, code):
    return await page.evaluate(code)

async def clear_all(page):
    return await e_run(page, """
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
    """)

async def sec_create(page, data, name):
    r = await e_run(page, f"""
        async () => {{
            try {{
                const doc = elementor.documents.getCurrent();
                const c = doc.container;
                const d = {json.dumps(data)};
                await $e.run("document/elements/create", {{ container: c, model: d, options: {{ edit: false, raise: false }} }});
                return {{ ok: true, cnt: c.children.length }};
            }} catch(e) {{ return {{ ok: false, error: e.message }}; }}
        }}
    """)
    ok = "OK" if r.get("ok") else "FAIL"
    print(f"  [{ok}] {name}")
    if not r.get("ok"): print(f"    Error: {r.get('error','')}")
    return r

async def w_create(page, container_selector, data, name):
    """Create a widget inside a specific container (section index, column index)"""
    r = await e_run(page, f"""
        async () => {{
            try {{
                const doc = elementor.documents.getCurrent();
                const c = doc.container;
                const target = {container_selector};
                const d = {json.dumps(data)};
                await $e.run("document/elements/create", {{ container: target, model: d, options: {{ edit: false, raise: false }} }});
                return {{ ok: true }};
            }} catch(e) {{ return {{ ok: false, error: e.message }}; }}
        }}
    """)
    ok = "OK" if r.get("ok") else "FAIL"
    print(f"  [{ok}] {name}")
    return r

async def save(page):
    r = await e_run(page, """
        async () => {
            try { await $e.run("document/save/update"); return { ok: true }; }
            catch(e) { return { ok: false, error: e.message }; }
        }
    """)
    return r

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE, headless=True, channel="chrome",
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        page = await browser.new_page()

        # Login
        print("[1] Login...")
        await page.goto(f"{WP_URL}/wp-login.php", wait_until="networkidle")
        if "wp-admin" not in page.url and "reauth" not in page.url:
            await page.fill("#user_login", USER)
            await page.fill("#user_pass", PASS)
            await page.click("#wp-submit")
            await page.wait_for_timeout(5000)
        await page.goto(f"{WP_URL}/wp-admin", wait_until="domcontentloaded")

        # Open page 298 in Elementor
        print("[2] Open Elementor editor...")
        await page.goto(f"{WP_URL}/wp-admin/post.php?post=298&action=elementor", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(8000)
        if "elementor" not in page.url:
            print("  FAIL - Elementor not loaded"); await browser.close(); return

        # Clear
        print("  Clear existing:", json.dumps(await clear_all(page)))

        # ====================================================================
        # SECTION 1 - HERO BANNER
        # ====================================================================
        print("\n[3] SECTION 1 - Hero Banner...")
        banner_url = f"{WP_URL}/wp-content/uploads/2025/01/1.banner.jpg"

        # Main hero section: full width, background image + overlay
        hero = {
            "elType": "section",
            "settings": {
                "background_background": "classic",
                "background_color": D["dark_1"],
                "background_image": {"url": banner_url, "id": str(IMAGES["1.banner.jpg"])},
                "background_position": "center center",
                "background_size": "cover",
                "background_overlay_background": "classic",
                "background_overlay_color": D["overlay"],
                "padding": {"unit": "px", "top": "120", "right": "40", "bottom": "100", "left": "40", "isLinked": False},
                "gap": "no",
                "min_height": {"size": 680, "unit": "px"},
                "_element_width": "full",
                "content_position": "middle",
            },
            "elements": [
                {
                    "elType": "column",
                    "settings": {
                        "_column_size": 100, "_inline_size": 100,
                        "content_position": "center",
                        "padding": {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": False}
                    },
                    "elements": [
                        # Eyebrow label
                        {"elType": "widget", "widgetType": "heading", "settings": {
                            "title": "BUILD WITH CONTAINERS",
                            "header_size": "span", "align": "left",
                            "title_color": D["primary"],
                            "typography_typography": "custom",
                            "typography_font_family": D["font_b"],
                            "typography_font_size": {"size": 13, "unit": "px"},
                            "typography_font_weight": "500",
                            "typography_text_transform": "uppercase",
                            "typography_letter_spacing": {"size": 4, "unit": "px"},
                            "background_background": "classic",
                            "background_color": "#FFFFFF00",
                            "border_border": "solid",
                            "border_color": "rgba(232,124,42,0.5)",
                            "border_width": {"unit": "px", "top": "1", "right": "1", "bottom": "1", "left": "1", "isLinked": True},
                            "padding": {"unit": "px", "top": "6", "right": "20", "bottom": "6", "left": "20", "isLinked": False},
                        }},
                        # Main title: 62px Oswald 700, uppercase, letter-spacing 1px
                        {"elType": "widget", "widgetType": "heading", "settings": {
                            "title": "Container Motel Buildings",
                            "header_size": "h1", "align": "left",
                            "title_color": D["white"],
                            "typography_typography": "custom",
                            "typography_font_family": D["font_h"],
                            "typography_font_size": {"size": 62, "unit": "px"},
                            "typography_font_weight": "700",
                            "typography_text_transform": "uppercase",
                            "typography_letter_spacing": {"size": 1, "unit": "px"},
                        }},
                        # Description
                        {"elType": "widget", "widgetType": "text-editor", "settings": {
                            "editor": "Premium modular container motel buildings engineered for fast deployment,<br>superior durability, and exceptional guest experience worldwide.",
                            "align": "left",
                            "text_color": "rgba(255,255,255,0.80)",
                            "typography_typography": "custom",
                            "typography_font_family": D["font_b"],
                            "typography_font_size": {"size": 17, "unit": "px"},
                        }},
                        # Inner section for two buttons side by side
                        {
                            "elType": "section",
                            "settings": {
                                "gap": "no",
                                "_element_width": "boxed",
                                "padding": {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": False}
                            },
                            "elements": [
                                # Column 1 - Primary button
                                {
                                    "elType": "column",
                                    "settings": {
                                        "_column_size": 50, "_inline_size": 50,
                                        "content_position": "center",
                                        "padding": {"unit": "px", "top": "0", "right": "8", "bottom": "0", "left": "0", "isLinked": False}
                                    },
                                    "elements": [
                                        {"elType": "widget", "widgetType": "button", "settings": {
                                            "text": "Get A Free Quote ›",
                                            "link": {"url": "#"},
                                            "align": "left",
                                            "button_size": "md",
                                            "background_color": D["primary"],
                                            "button_text_color": "#ffffff",
                                            "border_border": "solid",
                                            "border_color": D["primary"],
                                            "border_width": {"unit": "px", "top": "2", "right": "2", "bottom": "2", "left": "2", "isLinked": True},
                                            "padding": {"unit": "px", "top": "16", "right": "36", "bottom": "16", "left": "36", "isLinked": False},
                                            "typography_typography": "custom",
                                            "typography_font_family": D["font_b"],
                                            "typography_font_size": {"size": 14, "unit": "px"},
                                            "typography_font_weight": "600",
                                            "typography_text_transform": "uppercase",
                                            "typography_letter_spacing": {"size": 2, "unit": "px"},
                                            "hover_background_color": D["primary_dark"],
                                            "hover_color": "#ffffff",
                                        }}
                                    ]
                                },
                                # Column 2 - Outline button
                                {
                                    "elType": "column",
                                    "settings": {
                                        "_column_size": 50, "_inline_size": 50,
                                        "content_position": "center",
                                        "padding": {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "8", "isLinked": False}
                                    },
                                    "elements": [
                                        {"elType": "widget", "widgetType": "button", "settings": {
                                            "text": "View Brochure",
                                            "link": {"url": "#"},
                                            "align": "left",
                                            "button_size": "md",
                                            "background_color": "rgba(0,0,0,0)",
                                            "button_text_color": D["primary"],
                                            "border_border": "solid",
                                            "border_color": D["primary"],
                                            "border_width": {"unit": "px", "top": "2", "right": "2", "bottom": "2", "left": "2", "isLinked": True},
                                            "padding": {"unit": "px", "top": "14", "right": "32", "bottom": "14", "left": "32", "isLinked": False},
                                            "typography_typography": "custom",
                                            "typography_font_family": D["font_b"],
                                            "typography_font_size": {"size": 14, "unit": "px"},
                                            "typography_font_weight": "600",
                                            "typography_text_transform": "uppercase",
                                            "typography_letter_spacing": {"size": 2, "unit": "px"},
                                            "hover_background_color": D["primary"],
                                            "hover_color": "#ffffff",
                                        }}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        await sec_create(page, hero, "Hero Banner")
        await save(page)
        await page.screenshot(path=os.path.join(savedir, "52_hero_fixed.png"))

        # ====================================================================
        # SECTION 2 - WHY CHOOSE US
        # ====================================================================
        print("\n[4] SECTION 2 - Why Choose Us...")

        why = {
            "elType": "section",
            "settings": {
                "background_background": "classic",
                "background_color": D["dark_2"],
                "padding": {"unit": "px", "top": "100", "right": "0", "bottom": "100", "left": "0", "isLinked": False},
                "gap": "no",
                "_element_width": "boxed",
                "_element_custom_width": {"size": 1200, "unit": "px"},
            },
            "elements": [
                # Header column (100%)
                {
                    "elType": "column",
                    "settings": {
                        "_column_size": 100, "_inline_size": 100,
                        "content_position": "center",
                        "padding": {"unit": "px", "top": "0", "right": "20", "bottom": "0", "left": "20", "isLinked": False}
                    },
                    "elements": [
                        {"elType": "widget", "widgetType": "heading", "settings": {
                            "title": "WHY CHOOSE US",
                            "header_size": "span", "align": "center",
                            "title_color": D["primary"],
                            "typography_typography": "custom",
                            "typography_font_family": D["font_b"],
                            "typography_font_size": {"size": 13, "unit": "px"},
                            "typography_font_weight": "500",
                            "typography_text_transform": "uppercase",
                            "typography_letter_spacing": {"size": 3, "unit": "px"},
                        }},
                        {"elType": "widget", "widgetType": "heading", "settings": {
                            "title": "Why Choose Container Motel Buildings?",
                            "header_size": "h2", "align": "center",
                            "title_color": D["white"],
                            "typography_typography": "custom",
                            "typography_font_family": D["font_h"],
                            "typography_font_size": {"size": 40, "unit": "px"},
                            "typography_font_weight": "600",
                            "typography_text_transform": "uppercase",
                            "typography_letter_spacing": {"size": 1, "unit": "px"},
                        }},
                        {"elType": "widget", "widgetType": "text-editor", "settings": {
                            "editor": "Our container motel buildings combine industrial strength with modern design, delivering exceptional value for hospitality investors worldwide.",
                            "align": "center",
                            "text_color": D["text_sub"],
                            "typography_typography": "custom",
                            "typography_font_family": D["font_b"],
                            "typography_font_size": {"size": 16, "unit": "px"},
                        }},
                    ]
                },
                # Card column 1
                {
                    "elType": "column",
                    "settings": {
                        "_column_size": 25, "_inline_size": 25,
                        "content_position": "top",
                        "background_background": "classic",
                        "background_color": D["dark_3"],
                        "padding": {"unit": "px", "top": "32", "right": "24", "bottom": "32", "left": "24", "isLinked": False},
                        "border_radius": {"unit": "px", "top": "8", "right": "8", "bottom": "8", "left": "8", "isLinked": True},
                    },
                    "elements": [
                        {"elType": "widget", "widgetType": "heading", "settings": {
                            "title": "Rapid Construction",
                            "header_size": "h3", "align": "center",
                            "title_color": D["white"],
                            "typography_typography": "custom",
                            "typography_font_family": D["font_h"],
                            "typography_font_size": {"size": 22, "unit": "px"},
                            "typography_font_weight": "600",
                        }},
                        {"elType": "widget", "widgetType": "text-editor", "settings": {
                            "editor": "Complete a 20-room motel in just 7–14 days — 90% faster than conventional building methods.",
                            "align": "center",
                            "text_color": D["text_sub"],
                            "typography_typography": "custom",
                            "typography_font_family": D["font_b"],
                            "typography_font_size": {"size": 14, "unit": "px"},
                        }},
                    ]
                },
                # Card column 2
                {
                    "elType": "column",
                    "settings": {
                        "_column_size": 25, "_inline_size": 25,
                        "content_position": "top",
                        "background_background": "classic",
                        "background_color": D["dark_3"],
                        "padding": {"unit": "px", "top": "32", "right": "24", "bottom": "32", "left": "24", "isLinked": False},
                        "border_radius": {"unit": "px", "top": "8", "right": "8", "bottom": "8", "left": "8", "isLinked": True},
                    },
                    "elements": [
                        {"elType": "widget", "widgetType": "heading", "settings": {
                            "title": "Cost Effective",
                            "header_size": "h3", "align": "center",
                            "title_color": D["white"],
                            "typography_typography": "custom",
                            "typography_font_family": D["font_h"],
                            "typography_font_size": {"size": 22, "unit": "px"},
                            "typography_font_weight": "600",
                        }},
                        {"elType": "widget", "widgetType": "text-editor", "settings": {
                            "editor": "Save 30–40% on construction costs compared to traditional motel builds, with predictable pricing.",
                            "align": "center",
                            "text_color": D["text_sub"],
                            "typography_typography": "custom",
                            "typography_font_family": D["font_b"],
                            "typography_font_size": {"size": 14, "unit": "px"},
                        }},
                    ]
                },
                # Card column 3
                {
                    "elType": "column",
                    "settings": {
                        "_column_size": 25, "_inline_size": 25,
                        "content_position": "top",
                        "background_background": "classic",
                        "background_color": D["dark_3"],
                        "padding": {"unit": "px", "top": "32", "right": "24", "bottom": "32", "left": "24", "isLinked": False},
                        "border_radius": {"unit": "px", "top": "8", "right": "8", "bottom": "8", "left": "8", "isLinked": True},
                    },
                    "elements": [
                        {"elType": "widget", "widgetType": "heading", "settings": {
                            "title": "Global Standards",
                            "header_size": "h3", "align": "center",
                            "title_color": D["white"],
                            "typography_typography": "custom",
                            "typography_font_family": D["font_h"],
                            "typography_font_size": {"size": 22, "unit": "px"},
                            "typography_font_weight": "600",
                        }},
                        {"elType": "widget", "widgetType": "text-editor", "settings": {
                            "editor": "ISO & CE certified. Engineered for international building codes across Australia, USA, Middle East & Asia.",
                            "align": "center",
                            "text_color": D["text_sub"],
                            "typography_typography": "custom",
                            "typography_font_family": D["font_b"],
                            "typography_font_size": {"size": 14, "unit": "px"},
                        }},
                    ]
                },
                # Card column 4
                {
                    "elType": "column",
                    "settings": {
                        "_column_size": 25, "_inline_size": 25,
                        "content_position": "top",
                        "background_background": "classic",
                        "background_color": D["dark_3"],
                        "padding": {"unit": "px", "top": "32", "right": "24", "bottom": "32", "left": "24", "isLinked": False},
                        "border_radius": {"unit": "px", "top": "8", "right": "8", "bottom": "8", "left": "8", "isLinked": True},
                    },
                    "elements": [
                        {"elType": "widget", "widgetType": "heading", "settings": {
                            "title": "Eco-Friendly",
                            "header_size": "h3", "align": "center",
                            "title_color": D["white"],
                            "typography_typography": "custom",
                            "typography_font_family": D["font_h"],
                            "typography_font_size": {"size": 22, "unit": "px"},
                            "typography_font_weight": "600",
                        }},
                        {"elType": "widget", "widgetType": "text-editor", "settings": {
                            "editor": "Recycled steel structure. 70% less waste. Energy-efficient design reduces operational costs.",
                            "align": "center",
                            "text_color": D["text_sub"],
                            "typography_typography": "custom",
                            "typography_font_family": D["font_b"],
                            "typography_font_size": {"size": 14, "unit": "px"},
                        }},
                    ]
                },
            ]
        }

        await sec_create(page, why, "Why Choose Us")
        await save(page)
        await page.screenshot(path=os.path.join(savedir, "53_why_choose.png"))

        print("\n[*] Sections 1-2 complete! Check screenshots.")
        await browser.close()

asyncio.run(main())
