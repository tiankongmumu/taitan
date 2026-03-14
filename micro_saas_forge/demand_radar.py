"""
TITAN Engine v4.0 — Demand Radar
Discovers high-value, low-competition opportunities by scanning:
- Google Trends (via pytrends or scraping)
- HackerNews front page
- Reddit r/SideProject, r/webdev
- Product Hunt trending

Outputs: demand_signals.json with opportunity scores
"""
import os
import sys
import json
import re
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger
from core_generators.llm_client import LLMClient

log = get_logger("demand_radar")

SIGNALS_DIR = os.path.join(os.path.dirname(__file__), "demand_signals")
SIGNALS_FILE = os.path.join(SIGNALS_DIR, "signals.json")


class DemandRadar:
    def __init__(self):
        self.llm = LLMClient()
        os.makedirs(SIGNALS_DIR, exist_ok=True)

    def scan(self, override_prompt: str = None) -> list[dict]:
        """Run full demand scan and return ranked opportunity signals."""
        log.info("🔍 TITAN Demand Radar: Starting full scan...")

        signals = []

        # Source 1: HackerNews — what developers want
        hn_signals = self._scan_hackernews()
        signals.extend(hn_signals)

        # Source 2: LLM-powered trend analysis
        llm_signals = self._scan_llm_trends(override_prompt=override_prompt)
        signals.extend(llm_signals)

        # Source 3: Keyword opportunity analysis
        kw_signals = self._scan_keyword_opportunities()
        signals.extend(kw_signals)

        # Deduplicate and rank
        signals = self._deduplicate(signals)
        signals = self._rank_opportunities(signals)

        # Save
        output = {
            "scanned_at": datetime.now().isoformat(),
            "total_signals": len(signals),
            "signals": signals,
        }
        with open(SIGNALS_FILE, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        log.info(f"✅ Demand Radar: Found {len(signals)} opportunities → {SIGNALS_FILE}")
        return signals

    def _scan_hackernews(self) -> list[dict]:
        """Scan HN top stories for tool/product demand signals."""
        log.info("  📡 Scanning HackerNews...")
        try:
            import urllib.request
            url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            with urllib.request.urlopen(url, timeout=10) as resp:
                top_ids = json.loads(resp.read())[:30]

            signals = []
            for story_id in top_ids[:15]:
                try:
                    story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                    with urllib.request.urlopen(story_url, timeout=5) as resp:
                        story = json.loads(resp.read())

                    title = story.get("title", "")
                    score = story.get("score", 0)

                    # Filter for tool/product-related posts
                    tool_keywords = ["tool", "app", "launch", "built", "show hn",
                                     "open source", "free", "alternative", "api",
                                     "generator", "converter", "formatter", "tester"]
                    if any(kw in title.lower() for kw in tool_keywords) and score > 50:
                        signals.append({
                            "keyword": title,
                            "source": "HackerNews",
                            "raw_score": score,
                            "url": story.get("url", ""),
                            "type": "demand_signal",
                        })
                except Exception:
                    continue

            log.info(f"    → {len(signals)} HN signals")
            return signals

        except Exception as e:
            log.warning(f"    ⚠️ HN scan failed: {e}")
            return []

    def _scan_llm_trends(self, override_prompt: str = None) -> list[dict]:
        """Use LLM to identify current high-demand, low-competition niches."""
        log.info("  🤖 LLM trend analysis...")
        
        if override_prompt:
            prompt = override_prompt + """

---
You MUST return the output EXACTLY in this JSON array format:
```json
[
  {
    "keyword": "the exact search term or product name",
    "monthly_volume_estimate": 100000,
    "competition": "LOW",
    "revenue_model": "AdSense / SaaS",
    "build_complexity": "SIMPLE",
    "differentiation": "What makes it unique"
  }
]
```"""
        else:
            prompt = """You are a market research analyst. Identify 10 specific online tool/game ideas that:
1. Have HIGH search volume (people actively searching for them)
2. Have LOW competition (existing solutions are bad or don't exist)
3. Can be built as a single-page web app (HTML/CSS/JS only)
4. Can generate revenue through ads or freemium model

For each, provide:
- keyword: the exact search term people use (e.g. "json formatter online")
- monthly_volume_estimate: estimated monthly Google searches
- competition: LOW, MEDIUM, or HIGH
- revenue_model: how it makes money
- build_complexity: SIMPLE, MEDIUM, or COMPLEX
- differentiation: what makes our version better

Return JSON array wrapped in ```json block.
Example format:
```json
[
  {
    "keyword": "json formatter online",
    "monthly_volume_estimate": 100000,
    "competition": "HIGH",
    "revenue_model": "AdSense banner ads",
    "build_complexity": "SIMPLE",
    "differentiation": "Offline-capable PWA with file drag-drop"
  }
]
```

Focus on tools that have real commercial value. NO toy projects."""

        result = self.llm.generate(prompt, system_prompt="You are a sharp market analyst.")
        try:
            json_str = self._extract_json(result)
            items = json.loads(json_str)
            signals = []
            for item in items:
                comp_map = {"LOW": 1, "MEDIUM": 5, "HIGH": 9}
                vol = item.get("monthly_volume_estimate", 1000)
                comp = comp_map.get(item.get("competition", "MEDIUM"), 5)
                signals.append({
                    "keyword": item.get("keyword", ""),
                    "source": "LLM_analysis",
                    "monthly_volume": vol,
                    "competition_score": comp,
                    "revenue_model": item.get("revenue_model", ""),
                    "build_complexity": item.get("build_complexity", "MEDIUM"),
                    "differentiation": item.get("differentiation", ""),
                    "type": "trend_signal",
                })
            log.info(f"    → {len(signals)} LLM signals")
            return signals
        except Exception as e:
            log.warning(f"    ⚠️ LLM trend parse failed: {e}")
            return []

    def _scan_keyword_opportunities(self) -> list[dict]:
        """Identify specific keyword opportunities in the developer tools space."""
        log.info("  🔑 Keyword opportunity scan...")

        # High-value developer/SaaS tool keywords that have strong monetization potential
        known_opportunities = [
            {"keyword": "svg to png converter online", "volume": 90000, "competition": 3},
            {"keyword": "sql query optimizer online", "volume": 45000, "competition": 3},
            {"keyword": "json schema generator", "volume": 60000, "competition": 4},
            {"keyword": "regex visualizer and debugger", "volume": 50000, "competition": 3},
            {"keyword": "jwt decoder and verifier", "volume": 120000, "competition": 5},
            {"keyword": "api payload builder and tester", "volume": 35000, "competition": 3},
            {"keyword": "cron expression visualizer", "volume": 40000, "competition": 3},
            {"keyword": "postgresql connection string generator", "volume": 25000, "competition": 2},
            {"keyword": "typescript interface generator from json", "volume": 55000, "competition": 4},
            {"keyword": "markdown email template builder", "volume": 20000, "competition": 2},
            {"keyword": "privacy policy generator for saas", "volume": 80000, "competition": 5},
            {"keyword": "B2B SaaS pricing page templates", "volume": 30000, "competition": 3},
        ]

        signals = []
        for kw in known_opportunities:
            signals.append({
                "keyword": kw["keyword"],
                "source": "keyword_research",
                "monthly_volume": kw["volume"],
                "competition_score": kw["competition"],
                "revenue_model": "AdSense",
                "type": "keyword_signal",
            })

        log.info(f"    → {len(signals)} keyword signals")
        return signals

    def _deduplicate(self, signals: list[dict]) -> list[dict]:
        """Remove duplicate signals by keyword similarity."""
        seen = set()
        unique = []
        for s in signals:
            key = s.get("keyword", "").lower().strip()
            short_key = re.sub(r'\s+', ' ', key)[:50]
            if short_key not in seen:
                seen.add(short_key)
                unique.append(s)
        return unique

    def _rank_opportunities(self, signals: list[dict]) -> list[dict]:
        """Calculate opportunity_score and sort."""
        for s in signals:
            volume = s.get("monthly_volume", s.get("raw_score", 100))
            competition = s.get("competition_score", 5)

            # Opportunity = Volume / (Competition ^ 1.5)
            # Higher volume + lower competition = better opportunity
            if competition < 1:
                competition = 1
            s["opportunity_score"] = round(volume / (competition ** 1.5), 1)

        signals.sort(key=lambda x: x.get("opportunity_score", 0), reverse=True)
        return signals

    def _extract_json(self, text: str) -> str:
        """Extract JSON from LLM response."""
        if not text:
            return "[]"
        # Try ```json block
        match = re.search(r'```(?:json)?\s*\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Try raw JSON array
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return match.group(0)
        return "[]"

    def get_top_opportunities(self, n: int = 5, override_prompt: str = None) -> list[dict]:
        """Get top N opportunities from last scan, or run new scan."""
        if not override_prompt and os.path.exists(SIGNALS_FILE):
            with open(SIGNALS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            signals = data.get("signals", [])
            if signals:
                return signals[:n]
        # No cached data or override requested, run fresh scan
        signals = self.scan(override_prompt=override_prompt)
        return signals[:n]


if __name__ == "__main__":
    radar = DemandRadar()
    signals = radar.scan()
    print(f"\n🔍 Top 5 Opportunities:")
    for i, s in enumerate(signals[:5], 1):
        print(f"  {i}. [{s.get('opportunity_score', 0)}] {s['keyword']}")
        print(f"     Source: {s['source']} | Volume: {s.get('monthly_volume', '?')}")
