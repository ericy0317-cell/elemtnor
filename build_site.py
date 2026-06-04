# -*- coding: utf-8 -*-
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

D = {"primary": "#E87C2A", "primary_dark": "#c96820", "dark_bg": "#0d0d0d", "dark_1": "#1a1a1a", "dark_2": "#222222", "dark_3": "#2a2a2a", "dark_4": "#333333", "white": "#ffffff", "text_main": "#e8e8e8", "text_sub": "#aaaaaa", "border": "#3a3a3a", "overlay": "rgba(0,0,0,0.62)", "font_h": "Oswald", "font_b": "Inter"}

IMG = {"banner": "27", "intro": "262", "type_modular": "263", "type_portable": "264", "type_prefab": "265", "type_shipping": "266", "room_double": "267", "room_family": "268", "room_luxury": "269", "room_single": "270"}

async def run_js(page, code):
    return await page.evaluate(code)

async def create_elem(page, data, name=""):
    import json as _json
    d_str = _json.dumps(data)
    r = await page.evaluate(f"""
        async () => {{
            try {{
                const doc = elementor.documents.getCurrent();
                const c = doc.container;
                const d = {d_str};
                await .run("document/elements/create", {{ container: c, model: d, options: {{ edit: false, raise: false }} }});
                return {{ ok: true }};
            }} catch(e) {{ return {{ ok: false, error: e.message }}; }}
        }}
    """)
    ok = "OK" if r.get("ok") else "FAIL"
    print(f"  [{ok}] {name}")
    return r

async def save_pg(page):
    r = await run_js(page, """
        async () => { try { await .run("document/save/update"); return { ok: true }; } catch(e) { return { ok: false, error: e.message }; } }
    """)
    print(f"  [{'OK' if r.get('ok') else 'FAIL'}] Save")
    return r

