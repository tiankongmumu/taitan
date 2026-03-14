"""
Micro-SaaS Forge — SEO 引擎 (v2)
支持：LLM 生成高质量博客文章、长尾关键词挖掘、sitemap 片段。
"""
import os
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SEO_ASSETS_DIR
from logger import get_logger
from core_generators.llm_client import LLMClient

log = get_logger("seo")


class BasicSEO:
    def __init__(self):
        self.output_dir = SEO_ASSETS_DIR
        self.llm = LLMClient()

    def generate_seo_assets(self, app_spec: dict, deployment_url: str):
        """生成完整的 SEO 资产包：博客文章 + 社区推广帖 + SEO payload + sitemap 片段。"""
        os.makedirs(self.output_dir, exist_ok=True)
        app_seo_dir = os.path.join(self.output_dir, app_spec["slug"])
        os.makedirs(app_seo_dir, exist_ok=True)

        log.info(f"生成 SEO 资产: {app_spec['name']}")

        # 1. LLM 生成高质量博客文章
        blog_content = self._generate_blog_article(app_spec, deployment_url)

        # 2. 社区推广帖（Reddit/HackerNews 风格）
        launch_post = self._generate_launch_post(app_spec, deployment_url)

        # 3. SEO 元数据 payload
        longtail_keywords = [
            f"how to solve {app_spec['pain_point'].lower()}",
            f"best tool for {app_spec['pain_point'].lower()}",
            f"free {app_spec['name'].lower()} alternative",
            f"{app_spec['name'].lower()} online tool",
            f"solve {app_spec['pain_point'].lower()} fast",
        ]
        seo_json = {
            "title_tag": f"{app_spec['name']} - Solve {app_spec['pain_point']} Fast",
            "meta_description": f"The easiest way to deal with {app_spec['pain_point']}. Try {app_spec['name']} free.",
            "h1": app_spec["name"],
            "url": deployment_url,
            "keywords": longtail_keywords,
        }

        # 4. Sitemap XML 片段
        sitemap_entry = f"""  <url>
    <loc>{deployment_url}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>"""

        # 写入文件
        self._write(app_seo_dir, "BLOG_ARTICLE.md", blog_content)
        self._write(app_seo_dir, "LAUNCH_POST.md", launch_post)
        self._write(app_seo_dir, "seo_payload.json", json.dumps(seo_json, indent=2, ensure_ascii=False))
        self._write(app_seo_dir, "sitemap_entry.xml", sitemap_entry)

        log.info(f"SEO 资产已保存至 {app_seo_dir}")

    def _generate_blog_article(self, app_spec: dict, url: str) -> str:
        """用 LLM 生成一篇 800+ 字的 SEO 优化博客文章。"""
        log.info("LLM 生成博客文章...")
        prompt = f"""
Write a high-quality, SEO-optimized blog article (800-1000 words) in English about this tool:
- Name: {app_spec['name']}
- Problem it solves: {app_spec['pain_point']}
- Features: {', '.join(app_spec['core_features'])}
- URL: {url}

Requirements:
1. Title should be attention-grabbing and include the main keyword.
2. Use H2 and H3 headings for structure (markdown format).
3. Include a "How to use" section with step-by-step instructions.
4. End with a clear CTA linking to the tool.
5. Naturally include keywords like "how to solve {app_spec['pain_point'].lower()}" and "best tool for {app_spec['pain_point'].lower()}".
6. Write in a professional but approachable tone.
"""
        result = self.llm.generate(
            prompt,
            system_prompt="You are an expert SEO content writer who creates engaging, informative articles.",
        )
        return result if result else self._fallback_blog(app_spec, url)

    def _generate_launch_post(self, app_spec: dict, url: str) -> str:
        """生成社区推广帖。"""
        log.info("LLM 生成社区推广帖...")
        prompt = f"""
Write a brief, authentic-sounding launch post for sharing on Reddit (r/SideProject) or Hacker News.
- Tool: {app_spec['name']}
- Problem: {app_spec['pain_point']}
- URL: {url}

Requirements:
1. Keep it under 200 words. Be genuine, not salesy.
2. Mention you built this and are looking for feedback.
3. Include the URL naturally.
"""
        result = self.llm.generate(
            prompt,
            system_prompt="You are an indie developer who just launched a new tool.",
        )
        return result if result else f"# {app_spec['name']}\n\nCheck it out: {url}"

    def _fallback_blog(self, app_spec: dict, url: str) -> str:
        """LLM 失败时的兜底博客模板。"""
        features = "\n".join([f"- {f}" for f in app_spec["core_features"]])
        return f"""# How to Solve {app_spec['pain_point']} with {app_spec['name']}

Tired of {app_spec['pain_point']}? **{app_spec['name']}** is here to help.

## Key Features
{features}

## Try It Now
[Get started with {app_spec['name']}]({url})
"""

    def _write(self, directory: str, filename: str, content: str):
        path = os.path.join(directory, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    # ═══════════════════════════════════════════════════
    # v2: Dynamic SEO (Roundtable Upgrade 5)
    # ═══════════════════════════════════════════════════

    def generate_dynamic_meta(self, app_spec: dict, deployment_url: str) -> dict:
        """
        v2: 基于 analytics_data/forge_signals.json 的真实数据
        动态调整 SEO 标题和描述（而非写死的关键词）
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        signals_path = os.path.join(base_dir, "analytics_data", "forge_signals.json")

        # 读取分析信号
        performance_hint = ""
        if os.path.exists(signals_path):
            with open(signals_path, "r", encoding="utf-8") as f:
                signals = json.load(f)
            # 如果这个工具有 UI 测试高分，强调质量
            slug = app_spec.get("slug", "")
            tool_perf = signals.get("tool_performance", {}).get(slug, {})
            if tool_perf.get("ui_score", 0) >= 8:
                performance_hint = "This is a high-quality, well-tested tool. Emphasize reliability and polish."
            elif tool_perf.get("ui_score", 0) >= 5:
                performance_hint = "Emphasize simplicity and ease of use."

        prompt = f"""
Generate optimized SEO metadata for this web tool:
- Name: {app_spec.get('name', '')}
- Problem: {app_spec.get('pain_point', '')}
- URL: {deployment_url}
{performance_hint}

Return JSON:
{{
  "title": "< 60 chars, SEO optimized",
  "description": "< 155 chars, compelling with CTA",
  "keywords": ["kw1", "kw2", "kw3", "kw4", "kw5"],
  "h1": "main heading"
}}
Wrap in ```json block.
"""
        result = self.llm.generate(prompt)
        try:
            from core_generators.llm_client import LLMClient
            json_str = LLMClient().extract_code_block(result) if result else ""
            meta = json.loads(json_str) if json_str else {}
        except (json.JSONDecodeError, TypeError):
            meta = {
                "title": f"{app_spec.get('name', '')} - Solve {app_spec.get('pain_point', '')} Fast",
                "description": f"The easiest way to deal with {app_spec.get('pain_point', '')}. Try free.",
                "keywords": [app_spec.get('pain_point', '').lower()],
                "h1": app_spec.get('name', ''),
            }

        log.info(f"📈 Dynamic SEO: {meta.get('title', '')[:50]}")
        return meta

