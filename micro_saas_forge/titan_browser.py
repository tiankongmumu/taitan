"""
╔══════════════════════════════════════════════════════════════╗
║  TITAN Browser v1.0 — Playwright-Based Browser Automation    ║
║  Replaces OpenClaw's CDP browser control                     ║
║                                                              ║
║  Capabilities:                                                ║
║  • Page navigation + screenshot                               ║
║  • DOM scraping + text extraction                             ║
║  • Click / fill / keyboard automation                         ║
║  • Mobile device emulation                                    ║
║  • Automated QA checks (status, viewport, console errors)     ║
║  • Concurrent multi-page via browser contexts                 ║
╚══════════════════════════════════════════════════════════════╝

Requires: pip install playwright && playwright install chromium
"""

import asyncio
import logging
import json
from typing import Optional, Dict, List, Any
from pathlib import Path

log = logging.getLogger("titan_browser")

# Mobile device presets
DEVICES = {
    "iphone14": {
        "viewport": {"width": 390, "height": 844},
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "is_mobile": True,
        "has_touch": True,
        "device_scale_factor": 3,
    },
    "pixel7": {
        "viewport": {"width": 412, "height": 915},
        "user_agent": "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "is_mobile": True,
        "has_touch": True,
        "device_scale_factor": 2.625,
    },
    "desktop": {
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": None,
        "is_mobile": False,
        "has_touch": False,
        "device_scale_factor": 1,
    },
}


