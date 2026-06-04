# -*- coding: utf-8 -*-
import sys, os, json, asyncio, re
sys.stdout.reconfigure(encoding="utf-8")

from playwright.async_api import async_playwright

WP_URL = "https://yange14.sg-host.com"
USER = "243626599@qq.com"
PASS = "8008208820dhc"
PROFILE = os.path.join(os.path.dirname(__file__), "chrome_profile")
savedir = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(savedir, exist_ok=True)

# Design tokens from the demo
D = {
    "primary": "#E87C2A",
    "primary_dark": "#c96820",
    "dark_bg": "#0d0d0d",
    "dark_1": "#1a1a1a",
    "dark_2": "#222222",
    "dark_3": "#2a2a2a",
    "dark_4": "#333333",
    "white": "#ffffff",
    "text_main": "#e8e8e8",
    "text_sub": "#aaaaaa",
    "text_dark": "#333333",
    "text_muted": "#666666",
    "border": "#3a3a3a",
    "overlay": "rgba(0,0,0,0.62)",
    "font_heading": "Oswald",
    "font_body": "Inter",
}

# --- Elementor JSON builder functions ---
def sec(bg, pt=100, pb=100, width="boxed", cw=1200):
    s = {
        "elType": "section",
        "settings": {
            "background_background": "classic",
            "background_color": bg,
            "padding": {"unit": "px", "top": str(pt), "right": "0", "bottom": str(pb), "left": "0", "isLinked": False},
            "gap": "no",
            "_element_width": width,
        },
        "elements": []
    }
    if width == "boxed":
        s["settings"]["_element_custom_width"] = {"size": cw, "unit": "px"}
    return s

