import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        c = await b.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        page = await c.new_page()
        print("Goto URL...")
        await page.goto('https://v.douyin.com/MV0gw4XWdeY/')
        print("Wait for page to load...")
        # Wait a bit for JS to run and render the video tag
        try:
            # wait for network idle to ensure video is loaded
            await page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass
            
        try:
            # Douyin videos often use <video><source src="..."></video>
            src = await page.evaluate('''() => {
                let v = document.querySelector("video source");
                if (v) return v.src;
                let v2 = document.querySelector("video");
                if (v2) return v2.src;
                return "";
            }''')
            print('Video SRC:', src)
        except Exception as e:
            print('Error:', e)
        await b.close()

asyncio.run(run())
