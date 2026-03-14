import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        c = await b.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        page = await c.new_page()
        
        target_video_url = None
        
        async def handle_response(response):
            nonlocal target_video_url
            if "aweme/detail/" in response.url or "aweme/post/" in response.url or "iteminfo/" in response.url:
                try:
                    data = await response.json()
                    # print("Intercepted API:", response.url)
                    
                    if "aweme_detail" in data:
                        video_info = data["aweme_detail"].get("video", {})
                        play_addr = video_info.get("play_addr", {}).get("url_list", [])
                        if play_addr:
                            target_video_url = play_addr[0]
                            print("FOUND NO-WM URL IN DETAIL:", target_video_url)
                    elif "item_list" in data and len(data["item_list"]) > 0:
                        video_info = data["item_list"][0].get("video", {})
                        play_addr = video_info.get("play_addr", {}).get("url_list", [])
                        if play_addr:
                            target_video_url = play_addr[0]
                            print("FOUND NO-WM URL IN ITEM_LIST:", target_video_url)
                            
                except Exception as e:
                    pass

        page.on("response", handle_response)
        
        print("Visiting:", 'https://v.douyin.com/MV0gw4XWdeY/')
        await page.goto('https://v.douyin.com/MV0gw4XWdeY/', wait_until="networkidle", timeout=15000)
        
        await asyncio.sleep(2)
        if target_video_url:
            print("Final URL:", target_video_url)
        else:
            print("Failed to intercept API")
            
        await b.close()

asyncio.run(run())
