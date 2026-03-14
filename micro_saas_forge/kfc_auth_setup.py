import asyncio
import os
from loguru import logger
from playwright.async_api import async_playwright

logger.add("kfc_auth.log", rotation="5 MB")

async def main():
    context_dir = "./kfc_commercial_context"
    login_url = "https://m.kfc.com.cn/"
    
    print("==================================================")
    print("🍔 [Titan] KFC 商业级防封控自动化环境初始化 🍔")
    print("==================================================")
    print(f"正在启动浏览器，即将为您打开 KFC 手机版网页: {login_url}")
    print("请注意操作步骤：")
    print("1. 在弹出的浏览器中，点击『我的』或『立即点餐』。")
    print("2. 在登录页面，使用您的手机号获取短信验证码进行真实登录。")
    print("3. 【关键】登录成功并看到您的个人资料/点餐界面后，切回这个黑框终端。")
    print("4. 在此终端按下回车键，系统会自动帮您封存持久化身份。")
    print("==================================================")
    
    async with async_playwright() as p:
        
        context = await p.chromium.launch_persistent_context(
            user_data_dir=context_dir,
            headless=False,
            viewport={'width': 390, 'height': 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        try:
            await page.goto(login_url, wait_until="domcontentloaded")
            logger.info("浏览器已打开，等待用户完成登录...")
        except Exception as e:
            logger.error(f"无法访问肯德基页面: {e}")
            
        # 阻塞这里，等待用户在终端输入确认
        await asyncio.get_event_loop().run_in_executor(None, input, "\n👉 [完成登录] 请在浏览器中确认登录成功并进入点餐主页后，在此处按下 【回车键/Enter】 进行状态封存：")
        
        logger.success("收到封存指令，正在保存持久化 Auth Context 并安全退出内核...")
        await context.close()
        print("\n✅ 持久化环境已构建完成！您可以随时启动全自动下单引擎了。")

if __name__ == "__main__":
    asyncio.run(main())
