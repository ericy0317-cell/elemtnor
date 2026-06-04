# -*- coding: utf-8 -*-
import sys, os, json, asyncio
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

WP_URL = 'https://yange14.sg-host.com'
PROFILE = os.path.join('D:\\建站', 'chrome_profile')
savedir = os.path.join('D:\\建站', 'screenshots')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE, headless=True, channel='chrome',
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        page = await browser.new_page()
        
        print('Checking frontend...')
        await page.goto(f'{WP_URL}/?p=298', wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path=os.path.join(savedir, 'current_frontend.png'))
        
        title = await page.title()
        print(f'Title: {title}')
        
        info = await page.evaluate("""
            () => {
                const sections = document.querySelectorAll('section');
                const arr = [];
                sections.forEach((s, i) => {
                    const bg = window.getComputedStyle(s).backgroundImage;
                    const h = s.querySelector('h1, h2, h3');
                    const imgs = s.querySelectorAll('img');
                    arr.push({
                        idx: i,
                        bg: bg && bg !== 'none' ? bg.substring(0,80) : 'none',
                        heading: h ? h.textContent.substring(0,60) : 'none',
                        h: s.offsetHeight,
                        imgs: imgs.length
                    });
                });
                return arr;
            }
        """)
        print(f'Sections: {json.dumps(info, ensure_ascii=False)[:800]}')
        
        await browser.close()

asyncio.run(main())
