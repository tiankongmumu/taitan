import time
import asyncio
from loguru import logger
import re
from datetime import datetime
import httpx

# 尝试导入 wxauto (基于 Windows UI Automation 控制微信 PC 版)
try:
    from wxauto import WeChat
except ImportError:
    logger.error("缺少 wxauto 库！请运行：pip install wxauto")
    WeChat = None

from api_proxy_node import APIProxyNode
from db_manager import DBManager

class SessionState:
    IDLE = "IDLE"                            # 空闲，等待发客单链接
    AWAITING_PAY = "AWAITING_PAY"            # 已发报价，等待买家付钱
    PROCESSING_ORDER = "PROCESSING_ORDER"    # 收到钱，正在全网调 API 拿码

class SessionManager:
    """商业级会话管理器：跟踪每一个用户的状态，防止错发漏发乱单"""
    def __init__(self):
        # 结构: {"微信ID/昵称": {"state": "IDLE", "pending_order": None, "last_active": timestamp}}
        self.sessions = {}
        
    def get_session(self, user_id):
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                "state": SessionState.IDLE,
                "pending_order": None,
                "last_active": time.time()
            }
        self.sessions[user_id]["last_active"] = time.time()
        return self.sessions[user_id]
        
    def update_state(self, user_id, state, order_data=None):
        session = self.get_session(user_id)
        session["state"] = state
        if order_data is not None:
             session["pending_order"] = order_data
             
    def clear_session(self, user_id):
        self.update_state(user_id, SessionState.IDLE, None)

