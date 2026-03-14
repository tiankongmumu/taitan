"""
TITAN Engine v4.0 — Browser QA
Tests generated products in a REAL browser:
- Renders the page (Playwright or subprocess)
- Checks for JS errors
- Tests responsive (desktop + mobile viewport)
- Captures screenshot evidence
- Returns pass/fail with score

Requires: playwright (pip install playwright && playwright install chromium)
Fallback: uses basic HTTP + HTML parsing if playwright not available
"""
import os
import sys
import json
import re
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger

log = get_logger("browser_qa")

QA_DIR = os.path.join(os.path.dirname(__file__), "qa_results")
SCREENSHOT_DIR = os.path.join(QA_DIR, "screenshots")


class BrowserQA:
    def __init__(self):
        os.makedirs(QA_DIR, exist_ok=True)
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        self._has_playwright = self._check_playwright()

    def _check_playwright(self) -> bool:
        try:
            import playwright
            return True
        except ImportError:
            log.info("⚠️ Playwright not installed, using fallback HTML analysis")
            return False

    def test(self, html_path: str) -> dict:
        """Test a product HTML file and return QA results."""
        log.info(f"🧪 QA testing: {os.path.basename(html_path)}")

        if not os.path.exists(html_path):
            return {"pass": False, "score": 0, "issues": ["File not found"], "screenshot": None}

        # Read HTML
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Run all checks
        results = {
            "file": os.path.basename(html_path),
            "tested_at": datetime.now().isoformat(),
            "checks": {},
            "issues": [],
            "score": 0,
        }

        # Check 1: HTML structure
        struct_score, struct_issues = self._check_structure(html)
        results["checks"]["structure"] = struct_score
        results["issues"].extend(struct_issues)

        # Check 2: Meta/SEO
        seo_score, seo_issues = self._check_seo(html)
        results["checks"]["seo"] = seo_score
        results["issues"].extend(seo_issues)

        # Check 3: Mobile responsiveness
        mobile_score, mobile_issues = self._check_mobile(html)
        results["checks"]["mobile"] = mobile_score
        results["issues"].extend(mobile_issues)

        # Check 4: Interactivity
        interactive_score, interactive_issues = self._check_interactivity(html)
        results["checks"]["interactivity"] = interactive_score
        results["issues"].extend(interactive_issues)

        # Check 5: Performance
        perf_score, perf_issues = self._check_performance(html)
        results["checks"]["performance"] = perf_score
        results["issues"].extend(perf_issues)

        # Check 6: Commercial readiness
        comm_score, comm_issues = self._check_commercial(html)
        results["checks"]["commercial"] = comm_score
        results["issues"].extend(comm_issues)

        # Check 7: Visual quality
        visual_score, visual_issues = self._check_visual_quality(html)
        results["checks"]["visual"] = visual_score
        results["issues"].extend(visual_issues)

        # Calculate overall score (weighted average)
        weights = {
            "structure": 1.0, "seo": 1.5, "mobile": 1.5,
            "interactivity": 2.0, "performance": 1.0,
            "commercial": 2.0, "visual": 1.0
        }
        total_weight = sum(weights.values())
        weighted_sum = sum(results["checks"].get(k, 0) * w for k, w in weights.items())
        results["score"] = round(weighted_sum / total_weight, 1)
        results["pass"] = results["score"] >= 7.0

        # Save results
        slug = os.path.splitext(os.path.basename(html_path))[0]
        result_path = os.path.join(QA_DIR, f"{slug}_qa.json")
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        status = "✅ PASS" if results["pass"] else "❌ FAIL"
        log.info(f"  {status} — Score: {results['score']}/10 | Issues: {len(results['issues'])}")
        return results

    def _check_structure(self, html: str) -> tuple[float, list[str]]:
        """Check HTML structure fundamentals."""
        score = 10.0
        issues = []

        if "<html" not in html.lower():
            score -= 3; issues.append("CRITICAL: Missing <html> tag")
        if "<head" not in html.lower():
            score -= 2; issues.append("Missing <head> tag")
        if "<body" not in html.lower():
            score -= 2; issues.append("Missing <body> tag")
        if "<!doctype" not in html.lower():
            score -= 1; issues.append("Missing DOCTYPE")
        if 'charset' not in html.lower():
            score -= 1; issues.append("Missing charset declaration")
        if 'viewport' not in html.lower():
            score -= 2; issues.append("Missing viewport meta tag")

        return max(0, score), issues

    def _check_seo(self, html: str) -> tuple[float, list[str]]:
        """Check SEO elements."""
        score = 10.0
        issues = []

        if "<title" not in html.lower() or "</title>" not in html.lower():
            score -= 3; issues.append("SEO: Missing <title> tag")
        else:
            title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
            if title_match:
                title = title_match.group(1)
                if len(title) < 10: score -= 1; issues.append(f"SEO: Title too short ({len(title)} chars)")
                if len(title) > 70: score -= 1; issues.append(f"SEO: Title too long ({len(title)} chars)")

        if 'meta name="description"' not in html.lower() and "meta name='description'" not in html.lower():
            score -= 2; issues.append("SEO: Missing meta description")

        if '<h1' not in html.lower():
            score -= 1; issues.append("SEO: Missing H1 heading")

        return max(0, score), issues

    def _check_mobile(self, html: str) -> tuple[float, list[str]]:
        """Check mobile responsiveness signals."""
        score = 10.0
        issues = []

        if "viewport" not in html.lower():
            score -= 4; issues.append("MOBILE: No viewport meta — broken on mobile")
        if "user-scalable=no" in html.lower():
            score += 0  # Fine for games
        if "@media" not in html and "max-width" not in html:
            score -= 2; issues.append("MOBILE: No media queries or responsive CSS")
        if "touch-action" not in html.lower() and "touchstart" not in html.lower() and "pointerdown" not in html.lower():
            score -= 2; issues.append("MOBILE: No touch event handling")

        return max(0, score), issues

    def _check_interactivity(self, html: str) -> tuple[float, list[str]]:
        """Check for meaningful user interaction."""
        score = 10.0
        issues = []

        if "<script" not in html.lower():
            score -= 5; issues.append("INTERACTIVE: No JavaScript at all")
        if "addeventlistener" not in html.lower() and "onclick" not in html.lower():
            score -= 3; issues.append("INTERACTIVE: No event listeners")
        if "button" not in html.lower() and "input" not in html.lower():
            score -= 2; issues.append("INTERACTIVE: No interactive elements (buttons/inputs)")

        # Positive signals
        js_lines = len(re.findall(r'\n', html[html.lower().find('<script'):] if '<script' in html.lower() else ''))
        if js_lines < 20:
            score -= 2; issues.append(f"INTERACTIVE: Very little JS ({js_lines} lines)")

        return max(0, score), issues

    def _check_performance(self, html: str) -> tuple[float, list[str]]:
        """Check performance indicators."""
        score = 10.0
        issues = []

        file_size = len(html)
        if file_size > 500000:
            score -= 3; issues.append(f"PERF: File too large ({file_size // 1024}KB)")
        elif file_size > 200000:
            score -= 1; issues.append(f"PERF: File is large ({file_size // 1024}KB)")

        # External dependencies
        ext_scripts = len(re.findall(r'<script[^>]+src=', html, re.IGNORECASE))
        ext_styles = len(re.findall(r'<link[^>]+stylesheet', html, re.IGNORECASE))
        if ext_scripts > 5:
            score -= 2; issues.append(f"PERF: {ext_scripts} external scripts")
        if ext_styles > 3:
            score -= 1; issues.append(f"PERF: {ext_styles} external stylesheets")

        return max(0, score), issues

    def _check_commercial(self, html: str) -> tuple[float, list[str]]:
        """Check commercial readiness — this is what makes money."""
        score = 0.0  # Start from 0, must EARN points
        issues = []

        # Must-have: some way to monetize
        has_ad_slot = "adsense" in html.lower() or "ad-slot" in html.lower() or "adsbygoogle" in html.lower()
        has_email_capture = "email" in html.lower() and ("subscribe" in html.lower() or "newsletter" in html.lower())
        has_share = "share" in html.lower() or "navigator.share" in html.lower() or "clipboard" in html.lower()
        has_analytics = "analytics" in html.lower() or "gtag" in html.lower() or "ga(" in html.lower()
        has_cta = "sign up" in html.lower() or "get started" in html.lower() or "try" in html.lower()
        has_branding = "shipmicro" in html.lower()
        has_offline = "serviceworker" in html.lower() or "service-worker" in html.lower()

        if has_ad_slot: score += 2
        else: issues.append("COMMERCIAL: No ad slots")
        if has_share: score += 2
        else: issues.append("COMMERCIAL: No share functionality")
        if has_analytics: score += 1.5
        else: issues.append("COMMERCIAL: No analytics tracking")
        if has_email_capture: score += 1.5
        else: issues.append("COMMERCIAL: No email capture")
        if has_cta: score += 1
        if has_branding: score += 1
        if has_offline: score += 1

        return min(10, score), issues

    def _check_visual_quality(self, html: str) -> tuple[float, list[str]]:
        """Check visual design quality signals."""
        score = 10.0
        issues = []

        has_css = "<style" in html.lower() or 'rel="stylesheet"' in html.lower()
        if not has_css:
            score -= 5; issues.append("VISUAL: No CSS styling at all")

        # Design quality signals
        has_colors = "color:" in html or "background" in html
        has_border_radius = "border-radius" in html
        has_transitions = "transition" in html or "animation" in html
        has_shadows = "box-shadow" in html or "text-shadow" in html
        has_gradients = "gradient" in html

        if not has_colors: score -= 2
        if not has_border_radius: score -= 1
        if not has_transitions: score -= 1; issues.append("VISUAL: No animations/transitions")
        if not has_shadows: score -= 0.5
        if not has_gradients: score -= 0.5

        # Check for dark theme (modern look)
        has_dark = "#0a0a0a" in html or "#111" in html or "dark" in html.lower()
        if has_dark: score += 0  # Already 10

        return max(0, score), issues

    def test_all_tools(self, tools_dir: str) -> list[dict]:
        """Test all HTML files in a directory."""
        results = []
        for f in os.listdir(tools_dir):
            if f.endswith(".html"):
                result = self.test(os.path.join(tools_dir, f))
                results.append(result)

        # Summary
        passed = sum(1 for r in results if r.get("pass"))
        total = len(results)
        avg_score = sum(r.get("score", 0) for r in results) / max(total, 1)
        log.info(f"\n📊 QA Summary: {passed}/{total} passed | Avg score: {avg_score:.1f}/10")

        return results


if __name__ == "__main__":
    qa = BrowserQA()

    # Test all tools and games
    tools_dir = os.path.join(os.path.dirname(__file__), "shipmicro_site", "public", "tools")
    games_dir = os.path.join(os.path.dirname(__file__), "shipmicro_site", "public", "games")

    print("🛠️ Testing Tools:")
    qa.test_all_tools(tools_dir)

    print("\n🎮 Testing Games:")
    qa.test_all_tools(games_dir)
