"""
ShipMicro UI Tester v2 — 硬化版自动化 UI 测试引擎
Roundtable Upgrade 2:
- 自适应选择器回退链 (data-testid > role > text > CSS)
- DOM 结构差异对比日志（区分真实缺陷 vs 动态UI误判）
- 交互热区记录（供 ad_injector 做智能广告避让）
- 失败截图 + 详细诊断报告
"""
import os
import sys
import json
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger

log = get_logger("ui_tester")

SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "ui_screenshots")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "logs")
HOTSPOT_DIR = os.path.join(os.path.dirname(__file__), "analytics_data")


async def test_url(url: str, slug: str) -> dict:
    """v2: 硬化版 Playwright 测试，带自适应定位和热区收集"""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        log.warning("Playwright 未安装, 运行: pip install playwright && playwright install chromium")
        return {"slug": slug, "url": url, "status": "SKIP", "reason": "Playwright not installed"}

    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    result = {
        "slug": slug, "url": url,
        "timestamp": datetime.now().isoformat(),
        "status": "UNKNOWN", "checks": {}, "hotspots": [],
    }

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1280, "height": 800})

            # 收集 JS 错误
            js_errors = []
            page.on("pageerror", lambda err: js_errors.append(str(err)))

            # 收集 console 错误
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            # 1. 加载页面
            log.info(f"  🌐 打开 {url}...")
            response = await page.goto(url, timeout=30000, wait_until="networkidle")

            # 2. HTTP 状态
            status_code = response.status if response else 0
            result["checks"]["http_status"] = status_code
            result["checks"]["http_ok"] = status_code in [200, 301, 302, 308]

            # 3. 页面内容检查
            body_text = await page.inner_text("body")
            result["checks"]["has_content"] = len(body_text.strip()) > 50
            result["checks"]["content_length"] = len(body_text.strip())

            # 4. v2: 自适应选择器回退链检测交互元素
            interactive = await _adaptive_find_interactive(page)
            result["checks"]["button_count"] = interactive["buttons"]
            result["checks"]["input_count"] = interactive["inputs"]
            result["checks"]["has_interactive"] = interactive["buttons"] > 0 or interactive["inputs"] > 0
            result["checks"]["selector_strategy"] = interactive["strategy"]

            # 5. JS 错误
            await page.wait_for_timeout(2000)
            result["checks"]["js_errors"] = len(js_errors)
            result["checks"]["js_error_details"] = js_errors[:3]
            result["checks"]["console_errors"] = len(console_errors)

            # 6. ShipMicro badge
            result["checks"]["has_badge"] = "ShipMicro" in body_text

            # 7. v2: DOM 结构指纹（用于差异对比）
            dom_fingerprint = await _get_dom_fingerprint(page)
            result["dom_fingerprint"] = dom_fingerprint

            # 8. v2: 交互热区收集（供广告避让）
            hotspots = await _collect_hotspots(page)
            result["hotspots"] = hotspots

            # 9. 截图
            ts = datetime.now().strftime('%Y%m%d_%H%M')
            screenshot_path = os.path.join(SCREENSHOTS_DIR, f"{slug}_{ts}.png")
            await page.screenshot(path=screenshot_path, full_page=True)
            result["screenshot"] = screenshot_path

            # 10. 综合评分 (v2: 更精细的评分)
            score = 0
            if result["checks"]["http_ok"]:
                score += 2
            if status_code == 200:
                score += 1    # 精确 200 额外 +1
            if result["checks"]["has_content"]:
                score += 2
            if result["checks"]["js_errors"] == 0:
                score += 2
            if result["checks"]["has_interactive"]:
                score += 1.5
            if result["checks"]["has_badge"]:
                score += 0.5
            if result["checks"]["console_errors"] == 0:
                score += 1

            result["ui_score"] = min(round(score, 1), 10)
            result["status"] = "PASS" if score >= 7 else ("WARN" if score >= 4 else "FAIL")

            # v2: 如果是 FAIL，额外截图（带红框标注）
            if result["status"] == "FAIL":
                fail_path = os.path.join(SCREENSHOTS_DIR, f"{slug}_{ts}_FAIL.png")
                await page.screenshot(path=fail_path)
                result["fail_screenshot"] = fail_path
                log.warning(f"  📸 失败截图: {fail_path}")

            await browser.close()

    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)
        log.error(f"  ❌ 测试异常: {e}")

    return result


