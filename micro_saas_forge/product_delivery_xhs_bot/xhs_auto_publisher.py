# -*- coding: utf-8 -*-
"""
TITAN Engine - 小红书自动发布器
使用 Playwright 操作浏览器，自动上传图片、填写标题正文、发布笔记
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path

# ============================================================
# 配置
# ============================================================
XHS_CREATOR_URL = "https://creator.xiaohongshu.com/publish/publish?source=official"
# Playwright 浏览器用户数据目录 - 保持登录状态
USER_DATA_DIR = os.path.join(os.path.expanduser("~"), ".titan", "xhs_browser")
# 默认社交内容路径
PAYLOAD_PATH = os.path.join(os.path.dirname(__file__), "social_posts", "cn_payload_latest.json")


async def publish_note(title: str, body: str, image_paths: list[str], headless: bool = False):
    """
    发布一条小红书图文笔记（带合规检查）
    
    Args:
        title: 笔记标题
        body: 笔记正文
        image_paths: 封面图路径列表
        headless: 是否无头模式
    """
    # ── 合规检查 ──
    from xhs_compliance_checker import check_compliance, print_report
    result = check_compliance(title, body, is_ai_generated=True)
    print_report(result)
    
    if not result.passed:
        print("⚠️ 发现合规问题，自动修复中...")
        title = result.fixed_title
        body = result.fixed_body
        print(f"  修复后标题: {title[:30]}...")
        print(f"  修复后正文前50字: {body[:50]}...")
    elif result.tags_to_add:
        body = result.fixed_body  # 添加AI标签
    
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        # 使用持久化上下文保持登录态
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=headless,
            viewport={"width": 1280, "height": 900},
            locale="zh-CN",
        )
        page = context.pages[0] if context.pages else await context.new_page()
        
        print(f"[1/5] 打开小红书创作者中心...")
        await page.goto(XHS_CREATOR_URL, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
        
        # 检查是否需要登录
        if "login" in page.url.lower():
            print("=" * 50)
            print("!!! 需要登录 !!!")
            print("请在弹出的浏览器窗口中手动登录（扫码或短信）")
            print("登录后脚本会自动继续...")
            print("=" * 50)
            # 等待用户登录，最多5分钟
            for i in range(300):
                await asyncio.sleep(1)
                if "login" not in page.url.lower():
                    print("登录成功！继续发布...")
                    break
            else:
                print("登录超时，退出")
                await context.close()
                return False
            await page.goto(XHS_CREATOR_URL, wait_until="networkidle")
            await asyncio.sleep(2)

        # 确保在 "上传图文" 模式 (第二个 tab)
        print("[1.5] 切换到「上传图文」tab...")
        switched = await page.evaluate("""
            () => {
                // 查找所有 tab 元素
                const tabs = document.querySelectorAll('[class*="tab"], [role="tab"], span, div');
                for (const tab of tabs) {
                    const text = tab.textContent.trim();
                    if (text === '上传图文') {
                        tab.click();
                        return 'clicked: ' + tab.tagName + '.' + tab.className;
                    }
                }
                return 'not_found';
            }
        """)
        print(f"    Tab切换结果: {switched}")
        await asyncio.sleep(2)

        # [2/5] 上传图片
        print(f"[2/5] 上传图片 ({len(image_paths)} 张)...")
        # 找到 file input (通常是隐藏的)
        file_input = page.locator('input[type="file"]')
        fi_count = await file_input.count()
        print(f"    找到 {fi_count} 个 file input")
        
        if fi_count == 0:
            # 上传图文 tab 可能还没完全加载，等一下
            await asyncio.sleep(2)
            file_input = page.locator('input[type="file"]')
            fi_count = await file_input.count()
            print(f"    重试后找到 {fi_count} 个 file input")
        
        if fi_count > 0:
            # 如果有多个 input[type=file], 其中一个是给图文的
            await file_input.first.set_input_files(image_paths)
            print(f"    图片上传成功!")
            await asyncio.sleep(5)  # 等待上传完成
        else:
            print("    警告：未找到文件上传入口")
            # 打印当前页面所有 input 的信息
            inputs_info = await page.evaluate("""
                () => {
                    const inputs = document.querySelectorAll('input');
                    return Array.from(inputs).map(i => ({
                        type: i.type, 
                        id: i.id, 
                        cls: i.className.substring(0,50),
                        accept: i.accept
                    }));
                }
            """)
            print(f"    页面上所有input: {inputs_info}")

        # [3/5] 填写标题
        print(f"[3/5] 填写标题: {title[:20]}...")
        try:
            # 小红书标题可能是 input 或 contenteditable
            title_filled = await page.evaluate("""(titleText) => {
                // 方法1: 找 placeholder 包含 "标题" 的 input
                let inp = document.querySelector('input[placeholder*="标题"]');
                if (inp) {
                    inp.focus();
                    inp.value = titleText;
                    inp.dispatchEvent(new Event('input', {bubbles: true}));
                    return 'input found';
                }
                // 方法2: 找 contenteditable 中 placeholder 包含标题的
                const editables = document.querySelectorAll('[contenteditable="true"]');
                if (editables.length > 0) {
                    editables[0].focus();
                    editables[0].textContent = titleText;
                    editables[0].dispatchEvent(new Event('input', {bubbles: true}));
                    return 'contenteditable[0] used';
                }
                return 'not_found';
            }""", title)
            print(f"    标题填写结果: {title_filled}")
        except Exception as e:
            print(f"    标题填写异常: {e}")

        await asyncio.sleep(1)

        # [4/5] 填写正文
        print(f"[4/5] 填写正文 ({len(body)} 字)...")
        try:
            body_filled = await page.evaluate("""(bodyText) => {
                const editables = document.querySelectorAll('[contenteditable="true"]');
                // 正文通常是第二个 contenteditable (第一个是标题)
                let el = editables.length >= 2 ? editables[1] : 
                         editables.length === 1 ? editables[0] : null;
                if (!el) {
                    // 尝试 textarea
                    el = document.querySelector('textarea');
                }
                if (!el) {
                    return 'not_found (editables: ' + editables.length + ')';
                }
                el.focus();
                // 将文本按行分割，用 <p> 标签包裹
                const lines = bodyText.split('\\n');
                el.innerHTML = lines.map(l => '<p>' + (l || '<br>') + '</p>').join('');
                el.dispatchEvent(new Event('input', {bubbles: true}));
                el.dispatchEvent(new Event('change', {bubbles: true}));
                return 'filled (editables: ' + editables.length + ')';
            }""", body)
            print(f"    正文填写结果: {body_filled}")
        except Exception as e:
            print(f"    正文填写异常: {e}")

        await asyncio.sleep(2)

        # 确保截图目录存在
        ss_dir = os.path.join(os.path.dirname(__file__), "social_posts")
        os.makedirs(ss_dir, exist_ok=True)

        # [4.5] 强制开启 AI 内容声明 (2026 合规红线)
        print(f"[4.5] 添加 AI 生成声明合规标...")
        try:
            await page.evaluate("""
                () => {
                    const els = document.querySelectorAll('span, div, label, button, p');
                    for (const el of els) {
                        if (el.textContent && (el.textContent.includes('包含AI生成') || el.textContent.includes('AI声明'))) {
                            el.click();
                            return true;
                        }
                    }
                    return false;
                }
            """)
        except Exception as e:
            print(f"    AI声明添加异常: {e}")
            
        await asyncio.sleep(1)

        # [5/5] 发布
        print(f"[5/5] 点击发布...")
        # 先滚动到页面底部确保发布按钮可见
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        
        # 截图保存（发布前）
        screenshot_path = os.path.join(ss_dir, "xhs_before_publish.png")
        try:
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"    发布前截图已保存: {screenshot_path}")
        except Exception:
            pass
        
        # 直接用 JS 点击发布按钮（最可靠的方式）
        published = await page.evaluate("""
            () => {
                const btns = document.querySelectorAll('button');
                for (const btn of btns) {
                    const text = btn.textContent.trim();
                    if (text === '发布' || text === '发布笔记') {
                        btn.click();
                        return true;
                    }
                }
                // 尝试 class 包含 publish 的按钮
                const pBtns = document.querySelectorAll('[class*="publish"], [class*="submit"]');
                for (const btn of pBtns) {
                    if (btn.tagName === 'BUTTON' || btn.role === 'button') {
                        btn.click();
                        return true;
                    }
                }
                return false;
            }
        """)
        
        if published:
            print("    发布按钮已点击!")
        else:
            print("    JS未找到发布按钮，尝试 Playwright 选择器...")
            try:
                btn = page.locator('button:has-text("发布")').first
                await btn.click(force=True, timeout=5000)
                published = True
                print("    Playwright force-click 成功!")
            except Exception as e:
                print(f"    全部方法均失败: {e}")

        await asyncio.sleep(3)
        
        # 发布后截图
        screenshot_path2 = os.path.join(ss_dir, "xhs_after_publish.png")
        try:
            await page.screenshot(path=screenshot_path2)
            print(f"    发布后截图已保存: {screenshot_path2}")
        except Exception:
            pass
        
        if published:
            print("=" * 50)
            print("发布完成！")
        else:
            print("    未能点击发布按钮，请手动检查浏览器窗口")

        await context.close()
        return published


async def publish_all_notes(payload_path: str = None, image_dir: str = None, headless: bool = False):
    """
    从 cn_payload_latest.json 批量发布所有小红书笔记
    """
    payload_path = payload_path or PAYLOAD_PATH
    
    with open(payload_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    
    xhs_posts = payload.get("xiaohongshu_posts", [])
    if not xhs_posts:
        print("没有小红书笔记可发布")
        return
    
    print(f"共 {len(xhs_posts)} 条小红书笔记待发布")
    print("=" * 50)
    
    # 默认封面图目录
    if not image_dir:
        image_dir = os.path.join(
            os.path.expanduser("~"),
            ".gemini", "antigravity", "brain",
            "2463c55a-c7ba-49d7-b91c-00e8b4d2491c"
        )
    
    # 查找封面图
    cover_images = sorted(Path(image_dir).glob("xhs_note*_cover_*.png"))
    
    for i, post in enumerate(xhs_posts):
        title = post.get("title", f"笔记 {i+1}")
        body = post.get("body", "")
        
        # 选择对应的封面图
        if i < len(cover_images):
            images = [str(cover_images[i])]
        elif cover_images:
            images = [str(cover_images[0])]
        else:
            print(f"  跳过笔记 {i+1}：没有封面图")
            continue
        
        print(f"\n--- 发布笔记 {i+1}/{len(xhs_posts)}: {title[:30]}... ---")
        
        success = await publish_note(title, body, images, headless=headless)
        
        if success and i < len(xhs_posts) - 1:
            # 笔记间隔，避免频控
            wait = 60
            print(f"等待 {wait} 秒后发布下一条...")
            await asyncio.sleep(wait)
    
    print("\n" + "=" * 50)
    print("所有笔记发布完成！")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="TITAN 小红书自动发布器")
    parser.add_argument("--headless", action="store_true", help="无头模式运行")
    parser.add_argument("--single", action="store_true", help="只发布第一条")
    parser.add_argument("--title", type=str, help="自定义标题")
    parser.add_argument("--body", type=str, help="自定义正文")
    parser.add_argument("--image", type=str, help="自定义封面图路径")
    parser.add_argument("--payload", type=str, help="自定义 payload JSON 路径")
    args = parser.parse_args()
    
    if args.single or args.title:
        # 单条发布
        title = args.title or "家人们谁懂啊！我用Python写了个自动卖货机器人，躺赚🚀"
        body = args.body or """上班摸鱼，下班搞钱！家人们谁懂啊！💻
最近写了个 Python 自动化脚本，简直绝绝子~
全自动在闲鱼发货、在小红书发图文
连客服回复都是大模型全自动的！

🔥每天只需要挂在后台
一觉醒来就能看到叮叮叮的入账提示，这泼天的富贵终于轮到我了！

💡不需要懂很深的技术，小白会复制黏贴就能跑！
核心思路就是：用脚本卖脚本，零边际交付成本。
想要自用源码和保姆级部署教程的姐妹，
不要直接问哦，容易被吞，可以直接看看我主页顶置/瞬间你懂的~ ✨

#Python搞钱 #副业收入 #睡后收入 #独立开发者 #自动化赚钱"""
        image = args.image or str(next(
            Path(os.path.expanduser("~")).joinpath(
                ".gemini", "antigravity", "brain",
                "2463c55a-c7ba-49d7-b91c-00e8b4d2491c"
            ).glob("xhs_note*_cover_*.png"), 
            Path("cover.png")
        ))
        asyncio.run(publish_note(title, body, [image], headless=args.headless))
    else:
        # 批量发布
        asyncio.run(publish_all_notes(payload_path=args.payload, headless=args.headless))
