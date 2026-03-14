import asyncio
from loguru import logger
from titan_proxy_hub import TitanProxyHub

logger.add("semi_auto_cli.log", rotation="10 MB")

async def main():
    hub = TitanProxyHub()
    # 启动后台任务处理循环
    asyncio.create_task(hub._worker())
    
    print("="*50)
    print("🚀 Titan 闲鱼半自动代下接单系统 (MVP 直投版) 已启动！")
    print("说明：由于闲鱼PC版已彻底下架客服聊天功能，请您在手机端与闲鱼买家沟通。")
    print("当买家发来需要代下的链接时，请将其复制并粘贴到下方。")
    print("本系统将自动为您查出底价、计算代下价，并在您确认买家付款后，全自动下单提取取餐码！")
    print("="*50)
    
    while True:
        try:
            url = input("\n👇 请粘贴买家发来的平台商品链接 (输入 q 退出): ").strip()
            if not url:
                continue
            if url.lower() == 'q':
                break
                
            print("\n🤖 [Titan] 收到链接，系统正在飞速查价中，请稍候...")
            
            # 使用 hub 的询价接口或直接调用模拟方法
            from proxy_node_kfc import KFCProxyNode
            node = KFCProxyNode()
            price_info = await node.check_price(url)
            
            if not price_info:
                print("❌ [Titan] 查价失败或链接无效！")
                continue
                
            print(f"\n✅ [查价结果]")
            print(f"💰 商品原价: {price_info['original_price']} 元")
            print(f"📉 我们的进货底价: {price_info['cost']} 元")
            print(f"🤑 建议给闲鱼买家的代下报名价: {price_info['proxy_price']} 元")
            print("--------------------------------------------------")
            print(f"复制以下话术发给闲鱼买家：")
            print(f"【看到了亲。查询成功，内部代下特价为 {price_info['proxy_price']} 元。请直接在本链接拍下付款，秒出取餐码/券码！】")
            print("--------------------------------------------------")
            
            confirm = input("\n👉 请问买家是否已经付款？输入 'y' 确认付款并开始全自动下单，输入 'n' 取消该单: ").strip().lower()
            if confirm == 'y':
                print(f"\n⚙️ [Titan] 收到付款确认，正在调度爬虫潜入大厂后台执行真实扣款...")
                result = await node.place_order("MANUAL_" + url[-5:])
                if result and result.get("success"):
                    print(f"\n🎉 [Titan] 恭喜！全自动下单成功！")
                    print(f"🍟 请将以下取餐码发送给闲鱼买家：【 {result['pickup_code']} 】")
                    print(f"利润已入账：{round(price_info['proxy_price'] - price_info['cost'], 1)} 元！")
                else:
                    print(f"\n❌ [Titan] 执行下单节点失败！请人工介入处理退款。")
            else:
                print("🚫 订单已取消，等待下一位买家...")
            
        except Exception as e:
            logger.error(f"处理发生错误: {e}")
            print("发生内部错误，请观察日志记录。")

if __name__ == "__main__":
    asyncio.run(main())
