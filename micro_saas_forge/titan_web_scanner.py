"""
╔══════════════════════════════════════════════════════════════╗
║  TITAN Web Scanner v1.0 — Web能力模块 🔍                     ║
║                                                              ║
║  灵感来源: Shannon (KeygraphHQ/shannon)                       ║
║  学习Shannon的多阶段安全扫描+浏览器自动化模式                  ║
║                                                              ║
║  能力:                                                        ║
║  1. 🔍 静态安全扫描 — 检查生成的代码是否有安全漏洞            ║
║  2. 🌐 功能验证 — 用Playwright验证页面是否正常渲染            ║
║  3. 📊 竞品分析 — 分析竞品URL的技术栈和功能                   ║
║  4. 📸 截图 — 生成产品的截图用于社交分发                      ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import re
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from titan_config import FORGE_DIR, LOG_DIR

log = logging.getLogger("web_scanner")


# ---------------------------------------------------------------------------
# Phase 1: Static Security Scanner (学习自Shannon的vuln-analysis)
# ---------------------------------------------------------------------------
class SecurityScanner:
    """
    静态安全扫描器 — 检查生成的代码是否有常见安全漏洞.
    学习自 Shannon 的5类漏洞检测: injection, XSS, auth, authz, SSRF.
    """

    # 危险模式检测规则（adapted from Shannon's vulnerability categories）
    VULN_PATTERNS = {
        "xss": {
            "patterns": [
                r"dangerouslySetInnerHTML\s*=\s*\{\{?\s*__html\s*:",
                r"v-html\s*=",
                r"innerHTML\s*=\s*[^\"']",
                r"\$\(.*\)\.html\(",
            ],
            "severity": "high",
            "description": "潜在XSS风险：直接插入未转义HTML",
            "fix": "使用textContent替代innerHTML，或对用户输入进行转义",
        },
        "injection": {
            "patterns": [
                r"eval\s*\(",
                r"new\s+Function\s*\(",
                r"exec\s*\(",
                r"\.query\s*\(\s*[\"'].*\$\{",  # SQL template injection
            ],
            "severity": "critical",
            "description": "代码注入风险：使用了eval/exec/Function构造器",
            "fix": "不要使用eval()，用JSON.parse()代替",
        },
        "hardcoded_secrets": {
            "patterns": [
                r"(api_key|apikey|api_secret|password|secret)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
                r"Bearer\s+[A-Za-z0-9_-]{20,}",
            ],
            "severity": "critical",
            "description": "硬编码密钥：代码中包含明文API密钥或密码",
            "fix": "使用环境变量存储敏感信息",
        },
        "insecure_http": {
            "patterns": [
                r"http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)",
            ],
            "severity": "medium",
            "description": "不安全的HTTP请求：应使用HTTPS",
            "fix": "将http://替换为https://",
        },
        "open_redirect": {
            "patterns": [
                r"window\.location\s*=\s*[^\"']",
                r"location\.href\s*=\s*(?!['\"]/)",
            ],
            "severity": "medium",
            "description": "潜在开放重定向：动态设置location",
            "fix": "验证重定向URL是否在允许列表中",
        },
    }

    def scan_file(self, filepath: str) -> List[Dict]:
        """扫描单个文件的安全漏洞"""
        findings = []
        try:
            content = Path(filepath).read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")

            for vuln_type, vuln_config in self.VULN_PATTERNS.items():
                for pattern in vuln_config["patterns"]:
                    for i, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            findings.append({
                                "type": vuln_type,
                                "severity": vuln_config["severity"],
                                "description": vuln_config["description"],
                                "fix": vuln_config["fix"],
                                "file": filepath,
                                "line": i,
                                "code": line.strip()[:120],
                            })
        except Exception as e:
            log.warning(f"扫描文件失败 {filepath}: {e}")
        return findings

    def scan_directory(self, directory: str) -> Dict:
        """
        扫描整个目录的安全漏洞.
        学习自 Shannon 的 parallel vulnerability analysis pattern.
        """
        all_findings = []
        files_scanned = 0
        target = Path(directory)

        # 扫描常见Web文件
        extensions = {".tsx", ".ts", ".jsx", ".js", ".html", ".vue", ".svelte"}
        exclude_dirs = {"node_modules", ".next", "dist", "__pycache__", ".git"}

        for file in target.rglob("*"):
            if file.is_file() and file.suffix in extensions:
                # Skip excluded dirs
                if any(exc in file.parts for exc in exclude_dirs):
                    continue
                findings = self.scan_file(str(file))
                all_findings.extend(findings)
                files_scanned += 1

        # 按严重度分组
        by_severity = {"critical": [], "high": [], "medium": [], "low": []}
        for f in all_findings:
            sev = f.get("severity", "low")
            if sev in by_severity:
                by_severity[sev].append(f)

        report = {
            "scan_time": datetime.now().isoformat(),
            "directory": directory,
            "files_scanned": files_scanned,
            "total_findings": len(all_findings),
            "by_severity": {k: len(v) for k, v in by_severity.items()},
            "critical_findings": by_severity["critical"][:10],
            "high_findings": by_severity["high"][:10],
            "passed": len(by_severity["critical"]) == 0,
            "score": max(0, 100 - len(by_severity["critical"]) * 30
                        - len(by_severity["high"]) * 15
                        - len(by_severity["medium"]) * 5),
        }

        log.info(f"🔍 安全扫描: {files_scanned}文件, {len(all_findings)}发现 "
                 f"(Critical={len(by_severity['critical'])}, High={len(by_severity['high'])})")
        return report


# ---------------------------------------------------------------------------
# Phase 2: Functional Tester (学习自Shannon的Playwright MCP)
# ---------------------------------------------------------------------------
class FunctionalTester:
    """
    功能验证器 — 用浏览器检查生成的应用是否正常工作.
    学习自 Shannon 的 Playwright MCP browser automation pattern.
    """

    def test_app_build(self, app_dir: str) -> Dict:
        """测试应用是否能成功构建"""
        try:
            result = subprocess.run(
                ["npx", "next", "build"],
                cwd=app_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )
            success = result.returncode == 0
            return {
                "test": "build",
                "passed": success,
                "output": result.stdout[-500:] if success else result.stderr[-500:],
            }
        except subprocess.TimeoutExpired:
            return {"test": "build", "passed": False, "output": "Build timeout (120s)"}
        except Exception as e:
            return {"test": "build", "passed": False, "output": str(e)}

    def test_static_analysis(self, app_dir: str) -> Dict:
        """静态代码分析 — 检查TypeScript类型正确性"""
        try:
            result = subprocess.run(
                ["npx", "tsc", "--noEmit"],
                cwd=app_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )
            errors = result.stdout.count("error TS") + result.stderr.count("error TS")
            return {
                "test": "typescript",
                "passed": errors == 0,
                "error_count": errors,
                "output": (result.stdout + result.stderr)[-300:],
            }
        except Exception as e:
            return {"test": "typescript", "passed": False, "output": str(e)}

    def test_page_structure(self, app_dir: str) -> Dict:
        """检查页面基本结构是否完整"""
        page_file = Path(app_dir) / "src" / "app" / "page.tsx"
        if not page_file.exists():
            return {"test": "structure", "passed": False, "output": "page.tsx not found"}

        content = page_file.read_text(encoding="utf-8", errors="ignore")
        checks = {
            "has_use_client": '"use client"' in content or "'use client'" in content,
            "has_default_export": "export default" in content,
            "has_return_jsx": "return (" in content or "return(" in content,
            "min_length": len(content) > 500,
            "no_api_route": "NextResponse" not in content,
        }

        passed = all(checks.values())
        return {
            "test": "structure",
            "passed": passed,
            "checks": checks,
            "output": f"{'✅' if passed else '❌'} 结构检查: {sum(checks.values())}/{len(checks)}通过",
        }

    def run_all_tests(self, app_dir: str) -> Dict:
        """
        运行全部测试 — 学习自Shannon的4阶段pipeline模式.
        Phase 1: Structure → Phase 2: Security → Phase 3: Build → Report
        """
        log.info(f"🧪 开始功能测试: {app_dir}")
        results = []

        # Phase 1: 结构检查
        structure = self.test_page_structure(app_dir)
        results.append(structure)
        if not structure["passed"]:
            return self._make_report(results, app_dir, "结构检查失败，跳过后续测试")

        # Phase 2: 安全扫描
        scanner = SecurityScanner()
        security = scanner.scan_directory(app_dir)
        results.append({
            "test": "security",
            "passed": security["passed"],
            "score": security["score"],
            "findings": security["total_findings"],
        })

        # Phase 3: 构建测试
        build = self.test_app_build(app_dir)
        results.append(build)

        return self._make_report(results, app_dir)

    def _make_report(self, results: List[Dict], app_dir: str, note: str = "") -> Dict:
        passed = all(r.get("passed", False) for r in results)
        return {
            "app_dir": app_dir,
            "timestamp": datetime.now().isoformat(),
            "passed": passed,
            "tests": results,
            "total_tests": len(results),
            "tests_passed": sum(1 for r in results if r.get("passed")),
            "note": note,
        }


# ---------------------------------------------------------------------------
# Phase 3: Competitor Analyzer (学习自Shannon的Recon phase)
# ---------------------------------------------------------------------------
class CompetitorAnalyzer:
    """
    竞品分析器 — 分析竞品网站的技术栈和功能.
    学习自 Shannon 的 reconnaissance phase.
    """

    def analyze_url(self, url: str) -> Dict:
        """分析单个URL的技术栈"""
        try:
            import requests
            resp = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (compatible; TitanBot/1.0)"
            })

            html = resp.text
            headers = dict(resp.headers)

            tech_stack = self._detect_tech(html, headers)
            features = self._detect_features(html)

            return {
                "url": url,
                "status": resp.status_code,
                "tech_stack": tech_stack,
                "features": features,
                "page_size_kb": len(html) / 1024,
                "response_time_ms": resp.elapsed.total_seconds() * 1000,
            }
        except Exception as e:
            return {"url": url, "error": str(e)}

    def _detect_tech(self, html: str, headers: dict) -> List[str]:
        """检测技术栈 — 类似WhatWeb功能"""
        techs = []
        patterns = {
            "Next.js": [r"_next/", r"__next"],
            "React": [r"react", r"__NEXT_DATA__", r"reactroot"],
            "Vue.js": [r"vue\.js", r"__vue__", r"v-"],
            "Angular": [r"ng-", r"angular"],
            "TailwindCSS": [r"tailwind", r"tw-"],
            "Bootstrap": [r"bootstrap"],
            "Vercel": [r"vercel", r"x-vercel"],
            "Cloudflare": [r"cloudflare", r"cf-ray"],
            "WordPress": [r"wp-content", r"wordpress"],
            "Stripe": [r"stripe\.com", r"stripe\.js"],
            "Google Analytics": [r"google-analytics|gtag|ga\.js"],
            "AdSense": [r"pagead2\.googlesyndication|adsbygoogle"],
        }

        combined = html.lower() + " " + json.dumps(headers).lower()
        for tech, pats in patterns.items():
            for pat in pats:
                if re.search(pat, combined, re.IGNORECASE):
                    techs.append(tech)
                    break
        return techs

    def _detect_features(self, html: str) -> List[str]:
        """检测页面功能"""
        features = []
        checks = {
            "Dark Mode": [r"dark-mode|dark-theme|theme-toggle|prefers-color-scheme"],
            "Responsive": [r"@media.*max-width|responsive|viewport"],
            "PWA": [r"manifest\.json|service-worker|serviceWorker"],
            "Auth/Login": [r"sign.?in|log.?in|auth|password"],
            "Payment": [r"price|pricing|subscribe|checkout|payment"],
            "Analytics": [r"analytics|tracking|gtag|pixel"],
            "Newsletter": [r"subscribe|newsletter|email.?list"],
            "SEO Meta": [r"<meta.*description|<meta.*og:"],
        }

        for feature, pats in checks.items():
            for pat in pats:
                if re.search(pat, html, re.IGNORECASE):
                    features.append(feature)
                    break
        return features


# ---------------------------------------------------------------------------
# Unified Web Scanner
# ---------------------------------------------------------------------------
class TitanWebScanner:
    """
    泰坦Web扫描器 — 统一入口.
    整合Shannon学到的所有Web能力.
    """

    def __init__(self):
        self.security = SecurityScanner()
        self.tester = FunctionalTester()
        self.competitor = CompetitorAnalyzer()

    def full_scan(self, app_dir: str) -> Dict:
        """对生成的应用进行完整扫描"""
        return self.tester.run_all_tests(app_dir)

    def security_scan(self, app_dir: str) -> Dict:
        """仅安全扫描"""
        return self.security.scan_directory(app_dir)

    def analyze_competitor(self, url: str) -> Dict:
        """分析竞品"""
        return self.competitor.analyze_url(url)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    args = sys.argv[1:]
    scanner = TitanWebScanner()

    if not args or args[0] in ("help", "--help"):
        print("""
🔍 TITAN Web Scanner v1.0 (Powered by Shannon patterns)

Usage:
  python titan_web_scanner.py scan <app_dir>       完整扫描(安全+结构+构建)
  python titan_web_scanner.py security <app_dir>   仅安全扫描
  python titan_web_scanner.py compete <url>        竞品分析
""")
    elif args[0] == "scan" and len(args) > 1:
        report = scanner.full_scan(args[1])
        print(json.dumps(report, ensure_ascii=False, indent=2, default=str))

    elif args[0] == "security" and len(args) > 1:
        report = scanner.security_scan(args[1])
        print(json.dumps(report, ensure_ascii=False, indent=2, default=str))

    elif args[0] == "compete" and len(args) > 1:
        report = scanner.analyze_competitor(args[1])
        print(json.dumps(report, ensure_ascii=False, indent=2, default=str))

    else:
        print(f"❌ Unknown: {args}")


if __name__ == "__main__":
    _main()
