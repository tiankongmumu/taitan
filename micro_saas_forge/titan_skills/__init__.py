"""
TITAN Skills — Base class and auto-discovery for modular plugins.
Each skill folder contains a SKILL.md and main.py with a class extending TitanSkill.
"""

import os
import sys
import json
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

log = logging.getLogger("titan_skills")

SKILLS_DIR = Path(__file__).parent


class TitanSkill:
    """
    Base class for all TITAN skills.

    Subclasses must define:
      - name: str
      - description: str
      - triggers: list  (e.g. ["cron:0 9 * * *", "message:关键词", "manual"])

    And implement:
      - async execute(self, context: dict) -> dict
    """
    name: str = "unnamed"
    description: str = ""
    triggers: List[str] = ["manual"]
    version: str = "1.0"

    async def execute(self, context: dict) -> dict:
        """Execute the skill. Override in subclass."""
        raise NotImplementedError(f"Skill '{self.name}' has no execute() implementation")

    def matches_trigger(self, trigger_type: str, value: str = "") -> bool:
        """Check if this skill should fire for a given trigger."""
        for t in self.triggers:
            if ":" in t:
                ttype, tval = t.split(":", 1)
                if ttype == trigger_type and (not value or value in tval):
                    return True
            elif t == trigger_type:
                return True
        return False

    def info(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "triggers": self.triggers,
            "version": self.version,
        }


class SkillRegistry:
    """
    Auto-discover and manage skills.

    Skills are loaded from subdirectories of titan_skills/.
    Each subdirectory must have a main.py with a class extending TitanSkill.
    """

    def __init__(self, skills_dir: Path = SKILLS_DIR):
        self.skills_dir = skills_dir
        self._skills: Dict[str, TitanSkill] = {}
        self._discover()

    def _discover(self):
        """Scan subdirectories for skills."""
        for entry in sorted(self.skills_dir.iterdir()):
            if entry.is_dir() and (entry / "main.py").exists():
                try:
                    skill = self._load_skill(entry)
                    self._skills[skill.name] = skill
                    log.info(f"🔧 Loaded skill: {skill.name} ({skill.description[:50]})")
                except Exception as e:
                    log.warning(f"⚠️  Failed to load skill from {entry.name}: {e}")

    def _load_skill(self, skill_dir: Path) -> TitanSkill:
        """Dynamically import a skill module and instantiate its main class."""
        sys.path.insert(0, str(skill_dir))
        spec = importlib.util.spec_from_file_location(
            f"titan_skills.{skill_dir.name}.main",
            str(skill_dir / "main.py"),
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find the TitanSkill subclass in the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, TitanSkill)
                and attr is not TitanSkill
            ):
                return attr()

        raise ValueError(f"No TitanSkill subclass found in {skill_dir / 'main.py'}")

    def get(self, name: str) -> Optional[TitanSkill]:
        return self._skills.get(name)

    def list_all(self) -> List[dict]:
        return [s.info() for s in self._skills.values()]

    def find_by_trigger(self, trigger_type: str, value: str = "") -> List[TitanSkill]:
        """Find all skills matching a trigger."""
        return [s for s in self._skills.values() if s.matches_trigger(trigger_type, value)]

    async def execute(self, name: str, context: dict = None) -> dict:
        """Execute a skill by name."""
        skill = self.get(name)
        if not skill:
            return {"ok": False, "error": f"Skill '{name}' not found"}
        try:
            result = await skill.execute(context or {})
            return {"ok": True, "skill": name, "result": result}
        except Exception as e:
            log.error(f"Skill '{name}' execution error: {e}")
            return {"ok": False, "skill": name, "error": str(e)}

    async def dispatch_trigger(self, trigger_type: str, value: str = "", context: dict = None) -> List[dict]:
        """Find and execute all skills matching a trigger."""
        skills = self.find_by_trigger(trigger_type, value)
        results = []
        for skill in skills:
            r = await self.execute(skill.name, context)
            results.append(r)
        return results


# Quick test
if __name__ == "__main__":
    registry = SkillRegistry()
    print("=" * 50)
    print("🔧 TITAN Skills Registry")
    print("=" * 50)
    skills = registry.list_all()
    if skills:
        for s in skills:
            print(f"  • {s['name']:20s} | {s['description'][:40]}")
    else:
        print("  (no skills discovered yet — create subdirectories with main.py)")
    print(f"\nTotal: {len(skills)} skills")