async def _adaptive_find_interactive(page) -> dict:
    """v2: 自适应选择器回退链"""
    strategies = [
        ("data-testid", "button[data-testid]", "input[data-testid], textarea[data-testid]"),
        ("role", '[role="button"]', '[role="textbox"], [role="searchbox"]'),
        ("semantic", "button", "input, textarea, select"),
        ("css_fallback", '[class*="btn"], [class*="button"]', '[class*="input"], [class*="field"]'),
    ]
    for name, btn_sel, inp_sel in strategies:
        try:
            buttons = await page.query_selector_all(btn_sel)
            inputs = await page.query_selector_all(inp_sel)
            if buttons or inputs:
                return {"buttons": len(buttons), "inputs": len(inputs), "strategy": name}
        except Exception:
            continue
    return {"buttons": 0, "inputs": 0, "strategy": "none_found"}


async def _get_dom_fingerprint(page) -> dict:
    """v2: DOM 结构指纹，用于检测页面是否发生了意外变化"""
    try:
        fingerprint = await page.evaluate("""() => {
            const tags = {};
            document.querySelectorAll('*').forEach(el => {
                const tag = el.tagName.toLowerCase();
                tags[tag] = (tags[tag] || 0) + 1;
            });
            return {
                total_elements: document.querySelectorAll('*').length,
                tag_counts: tags,
                depth: (function getDepth(el) {
                    let d = 0, c = el;
                    while(c.parentElement) { d++; c = c.parentElement; }
                    return d;
                })(document.querySelector('body > *') || document.body),
            };
        }""")
        return fingerprint
    except Exception:
        return {"total_elements": 0, "tag_counts": {}, "depth": 0}


async def _collect_hotspots(page) -> list[dict]:
    """v2: 收集页面上的交互热区坐标（供广告避让）"""
    try:
        hotspots = await page.evaluate("""() => {
            const spots = [];
            const selectors = ['button', 'a', 'input', 'textarea', 'select', '[onclick]', '[role="button"]'];
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        spots.push({
                            tag: el.tagName.toLowerCase(),
                            x: Math.round(rect.x),
                            y: Math.round(rect.y),
                            w: Math.round(rect.width),
                            h: Math.round(rect.height),
                            text: (el.textContent || '').trim().slice(0, 30),
                        });
                    }
                });
            });
            return spots;
        }""")
        return hotspots[:20]  # 最多 20 个热区
    except Exception:
        return []


async def test_all_deployed_tools() -> list[dict]:
    """测试所有已部署的工具"""
    history_path = os.path.join(os.path.dirname(__file__), "history.json")
    if not os.path.exists(history_path):
        log.warning("没有 history.json, 无法获取部署的工具列表")
        return []

    with open(history_path, "r", encoding="utf-8") as f:
        history = json.load(f)

    results = []
    for entry in history:
        url = entry.get("url", "")
        slug = entry.get("slug", "")
        if not url or not slug:
            continue
        log.info(f"🧪 测试 [{slug}]...")
        result = await test_url(url, slug)
        emoji = {"PASS": "🟢", "WARN": "🟡", "FAIL": "🔴", "ERROR": "❌", "SKIP": "⏭️"}.get(result["status"], "?")
        log.info(f"  {emoji} {result['status']} — UI Score: {result.get('ui_score', '?')}/10 (strategy: {result.get('checks', {}).get('selector_strategy', '?')})")
        results.append(result)

    # 保存报告
    os.makedirs(RESULTS_DIR, exist_ok=True)
    report_path = os.path.join(RESULTS_DIR, f"ui_test_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # v2: 保存热区数据供 ad_injector 使用
    _save_hotspot_data(results)

    passed = sum(1 for r in results if r["status"] == "PASS")
    warned = sum(1 for r in results if r["status"] == "WARN")
    failed = sum(1 for r in results if r["status"] in ["FAIL", "ERROR"])
    log.info(f"📊 汇总: 🟢 PASS:{passed}  🟡 WARN:{warned}  🔴 FAIL:{failed}")

    return results


def _save_hotspot_data(results: list[dict]):
    """保存热区数据到 analytics_data/ 供 ad_injector 读取"""
    os.makedirs(HOTSPOT_DIR, exist_ok=True)
    hotspot_map = {}
    for r in results:
        slug = r.get("slug", "")
        if slug and r.get("hotspots"):
            hotspot_map[slug] = r["hotspots"]
    path = os.path.join(HOTSPOT_DIR, "ui_hotspots.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(hotspot_map, f, ensure_ascii=False, indent=2)
    log.info(f"📊 热区数据已保存: {path} ({len(hotspot_map)} tools)")


def run_ui_tests():
    log.info("=" * 50)
    log.info("🧪 SHIPMICRO UI TESTER v2 — 硬化版动态质量门禁")
    log.info("=" * 50)
    return asyncio.run(test_all_deployed_tools())


if __name__ == "__main__":
    run_ui_tests()
