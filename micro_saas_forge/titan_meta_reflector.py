"""
TITAN System 3: Meta-Reflector
The "Sleep Cycle" algorithm. 
Runs asynchronously after N deployments to analyze successes/failures and write permanent "Knowledge Axioms".
"""
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import FORGE_ROOT
from logger import get_logger
from core_generators.llm_client import LLMClient

log = get_logger("meta_reflector")

class TitanMetaReflector:
    def __init__(self):
        self.llm = LLMClient()
        self.deploy_file = os.path.join(FORGE_ROOT, "deploy_history.json")
        self.revenue_file = os.path.join(FORGE_ROOT, "revenue_state.json")
        self.axioms_file = os.path.join(FORGE_ROOT, "knowledge_axioms.json")
        self.patterns_file = os.path.join(FORGE_ROOT, "memory", "architectural_patterns.json")
        
    def run_sleep_cycle(self):
        """
        Deeply analyzes the past deployments and synthesizes permanent operational rules (Axioms).
        """
        log.info("🛌 TITAN System 3 'Sleep Cycle' Initialized. Synthesizing new knowledge...")
        
        deploys = self._load_json(self.deploy_file, [])
        revenue = self._load_json(self.revenue_file, {})
        existing_axioms = self._load_json(self.axioms_file, [])
        
        if len(deploys) < 3:
            log.info("  💤 Not enough data for deep reflection (Need > 3 deploys). Sleep cycle skipping.")
            return

        # Prepare context payload for the LLM
        recent_deploys = deploys[-10:] # Analyze last 10
        context_payload = []
        for d in recent_deploys:
            slug = d.get("slug")
            kw = d.get("keyword")
            rev = revenue.get("revenues", {}).get(slug, {}).get("total", 0)
            context_payload.append(f"Tool: {kw} | State: {d.get('state', 'unknown')} | Revenue: ${rev:.2f}")

        # Add recent learned patterns from GitHub for reflection
        patterns = self._load_json(self.patterns_file, [])
        recent_patterns = patterns[-5:] # Digest last 5 learned patterns
        pattern_payload = []
        for p in recent_patterns:
            pattern_payload.append(f"Source: {p.get('source_repo')} | Insight: {p.get('description')}")
        
        if not context_payload and not pattern_payload:
            return
            
        context_str = "\n".join(context_payload)
        pattern_str = "\n".join(pattern_payload)

        prompt = f"""You are the System 3 Meta-Reasoning layer of an autonomous AI corporation.
Your job is to analyze the recent deployment logs and synthesize 1-2 permanent, unbreakable 'Knowledge Axioms'.
An Axiom is a strict rule the AI workers MUST follow in future generations to prevent failures or maximize revenue.

Recent Architecture & Commercial Data (Internal):
{context_str}

Recent GitHub Architectural Insights (External Learning):
{pattern_str}

Current Existing Axioms:
{json.dumps(existing_axioms)}

Task:
Look at which tools generated the most revenue, and which failed or stagnated.
Formulate exactly ONE new Axiom that extracts a generalized lesson from this data.
Make it an absolute imperative instruction. Example: "AXIOM: Always include a prominent Dark/Light mode toggle in utility tools to boost retention."

Return a JSON array containing the new Axioms (as strings). 
Return ONLY the JSON array.
"""
        try:
            response = self.llm.generate(prompt, system_prompt="You are an AGI meta-reflector.")
            import re
            match = re.search(r'\[.*\]', response.strip(), re.DOTALL)
            if match:
                new_axioms = json.loads(match.group(0))
            else:
                new_axioms = json.loads(response)
                
            if new_axioms and isinstance(new_axioms, list):
                existing_axioms.extend(new_axioms)
                
                # Keep only the 10 most potent axioms so we don't blow up the prompt context
                if len(existing_axioms) > 10:
                    existing_axioms = existing_axioms[-10:]
                    
                self._save_json(self.axioms_file, existing_axioms)
                for ax in new_axioms:
                    log.info(f"  🧠 NEW AXIOM SYNTHESIZED: {ax}")
            else:
                log.warning("  ⚠️ Sleep cycle yielded no new axioms.")
                
        except Exception as e:
            log.error(f"  ❌ Meta-Reflection failed and caused a nightmare: {e}")

    def get_active_axioms(self) -> str:
        """Returns the current list of accumulated axioms as a formatted string for injection."""
        axioms = self._load_json(self.axioms_file, [])
        if not axioms:
            return ""
        return "\n".join([f"- {ax}" for ax in axioms])

    def _load_json(self, path, default):
        if not os.path.exists(path): return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def _save_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    reflector = TitanMetaReflector()
    reflector.run_sleep_cycle()
