# -*- coding: utf-8 -*-
"""修改已发布笔记 - 使用正确的URL和JS替换"""
import asyncio
import os
import sys
sys.path.insert(0, r"d:\Project\1\micro_saas_forge")
from xhs_auto_publisher import USER_DATA_DIR

# 需要替换的内容（不使用emoji避免编码问题）
REPLACEMENTS = [
    ["shipmicro.com", "Check My Bio"],
    ["xiaobot.net", "Check My Bio"],
]

async def fix_all_notes():
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            viewport={"width": 1280, "height": 900},
            locale="zh-CN",
        )
        page = context.pages[0] if context.pages else await context.new_page()
        
        ss_dir = r"d:\Project\1\micro_saas_forge\social_posts"
        os.makedirs(ss_dir, exist_ok=True)
        
        # 1. 打开笔记管理 (正确URL)
        print("[1] 打开笔记管理...")
        await page.goto("https://creator.xiaohongshu.com/new/note-manager",
                        wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)
        
        await page.screenshot(path=os.path.join(ss_dir, "note_mgr.png"))
        
        # 2. 获取所有"编辑"链接
        edit_links = await page.evaluate("""
            () => {
                const links = [];
                document.querySelectorAll('a').forEach(a => {
                    if (a.textContent.trim() === '编辑' && a.href) {
                        links.push(a.href);
                    }
                });
                return links;
            }
        """)
        print(f"    找到 {len(edit_links)} 个编辑链接")
        for link in edit_links:
            print(f"    - {link}")
        
        # 3. 逐个编辑
        edited = 0
        for i, link in enumerate(edit_links):
            print(f"\n[编辑笔记 {i+1}/{len(edit_links)}]")
            print(f"    URL: {link}")
            
            await page.goto(link, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
            
            # 用JS检查并替换
            result = await page.evaluate("""(replacements) => {
                const editables = document.querySelectorAll('[contenteditable="true"]');
                let totalChanged = 0;
                for (const el of editables) {
                    let html = el.innerHTML;
                    let original = html;
                    for (const [find, replace] of replacements) {
                        if (html.includes(find)) {
                            html = html.split(find).join(replace);
                            totalChanged++;
                        }
                    }
                    if (html !== original) {
                        el.innerHTML = html;
                        el.dispatchEvent(new Event('input', {bubbles: true}));
                    }
                }
                
                // 也检查 input
                document.querySelectorAll('input').forEach(inp => {
                    let v = inp.value;
                    for (const [find, replace] of replacements) {
                        if (v.includes(find)) {
                            inp.value = v.split(find).join(replace);
                            inp.dispatchEvent(new Event('input', {bubbles: true}));
                            totalChanged++;
                        }
                    }
                });
                
                return {changed: totalChanged, editables: editables.length};
            }""", REPLACEMENTS)
            
            print(f"    替换结果: {result}")
            
            if result['changed'] > 0:
                await asyncio.sleep(1)
                await page.screenshot(path=os.path.join(ss_dir, f"note_edit_{i+1}.png"))
                
                # 点击发布
                pub = await page.evaluate("""
                    () => {
                        const btns = document.querySelectorAll('button');
                        for (const btn of btns) {
                            const t = btn.textContent.trim();
                            if (t === '发布' || t === '保存' || t === '更新') {
                                btn.click();
                                return t;
                            }
                        }
                        return 'no_button';
                    }
                """)
                print(f"    点击: {pub}")
                await asyncio.sleep(3)
                await page.screenshot(path=os.path.join(ss_dir, f"note_saved_{i+1}.png"))
                edited += 1
            else:
                print(f"    无需修改（可能已经改过了）")
            
            # 返回笔记管理
            await page.goto("https://creator.xiaohongshu.com/new/note-manager",
                           wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)
        
        print(f"\n{'='*50}")
        print(f"共编辑 {edited}/{len(edit_links)} 条笔记")
        print(f"{'='*50}")
        
        await context.close()

if __name__ == "__main__":
    asyncio.run(fix_all_notes())
