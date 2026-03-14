import asyncio
import re
from loguru import logger

# 配置日志
logger.add("proxy_hub.log", rotation="10 MB")

class TitanProxyHub:
    """
    Titan Proxy Hub: 闲鱼全自动代下接单系统中枢
    负责接收订单需求、分发给执行节点查价、以及确认后执行下单。
    """
    def __init__(self):
        self.task_queue = asyncio.Queue()
        self.active_tasks = {}
        
    async def start(self):
        logger.info("🚀 Titan Proxy Hub 已启动，监听新的代下需求...")
        # 启动工作进程
        asyncio.create_task(self._worker())
        
    async def _worker(self):
        while True:
            task = await self.task_queue.get()
            try:
                await self.process_task(task)
            except Exception as e:
                logger.error(f"❌ 任务处理失败: {task['id']} - {e}")
            finally:
                self.task_queue.task_done()
                
    async def submit_inquiry(self, item_url, buyer_id):
        """提交询价任务，由闲鱼客服机器人调用"""
        task_id = f"INQ_{buyer_id}_{int(asyncio.get_event_loop().time())}"
        task = {
            "id": task_id,
            "type": "inquiry",
            "url": item_url,
            "buyer": buyer_id,
            "status": "pending"
        }
        await self.task_queue.put(task)
        logger.info(f"📥 收到新的询价任务 [{task_id}]: {item_url}")
        return task_id
        
    async def submit_order(self, task_id):
        """确认付款后，提交正式下单任务"""
        logger.info(f"💳 订单已支付，开始执行下单 [{task_id}]")
        order_task = {
            "id": f"ORD_{task_id}",
            "type": "order",
            "ref_id": task_id
        }
        await self.task_queue.put(order_task)
        
    async def process_task(self, task):
        # 路由分发
        if task["type"] == "inquiry":
            await self._handle_inquiry(task)
        elif task["type"] == "order":
            await self._handle_order(task)
            
    async def _handle_inquiry(self, task):
        from proxy_node_kfc import KFCProxyNode
        url = task["url"]
        logger.info(f"🔍 开始解析链接并查价: {url}")
        
        # 假定路由到 KFC 节点
        node = KFCProxyNode()
        price_info = await node.check_price(url)
        
        if price_info:
            logger.success(f"💰 查价成功! 原价 {price_info['original_price']}, 我们代下价: {price_info['proxy_price']}")
            # TODO: 将价格回复给闲鱼买家
        else:
            logger.warning(f"⚠️ 查价失败，可能是不支持的链接或商品已下架。")

    async def _handle_order(self, task):
        from proxy_node_kfc import KFCProxyNode
        logger.info(f"⚙️ 正在执行全自动下单流程: {task['id']}")
        node = KFCProxyNode()
        result = await node.place_order(task["ref_id"])
        
        if result and result.get("success"):
            logger.success(f"🎉 下单成功！取餐码: {result['pickup_code']}")
            # TODO: 将取餐码自动发送给闲鱼买家，并点击发货
        else:
            logger.error("❌ 下单失败，需介入退款。")


async def main():
    hub = TitanProxyHub()
    await hub.start()
    
    # 模拟闲鱼流量网关接收到了买家消息
    logger.info("🤖 [模拟闲鱼网关] 买家 '闲鱼用户A' 丢来了一个产品口令")
    mock_url = "https://example-kfc.com/item/109283"
    
    task_id = await hub.submit_inquiry(mock_url, "buyer_A")
    
    # 等待查价完成
    await asyncio.sleep(4)
    
    # 模拟买家已付款
    logger.info("🤖 [模拟闲鱼网关] 检测到买家已在闲鱼付款 12.5 元！")
    await hub.submit_order(task_id)
    
    # 等待下单完成
    await asyncio.sleep(5)
    logger.info("🛑 演示流程结束。")

if __name__ == "__main__":
    asyncio.run(main())
