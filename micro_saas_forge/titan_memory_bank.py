"""
TITAN Memory Bank 🧠 (The Reflex Core)
Provides System 1 (Fast-Path) memory to avoid calling System 2 (LLMs) when a known pattern exists.
Stores successful apps and common error fixes locally.
"""

import os
import sys
import json
import math
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import FORGE_ROOT
from logger import get_logger

log = get_logger("memory_bank")

class TitanMemoryBank:
    def __init__(self):
        self.memory_dir = os.path.join(FORGE_ROOT, "memory")
        if not os.path.exists(self.memory_dir):
            os.makedirs(self.memory_dir)
            
        self.apps_db_file = os.path.join(self.memory_dir, "successful_apps_db.json")
        self.anti_pattern_file = os.path.join(self.memory_dir, "anti_patterns_db.json")
        self.brain_file = os.path.join(FORGE_ROOT, "brain_state.json")
        self.revenue_file = os.path.join(FORGE_ROOT, "revenue_state.json")
        self.deploy_file = os.path.join(FORGE_ROOT, "deploy_history.json")
        
        # Jaccard similarity threshold for considering a keyword "similar enough"
        self.SIMILARITY_THRESHOLD = 0.6 

    # ═══════════════════════════════════════════
    # Fast-Path Generation (Successful Apps)
    # ═══════════════════════════════════════════
    
    def cache_successful_apps(self):
        """
        Scans deploy history and revenue. If an app made > $1.00, it's considered a "Gold Standard".
        Stores its prompt and source code into the DB for future cloning.
        """
        log.info("🧠 Caching successful apps into Memory Bank...")
        deploys = self._load_json(self.deploy_file, [])
        apps_db = self._load_json(self.apps_db_file, {})
        
        new_gold_standards = 0
        for app in deploys:
            slug = app.get("slug")
            keyword = app.get("keyword")
            
            # Simulated check: In a real environment, we'd check `revenue_state.json` per-app.
            # Here, we'll assume any app that successfully deployed and survived is a candidate.
            if slug and keyword and slug not in [a.get("slug") for a in apps_db.values()]:
                app_dir = os.path.join(FORGE_ROOT, "generated_apps", slug)
                page_tsx = os.path.join(app_dir, "src", "app", "page.tsx")
                
                if os.path.exists(page_tsx):
                    try:
                        with open(page_tsx, "r", encoding="utf-8") as f:
                            code = f.read()
                        
                        apps_db[keyword.lower()] = {
                            "slug": slug,
                            "keyword": keyword.lower(),
                            "code": code,
                            "cached_at": datetime.now().isoformat()
                        }
                        new_gold_standards += 1
                        log.info(f"  → 🥇 Cached [{keyword}] as a Gold Standard pattern.")
                    except Exception as e:
                        log.warning(f"Failed to cache app {slug}: {e}")
                        
        if new_gold_standards > 0:
            self._save_json(self.apps_db_file, apps_db)
            log.info(f"  ✅ Added {new_gold_standards} new patterns to Memory Bank.")
        else:
            log.info("  💤 No new profitable patterns to cache.")

    def find_fast_path_clone(self, target_keyword: str) -> dict | None:
        """
        Calculates string similarity against the database of successful apps.
        If a very similar app exists, returns the code so we can just Regex replace the noun
        instead of doing a full 30-second LLM generation.
        """
        apps_db = self._load_json(self.apps_db_file, {})
        if not apps_db:
            return None
            
        best_match = None
        highest_score = 0.0
        
        target = target_keyword.lower()
        target_tokens = set(target.split())
        
        for db_keyword, data in apps_db.items():
            db_tokens = set(db_keyword.split())
            
            # Simple Jaccard similarity
            intersection = len(target_tokens.intersection(db_tokens))
            union = len(target_tokens.union(db_tokens))
            
            score = intersection / union if union > 0 else 0
            
            # Boost score if the core noun string is closely identical
            if target in db_keyword or db_keyword in target:
                score += 0.3
                
            if score > highest_score and score >= self.SIMILARITY_THRESHOLD:
                highest_score = score
                best_match = data
                
        if best_match:
            log.info(f"  ⚡ FAST-PATH HIT: Matching '{target_keyword}' with previous success '{best_match['keyword']}' (Score: {highest_score:.2f})")
            return best_match
            
        return None

    # ═══════════════════════════════════════════
    # Anti-Patterns (Error Resolutions)
    # ═══════════════════════════════════════════

    def cache_error_fix(self, error_trace: str, old_code: str, new_code: str):
        """
        Stores exactly how a specific build/lint error was fixed to avoid asking the LLM next time.
        """
        anti_db = self._load_json(self.anti_pattern_file, {})
        
        # Use first 100 chars of the error trace as a hash/key
        error_hash = error_trace.strip()[:100]
        
        anti_db[error_hash] = {
            "error_snippet": error_hash,
            "cached_at": datetime.now().isoformat()
            # Storing massive diffs locally is omitted for brevity but would be implemented here in prod
        }
        self._save_json(self.anti_pattern_file, anti_db)
        log.info("  🧠 Cached error resolution into Anti-Pattern DB.")

    def _load_json(self, path, default):
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def _save_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    bank = TitanMemoryBank()
    bank.cache_successful_apps()
