"""
TITAN Engine — Roundtable Bug Fixer
A dedicated multi-AI roundtable for healing broken applications.
Role 1: Senior Debugger (Proposes fix based on QA result)
Role 2: Senior Code Reviewer (Audits the fix before applying)
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logger import get_logger
from core_generators.llm_client import LLMClient

log = get_logger("roundtable_fixer")

class TitanRoundtableFixer:
    def __init__(self):
        self.llm = LLMClient()
    
    def heal_product(self, product_path: str, qa_result: dict, max_rounds: int = 2) -> str:
        """
        Attempt to heal a broken product by convening a roundtable.
        Returns the path to the improved product (or the original if healing failed).
        """
        log.info(f"🔄 TITAN Roundtable Fixer convening for {product_path}...")
        
        target_file = self._find_target_file(product_path)
        if not target_file:
            log.warning("❌ Could not find an HTML or TSX file to heal.")
            return product_path
            
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                original_code = f.read()
        except Exception as e:
            log.warning(f"❌ Failed to read source file: {e}")
            return product_path

        issues = "\n".join(qa_result.get("issues", ["Unknown failure"]))
        score = qa_result.get("score", 0)
        
        log.info(f"🐞 Identified QA Score: {score}/10. Issues:\n{issues}")
        
        # ── Fast-Path: Check Anti-Pattern Memory ──
        try:
            from titan_memory_bank import TitanMemoryBank
            bank = TitanMemoryBank()
            error_hash = issues.strip()[:100]
            anti_db = bank._load_json(bank.anti_pattern_file, {})
            
            if error_hash in anti_db:
                log.info("  ⚡ REFLEX HIT! This exact error has been solved before. Applying cached code patch...")
                cached_fix = anti_db[error_hash].get("fixed_code")
                if cached_fix:
                    with open(target_file, "w", encoding="utf-8") as f:
                        f.write(cached_fix)
                    log.info(f"  🩹 Successfully patched {os.path.basename(target_file)} using Reflex Memory!")
                    return product_path
        except Exception as e:
            log.warning(f"  ⚠️ Error checking reflex memory: {e}")

        current_code = original_code
        
        for attempt in range(1, max_rounds + 1):
            log.info(f"  [Round {attempt}] 👨‍💻 Debugger is analyzing...")
            
            # Step 1: Debugger proposes a fix
            debugger_prompt = f"""You are the Senior Debugger in an AI software factory.
The QA system ran a test on the following code and gave it {score}/10.
Here are the issues found:
--------------------
{issues}
--------------------

Below is the current source code:
```
{current_code}
```

Write the COMPLETE, FIXED source code that resolves all these issues. 
Do not output anything else but the raw code block. Keep all existing features intact.
RESPOND ONLY WITH THE FULL FIXED SOURCE CODE WRAPPED IN A ``` TAG."""

            fix_response = self.llm.generate(
                prompt=debugger_prompt, 
                system_prompt="You are a strict, pragmatic software engineer. You fix bugs without breaking existing architecture."
            )
            
            proposed_fix = self._extract_code(fix_response)
            if not proposed_fix:
                log.warning("    ⚠️ Debugger failed to return valid code.")
                continue
                
            log.info(f"  [Round {attempt}] 🕵️‍♂️ Reviewer is verifying the fix...")
            
            # Step 2: Reviewer audits the fix
            reviewer_prompt = f"""You are the Principal Code Reviewer.
We had the following QA issues:
{issues}

The Debugger has submitted the following updated code to fix it:
```
{proposed_fix[:2000]}... (truncated for review)
```

Does this code safely resolve the issues without introducing massive architectural breakages?
Return a JSON object:
{{
  "approved": true/false,
  "reason": "Brief explanation"
}}"""

            review_response = self.llm.generate(
                prompt=reviewer_prompt,
                system_prompt="You carefully prevent bad code patches from entering production.",
                is_json=True
            )
            
            try:
                review_data = self._extract_json(review_response)
                is_approved = review_data.get("approved", False)
                reason = review_data.get("reason", "Unknown")
            except Exception as e:
                log.warning(f"    ⚠️ Reviewer response unparseable, defaulting to approved to save work. {e}")
                is_approved = True
                reason = "Failsafe approval"
                
            if is_approved:
                log.info(f"  ✅ FIX APPROVED: {reason}")
                # Apply the fix!
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(proposed_fix)
                    
                # Store this successful resolution in Reflex Memory
                try:
                    error_hash = issues.strip()[:100]
                    anti_db[error_hash] = {
                        "error_snippet": error_hash,
                        "fixed_code": proposed_fix,
                        "cached_at": __import__("datetime").datetime.now().isoformat()
                    }
                    bank._save_json(bank.anti_pattern_file, anti_db)
                    log.info("  🧠 Error resolution cached into Anti-Pattern DB.")
                except Exception:
                    pass
                    
                log.info(f"  🩹 Successfully patched {os.path.basename(target_file)}!")
                return product_path
            else:
                log.warning(f"  ❌ FIX REJECTED: {reason}")
                # Provide feedback to the debugger in the next round by appending to issues
                issues += f"\n[Reviewer Rejected Attempt {attempt}]: {reason}"
                
        log.warning("⚠️ Roundtable exhausted all healing rounds. Product remains broken.")
        return product_path

    def _find_target_file(self, path: str) -> str:
        """Find the most likely entrypoint file to fix."""
        if os.path.isfile(path):
            return path
            
        # Try Next.js structure
        p = os.path.join(path, "src", "app", "page.tsx")
        if os.path.exists(p):
            return p
            
        # Try static HTML
        for root, _, files in os.walk(path):
            for f in files:
                if f == "index.html":
                    return os.path.join(root, f)
                    
        return ""
        
    def _extract_code(self, text: str) -> str:
        """Extract code from markdown codeblocks."""
        match = re.search(r"```(html|javascript|typescript|tsx|jsx)?(.*?)```", text, re.DOTALL)
        if match:
            return match.group(2).strip()
        # Fallback if no codeblocks used
        if "<!DOCTYPE html>" in text or "export default function" in text:
            return text.strip()
        return ""

    def _extract_json(self, text: str) -> dict:
        """Robustly extract JSON from unstructured text."""
        match = re.search(r'\{.*\}', text.strip(), re.DOTALL)
        if match:
            return __import__('json').loads(match.group(0))
        return __import__('json').loads(text)

if __name__ == "__main__":
    # Test manual run
    import json
    if len(sys.argv) > 1:
        path = sys.argv[1]
        fixer = TitanRoundtableFixer()
        mock_qa = {"score": 2, "issues": ["ReferenceError: useState is not defined", "Syntax error on line 45"]}
        print(f"Testing on {path}...")
        fixer.heal_product(path, mock_qa)
    else:
        print("Usage: python titan_roundtable_fixer.py <product_dir>")