class TitanBrowser:
    """
    Playwright-based browser automation engine.

    Usage:
        async with TitanBrowser() as browser:
            page = await browser.open("https://example.com")
            await browser.screenshot("https://example.com", "output.png")
            content = await browser.scrape("https://example.com", "h1")
            qa = await browser.qa_check("https://example.com")
    """

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright = None
        self._browser = None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *args):
        await self.stop()

    async def start(self):
        try:
            from playwright.async_api import async_playwright
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"],
            )
            log.info("🌐 Playwright browser started")
        except ImportError:
            raise RuntimeError(
                "Playwright not installed. Run: pip install playwright && playwright install chromium"
            )

    async def stop(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        log.info("🌐 Browser stopped")

    async def _new_context(self, device: str = "desktop"):
        preset = DEVICES.get(device, DEVICES["desktop"])
        ctx_opts = {"viewport": preset["viewport"]}
        if preset.get("user_agent"):
            ctx_opts["user_agent"] = preset["user_agent"]
        if preset.get("is_mobile"):
            ctx_opts["is_mobile"] = preset["is_mobile"]
            ctx_opts["has_touch"] = preset["has_touch"]
        if preset.get("device_scale_factor"):
            ctx_opts["device_scale_factor"] = preset["device_scale_factor"]
        return await self._browser.new_context(**ctx_opts)

    # ─── Core Actions ────────────────────────────────────────

    async def open(self, url: str, device: str = "desktop", wait: str = "networkidle"):
        """Open a URL and return the page object."""
        ctx = await self._new_context(device)
        page = await ctx.new_page()
        await page.goto(url, wait_until=wait, timeout=30000)
        return page

    async def screenshot(self, url: str, output_path: str = "", device: str = "desktop", full_page: bool = True) -> bytes:
        """Take a screenshot of a URL. Returns PNG bytes."""
        ctx = await self._new_context(device)
        page = await ctx.new_page()
        await page.goto(url, wait_until="networkidle", timeout=30000)
        data = await page.screenshot(full_page=full_page)
        if output_path:
            Path(output_path).write_bytes(data)
            log.info(f"📸 Screenshot saved: {output_path}")
        await ctx.close()
        return data

    async def scrape(self, url: str, selector: str = "body", device: str = "desktop") -> str:
        """Scrape text content from a URL using a CSS selector."""
        ctx = await self._new_context(device)
        page = await ctx.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        try:
            element = await page.query_selector(selector)
            text = await element.text_content() if element else ""
        except Exception as e:
            log.warning(f"Scrape selector '{selector}' failed: {e}")
            text = ""
        await ctx.close()
        return text.strip()

    async def scrape_all(self, url: str, selector: str, device: str = "desktop") -> List[str]:
        """Scrape text from ALL matching elements."""
        ctx = await self._new_context(device)
        page = await ctx.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        elements = await page.query_selector_all(selector)
        texts = []
        for el in elements:
            t = await el.text_content()
            if t:
                texts.append(t.strip())
        await ctx.close()
        return texts

    async def click(self, page, selector: str):
        """Click an element on a page."""
        await page.click(selector, timeout=5000)

    async def fill(self, page, selector: str, value: str):
        """Fill an input field."""
        await page.fill(selector, value, timeout=5000)

    async def evaluate(self, page, js_code: str):
        """Execute JavaScript on a page."""
        return await page.evaluate(js_code)

    # ─── QA Automation ───────────────────────────────────────

    async def qa_check(self, url: str, device: str = "desktop") -> dict:
        """
        Automated QA check on a URL.
        Returns: status code, load time, console errors, viewport match, title, etc.
        """
        ctx = await self._new_context(device)
        page = await ctx.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        import time
        t0 = time.time()

        response = await page.goto(url, wait_until="networkidle", timeout=30000)
        load_time = round(time.time() - t0, 2)

        title = await page.title()
        viewport = page.viewport_size

        # Check for common issues
        issues = []
        if response and response.status >= 400:
            issues.append(f"HTTP {response.status}")
        if console_errors:
            issues.append(f"{len(console_errors)} console error(s)")
        if not title:
            issues.append("Missing page title")

        result = {
            "url": url,
            "status_code": response.status if response else 0,
            "load_time_seconds": load_time,
            "title": title,
            "viewport": viewport,
            "device": device,
            "console_errors": console_errors[:10],
            "issues": issues,
            "passed": len(issues) == 0,
        }

        await ctx.close()
        return result

    async def qa_batch(self, urls: List[str], device: str = "desktop") -> List[dict]:
        """Run QA checks on multiple URLs concurrently."""
        tasks = [self.qa_check(url, device) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def multi_device_qa(self, url: str) -> Dict[str, dict]:
        """Run QA check on all device presets."""
        results = {}
        for device_name in DEVICES:
            results[device_name] = await self.qa_check(url, device_name)
        return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
async def _main():
    import sys
    args = sys.argv[1:]

    if not args or args[0] in ("help", "--help", "-h"):
        print("""
TITAN Browser v1.0 — Usage:
  python titan_browser.py screenshot <url> [output.png]
  python titan_browser.py scrape <url> <selector>
  python titan_browser.py qa <url>
  python titan_browser.py qa-multi <url>     (test all devices)
""")
        return

    cmd = args[0]
    async with TitanBrowser() as browser:
        if cmd == "screenshot" and len(args) >= 2:
            output = args[2] if len(args) > 2 else "screenshot.png"
            await browser.screenshot(args[1], output)
            print(f"✅ Saved: {output}")

        elif cmd == "scrape" and len(args) >= 3:
            text = await browser.scrape(args[1], args[2])
            print(text[:2000])

        elif cmd == "qa" and len(args) >= 2:
            result = await browser.qa_check(args[1])
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif cmd == "qa-multi" and len(args) >= 2:
            results = await browser.multi_device_qa(args[1])
            for device, r in results.items():
                status = "✅" if r.get("passed") else "❌"
                print(f"{status} {device}: {r.get('load_time_seconds', '?')}s | {r.get('title', '')[:40]}")
                if r.get("issues"):
                    for issue in r["issues"]:
                        print(f"   ⚠️  {issue}")

        else:
            print("❌ Unknown command. Run with --help")


if __name__ == "__main__":
    asyncio.run(_main())
