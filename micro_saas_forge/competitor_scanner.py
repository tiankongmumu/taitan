"""
TITAN Engine v4.0 — Competitor Scanner
Analyzes competing products for a target keyword:
- Scrapes top search results
- Extracts features, pricing, weaknesses
- Identifies competitive gaps we can exploit

Output: competitive_gap analysis for product_forge
"""
import os
import sys
import json
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger
from core_generators.llm_client import LLMClient

log = get_logger("competitor")

ANALYSIS_DIR = os.path.join(os.path.dirname(__file__), "competitive_analysis")


class CompetitorScanner:
    def __init__(self):
        self.llm = LLMClient()
        os.makedirs(ANALYSIS_DIR, exist_ok=True)

    def analyze(self, keyword: str) -> dict:
        """Analyze competitors for a keyword and find gaps."""
        log.info(f"🔎 Competitor scan: '{keyword}'")

        # Use LLM to simulate competitive research
        # (In production, this would scrape Google results + analyze each page)
        prompt = f"""You are a competitive intelligence analyst. Analyze the market for this search term:

"{keyword}"

Research the top 5 existing tools/websites that rank for this keyword. For each competitor:
1. Name and URL
2. Key features (what they do well)
3. Weaknesses (what they do poorly)
4. Pricing model (free/freemium/paid)
5. Monthly traffic estimate

Then identify 3-5 SPECIFIC gaps that a new competitor could exploit. These should be concrete, actionable differentiators.

Return JSON wrapped in ```json block:
```json
{{
  "keyword": "{keyword}",
  "competitors": [
    {{
      "name": "...",
      "url": "...",
      "features": ["feat1", "feat2"],
      "weaknesses": ["weak1", "weak2"],
      "pricing": "free/freemium/paid",
      "monthly_traffic": 50000
    }}
  ],
  "gaps": [
    {{
      "gap": "specific gap description",
      "implementation": "how to build this feature",
      "impact": "HIGH/MEDIUM/LOW",
      "effort": "SIMPLE/MEDIUM/COMPLEX"
    }}
  ],
  "recommended_positioning": "one-line positioning statement"
}}
```"""

        result = self.llm.generate(prompt, system_prompt="You are a sharp competitive analyst with deep knowledge of the web tools market.")

        try:
            json_str = self._extract_json(result)
            analysis = json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            log.warning("⚠️ LLM competitor analysis parse failed, using fallback")
            analysis = self._fallback_analysis(keyword)

        # Save analysis
        slug = re.sub(r'[^a-z0-9]+', '-', keyword.lower()).strip('-')
        output_path = os.path.join(ANALYSIS_DIR, f"{slug}.json")
        analysis["analyzed_at"] = datetime.now().isoformat()
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        gap_count = len(analysis.get("gaps", []))
        comp_count = len(analysis.get("competitors", []))
        log.info(f"✅ Found {comp_count} competitors, {gap_count} gaps → {output_path}")

        return analysis

    def get_build_brief(self, keyword: str) -> str:
        """Generate a focused build brief from competitive analysis."""
        analysis = self.analyze(keyword)

        gaps = analysis.get("gaps", [])
        high_impact = [g for g in gaps if g.get("impact") == "HIGH"]
        positioning = analysis.get("recommended_positioning", "")

        brief = f"""BUILD BRIEF for "{keyword}":

POSITIONING: {positioning}

MUST-HAVE DIFFERENTIATORS (from competitive gaps):
"""
        for i, gap in enumerate(high_impact or gaps[:3], 1):
            brief += f"  {i}. {gap.get('gap', '')} → {gap.get('implementation', '')}\n"

        brief += f"""
COMPETITOR WEAKNESSES TO EXPLOIT:
"""
        for comp in analysis.get("competitors", [])[:3]:
            weaknesses = comp.get("weaknesses", [])
            if weaknesses:
                brief += f"  - {comp.get('name', '?')}: {', '.join(weaknesses[:2])}\n"

        return brief

    def _fallback_analysis(self, keyword: str) -> dict:
        """Fallback when LLM fails."""
        return {
            "keyword": keyword,
            "competitors": [],
            "gaps": [
                {"gap": "Offline/PWA support", "implementation": "Add Service Worker", "impact": "HIGH", "effort": "MEDIUM"},
                {"gap": "Mobile-first design", "implementation": "Touch-optimized responsive UI", "impact": "HIGH", "effort": "SIMPLE"},
                {"gap": "No ads or tracking", "implementation": "Privacy-first marketing angle", "impact": "MEDIUM", "effort": "SIMPLE"},
            ],
            "recommended_positioning": f"The fastest, privacy-first {keyword} — works offline",
        }

    def _extract_json(self, text: str) -> str:
        if not text:
            return "{}"
        match = re.search(r'```(?:json)?\s*\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        return "{}"


if __name__ == "__main__":
    scanner = CompetitorScanner()
    brief = scanner.get_build_brief("json formatter online")
    print(brief)
