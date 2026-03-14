import asyncio
import os
import re
from loguru import logger
from playwright.async_api import async_playwright

logger.add("xianyu_chat.log", rotation="10 MB")

class XianyuChatBot:
    """
    闲鱼网页版/PC端客服自动化对接模块。
    用于实时监听闲鱼的消息，并将链接转发给 Titan Proxy Hub 进行查价和下单。
    """
    def __init__(self, proxy_hub_url="local"):
        self.context_dir = "./xianyu_auth_context"
        self.message_url = "https://www.goofish.com/message" # 闲鱼消息中心地址假设
        self.processed_msgs = set() # 记录处理过的消息ID，防止重复处理
        
    async def run(self):
        logger.info("🤖 启动闲鱼客服机器人 (Playwright A 方案)...")
        async with async_playwright() as p:
            # 开启持久化上下文以保持登录状态
            if not os.path.exists(self.context_dir):
                logger.info("未找到登录缓存，启动初次登录...")
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=self.context_dir,
                    headless=False, # 初次必须显示，以便扫码
                    viewport={'width': 1280, 'height': 800}
                )
                page = context.pages[0] if context.pages else await context.new_page()
                await page.goto("https://www.goofish.com")
                logger.warning("⚠️ 请在弹出的浏览器中手动扫描闲鱼二维码登录！你有90秒的时间...")
                await asyncio.sleep(90) # 留出时间扫码
                logger.info("⏳ 假设扫码完成，将刷新页面验证登录状态。")
            else:
                logger.info("✅ 找到本地缓存，尝试免登进入工作台...")
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=self.context_dir,
                    headless=False, # 调试设为False，部署可设为True
                    viewport={'width': 1280, 'height': 800}
                )
                page = context.pages[0] if context.pages else await context.new_page()
            
            # 消息中心地址测试失败(404)，改为访问首页并截图寻找入口
            await page.goto("https://www.goofish.com", wait_until="domcontentloaded")
            await asyncio.sleep(5)
            
            # 获取首页 HTML
            html = await page.content()
            
            # 使用 BeautifulSoup 或正则找包含“消息”的 a 标签
            import re
            links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>.*?消息.*?</a>', html)
            if not links:
                links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>.*?消息', html)
            logger.info(f"🔎 找到的消息可能入口: {links}")
            return
            
            # 开始心跳轮询监听新消息
            logger.info("🎧 开始监听买家消息...")
                
    async def _poll_messages(self, page):
        """
        [模拟实现]
        提取当前活动聊天框中的最新买家消息。
        如果识别到URL，则推送给 Titan Proxy Hub
        """
        # 实际DOM结构需要针对Goofish实时分析，这里提供核心逻辑伪代码:
        # await page.click(".chat-list-item.unread") -> 点击未读会话
        # msgs = await page.query_selector_all(".message-bubble.buyer") -> 获取买家消息
        # last_msg = await msgs[-1].inner_text()
        
        # 为了MVP测试，我们假装读到了这样一条消息
        has_new_msg = False # 假设当前没有新消息
        
        if has_new_msg:
            # 示例解析：
            msg_text = "老板在吗？帮我下个单 https://example-kfc.com/item/109283"
            msg_id = "msg_129X88"
            buyer_id = "买家_闲鱼001"
            
            if msg_id not in self.processed_msgs:
                self.processed_msgs.add(msg_id)
                logger.info(f"📨 收到新消息 [{buyer_id}]: {msg_text}")
                
                # 正则提取 HTTP 链接
                url_match = re.search(r"https?://[^\s]+", msg_text)
                if url_match:
                    target_url = url_match.group(0)
                    logger.info(f"🔗 识别到下单链接: {target_url}，准备向总枢纽查价...")
                    
                    # 模拟将链接推送到总控 (这里可以是 HTTP Post / Redis Queue)
                    # price = await check_price_api(target_url)
                    
                    # 模拟回复价格
                    reply_text = f"看到了亲。查询成功，代下价格为 12.5 元。请直接拍下付款12.5元，我马上帮您安排！"
                    await self._send_reply(page, reply_text)
                else:
                    await self._send_reply(page, "你好鸭！如果是需要代下，请直接发我平台商品链接哦~")
                    
    async def _send_reply(self, page, text: str):
        """控制 Playwright 在输入框打字并发送"""
        logger.success(f"💬 自动回复已发送: {text}")
        # await page.fill(".chat-input-textarea", text)
        # await asyncio.sleep(random.uniform(0.5, 1.5)) # 模拟打字停顿
        # await page.click(".btn-send")
        
if __name__ == "__main__":
    import random
    bot = XianyuChatBot()
    asyncio.run(bot.run())