async def clear_pg(page):
    r = await run_js(page, """
        async () => {
            try {
                const doc = elementor.documents.getCurrent();
                const c = doc.container;
                while (c.children.length > 0) {
                    await .run("document/elements/delete", { container: c.children[0] });
                }
                return { ok: true, remaining: c.children.length };
            } catch(e) { return { ok: false, error: e.message }; }
        }
    """)
    print(f"  [{'OK' if r.get('ok') else 'FAIL'}] Clear ({r.get('remaining','?')} left)")
    return r

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE, headless=False, channel="chrome",
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        page = await browser.new_page()

        print("=" * 60)
        print("STEP 1: Logging into WordPress")
        await page.goto(f"{WP_URL}/wp-login.php", wait_until="networkidle")
        if "wp-admin" not in page.url and "reauth" not in page.url:
            await page.fill("#user_login", USER)
            await page.fill("#user_pass", PASS)
            await page.click("#wp-submit")
            await page.wait_for_timeout(5000)
        await page.goto(f"{WP_URL}/wp-admin", wait_until="domcontentloaded")
        print(f"  Logged in")

        print("\nSTEP 2: Open Elementor (Page 298)")
        await page.goto(f"{WP_URL}/wp-admin/post.php?post=298&action=elementor", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(10000)
        if "elementor" not in page.url:
            print(f"  FAIL - Elementor not loaded")
            await browser.close()
            return
        print("  Elementor loaded!")

        print("\nSTEP 3: Clear existing sections")
        await clear_pg(page)
        await page.screenshot(path=os.path.join(savedir, "01_cleared.png"))

        banner_url = f"{WP_URL}/wp-content/uploads/2025/01/1.banner.jpg"

        # HERO SECTION
        hero = {"elType": "section", "settings": {"background_background": "classic", "background_color": D["dark_1"], "background_image": {"url": banner_url, "id": IMG["banner"]}, "background_position": "center center", "background_size": "cover", "background_repeat": "no-repeat", "background_overlay_background": "classic", "background_overlay_color": D["overlay"], "padding": {"unit": "px", "top": "180", "right": "40", "bottom": "180", "left": "40", "isLinked": False}, "gap": "no", "min_height": {"size": 680, "unit": "px"}, "content_position": "middle", "_element_width": "full"}, "elements": [{"elType": "column", "settings": {"_column_size": 100, "_inline_size": 100, "content_position": "center", "padding": {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": True}}, "elements": [{"elType": "widget", "widgetType": "heading", "settings": {"title": "ZN Prefab Solutions", "header_size": "span", "align": "left", "title_color": D["primary"], "typography_typography": "custom", "typography_font_family": D["font_b"], "typography_font_size": {"size": 13, "unit": "px"}, "typography_font_weight": "500", "typography_text_transform": "uppercase", "typography_letter_spacing": {"size": 4, "unit": "px"}, "border_border": "solid", "border_color": "rgba(232,124,42,0.5)", "border_width": {"unit": "px", "top": "1", "right": "1", "bottom": "1", "left": "1", "isLinked": True}, "padding": {"unit": "px", "top": "6", "right": "20", "bottom": "6", "left": "20", "isLinked": False}}}, {"elType": "widget", "widgetType": "heading", "settings": {"title": "Container Motel Buildings", "header_size": "h1", "align": "left", "title_color": D["white"], "typography_typography": "custom", "typography_font_family": D["font_h"], "typography_font_size": {"size": 62, "unit": "px"}, "typography_font_weight": "700", "typography_text_transform": "uppercase", "typography_letter_spacing": {"size": 2, "unit": "px"}, "typography_line_height": {"size": 1.1, "unit": "em"}}}, {"elType": "widget", "widgetType": "text-editor", "settings": {"editor": "Factory-built container motel units designed for fast deployment across remote sites, highways, and hospitality destinations. Durable, customizable, and cost-efficient modular solutions.", "align": "left", "text_color": "rgba(255,255,255,0.82)", "typography_typography": "custom", "typography_font_family": D["font_b"], "typography_font_size": {"size": 18, "unit": "px"}, "typography_font_weight": "400", "typography_line_height": {"size": 1.8, "unit": "em"}}}, {"elType": "section", "settings": {"gap": "no", "_element_width": "boxed", "_element_custom_width": {"size": 520, "unit": "px"}, "padding": {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": True}}, "elements": [{"elType": "column", "settings": {"_column_size": 50, "_inline_size": 50, "content_position": "center", "padding": {"unit": "px", "top": "5", "right": "8", "bottom": "5", "left": "0", "isLinked": False}}, "elements": [{"elType": "widget", "widgetType": "button", "settings": {"text": "Get A Free Quote \u203a", "link": {"url": "#"}, "align": "left", "background_color": D["primary"], "button_text_color": "#ffffff", "border_border": "solid", "border_color": D["primary"], "border_width": {"unit": "px", "top": "2", "right": "2", "bottom": "2", "left": "2", "isLinked": True}, "border_radius": {"unit": "px", "top": "4", "right": "4", "bottom": "4", "left": "4", "isLinked": True}, "padding": {"unit": "px", "top": "16", "right": "36", "bottom": "16", "left": "36", "isLinked": False}, "typography_typography": "custom", "typography_font_family": D["font_b"], "typography_font_size": {"size": 14, "unit": "px"}, "typography_font_weight": "600", "typography_text_transform": "uppercase", "typography_letter_spacing": {"size": 2, "unit": "px"}, "hover_background_color": D["primary_dark"], "hover_color": "#ffffff"}}]}, {"elType": "column", "settings": {"_column_size": 50, "_inline_size": 50, "content_position": "center", "padding": {"unit": "px", "top": "5", "right": "0", "bottom": "5", "left": "8", "isLinked": False}}, "elements": [{"elType": "widget", "widgetType": "button", "settings": {"text": "View Brochure", "link": {"url": "#"}, "align": "left", "background_color": "rgba(0,0,0,0)", "button_text_color": D["primary"], "border_border": "solid", "border_color": D["primary"], "border_width": {"unit": "px", "top": "2", "right": "2", "bottom": "2", "left": "2", "isLinked": True}, "border_radius": {"unit": "px", "top": "4", "right": "4", "bottom": "4", "left": "4", "isLinked": True}, "padding": {"unit": "px", "top": "14", "right": "32", "bottom": "14", "left": "32", "isLinked": False}, "typography_typography": "custom", "typography_font_family": D["font_b"], "typography_font_size": {"size": 14, "unit": "px"}, "typography_font_weight": "600", "typography_text_transform": "uppercase", "typography_letter_spacing": {"size": 2, "unit": "px"}, "hover_background_color": D["primary"], "hover_color": "#ffffff"}}]}]}]}]}

        print("\nSECTION 1 - Hero Banner")
        await create_elem(page, hero, "Hero")
        await save_pg(page)
        await page.screenshot(path=os.path.join(savedir, "02_hero.png"))
        print(f"\nCheck: {savedir}\\02_hero.png")

        await browser.close()

asyncio.run(main())
