import asyncio
from playwright.async_api import async_playwright

async def test_msg_click():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir="./xianyu_auth_context",
            headless=True,
            viewport={'width': 1280, 'height': 800}
        )
        page = context.pages[0] if context.pages else await context.new_page()
        
        print("Navigating to Goofish...")
        await page.goto("https://www.goofish.com", wait_until="domcontentloaded")
        await asyncio.sleep(5)
        
        print("Attempting to find '消息' text...")
        try:
            # Look for elements containing "消息"
            msg_element = page.locator("text=消息").first
            is_visible = await msg_element.is_visible()
            print(f"'消息' element visible: {is_visible}")
            
            if is_visible:
                print("Clicking '消息'...")
                await msg_element.click()
                await asyncio.sleep(4)
                await page.screenshot(path="after_msg_click.png", full_page=True)
                print("Screenshot saved to after_msg_click.png")
            else:
                print("Could not find a visible '消息' element.")
        except Exception as e:
            print(f"Error finding or clicking: {e}")
            
        await context.close()

if __name__ == "__main__":
    asyncio.run(test_msg_click())
