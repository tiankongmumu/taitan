"""
TITAN Pivot Manager 🔄
Responsible for assessing the ROI of the deployed fleet. 
If the engine is losing money (or not making enough given the deployment count), 
it triggers PANIC_MODE and forcibly modifies the discovery/generation strategy.
"""

import os
import sys
import json
import random
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import FORGE_ROOT
from logger import get_logger

log = get_logger("pivot")

class TitanPivotManager:
    def __init__(self):
        self.revenue_file = os.path.join(FORGE_ROOT, "revenue_state.json")
        self.deploy_file = os.path.join(FORGE_ROOT, "deploy_history.json")
        self.override_file = os.path.join(FORGE_ROOT, "strategy_override.json")
        
        # Performance Thresholds
        self.MIN_ROD = 2.0  # Minimum Return on Deployment (Revenue per shipped app)
        self.MIN_APPS_TO_JUDGE = 5  # Give the engine at least N apps before panicking

        # Allowed Pivot Strategies
        self.AVAILABLE_PIVOTS = [
            {
                "id": "shift_to_creators",
                "name": "Niche Pivot: Creator Tools",
                "override_prompt": "CRITICAL SHIFT: Stop building generic utilities. Build tools strictly for content creators, YouTubers, and writers. Monetize via Xiaobot/Newsletters.",
                "ad_style": "embedded"
            },
            {
                "id": "aggressive_monetization",
                "name": "Design Pivot: Aggressive Interstitials",
                "override_prompt": "CRITICAL SHIFT: The tools must have massive, impossible-to-miss monetization components. The UI should guide users directly to the sponsored links.",
                "ad_style": "popup"
            },
            {
                "id": "shift_to_crypto",
                "name": "Niche Pivot: Web3 & Crypto",
                "override_prompt": "CRITICAL SHIFT: Traffic is too low. Pivot exclusively to Web3, Crypto trackers, Gas estimators, and Airdrop tools to hijack high-value crypto traffic.",
                "ad_style": "banner"
            },
             {
                "id": "complex_apps",
                "name": "Engineering Pivot: High-Value Apps",
                "override_prompt": "CRITICAL SHIFT: Our tools are too simple. Generate robust, complex 1000-line multi-step applications. Focus on enterprise utilities (DB schema generators, Docker-compose builders).",
                "ad_style": "subtle"
            }
        ]

    def evaluate_and_pivot(self, context: str = "") -> dict:
        """
        Check current ROI. If it's failing, apply a pivot.
        Returns the current active strategy override.
        """
        log.info("🔄 Evaluating Strategy ROI...")
        if context:
            log.info("🧠 Brain context received for pivot decision.")
        
        revenue = self._load_json(self.revenue_file, {})
        deploys = self._load_json(self.deploy_file, [])
        
        deploy_count = len(deploys)
        total_rev = revenue.get("total", 0.0)
        
        # Load existing override if any
        current_strategy = self._load_json(self.override_file, {})
        
        if deploy_count < self.MIN_APPS_TO_JUDGE:
            log.info(f"  → Accumulating data: {deploy_count}/{self.MIN_APPS_TO_JUDGE} deploys. Holding steady.")
            return current_strategy

        current_rod = total_rev / deploy_count
        log.info(f"  → Current Return on Deployment (RoD): ${current_rod:.2f} per app")
        
        # Is the engine failing?
        if current_rod < self.MIN_ROD:
            # How long have we been on the current strategy? (Count deploys applied)
            deploys_since_pivot = current_strategy.get("deploys_since_applied", 0)
            
            if deploys_since_pivot == 0 or deploys_since_pivot >= self.MIN_APPS_TO_JUDGE:
                # Time to panic and pivot!
                log.warning(f"  🚨 PANIC MODE: RoD (${current_rod:.2f}) is below threshold (${self.MIN_ROD}). Triggering Pivot!")
                new_pivot = self._select_new_pivot(current_strategy.get("id"))
                
                override_data = {
                    "id": new_pivot["id"],
                    "name": new_pivot["name"],
                    "override_prompt": new_pivot["override_prompt"],
                    "ad_style": new_pivot["ad_style"],
                    "deploys_since_applied": 0,
                    "applied_at": datetime.now().isoformat()
                }
                
                with open(self.override_file, "w", encoding="utf-8") as f:
                    json.dump(override_data, f, ensure_ascii=False, indent=2)
                    
                log.info(f"  💥 STRATEGY SHIFTED TO: {override_data['name']}")
                return override_data
            else:
                # Increment time spent on current strategy
                current_strategy["deploys_since_applied"] = deploys_since_pivot + 1
                with open(self.override_file, "w", encoding="utf-8") as f:
                    json.dump(current_strategy, f, ensure_ascii=False, indent=2)
                return current_strategy
        else:
            log.info("  ✅ Profitability is healthy. Maintaining current course.")
            # We are making money. Clear the override if we want, or keep riding it.
            if "id" in current_strategy:
                 current_strategy["deploys_since_applied"] = current_strategy.get("deploys_since_applied", 0) + 1
                 with open(self.override_file, "w", encoding="utf-8") as f:
                    json.dump(current_strategy, f, ensure_ascii=False, indent=2)
                 
            return current_strategy
            
    def _select_new_pivot(self, current_id: str) -> dict:
        candidates = [p for p in self.AVAILABLE_PIVOTS if p["id"] != current_id]
        if not candidates:
            return random.choice(self.AVAILABLE_PIVOTS)
        return random.choice(candidates)

    def _load_json(self, path, default):
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

if __name__ == "__main__":
    pm = TitanPivotManager()
    print(pm.evaluate_and_pivot())
