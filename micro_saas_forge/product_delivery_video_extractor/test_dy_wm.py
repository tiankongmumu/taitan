import asyncio
import re
import urllib.request
import json
from playwright.async_api import async_playwright

async def run():
    print("启动浏览器...")
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        c = await b.new_context(user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1')
        page = await c.new_page()
        print("访问分享链接...")
        await page.goto('https://v.douyin.com/MV0gw4XWdeY/', wait_until="domcontentloaded")
        
        # 1. 获取重定向后的真实 URL，提取 video ID
        await asyncio.sleep(2)
        real_url = page.url
        print("重定向后的 URL:", real_url)
        
        vid_match = re.search(r'video/(\d+)', real_url)
        if not vid_match:
            print("未找到视频ID")
            return
            
        vid = vid_match.group(1)
        print("成功提取视频ID:", vid)
        
        # 2. 拼接无水印接口
        # 抖音真实的无水印接口其实就是将 playwm (play watermark) 替换成 play
        # 第一步：获取带水印的网页端视频 src
        src = await page.evaluate('''() => {
            let v = document.querySelector("video source");
            if (v) return v.src;
            let v2 = document.querySelector("video");
            if (v2) return v2.src;
            return "";
        }''')
        
        print("原始视频SRC:", src)
        
        # 很多时候 src 里面并没有明显的 playwm 字段，而是直接一段 blob 或者加密直链
        # 真正的无水印黑科技：调用第三方或官方公共 API 获取
        api_url = f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={vid}"
        print("尝试调用官方遗留接口:", api_url)
        
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data.get("item_list"):
                    item = data["item_list"][0]
                    # 获取真实的无水印 URI
                    uri = item.get("video", {}).get("play_addr", {}).get("uri")
                    if uri:
                        no_wm_url = f"https://aweme.snssdk.com/aweme/v1/play/?video_id={uri}&ratio=1080p&line=0"
                        print("====> 最终无水印真链:", no_wm_url)
                    else:
                        print("接口中未找到 URI")
                else:
                    print("接口返回空列表或失效了拉闸！！")
        except Exception as e:
            print("请求接口失败:", e)

        await b.close()

asyncio.run(run())
