"""
TITAN Engine - 闲鱼虚拟商品需求扫描器
(Xianyu Virtual Product Demand Scanner)
用于扫描闲鱼全站的热门虚拟商品，提取高销量或高需求特征的产品画像。
由于闲鱼反爬严格，通过 Playwright 模拟用户进行搜索和页面解析。
"""
import asyncio
import os
import json
from loguru import logger as log
from playwright.async_api import async_playwright

USER_DATA_DIR = os.path.join(os.path.expanduser("~"), ".titan", "xy_browser")

async def scan_xianyu_demand(keywords: list[str], max_scrolls: int = 5):
    """
    搜索关键字，提取具有代表性的热门商品信息
    """
    log.info("🔍 启动闲鱼虚拟商品需求雷达 (Playwright)...")
    results = []
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False, # 需可见以应对可能的滑块
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.pages[0] if context.pages else await context.new_page()
        
        # 1. 尝试进入闲鱼首页
        # 直接使用闲鱼官网 goofish.com
        for kw in keywords:
            log.info(f"👉 正在扫描关键词: 【{kw}】")
            # 使用闲鱼PC版搜索URL
            search_url = f"https://www.goofish.com/search?q={kw}"
            
            await page.goto(search_url, wait_until="domcontentloaded")
            await asyncio.sleep(4)
            
            # 手动登录检查拦截 (如果在闲鱼官网或跳到了登录页，或者页面上有“立即登录”字样)
            page_text = await page.evaluate("document.body.innerText")
            if "login.taobao.com" in page.url or "立即登录" in page_text or "请登录" in page_text:
                log.warning("⚠️ 被闲鱼拦截登录！请在弹出的浏览器中手动扫码登录。")
                alerted = False
                for _ in range(90): # 给90秒时间扫码
                    await asyncio.sleep(1)
                    if "login" not in page.url and "立即登录" not in await page.evaluate("document.body.innerText"):
                        log.info("✅ 登录成功，等待页面跳转加载...")
                        await asyncio.sleep(5)
                        break
                    if not alerted and _ == 10:
                        log.warning("请尽快打开闲鱼App扫码...")
                        alerted = True
                else:
                    log.error("❌ 登录超时，结束扫描。")
                    return []
            
            # 模拟向下滚动加载更多商品
            for i in range(max_scrolls):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1.5)
                
            # 调试：保存页面源码以备分析
            html_dump = await page.content()
            with open("xy_debug.html", "w", encoding="utf-8") as f:
                f.write(html_dump)
                
            # 提取商品信息 (尝试通配符和泛型解析 Goofish 新版UI)
            items = await page.evaluate("""
                () => {
                    let data = [];
                    // 尝试获取所有的链接，闲鱼的商品卡片通常是 a 标签
                    const links = Array.from(document.querySelectorAll('a'));
                    links.forEach(a => {
                        let text = a.innerText.trim();
                        if (text.includes('¥') || text.includes('￥')) {
                            let lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
                            let price = lines.find(l => l.includes('¥') || l.includes('￥'));
                            // Title is usually the longest text without ¥ or numbers
                            let title = lines.find(l => !l.includes('¥') && !l.includes('￥') && l.length > 5);
                            let sales = lines.find(l => l.includes('人想要') || l.includes('人付款') || l.includes('人浏览'));
                            
                            if (title && price && title.length > 4) {
                                // 排除明显是实物的词汇
                                const physicalWords = ['包邮', '全新', '正品', '发货', '同城'];
                                const isLikelyVirtual = !physicalWords.some(w => title.includes(w)) || title.includes('软件') || title.includes('脚本') || title.includes('教程') || title.includes('源码') || title.includes('工具');
                                
                                if (isLikelyVirtual) {
                                    data.push({ title: title, price: price, sales: sales || '未知' });
                                }
                            }
                        }
                    });
                    
                    // 去重
                    const uniqueData = Array.from(new Set(data.map(a => a.title)))
                        .map(title => data.find(a => a.title === title));
                        
                    return uniqueData;
                }
            """)
            
            log.info(f"   找到 {len(items)} 个相关商品")
            for item in items:
                item['keyword'] = kw
                results.append(item)
                
        await context.close()
        
    return results

def analyze_and_propose(items: list):
    """
    本地规则提炼：找出闲鱼真正赚钱的虚拟工具
    """
    log.info("\n📊 === 闲鱼虚拟商品需求分析报告 ===")
    if not items:
        log.warning("未抓取到任何数据！")
        return
        
    # 按出现频率和疑似热度粗略排序
    print(f"共抓取 {len(items)} 个虚拟商品特征数据。")
    print("代表性商品 (随机展示前10个):")
    for i, item in enumerate(items[:10]):
        print(f"[{item['price']}] {item['title']} (热度: {item['sales']})")
        
    # TODO: 接入大模型深度分析，归纳出Top 3最值得开发的工具类目
    log.info("🔜 下一步：将抓取结果送入 LLM 进行商业判断，指导 TITAN D-Agent 自动写码。")

if __name__ == "__main__":
    test_keywords = ["全自动脚本", "代下", "解除限制", "批量工具", "自动发帖"]
    data = asyncio.run(scan_xianyu_demand(test_keywords, max_scrolls=2))
    
    # 保存原始数据
    out_path = os.path.join(os.path.dirname(__file__), "xianyu_demand_raw.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    analyze_and_propose(data)
