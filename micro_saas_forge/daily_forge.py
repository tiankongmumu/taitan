"""
Micro-SaaS Forge — Daily Forge (v3 - Restored)
=================================================
Generates, validates, and ships new micro-tool/game ideas daily.
Called by autonomous_ceo.py in frenzy mode.
"""
import os
import sys
import json
import time
import random
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field
import re
import hashlib
from enum import Enum
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from forge_master import ForgeMaster
from logger import get_logger

log = get_logger("daily")


class Verdict(str, Enum):
    SHIP = "SHIP"
    MAYBE = "MAYBE"
    KILL = "KILL"


@dataclass
class Idea:
    name: str
    description: str
    category: str
    tech_stack: List[str] = field(default_factory=list)
    score: Optional[int] = None
    utility: Optional[int] = None
    uniqueness: Optional[int] = None
    seo: Optional[int] = None
    feasibility: Optional[int] = None
    verdict: Optional[Verdict] = None
    id: str = field(default_factory=lambda: hashlib.sha256(
        f"{time.time_ns()}{random.random()}".encode()
    ).hexdigest()[:12])
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['weighted_score'] = self.weighted_score
        return data

    @property
    def weighted_score(self) -> float:
        if None in (self.utility, self.uniqueness, self.seo, self.feasibility):
            return 0.0
        weights = [0.35, 0.25, 0.25, 0.15]  # utility, uniqueness, seo, feasibility
        scores = [self.utility, self.uniqueness, self.seo, self.feasibility]
        return sum(w * s for w, s in zip(weights, scores)) * 3.33


class IdeaGenerator:
    """Generate innovative micro-tool and game ideas via LLM."""

    CATEGORIES = [
        "Code", "Data", "API", "Design", "Text", "Security",
        "DevOps", "Productivity", "Game", "AI", "Web3", "Mobile"
    ]

    TECH_STACKS = {
        "Code": ["Next.js 15", "TypeScript", "Tailwind CSS", "Framer Motion"],
        "Game": ["HTML5 Canvas", "CSS Animations", "JavaScript", "Web Audio API"],
        "AI": ["TensorFlow.js", "OpenAI API", "Vercel AI SDK"],
        "Design": ["GSAP", "Three.js", "Canvas API", "SVG"],
        "Data": ["D3.js", "Chart.js", "Recharts", "Observable"],
    }

    def __init__(self):
        self.llm = LLMClient()

    def generate_prompt(self, num_candidates: int) -> str:
        current_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        categories = ', '.join(random.sample(self.CATEGORIES, min(6, len(self.CATEGORIES))))

        return f"""You are the Chief Product Officer at ShipMicro.com.
Today is {current_date}. Generate exactly {num_candidates} innovative micro-tool or game ideas.

REQUIREMENTS:
1. Each must be buildable as a single HTML file with embedded CSS/JS
2. Must work entirely client-side (no server needed)
3. Must be immediately useful or fun
4. Should have strong SEO potential (people searching for this tool)
5. Must be visually polished with dark mode and smooth animations

Categories to focus on: {categories}

For EACH idea, provide a JSON array:
```json
[
  {{
    "name": "Tool Name Here",
    "description": "One compelling sentence about what it does and why it's useful.",
    "category": "Category",
    "tech_stack": ["HTML5", "CSS3", "JavaScript"]
  }}
]
```

Be creative and practical. Avoid generic converters. Think about what developers and creators actually need."""

    def generate_ideas(self, num_candidates: int = 5) -> List[Idea]:
        """Generate ideas via LLM."""
        prompt = self.generate_prompt(num_candidates)
        response = self.llm.generate(prompt, is_json=True)

        if not response:
            log.warning("LLM returned empty response, using curated fallback")
            return self.get_curated_ideas()[:num_candidates]

        return self.parse_response(response, num_candidates)

    def parse_response(self, response: str, num_candidates: int) -> List[Idea]:
        """Parse LLM response into Idea objects."""
        ideas = []

        # Try to extract JSON
        json_str = None
        for pattern in [r'```json\s*(.*?)\s*```', r'```\s*(.*?)\s*```', r'\[\s*\{.*?\}\s*\]']:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                json_str = match.group(1).strip() if '```' in pattern else match.group(0)
                break

        if not json_str:
            json_str = response.strip()

        try:
            data = json.loads(json_str)
            if not isinstance(data, list):
                data = [data]

            for item in data[:num_candidates]:
                try:
                    idea = Idea(
                        name=self._clean_name(item.get('name', 'Unnamed Tool')),
                        description=item.get('description', 'No description.'),
                        category=item.get('category', 'Code'),
                        tech_stack=item.get('tech_stack', ['HTML5', 'CSS3', 'JavaScript']),
                    )
                    ideas.append(idea)
                except Exception as e:
                    log.debug(f"Failed to parse item: {e}")
                    continue
        except json.JSONDecodeError as e:
            log.warning(f"JSON decode failed: {e}")

        if not ideas:
            log.warning("No ideas parsed, falling back to curated list")
            ideas = self.get_curated_ideas()[:num_candidates]

        return ideas

    def _clean_name(self, name: str) -> str:
        name = re.sub(r'[^\w\s\-\.]', '', name)
        return ' '.join(word.capitalize() for word in name.split())

    def get_curated_ideas(self) -> List[Idea]:
        """Fallback curated ideas if LLM fails."""
        return [
            Idea(name="Regex Playground", description="Interactive regex tester with real-time matching, explanation, and common pattern library.", category="Code"),
            Idea(name="CSS Grid Builder", description="Visual CSS Grid layout builder with drag-and-drop and live code output.", category="Design"),
            Idea(name="API Status Dashboard", description="Real-time status checker for popular APIs with latency graphs.", category="DevOps"),
            Idea(name="Pixel Art Creator", description="Browser-based pixel art editor with layers, animation, and GIF export.", category="Game"),
            Idea(name="Markdown Resume Builder", description="Write your resume in Markdown, export as beautiful PDF.", category="Productivity"),
        ]


