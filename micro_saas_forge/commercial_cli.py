import asyncio
import time
from loguru import logger
from db_manager import DBManager
from real_proxy_node import RealProxyNode
from api_proxy_node import APIProxyNode

logger.add("commercial_proxy.log", rotation="50 MB")

async def main():
    db = DBManager()
    node = RealProxyNode()
    
    print("="*60)
    print("💎 Titan Proxy Hub (商业旗舰版 v2.0) 💎")
    print("============================================================")
    print("【系统模式选择】")
    print("1. 🕸️ Web UI 漏斗引擎 (适合所有通用页面，速度中)")
    print("2. ⚡ API 直连印钞引擎 (适合已对接平台，0风控，速度极快)")
    mode = input("请选择您的引擎节点 (1/2) [默认2]: ").strip()
    
    if mode == "1":
        node = RealProxyNode()
        print("▶️ 已加载: Web UI 漏斗引擎")
    else:
        node = APIProxyNode()
        print("▶️ 已加载: API 直连印钞引擎")
    print("============================================================")
    
    stats = db.get_daily_revenue()
    print(f"📈 今日已结单: {stats['orders']} 笔 | 今日预估总利润: {stats['revenue']} 元\n")
    
    while True:
        try:
            try:
                url = input("🔗 请粘贴闲鱼客单链接 (输入 'q' 退出, 's' 查看今日流水): ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n收到退出信号，系统关闭。")
                break
                
            if not url:
                continue
            if url.lower() == 'q':
                break
            if url.lower() == 's':
                stats = db.get_daily_revenue()
                print(f"\n📊 [财务报表] 今日完单: {stats['orders']} 笔，累计净利润: ¥{stats['revenue']}\n")
                continue
                
            print("\n🤖 [Titan 商业中枢] 正在调度无头节点前往目标平台...")
            order_id = f"TD_{int(time.time())}"
            
            # 使用真实的 Playwright 节点进行查价探针
            price_info = await node.check_price(url)
            
            if not price_info:
                print("❌ [Titan] 查价失败！可能是平台拒绝访问或商品已下架。")
                continue
                
            orig = price_info['original_price']
            cost = price_info['cost']
            proxy = price_info['proxy_price']
            item_name = price_info.get('item_name', '通用代下单')
            
            print(f"\n✅ [查价结果返回: {item_name}]")
            print(f"🛒 平台原价: ¥{orig}")
            print(f"📉 核算底价: ¥{cost} (毛利空间: {round(orig - cost, 2)}元)")
            print(f"🤑 对外报价: ¥{proxy} (您的净利润: {round(proxy - cost, 2)}元)")
            print("-" * 50)
            print(f"📋 请回复买家话术：")
            print(f"【亲，查询成功，通过内部通道代下仅需 {proxy} 元哦。麻烦直接拍本商品付款，秒出单！】")
            print("-" * 50)
            
            # 将询价单暂存在数据库
            db.create_order(order_id, url, orig, cost, proxy, status="PENDING_PAY")
            
            try:
                confirm = input("\n👉 请问闲鱼买家是否已经完成付款？[ y(确认付款并发车) / n(取消) ]: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                confirm = 'n'
                
            if confirm == 'y':
                print(f"\n⚙️ [Titan] 收到款项，正在执行商业自动下单并发版机制...")
                db.update_status(order_id, "PROCESSING")
                
                # 真实下单逻辑
                result = await node.place_order(order_id, proxy, cost)
                
                if result and result.get("success"):
                    print(f"\n🎉 [Titan] 订单核销/下达成功！")
                    print(f"🎫 请将此核销码发送给买家：【 {result['pickup_code']} 】")
                    print(f"💰 本单利润 ¥{round(proxy - cost, 2)} 已记录到财务库！\n")
                else:
                    db.update_status(order_id, "FAILED")
                    print(f"\n❌ [Titan] 执行下单节点失败！订单已标记为异常。")
            else:
                db.update_status(order_id, "CANCELLED")
                print("🚫 订单已取消，记录归档。\n")
            
        except Exception as e:
            logger.error(f"处理发生致命错误: {e}")
            print("系统异常拦截，服务已恢复。")

if __name__ == "__main__":
    asyncio.run(main())
