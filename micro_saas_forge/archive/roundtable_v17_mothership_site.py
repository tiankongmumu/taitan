"""
ShipMicro Roundtable v17 — The Mothership Portal Blueprint
主题：在对外扩张前，先将核心大本营 (shipmicro_site) 打造至 100% 完美。
参与者：产品经理 (PM)、高级视觉设计师 (UI/UX)、商业化总监 (CBO)、架构师 (Architect)
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from logger import get_logger

log = get_logger("roundtable_v17")

class RoundtableV17Mothership:
    def __init__(self):
        self.llm = LLMClient()
        self.history_file = os.path.join(os.path.dirname(__file__), "history.json")

    def run_roundtable(self):
        log.info("="*60)
        log.info(f"🎤 SHIPMICRO ROUNDTABLE V17: The Mothership Portal")
        log.info("="*60)

        transcript = []
        
        system_context = f"""
Current Situation: 
ShipMicro's production engine (Autopilot v3) is fully operational. It autonomously generates, tests, and deploys Next.js micro-tools to Vercel and logs them in `history.json`.
However, the "Mothership" (the main shipmicro_site portal that aggregates these tools) is currently a basic, static 1% complete skeleton. 
The Boss has halted external promotion to focus entirely on perfecting this main website first.

The goal: Design the ultimate Web 4.0 portal that acts as the hub for all generated tools, handles user accounts/monetization, and provides a web-based CEO dashboard.
"""

        # Round 1: Core Portal Design
        log.info("\n🗣️ Phase 1: Mothesite Feature Blueprint")

        pm_prompt = f"""{system_context}
You are the Product Manager.
What are the absolute must-have features for the main portal to make it an irresistible directory/hub for developers looking for micro-tools? 
Think about tool discovery, categories, search, and user journey.
Keep it under 150 words. Be specific.
"""
        pm_response = self.llm.generate(pm_prompt)
        log.info(f"\n[Product Manager]:\n{pm_response}")
        transcript.append(f"**Product Manager**: {pm_response}")

        design_prompt = f"""{system_context}
Product Manager just said: "{pm_response}"
You are the Lead UI/UX Designer (obsessed with premium Web 4.0 aesthetics).
Basic Tailwind is not enough. How do we make the site look like a $100M+ tech company's platform?
Detail the visual language (colors, gradients, glassmorphism, micro-animations) we must use in the Next.js `index.css` and components.
Keep it under 150 words.
"""
        design_response = self.llm.generate(design_prompt)
        log.info(f"\n[UI/UX Designer]:\n{design_response}")
        transcript.append(f"**UI/UX Designer**: {design_response}")
        
        cbo_prompt = f"""{system_context}
You are the Monetization Director.
Instead of monetizing each tool individually with separate Stripe accounts, how should the *Mothership* handle monetization centrally? 
(e.g., Credit system, Universal Pro subscription, API keys for the tools).
Keep it under 150 words.
"""
        cbo_response = self.llm.generate(cbo_prompt)
        log.info(f"\n[Monetization Director]:\n{cbo_response}")
        transcript.append(f"**Monetization Director**: {cbo_response}")

        arch_prompt = f"""{system_context}
Colleagues' inputs:
PM: {pm_response}
UI/UX: {design_response}
CBO: {cbo_response}

You are the Lead Next.js Architect.
How do we technically build this in `shipmicro_site`? Detail the Next.js App Router structure, how it reads from `history.json` dynamically (or needs a DB), Auth (NextAuth/Clerk?), and the Web CEO Dashboard route.
Keep it under 200 words.
"""
        arch_response = self.llm.generate(arch_prompt)
        log.info(f"\n[Lead Architect]:\n{arch_response}")
        transcript.append(f"**Lead Architect**: {arch_response}")

        # Round 2: Resolution
        log.info("\n🗣️ Phase 2: 制定工作计划并输出")

        final_prompt = f"""
Summary of the discussion:
PM: Tool discovery and user journey.
UI/UX: Premium Web 4.0 aesthetics.
CBO: Centralized monetization.
Architect: Next.js App Router technical structure.

You are the CEO AI.
We need to upgrade the `shipmicro_site` from 1% to 100%.
Synthesize the discussion into EXACTLY 4 actionable, sequential development tasks (Task 1 to Task 4) for our AI engineer to execute today.
Format as a strict markdown list:
- [ ] Task 1: [Name] - [Specific details required]
- [ ] Task 2: [Name] - [Specific details required]
- [ ] Task 3: [Name] - [Specific details required]
- [ ] Task 4: [Name] - [Specific details required]
"""
        resolution = self.llm.generate(final_prompt)
        log.info(f"\n[CEO AI (Resolution)]:\n{resolution}")
        transcript.append(f"**CEO AI**: {resolution}")

        # Save transcript
        report_path = os.path.join(os.path.dirname(__file__), f"roundtable_v17_mothership_site.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# ShipMicro Portal (Mothership) Roundtable (v17)\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Transcript\n\n")
            f.write("\n\n".join(transcript))
        log.info(f"\n📝 会议记录已保存至: {report_path}")

if __name__ == "__main__":
    rt = RoundtableV17Mothership()
    rt.run_roundtable()
