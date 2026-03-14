import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        print("Navigating to goofish...")
        await page.goto("https://www.goofish.com/search?q=全自动脚本", wait_until="domcontentloaded")
        await asyncio.sleep(5)
        
        text = await page.evaluate("document.body.innerText")
        print("\n--- TEXT START ---")
        print(text[:2000]) # Print first 2000 chars of visible text
        print("--- TEXT END ---\n")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect())