class QualityChecker:
    """Score and filter ideas for quality."""

    def __init__(self):
        self.llm = LLMClient()
        self._existing_slugs = self._load_existing_slugs()

    def _load_existing_slugs(self) -> set:
        """Load existing tool slugs from history.json for dedup."""
        history_path = os.path.join(os.path.dirname(__file__), "history.json")
        if os.path.exists(history_path):
            try:
                with open(history_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
                return {h.get("slug", "").lower() for h in history}
            except Exception:
                pass
        return set()

    def _is_duplicate(self, idea: Idea) -> bool:
        """Check if idea is too similar to an existing tool."""
        slug = re.sub(r'[^a-z0-9]+', '-', idea.name.lower()).strip('-')
        if slug in self._existing_slugs:
            return True
        # Check name similarity with existing slugs
        for existing in self._existing_slugs:
            existing_words = set(existing.split('-'))
            new_words = set(slug.split('-'))
            if existing_words and new_words:
                overlap = len(existing_words & new_words) / max(len(existing_words), len(new_words))
                if overlap >= 0.8:
                    return True
        return False

    def evaluate(self, idea: Idea) -> Idea:
        """Score an idea using LLM with dedup check."""
        # Dedup check first
        if self._is_duplicate(idea):
            log.info(f"  🔄 DEDUP: '{idea.name}' 与已有工具重复，自动 KILL")
            idea.utility = 1
            idea.uniqueness = 1
            idea.seo = 1
            idea.feasibility = 1
            idea.verdict = Verdict.KILL
            return idea

        prompt = f"""Rate this micro-tool/game idea on four dimensions (1-10 each):

Name: {idea.name}
Description: {idea.description}
Category: {idea.category}

Rate:
1. utility (1-10): How useful/fun is this? Would people actually use it regularly?
2. uniqueness (1-10): How novel is this compared to existing free tools online?
3. seo (1-10): How likely are people to actively search for this exact tool?
4. feasibility (1-10): Can this be built as a single-page client-side app with NO backend? (10=pure frontend, 1=needs complex server)

ALSO give a verdict: SHIP (avg >= 7.8), MAYBE (5.5-7.7), or KILL (< 5.5).
Be HONEST and HARSH. Most ideas should be MAYBE, not SHIP.

Respond in JSON:
{{"utility": 8, "uniqueness": 7, "seo": 6, "feasibility": 9, "verdict": "SHIP"}}"""

        response = self.llm.generate(prompt, is_json=True)

        try:
            json_match = re.search(r'\{.*?\}', response, re.DOTALL)
            if json_match:
                scores = json.loads(json_match.group())
                idea.utility = max(1, min(10, int(scores.get('utility', 5))))
                idea.uniqueness = max(1, min(10, int(scores.get('uniqueness', 5))))
                idea.seo = max(1, min(10, int(scores.get('seo', 5))))
                idea.feasibility = max(1, min(10, int(scores.get('feasibility', 5))))
                verdict_str = scores.get('verdict', 'MAYBE').upper()
                idea.verdict = Verdict(verdict_str) if verdict_str in Verdict.__members__ else Verdict.MAYBE
            else:
                idea.utility = 6
                idea.uniqueness = 5
                idea.seo = 5
                idea.feasibility = 6
                idea.verdict = Verdict.MAYBE
        except Exception as e:
            log.warning(f"Failed to parse quality scores: {e}")
            idea.utility = 6
            idea.uniqueness = 5
            idea.seo = 5
            idea.feasibility = 6
            idea.verdict = Verdict.MAYBE

        return idea


def main():
    parser = argparse.ArgumentParser(description="Daily Forge — Generate and ship micro-tools")
    parser.add_argument('--count', type=int, default=3, help='Number of ideas to generate')
    parser.add_argument('--limit', type=int, default=1, help='Number of top ideas to actually build')
    parser.add_argument('--dry-run', action='store_true', help='Generate ideas without building')
    parser.add_argument('--stats', action='store_true', help='Show run statistics')
    args = parser.parse_args()

    if args.stats:
        from run_history import print_stats
        print_stats()
        return

    log.info("=" * 60)
    log.info("🔥 DAILY FORGE — 启动产品铸造流程")
    log.info(f"  生成 {args.count} 个点子, 取 Top-{args.limit} 构建")
    log.info("=" * 60)

    generator = IdeaGenerator()
    ideas = generator.generate_ideas(args.count)
    log.info(f"✅ 生成了 {len(ideas)} 个点子")

    if not ideas:
        log.error("❌ 没有生成任何点子, 退出")
        return

    checker = QualityChecker()
    for i, idea in enumerate(ideas):
        log.info(f"\n📊 评估 [{i+1}/{len(ideas)}]: {idea.name}")
        ideas[i] = checker.evaluate(idea)
        log.info(f"  评分: U={idea.utility} Q={idea.uniqueness} S={idea.seo} F={idea.feasibility} → {idea.weighted_score:.1f} [{idea.verdict.value}]")

    ideas.sort(key=lambda x: x.weighted_score, reverse=True)
    top_ideas = [i for i in ideas if i.verdict != Verdict.KILL][:args.limit]

    if not top_ideas:
        log.warning("⚠️ 没有通过质量筛选的点子")
        top_ideas = ideas[:args.limit]

    log.info(f"\n🏆 Top {len(top_ideas)} 点子:")
    for i, idea in enumerate(top_ideas):
        log.info(f"  #{i+1}: {idea.name} (score={idea.weighted_score:.1f}, verdict={idea.verdict.value})")

    if args.dry_run:
        log.info("🏁 Dry-run 模式 — 跳过构建")
        for idea in top_ideas:
            print(json.dumps(idea.to_dict(), ensure_ascii=False, indent=2))
        return

    forge = ForgeMaster()
    for idea in top_ideas:
        raw_idea = f"{idea.name}: {idea.description}"
        log.info(f"\n🚀 开始构建: {idea.name}")
        result = forge.run_pipeline(raw_idea)
        if result['success']:
            log.info(f"✅ 构建成功: {result.get('url', 'N/A')}")
        else:
            log.warning(f"⚠️ 构建失败: {idea.name}")


if __name__ == "__main__":
    main()