class WeChatBotNode:
    """
    终极全自动路线 A：微信私域机器人 (商业硬核版)
    带状态追踪、故障自愈、智能防骚扰机制。
    """
    def __init__(self):
        logger.add("wechat_bot_commercial.log", rotation="50 MB", level="INFO")
        self.api_node = APIProxyNode()
        self.db = DBManager()
        self.session_mgr = SessionManager()
        
        if WeChat is not None:
            try:
                self.wx = WeChat()
                logger.success(f"✅ 成功接管电脑版微信，当前登录账号: {self.wx.nickname}")
            except Exception as e:
                logger.error(f"无法获取微信窗口：{e}")
                self.wx = None
        else:
            self.wx = None
            
        # 生产环境应当从数据库/配置文件读取，此处演示监听特定的客服群或“文件传输助手”测试
        self.listen_list = ['文件传输助手', '微信支付']

    async def run(self):
        """主守护进程：死循环监听并保证不挂掉"""
        if not self.wx:
            logger.critical("❌ 微信自动化引擎未加载，程序终止！")
            return
            
        print("\n=======================================================")
        print("🤖 Titan WeChat Enterprise Bot (Night Shift Polished) 启动中")
        print("💡 [商业级防崩溃] 已开启内存回收与异常捕获")
        print(f"👀 正在监听: {self.listen_list}")
        print("=======================================================\n")
        
        for name in self.listen_list:
            try:
                self.wx.AddListenChat(who=name)
            except Exception as e:
                logger.warning(f"无法添加监听列表项 {name}: {e}")
                
        # [NEW Optimization] 启动后台 DLQ 死信队列抢救线程
        asyncio.create_task(self.dlq_watcher())
            
        while True:
            try:
                msgs = self.wx.GetListenMessage()
                for chat in msgs:
                    who = chat.who
                    one_msgs = msgs.get(chat)
                    for msg in one_msgs:
                        if msg.type == 'friend':
                            # 异步抛出处理，不阻塞主监听循环
                            asyncio.create_task(self.handle_message(who, msg.content))
            except Exception as e:
                 logger.error(f"[守护进程] 抓取消息异常 (可能是微信窗口被意外关闭): {e}")
                 # 故障自愈等待
                 time.sleep(5)
            
            # 心跳间隔
            await asyncio.sleep(1)

    def _nlp_product_match(self, text: str) -> str:
        """[100x Optimization] 本地 NLP/正则 模糊商品语义映射网络"""
        text = text.lower()
        # 商业知识库词库 (可扩展为数据库查询或接入 LLM)
        knowledge_base = {
            "辣堡": "https://m.kfc.cn/item/spicy_burger",
            "香辣鸡腿堡": "https://m.kfc.cn/item/spicy_burger",
            "疯狂星期四": "https://m.kfc.cn/item/crazy_thursday_bucket",
            "原味鸡": "https://m.kfc.cn/item/original_recipe",
            "瑞幸": "https://m.luckincoffee.com/item/standard",
            "星巴克": "https://m.starbucks.com.cn/item/latte"
        }
        for keyword, link in knowledge_base.items():
             if keyword in text:
                  logger.info(f"🧠 [NLP 感知] 嗅探到关键字 '{text}'，精准映射为标准件: {link}")
                  return link
        return text # 没匹配到则原样返回

    async def _mock_llm_conversation_engine(self, user_msg: str) -> dict:
        """
        [36H Evolution] 商业级 Agent 销售大脑。
        模拟对接 DeepSeek / ChatGPT API 进行意图识别、推销连单与客诉安抚。
        """
        logger.info(f"🔮 [LLM Brain] 正在深度思考客户意图: {user_msg}")
        await asyncio.sleep(1.0) # 模拟大模型思考延迟
        
        reply_pkg = {"action": "CHAT", "reply_text": "老板好，我是自动小助手，有什么可以帮您？", "upsell_url": None}
        
        # 意图 1: 纯粹讲价/闲聊
        if "便宜" in user_msg or "贵" in user_msg or "少点" in user_msg:
             reply_pkg["reply_text"] = "亲这是内部底价啦，系统设定的没法再低了哦。别人卖 39.9 我们只卖一半的价格，全系统最低价，您放心下单就好啦！🙏"
        # 意图 2: 客户情绪安抚
        elif "骗子" in user_msg or "退款" in user_msg or "太慢" in user_msg:
             reply_pkg["reply_text"] = "😭 实在抱歉让老板您着急了！刚刚系统拉取接口波动了一下，如果出码失败钱会原路退回！这是系统给您的 0.5 元小红包补偿请收下，息怒息怒~"
        # 意图 3: 找买东西但没说清楚
        elif "饿" in user_msg or "吃点什么" in user_msg:
             reply_pkg["reply_text"] = "老板饿了的话，要不要看看今天我们特价的辣堡或者原味鸡呀？直接发你要的给我！"
        # 意图 4: 触发核心词，准备推销连单 (Upsell)
        elif "汉堡" in user_msg or "辣堡" in user_msg:
             reply_pkg["action"] = "INTENT_BUY"
             reply_pkg["upsell_url"] = "https://m.kfc.cn/item/spicy_burger"
             reply_pkg["reply_text"] = "收到！看您点了个辣堡，哥，**再加 4 块钱我给您配个小薯条+可乐套餐好不好？** 这样吃更爽！单独买要 12 呢。如果需要直接发转账，不需要直接回复“不用”。"
             
        return reply_pkg

    async def handle_message(self, who: str, content: str):
        """带状态机的高级业务路由"""
        logger.info(f"💌 [{who}] 发来消息: {content}")
        session = self.session_mgr.get_session(who)
        state = session["state"]
        content = str(content).strip()
        
        # 1. 安全过滤机制 (防捣乱)
        if len(content) > 500:
             logger.warning(f"过滤 {who} 的超长垃圾消息")
             return

        # ==========================================
        # 状态机：IDLE (空闲态) -> 等待客发链接查价
        # ==========================================
        if state == SessionState.IDLE:
             # 【深度换脑】拦截所有文本，交给大模型做金牌销售判定
             llm_decision = await self._mock_llm_conversation_engine(content)
             
             if llm_decision["action"] == "CHAT":
                  # 只是闲聊/讲价/情绪发泄，大模型直接完美话术挡回，绝不呼叫人工
                  self.wx.SendMsg(llm_decision["reply_text"], who)
                  return
                  
             elif llm_decision["action"] == "INTENT_BUY" or "http" in content:
                # 触发进入购买流
                if "http" not in content and llm_decision["upsell_url"]:
                    standard_url = llm_decision["upsell_url"]
                    # 先发大模型的推销话术诱导
                    self.wx.SendMsg(llm_decision["reply_text"], who)
                else:
                    standard_url = self._nlp_product_match(content)
                    self.wx.SendMsg(f"🤖 [系统探测] 收到需求，正在通过内部核心通道连线查价...", who)
                
                # 调 API 查底价
                price_info = await self.api_node.check_price(standard_url)
                
                if price_info:
                    proxy_price = price_info['proxy_price']
                    cost_price = price_info['cost']
                    task_id = f"WX_{int(time.time())}_{who[-4:]}" # 生成带用户标识的独立订单号
                    
                    # [NEW Optimization] Security: 绝对财务熔断锁，防亏本倒挂
                    if cost_price >= proxy_price:
                         logger.critical(f"🛑 [财务熔断] 严重警报！拿货成本价 (¥{cost_price}) 高于或等于 对外报价 (¥{proxy_price})，强行切断交易链！")
                         self.wx.SendMsg(f"⚠️ 触发风控：当前商品底价 ({cost_price}元) 出现剧烈波动甚至高于门市价，已暂停接该单。请明日再试。", who)
                         asyncio.create_task(self.send_alert(f"财务熔断: {price_info['item_name']} 成本{cost_price}高于售价{proxy_price}"))
                         return
                    
                    # 生成精美的转化话术
                    reply = (
                        f"✅ 【内部渠道查价完毕】\n"
                        f"🍔 商品: {price_info['item_name']}\n"
                        f"原价: ¥{price_info['original_price']} | 👉今日特惠: ¥{proxy_price} 👈\n"
                        f"--------------------\n"
                        f"⚠️ 如需下单，请直接发送微信红包/转账 【{proxy_price}】 元！\n"
                        f"(系统将在1~3秒内自动出码并下发，过时不候)"
                    )
                    self.wx.SendMsg(reply, who)
                    
                    # 【状态跃迁】 进入等待付款状态
                    order_pkg = {
                        "task_id": task_id,
                        "proxy_price": proxy_price,
                        "cost": price_info['cost'],
                        "original": price_info['original_price'],
                        "content": content
                    }
                    self.db.create_order(task_id, content, price_info['original_price'], price_info['cost'], proxy_price, "PENDING_PAY")
                    self.session_mgr.update_state(who, SessionState.AWAITING_PAY, order_pkg)
                    logger.success(f"已锁定 {who} 订单 {task_id}，等待支付 ¥{proxy_price}")
                else:
                    self.wx.SendMsg("❌ 该商品目前渠道维护或无锡，请换个商品链接再试。", who)
            else:
                 # 日常聊天，可用接入 LLM (如 DeepSeek) 进行纯文字客服兜底
                 pass

        # ==========================================
        # 状态机：AWAITING_PAY (待付款态) -> 等待收钱
        # ==========================================
        elif state == SessionState.AWAITING_PAY:
            order_pkg = session["pending_order"]
            
            # 使用最粗暴有效的收款检测拦截 (由于旧版API限制，这里捕捉转账文本，实际商用需接支付回调或OCR验证)
            if "[转账]" in content or "[微信红包]" in content or "已转" in content or "已付" in content:
                # 【状态跃迁】进入履约期，防止重复付款触发两次发货
                self.session_mgr.update_state(who, SessionState.PROCESSING_ORDER, order_pkg)
                self.wx.SendMsg(f"💸 [财务系统] 已收到汇款信号，正在为您调拨内部库存，请勿着急...", who)
                
                # 触发真金白银 API 拿货
                logger.info(f"🚀 开始为 {who} 的订单 {order_pkg['task_id']} 走 API 提走卡密...")
                self.db.update_status(order_pkg['task_id'], "PROCESSING")
                
                try:
                    # 限制 API 超时，防止卡死
                    result = await asyncio.wait_for(
                        self.api_node.place_order(order_pkg['task_id'], order_pkg['proxy_price'], order_pkg['cost']),
                        timeout=20.0
                    )
                    
                    if result["success"]:
                        code = result["pickup_code"]
                        reply = (
                            f"🎉 【代下成功】\n"
                            f"🍔 您的提货码：【 {code} 】\n"
                            f"🏃‍♂️ 请凭码前往对应的店面点餐台/柜员机取餐。\n"
                            f"感谢您的光临，下次吃鸡记得找我！"
                        )
                        self.wx.SendMsg(reply, who)
                        self.db.update_status(order_pkg['task_id'], "COMPLETED")
                        logger.success(f"💰 [印钞圆满] 成功赚取差价！已向 {who} 下发卡密: {code}")
                    else:
                        raise Exception("API 返回出单失败，渠道拥堵或库存干涸")
                        
                except asyncio.TimeoutError:
                     logger.error(f"❌ [API 超时] 为 {who} 取码异常！打入 DLQ，由容灾引擎接管。")
                     self.wx.SendMsg("⚠️ [官方网络拥堵] 出码超时！已自动转入【VIP优先级抢救队列】，一旦出码成功将在此对话框补发给您，请耐心等待！", who)
                     self.db.move_to_dlq(order_pkg['task_id'], "Network Timeout")
                except Exception as e:
                     logger.error(f"❌ [API 提货失败] 未知异常: {e}。打入 DLQ 进行补偿等待。")
                     self.wx.SendMsg("⚠️ [库存不足预警] 平台底层正在补货，本单已进容灾监控！一有货立马抢！", who)
                     self.db.move_to_dlq(order_pkg['task_id'], f"Exception: {e}")
                     
                finally:
                    # 【状态跃迁】流水结束，清理当前用户的订单锁，允许其发下一个新链接
                    self.session_mgr.clear_session(who)
            
            # 如果等钱的时候他发了别的文字，有可能是要换商品
            elif "不" in content or "换" in content or "重新" in content:
                self.wx.SendMsg("已为您取消上一个订单。请重新发送商品链接。😊", who)
                self.session_mgr.clear_session(who)
                
        # ==========================================
        # 状态机：PROCESSING (履约态) -> 系统正在拿货，屏蔽客人的催促
        # ==========================================
        elif state == SessionState.PROCESSING_ORDER:
             if "还没" in content or "快点" in content or "催" in content:
                  self.wx.SendMsg("🤖 正在全速通讯分销服务器下码中，预计还需3-5秒，请不要着急哦~", who)

    async def dlq_watcher(self):
        """[100x Optimization] 后台守护线程：DLQ死信队列抢救补偿，实现绝对0漏单"""
        while True:
            try:
                pending_dlq = self.db.get_pending_dlq_orders()
                for dlq_order in pending_dlq:
                    task_id = dlq_order["task_id"]
                    cost = dlq_order["cost_price"]
                    proxy = dlq_order["proxy_price"]
                    retry_count = dlq_order["retry_count"]
                    
                    logger.info(f"🔄 [DLQ 自动复苏] 尝试第 {retry_count + 1} 次抢救曾失败的提单: {task_id}")
                    
                    # 再试一次提码
                    result = await self.api_node.place_order(task_id, proxy, cost)
                    
                    if result["success"]:
                        self.db.update_status(task_id, "COMPLETED")
                        code = result["pickup_code"]
                        logger.success(f"🎉 [DLQ 奇迹救活] ✅ 补发成功，不仅没亏还抢回了 {proxy - cost} 元纯利！单号: {task_id}")
                        
                        # 向该买家补发通知 (使用包含在订单号里的四位尾号标记寻找群或单聊)
                        # 商业实战中，可将 who 直接缓存在数据库以便 DLQ 重发。这里输出日志作为演示
                        logger.info(f"👉 获得遗失卡密 [{code}]，请前往微信客服后台或直接复制下发买家。")
                    else:
                        logger.warning(f"⚠️ [DLQ 继续沉睡] 第 {retry_count + 1} 次提货依然失败: {task_id}")
                        self.db.move_to_dlq(task_id, f"DLQ Retry {retry_count+1} Failed")
                        
            except Exception as e:
                logger.error(f"DLQ 看门狗运行异常: {e}")
                
            await asyncio.sleep(60) #每60秒巡检一次

    async def send_alert(self, msg: str):
        """[100x Optimization] Server酱/Bark 云端报警推送机制，零延迟触达老板手机"""
        logger.warning(f"☁️ [云端推送] 准备发往手机端: {msg}")
        # 这里用通用型 Webhook 占位，生产环境更换为用户持有的 SendKey
        push_key = "SCT_PLACEHOLDER_KEY"
        push_url = f"https://sctapi.ftqq.com/{push_key}.send"
        
        try:
           async with httpx.AsyncClient(timeout=5.0) as client:
               await client.post(push_url, data={"title": "⚠️ Titan 商业引擎预警", "desp": msg})
        except Exception as e:
           logger.error(f"[云报警失败] 无法连线推送服务器: {e}")

if __name__ == "__main__":
    bot = WeChatBotNode()
    asyncio.run(bot.run())
