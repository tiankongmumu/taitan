"""
╔══════════════════════════════════════════════════╗
║  TITAN Forge v1.0 — 统一代码生成器               ║
║  合并自: forge_master + hyper_forge + daily_forge ║
║  功能: 创意生成 → 质量评分 → 代码构建 → 断点恢复  ║
╚══════════════════════════════════════════════════╝
"""
import os
import sys
import json
import time
import hashlib
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from core_generators.app_builder import AppBuilder
from logger import get_logger

log = get_logger("titan_forge")

FORGE_DIR = os.path.dirname(os.path.abspath(__file__))
CHECKPOINT_FILE = os.path.join(FORGE_DIR, "checkpoint.json")
HISTORY_FILE = os.path.join(FORGE_DIR, "history.json")


# ═══════════════════════════════════════════
# Data Models (来自 daily_forge)
# ═══════════════════════════════════════════

class Verdict(Enum):
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
    verdict: Optional[str] = None
    slug: str = field(default_factory=lambda: "")

    def __post_init__(self):
        if not self.slug:
            self.slug = self.name.lower().replace(" ", "-").replace("_", "-")[:30]

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}

    def weighted_score(self):
        scores = [s for s in [self.utility, self.uniqueness, self.seo] if s]
        return sum(scores) / len(scores) if scores else 0


# ═══════════════════════════════════════════
# Idea Generator (来自 daily_forge)
# ═══════════════════════════════════════════

class IdeaGenerator:
    """生成创新的微工具和游戏创意"""

    CATEGORIES = [
        "Code", "Data", "API", "Design", "Text", "Security",
        "DevOps", "Productivity", "Game", "AI", "Web3", "Mobile"
    ]

    def __init__(self):
        self.llm = LLMClient()

    def generate_ideas(self, num_candidates: int = 5) -> List[Idea]:
        """通过LLM生成创意"""
        prompt = f"""You are a product strategist. Generate {num_candidates} innovative micro-SaaS tool ideas.
Each should be a focused, viral-worthy web tool or game.
Reply in JSON array: [{{"name": "...", "description": "...", "category": "...", "tech_stack": ["Next.js", "TypeScript"]}}]
Categories: {', '.join(self.CATEGORIES)}"""

        try:
            response = self.llm.generate(prompt)
            return self._parse_response(response, num_candidates)
        except Exception as e:
            log.warning(f"LLM创意生成失败: {e}, 使用备选方案")
            return self._get_curated_ideas()

    def _parse_response(self, response: str, num: int) -> List[Idea]:
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            data = json.loads(json_str) if isinstance(json_str, str) else json_str
            if isinstance(data, list):
                return [Idea(**{k: v for k, v in item.items() if k in Idea.__dataclass_fields__}) for item in data[:num]]
        except Exception as e:
            log.warning(f"解析响应失败: {e}")
        return self._get_curated_ideas()

    def _get_curated_ideas(self) -> List[Idea]:
        return [
            Idea("JSON Diff Viewer", "Compare two JSON objects with visual diff highlighting", "Code"),
            Idea("Color Palette AI", "Generate harmonious color palettes with AI suggestions", "Design"),
            Idea("Speed Reader", "Chunked text display for faster reading with WPM tracking", "Productivity"),
        ]


# ═══════════════════════════════════════════
# Quality Checker (来自 daily_forge)
# ═══════════════════════════════════════════