def col(w, bg="", pad=0, pos="center"):
    c = {
        "elType": "column",
        "settings": {
            "_column_size": int(w) if w > 1 else w,
            "_inline_size": int(w) if w > 1 else w,
            "content_position": pos,
            "padding": {"unit": "px", "top": str(pad), "right": str(pad), "bottom": str(pad), "left": str(pad), "isLinked": True} if pad else {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": True}
        },
        "elements": []
    }
    if bg:
        c["settings"]["background_background"] = "classic"
        c["settings"]["background_color"] = bg
    return c

def hdg(t, tag="h2", s=40, c="#ffffff", f="Oswald", w=600, a="center", ls=1, uc=True):
    h = {
        "elType": "widget",
        "widgetType": "heading",
        "settings": {
            "title": t,
            "header_size": tag,
            "align": a,
            "title_color": c,
            "typography_typography": "custom",
            "typography_font_family": f,
            "typography_font_size": {"size": s, "unit": "px"},
            "typography_font_weight": str(w),
            "typography_text_transform": "uppercase" if uc else "none",
        }
    }
    if ls != 0:
        h["settings"]["typography_letter_spacing"] = {"size": ls, "unit": "px"}
    return h

def txt(content, c="#aaaaaa", s=16, a="center", f="Inter"):
    return {
        "elType": "widget",
        "widgetType": "text-editor",
        "settings": {
            "editor": content,
            "align": a,
            "text_color": c,
            "typography_typography": "custom",
            "typography_font_family": f,
            "typography_font_size": {"size": s, "unit": "px"}
        }
    }

def imgw(url, img_id="", alt=""):
    return {
        "elType": "widget",
        "widgetType": "image",
        "settings": {
            "image": {"url": url, "id": str(img_id)},
            "image_size": "full",
            "align": "center",
            "width": {"size": 100, "unit": "%"}
        }
    }

def bt(t, lk="#", st="primary"):
    b = {
        "elType": "widget",
        "widgetType": "button",
        "settings": {
            "text": t,
            "link": {"url": lk},
            "align": "center",
            "button_size": "md",
            "border_border": "solid",
            "border_width": {"unit": "px", "top": "2", "right": "2", "bottom": "2", "left": "2", "isLinked": True},
            "padding": {"unit": "px", "top": "16", "right": "36", "bottom": "16", "left": "36", "isLinked": False},
            "typography_typography": "custom",
            "typography_font_family": "Inter",
            "typography_font_size": {"size": 14, "unit": "px"},
            "typography_font_weight": "600",
            "typography_text_transform": "uppercase",
            "typography_letter_spacing": {"size": 2, "unit": "px"},
        }
    }
    if st == "primary":
        b["settings"].update({
            "background_color": D["primary"],
            "button_text_color": "#ffffff",
            "border_color": D["primary"],
            "hover_background_color": D["primary_dark"],
            "hover_color": "#ffffff"
        })
    else:
        b["settings"].update({
            "background_color": "rgba(0,0,0,0)",
            "button_text_color": D["primary"],
            "border_color": D["primary"],
            "hover_background_color": D["primary"],
            "hover_color": "#ffffff"
        })
    return b

def label(t):
    return {
        "elType": "widget",
        "widgetType": "heading",
        "settings": {
            "title": t,
            "header_size": "span",
            "align": "center",
            "title_color": D["primary"],
            "typography_typography": "custom",
            "typography_font_family": "Inter",
            "typography_font_size": {"size": 13, "unit": "px"},
            "typography_font_weight": "500",
            "typography_text_transform": "uppercase",
            "typography_letter_spacing": {"size": 3, "unit": "px"},
        }
    }

async def create_section(page, section_data, section_name):
    """Create a section using Elementor API and return result"""
    result = await page.evaluate(f"""
        async () => {{
            try {{
                const doc = elementor.documents.getCurrent();
                const container = doc.container;
                const sectionData = {json.dumps(section_data)};
                const result = await $e.run('document/elements/create', {{
                    container: container,
                    model: sectionData,
                    options: {{ edit: false, raise: false }}
                }});
                return {{ success: true, childCount: container.children.length }};
            }} catch(e) {{
                return {{ success: false, error: e.message, stack: e.stack?.substring(0, 300) }};
            }}
        }}
    """)
    print(f"    {section_name}: {json.dumps(result)}")
    return result

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE,
            headless=True,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        page = await browser.new_page()

        # Step 1: Login
        print("[1] Logging in...")
        await page.goto(f"{WP_URL}/wp-login.php", wait_until="networkidle")
        if "wp-admin" not in page.url and "reauth" not in page.url:
            await page.fill("#user_login", USER)
            await page.fill("#user_pass", PASS)
            await page.click("#wp-submit")
            await page.wait_for_timeout(5000)
        await page.goto(f"{WP_URL}/wp-admin", wait_until="domcontentloaded")
        print(f"    Admin: {page.url[:80]}")

        # Step 2: Get media attachment IDs
        print("\n[2] Getting media attachment IDs...")
        await page.goto(f"{WP_URL}/wp-admin/upload.php", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        # Try REST API to get media
        nonce = await page.evaluate("""
            () => {
                const m = document.querySelector('meta[name="wp-nonce"], #_wpnonce');
                return m ? (m.content || m.value) : '';
            }
        """)
        
        media_result = await page.evaluate(f"""
            async () => {{
                try {{
                    const r = await fetch('{WP_URL}/wp-json/wp/v2/media?per_page=100');
                    const data = await r.json();
                    const items = {{}};
                    data.forEach(item => {{
                        const url = item.source_url || '';
                        const filename = url.split('/').pop();
                        items[filename] = {{ id: item.id, url: url, title: item.title?.rendered || '' }};
                    }});
                    return items;
                }} catch(e) {{
                    return {{ error: e.message }};
                }}
            }}
        """)
        
        print(f"    Media items found: {len(media_result)}")
        file_to_id = {}
        for fname, info in media_result.items():
            file_to_id[fname] = info["id"]
            print(f"      ID={info['id']}: {fname}")
        
        if not file_to_id:
            print("    No media found, checking uploads...")
            # Check wp-content/uploads
            await page.goto(f"{WP_URL}/wp-admin/upload.php", wait_until="domcontentloaded")
            content = await page.content()
            # Try parsing the table
            print(f"    Page title: {await page.title()}")
        
        # Map our image filenames to IDs
        our_images = {
            "1.banner.jpg": file_to_id.get("1.banner.jpg", ""),
            "2.jpg": file_to_id.get("2.jpg", ""),
            "4.Modular-Motel-Buildings.jpg": file_to_id.get("4.Modular-Motel-Buildings.jpg", ""),
            "4.Portable-Motel.jpg": file_to_id.get("4.Portable-Motel.jpg", ""),
            "4.Prefab-Motel.jpg": file_to_id.get("4.Prefab-Motel.jpg", ""),
            "4.Shipping-Container-Motel.jpg": file_to_id.get("4.Shipping-Container-Motel.jpg", ""),
            "5.Double Occupancy Motel Room.jpg": file_to_id.get("5.Double Occupancy Motel Room.jpg", ""),
            "5.Family-Motel-Unit.jpg": file_to_id.get("5.Family-Motel-Unit.jpg", ""),
            "5.Luxury-Modular-Motel-Suite.jpg": file_to_id.get("5.Luxury-Modular-Motel-Suite.jpg", ""),
            "5.Single-Room-Layout.jpg": file_to_id.get("5.Single-Room-Layout.jpg", ""),
        }
        print(f"\n    Mapped images: {json.dumps(our_images, indent=2)}")
        
        # Step 3: Create new page and open in Elementor
        print("\n[3] Creating new page...")
        await page.goto(f"{WP_URL}/wp-admin/post-new.php?post_type=page", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Check if Elementor panel is there
        e_btn = await page.query_selector("#elementor-switch-mode-button")
        if e_btn:
            await e_btn.click()
        else:
            # Try direct elementor URL
            await page.goto(f"{WP_URL}/wp-admin/post-new.php?post_type=page", wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(2000)
            
            # Fill title and save draft
            try:
                title_input = await page.query_selector(".editor-post-title__input, #title")
                if title_input:
                    await title_input.click()
                    await title_input.fill("Container Motel – ZN House (Container)")
            except:
                pass
            
            # Save draft
            save_btn = await page.query_selector(".editor-post-publish-button__button, #save-post, .editor-post-save-draft")
            if save_btn:
                await save_btn.click()
                await page.wait_for_timeout(3000)
            
            # Get post ID from URL
            current_url = page.url
            post_id_match = re.search(r'post=(\d+)', current_url)
            if post_id_match:
                post_id = post_id_match.group(1)
                print(f"    Post ID: {post_id}")
                
                # Open in Elementor
                await page.goto(f"{WP_URL}/wp-admin/post.php?post={post_id}&action=elementor", wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(10000)
                
                if "elementor" in page.url:
                    print("    Elementor editor loaded!")
                    await page.wait_for_timeout(5000)
                    await page.screenshot(path=os.path.join(savedir, "40_elementor_empty.png"))
                else:
                    print(f"    Elementor not loaded: {page.url[:100]}")
                    await browser.close()
                    return False
        
        # Step 4: Build SECTION 1 - HERO BANNER
        print("\n[4] Building Section 1 - Hero Banner...")
        
        banner_url = f"{WP_URL}/wp-content/uploads/2025/01/1.banner.jpg" if our_images.get("1.banner.jpg") else ""
        banner_id = our_images.get("1.banner.jpg", "")
        
        # Hero section - full width background with overlay
        hero_section = {
            "elType": "section",
            "settings": {
                "background_background": "classic",
                "background_color": D["dark_1"],
                "background_image": {"url": banner_url, "id": str(banner_id)},
                "background_position": "center center",
                "background_size": "cover",
                "background_overlay_background": "classic",
                "background_overlay_color": D["overlay"],
                "padding": {"unit": "px", "top": "180", "right": "0", "bottom": "180", "left": "0", "isLinked": False},
                "gap": "no",
                "min_height": {"size": 680, "unit": "px"},
                "_element_width": "full",
                "content_position": "middle",
            },
            "elements": [
                col(100, pad=20, pos="center"),
            ]
        }
        
        # Add widgets to hero column
        hero_col = hero_section["elements"][0]
        
        # Label
        hero_col["elements"].append(label("BUILD WITH CONTAINERS"))
        
        # Main heading
        hero_col["elements"].append(hdg(
            "Container Motel<br>Buildings",
            tag="h1", s=56, c=D["white"], f="Oswald", w=700, a="center", ls=1
        ))
        
        # Description
        hero_col["elements"].append(txt(
            "Premium modular container motel buildings engineered for fast deployment,<br>superior durability, and exceptional guest experience worldwide.",
            c="rgba(255,255,255,0.80)", s=18, a="center"
        ))
        
        # Buttons container column
        hero_col["elements"].append({
            "elType": "widget",
            "widgetType": "button",
            "settings": {
                "text": "REQUEST A QUOTE ›",
                "link": {"url": "#"},
                "align": "center",
                "button_size": "md",
                "background_color": D["primary"],
                "button_text_color": "#ffffff",
                "border_border": "solid",
                "border_color": D["primary"],
                "border_width": {"unit": "px", "top": "2", "right": "2", "bottom": "2", "left": "2", "isLinked": True},
                "padding": {"unit": "px", "top": "16", "right": "36", "bottom": "16", "left": "36", "isLinked": False},
                "typography_typography": "custom",
                "typography_font_family": "Inter",
                "typography_font_size": {"size": 14, "unit": "px"},
                "typography_font_weight": "600",
                "typography_text_transform": "uppercase",
                "typography_letter_spacing": {"size": 2, "unit": "px"},
                "hover_background_color": D["primary_dark"],
                "hover_color": "#ffffff"
            }
        })
        
        r1 = await create_section(page, hero_section, "Hero Banner")
        if r1.get("success"):
            await page.screenshot(path=os.path.join(savedir, "41_section1_hero.png"))
        
        # Save
        save_result = await page.evaluate("""
            async () => {
                try { await $e.run('document/save/update'); return { success: true }; }
                catch(e) { return { success: false, error: e.message }; }
            }
        """)
        print(f"    Save: {json.dumps(save_result)}")
        
        print("\n[*] Section 1 complete! Check screenshot.")
        await browser.close()
        return True

asyncio.run(main())
