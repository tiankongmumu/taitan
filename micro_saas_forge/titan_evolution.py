import os
import json
import random
import time
from datetime import datetime
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from loguru import logger as log
from core_generators.llm_client import LLMClient

# Setup logging specific for evolution
os.makedirs("logs", exist_ok=True)
log.add("logs/titan_evolution.log", rotation="5 MB", level="INFO")

class TitanEvolution:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.history_file = os.path.join(self.base_dir, "deploy_history.json")
        self.tools_dir = os.path.join(self.base_dir, "shipmicro_site", "src", "app", "tools")
        self.llm = LLMClient()
        
    def analyze_failures(self):
        """Analyze deployment/build failures from history and learn from them."""
        log.info("🧠 Analyzing past failures...")
        if not os.path.exists(self.history_file):
            log.warning("No deploy history found to analyze.")
            return

        with open(self.history_file, 'r', encoding='utf-8') as f:
            try:
                history = json.load(f)
            except:
                history = []

        # Find failures
        failures = [item for item in history if item.get('status') == 'failed']
        
        if not failures:
            log.info("✅ No failed deployments found. Engine is performing perfectly.")
            return
            
        # Grab the latest 3 failures to avoid massive prompts
        recent_failures = failures[-3:]
        
        prompt = f"""You are the core logic updater for an AI software factory.
Analyze these recent build/deployment failures:
{json.dumps(recent_failures, indent=2, ensure_ascii=False)}

Identify the root cause of these failures. Are they strict TypeScript typing issues? Vercel deployment configs missing? Next.js routing problems?
Generate a bulleted list of 3 STRICT RULES that the code generator must obey in the future to prevent these specific errors.
Focus on actionable coding constraints, not vague advice.
"""
        log.info("Sending failure data to LLM for post-mortem analysis...")
        try:
            analysis = self.llm.generate(prompt, is_json=False)
            log.info("📝 Evolution Report Generated:")
            print("\n" + "="*40 + "\n" + analysis + "\n" + "="*40 + "\n")
            
            # Save the evolution mandate so the main engine could theoretically read it later
            mandate_file = os.path.join(self.base_dir, "evolution_mandates.txt")
            with open(mandate_file, "a", encoding="utf-8") as mf:
                mf.write(f"\n\n--- Evolution Mandate ({datetime.now().isoformat()}) ---\n")
                mf.write(analysis)
                
        except Exception as e:
            log.error(f"Failed to analyze failures: {e}")


    def refactor_portfolio(self):
        """Randomly select an existing tool and improve its code quality or UI."""
        log.info("🔨 Initiating portfolio refactoring...")
        
        if not os.path.exists(self.tools_dir):
            log.warning(f"Tools directory not found: {self.tools_dir}")
            return
            
        # Get list of existing tools
        tools = [d for d in os.listdir(self.tools_dir) 
                 if os.path.isdir(os.path.join(self.tools_dir, d)) and d != "[slug]"]
                 
        if not tools:
            log.warning("No tools found to refactor.")
            return
            
        # Pick a random tool to refactor tonight
        target_tool = random.choice(tools)
        target_file = os.path.join(self.tools_dir, target_tool, "page.tsx")
        
        if not os.path.exists(target_file):
            log.warning(f"No page.tsx found in {target_tool}.")
            return
            
        log.info(f"✨ Selected '{target_tool}' for nocturnal enhancement.")
        
        with open(target_file, "r", encoding="utf-8") as f:
            original_code = f.read()
            
        # Very lightweight refactor prompt to prevent destroying working code
        prompt = f"""You are a senior Next.js & Tailwind expert.
Review this working React component for '{target_tool}'.

YOUR GOAL: Enhance the aesthetic appeal (UI/UX) and TypeScript code quality of this component WITHOUT breaking any existing functionality.
- Add better Tailwind gradients, hover effects, or glassmorphism if it looks plain.
- Ensure strict TypeScript typing is utilized where possible (no implicit anys if easy to fix).
- DO NOT change the core logic, API endpoints, or break any React hooks.
- Return ONLY the fully updated, complete TypeScript React code block. No markdown wrapping if possible, or only one ```tsx block.

Original Code:
```tsx
{original_code[-4000:]} # Sending last 4000 chars to avoid token limits for now
```
"""     # In a real heavy evolution, we would chunk or send the whole file. 
        # For prototype safety during the night, we do a limited scope.

        log.info("🚀 Requesting enhanced code from LLM for live nocturnal evolution...")
        try:
            enhanced_code = self.llm.generate(prompt, is_json=False)
            
            # Parse the code block from the LLM response
            import re
            match = re.search(r'```(?:tsx|typescript|jsx|javascript)?(.*?)```', enhanced_code, re.DOTALL | re.IGNORECASE)
            if match:
                clean_code = match.group(1).strip()
            else:
                # Fallback if the LLM didn't use markdown code blocks
                clean_code = enhanced_code.strip()
                
            if clean_code and len(clean_code) > 100:
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(clean_code)
                log.info(f"✅ Live refactor for '{target_tool}' successfully completed and written to disk.")
            else:
                log.warning(f"⚠️ LLM generated empty or suspiciously small code for '{target_tool}'. Aborting write.")
                
        except Exception as e:
            log.error(f"❌ Evolution refactor failed for '{target_tool}': {e}")
def run_evolution_cycle():
    """Main entrypoint for the nightly evolution cycle (called by titan_brain.py between 1am-6am)."""
    log.info("\n" + "="*50)
    log.info("🌟 INITIATING NOCTURNAL EVOLUTION CYCLE 🌟")
    log.info("="*50)
    
    evo = TitanEvolution()
    
    # 0. Learn from the world (GitHub Scholarship)
    log.info("📚 Step 0: Global Scholarship - Scanning GitHub for architectural patterns...")
    try:
        from github_scholar import GitHubScholar
        scholar = GitHubScholar()
        scholar.run(top_n=3) # Limit to top 3 for nightly cycle to manage API/time
        
        from skill_extractor import SkillExtractor
        extractor = SkillExtractor()
        extractor.run_all()
        log.info("✅ Global scholarship and skill extraction complete.")
    except Exception as e:
        log.error(f"⚠️ Global learning failed: {e}")

    # 1. Learn from mistakes
    evo.analyze_failures()
    
    # 2. Improve existing assets
    evo.refactor_portfolio()
    
    log.info("="*50)
    log.info("🏁 NOCTURNAL EVOLUTION CYCLE COMPLETE")
    log.info("="*50)

if __name__ == "__main__":
    # For manual testing
    run_evolution_cycle()