class QualityChecker:
    """评分和过滤创意质量"""

    def __init__(self):
        self.llm = LLMClient()
        self._existing_slugs = self._load_existing()

    def _load_existing(self) -> set:
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return {item.get("slug", "") for item in json.load(f)}
        except Exception:
            pass
        return set()

    def is_duplicate(self, idea: Idea) -> bool:
        return idea.slug in self._existing_slugs

    def evaluate(self, idea: Idea) -> Idea:
        """使用LLM评分"""
        if self.is_duplicate(idea):
            idea.verdict = Verdict.KILL.value
            idea.score = 0
            return idea

        prompt = f"""Rate this micro-SaaS idea (1-10 each):
Name: {idea.name}
Description: {idea.description}
Reply JSON: {{"utility": 8, "uniqueness": 7, "seo": 6, "verdict": "SHIP"}}
verdict: SHIP (score>=7), MAYBE (5-6), KILL (<5)"""

        try:
            response = self.llm.generate(prompt)
            if "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
                if response.startswith("json"):
                    response = response[4:].strip()
            data = json.loads(response)
            idea.utility = data.get("utility", 5)
            idea.uniqueness = data.get("uniqueness", 5)
            idea.seo = data.get("seo", 5)
            idea.score = round(idea.weighted_score())
            idea.verdict = data.get("verdict", "MAYBE")
        except Exception as e:
            log.warning(f"评分失败: {e}")
            idea.score = 5
            idea.verdict = "MAYBE"
        return idea


# ═══════════════════════════════════════════
# Unified Forge Pipeline (来自 forge_master)
# ═══════════════════════════════════════════

class TitanForge:
    """统一的代码生成流水线 — 合并3个旧生成器"""

    CIRCUIT_BREAKER_THRESHOLD = 2
    CIRCUIT_BREAKER_COOLDOWN = 300

    def __init__(self):
        self.builder = AppBuilder()
        self.idea_gen = IdeaGenerator()
        self.quality = QualityChecker()
        self._failures = 0

    def run_pipeline(self, raw_idea: str = None, dry_run: bool = False) -> dict:
        """执行完整的生成流水线"""
        start = time.time()
        result = {"success": False, "idea": None, "path": None, "url": None}

        try:
            # 1. 获取创意
            if raw_idea:
                idea = Idea(name=raw_idea, description=raw_idea, category="Custom")
            else:
                ideas = self.idea_gen.generate_ideas(num_candidates=3)
                # 评分筛选
                scored = [self.quality.evaluate(i) for i in ideas]
                ships = [i for i in scored if i.verdict == "SHIP"]
                idea = ships[0] if ships else scored[0]
                log.info(f"📋 选定创意: {idea.name} (score: {idea.score})")

            result["idea"] = idea.to_dict()

            if dry_run:
                log.info("  [DRY RUN] 跳过构建")
                return result

            # 2. 构建
            spec = self.builder.transform_idea(idea.description)
            path = self.builder.generate_and_inject(spec)

            if path:
                result["path"] = path
                result["success"] = True
                self._failures = 0
                self._record(idea, path)
                log.info(f"✅ 构建成功: {path}")
            else:
                self._failures += 1
                log.warning(f"❌ 构建失败 (连续{self._failures}次)")

        except Exception as e:
            self._failures += 1
            log.error(f"流水线异常: {e}")
            result["error"] = str(e)

        result["duration"] = round(time.time() - start, 1)
        return result

    def _record(self, idea: Idea, path: str):
        """记录构建历史"""
        try:
            records = []
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    records = json.load(f)
            records.append({
                "slug": idea.slug,
                "name": idea.name,
                "category": idea.category,
                "path": path,
                "built_at": datetime.now().isoformat(),
            })
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _check_circuit_breaker(self) -> bool:
        return self._failures < self.CIRCUIT_BREAKER_THRESHOLD


# ═══════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="TITAN Forge v1.0 — 统一代码生成器")
    parser.add_argument("idea", nargs="?", help="Custom idea to build")
    parser.add_argument("--dry-run", action="store_true", help="Generate ideas only, don't build")
    parser.add_argument("--batch", type=int, default=1, help="Number of apps to generate")
    args = parser.parse_args()

    forge = TitanForge()

    for i in range(args.batch):
        if args.batch > 1:
            log.info(f"\n🔨 Batch {i+1}/{args.batch}")
        result = forge.run_pipeline(raw_idea=args.idea, dry_run=args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
