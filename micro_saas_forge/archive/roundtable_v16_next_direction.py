"""
ShipMicro Roundtable v16 — Post-Launch Strategic Direction
主题：Web 4.0 已落地并在全自动运行，接下来的突破口在哪里？
参与者：架构师 (Architect)、产品经理 (Product Manager)、增长黑客 (Growth Hacker)、商业化总监 (Monetization Director)
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from logger import get_logger

log = get_logger("roundtable_v16")

class RoundtableV16NextDirection:
    def __init__(self):
        self.llm = LLMClient()
        self.history_file = os.path.join(os.path.dirname(__file__), "history.json")
        self.stats = self._get_system_stats()

    def _get_system_stats(self):
        import json
        history_count = 0
        success_count = 0
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                history_count = len(history)
                success_count = sum(1 for h in history if h.get("success", False))
                
        # 尝试读取 UI 评分
        logs_dir = os.path.join(os.path.dirname(__file__), "logs")
        avg_ui_score = "N/A"
        if os.path.isdir(logs_dir):
            report_files = sorted([f for f in os.listdir(logs_dir) if f.startswith("ui_test_report")])
            if report_files:
                with open(os.path.join(logs_dir, report_files[-1]), "r", encoding="utf-8") as f:
                    ui_data = json.load(f)
                    scores = [r.get("ui_score", 0) for r in ui_data]
                    if scores:
                        avg_ui_score = f"{sum(scores)/len(scores):.1f}/10"

        return {
            "total_runs": history_count,
            "success_rate": f"{success_count}/{max(history_count, 1)}",
            "avg_ui_score": avg_ui_score,
            "current_status": "Web 4.0 Pipeline (Autopilot v3) fully operational.",
            "pipeline_steps": "1.News Scrape 2.LLM Forge 3.Quality Check 4.Social Promo 5.Analytics Inject 6.AdSense Inject 7.CEO Dashboard",
            "upgrades_completed": "Quality-Weighted RAG, Adaptive UI Tester, Analytics Feedback Loop, Smart Ads, Social-SEO Matrix."
        }

    def run_roundtable(self):
        log.info("="*60)
        log.info(f"🎤 SHIPMICRO ROUNDTABLE V16: Post-Launch Strategy")
        log.info(f"📊 当前系统状态: \n{self.stats}")
        log.info("="*60)

        transcript = []
        
        system_context = f"""
Current System State (ShipMicro Web 4.0):
{self.stats}

Background:
We have successfully built and launched the ShipMicro Autopilot v3 pipeline. It is a fully autonomous Web 4.0 business engine that runs 7 steps without human intervention: Scraping news for ideas -> Forging Next.js 14 apps -> Quality testing -> Auto-posting to Reddit/X -> Injecting Analytics -> Injecting Google AdSense -> Generating a CEO dashboard. It includes a self-healing capability with a Memory Bank and Skill Learner. The recent production run successfully generated and deployed 2 new tools in under 20 minutes.

The discussion topic: "What is the absolute highest leverage next step for ShipMicro? We have autonomous production, but how do we scale traffic, revenue, or capability to the next level?"
"""

        # Round 1: Initial Thoughts
        log.info("\n🗣️ Phase 1: 现状剖析与战略定调")

        pm_prompt = f"""{system_context}
You are the Action-Oriented Product Manager.
You observe that production is solved, but a product without users is dead code.
Analyze the current pipeline. Where is the biggest product/market gap?
Keep it under 150 words. Be direct.
"""
        pm_response = self.llm.generate(pm_prompt)
        log.info(f"\n[Product Manager]:\n{pm_response}")
        transcript.append(f"**Product Manager**: {pm_response}")

        growth_prompt = f"""{system_context}
Product Manager just said: "{pm_response}"
You are the Aggressive Growth Hacker.
You don't care about code; you care about eyeballs and virality. Auto-posting to Reddit/X is cute, but it's not a moat and might get shadowbanned.
What is the most aggressive growth loop we can build next? 
Keep it under 150 words.
"""
        growth_response = self.llm.generate(growth_prompt)
        log.info(f"\n[Growth Hacker]:\n{growth_response}")
        transcript.append(f"**Growth Hacker**: {growth_response}")
        
        cbo_prompt = f"""{system_context}
Growth Hacker said: "{growth_response}"
You are the Chief Business Officer (Monetization Director).
Currently, we just inject AdSense placeholders. AdSense requires massive traffic for pennies.
What is the most lucrative monetization strategy we can pivot to or add to these micro-tools?
Keep it under 150 words.
"""
        cbo_response = self.llm.generate(cbo_prompt)
        log.info(f"\n[Monetization Director]:\n{cbo_response}")
        transcript.append(f"**Monetization Director**: {cbo_response}")

        arch_prompt = f"""{system_context}
Colleagues' inputs:
PM: {pm_response}
Growth: {growth_response}
CBO: {cbo_response}

You are the Pragmatic Lead Architect.
Look at what they want. What is technically feasible and brings the highest ROI in the next 2-3 days of coding?
Propose a concrete Web 5.0 (or Phase 28) technical architecture that unifies these goals.
Keep it under 200 words.
"""
        arch_response = self.llm.generate(arch_prompt)
        log.info(f"\n[Lead Architect]:\n{arch_response}")
        transcript.append(f"**Lead Architect**: {arch_response}")

        # Round 2: Resolution
        log.info("\n🗣️ Phase 2: 敲定下一步行动方案")

        final_prompt = f"""
Summary of the discussion:
PM: Focused on product/market gap.
Growth: Focused on virality over simple auto-posting.
CBO: Focused on moving past AdSense pennies.
Architect: {arch_response}

You are the CEO AI.
Synthesize the discussion into EXACTLY 3 actionable, high-priority upgrades for Phase 28.
Format as a strict markdown list with check boxes:
- [ ] Upgrade 1: [Name] - [What it is and why]
- [ ] Upgrade 2: [Name] - [What it is and why]
- [ ] Upgrade 3: [Name] - [What it is and why]
"""
        resolution = self.llm.generate(final_prompt)
        log.info(f"\n[CEO AI (Resolution)]:\n{resolution}")
        transcript.append(f"**CEO AI**: {resolution}")

        # Save transcript
        report_path = os.path.join(os.path.dirname(__file__), f"roundtable_v16_strategy.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# ShipMicro Post-Launch Strategy Roundtable (v16)\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Transcript\n\n")
            f.write("\n\n".join(transcript))
        log.info(f"\n📝 会议记录已保存至: {report_path}")

if __name__ == "__main__":
    rt = RoundtableV16NextDirection()
    rt.run_roundtable()
