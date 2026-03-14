"""

TITAN Engine v5.2 ?Autonomous Brain (Skill-Enhanced)

The central controller that runs the full commercial feedback loop:



    Discover ?Analyze ?Build ?Scan ?Test ?Deploy ?Distribute ?Loop



v5.2: 接入技能系?claude-skills) + Web Scanner质量?Shannon) + 成本追踪(pi-mono)

"""

import os

import sys

import json

import time

import argparse

import threading

from datetime import datetime



sys.path.insert(0, os.path.dirname(__file__))

from logger import get_logger



log = get_logger("titan_brain")



BRAIN_STATE_FILE = os.path.join(os.path.dirname(__file__), "brain_state.json")





class TitanBrain:

    """

    TITAN v5.2 Autonomous Brain.

    Orchestrates the full commercial loop with decision-making.

    """



    def __init__(self):

        self.state = self._load_state()

        self.cycle_count = self.state.get("total_cycles", 0)

        

        try:

            from titan_memory_manager import TitanMemoryManager

            self.memory_manager = TitanMemoryManager()

        except ImportError:

            self.memory_manager = None



    # ══════════════════════════════════════════?

    # Core Loop

    # ══════════════════════════════════════════?



    def run_cycle(self, dry_run: bool = False) -> dict:

        """Execute one full autonomous cycle."""

        cycle_start = time.time()

        self.cycle_count += 1

        cycle_id = f"cycle_{self.cycle_count}"



        log.info(f"\n{'='*60}")

        log.info(f"🧠 TITAN BRAIN v5.2 �� Cycle #{self.cycle_count}")

        log.info(f"{'='*60}")



        report = {

            "cycle_id": cycle_id,

            "started_at": datetime.now().isoformat(),

            "steps": {},

            "decisions": [],

            "success": False,

        }



        try:

            # ── Step 0: Evaluate Monetization Pivot ──

            log.info("\n🔄 Step 0/9: Evaluate Monetization Pivot")

            

            # Inject memory context into pivot decisions

            memory_context = ""

            if self.memory_manager:

                memory_context = self.memory_manager.get_context_for_brain()

                

            pivot_strategy = self._step_eval_pivot(memory_context)

            report["steps"]["pivot_eval"] = pivot_strategy.get("id", "none")

            

            # ── Step 1: Demand Discovery ──

            log.info("\n📡 Step 1/9: Demand Discovery")

            if pivot_strategy and "override_prompt" in pivot_strategy:

                log.info(f"  ⚠️ Applying Strategy Override: {pivot_strategy['name']}")

                

            opportunities = self._step_discover(pivot_strategy)

            report["steps"]["discover"] = {

                "found": len(opportunities),

                "top_3": [o.get("keyword", "?") for o in opportunities[:3]],

            }



            if not opportunities:

                report["decisions"].append("ABORT: No opportunities found")

                return self._finalize(report, cycle_start)



            # ── Step 2: Pick Best Opportunity ──

            log.info("\n🎯 Step 2/8: Select Best Opportunity")

            target = self._step_select(opportunities)

            report["steps"]["select"] = {"chosen": target.get("keyword", "?")}

            log.info(f"  ?Target: {target.get('keyword')} (score: {target.get('opportunity_score', '?')})")



            # ── Step 3: Competitive Analysis ──

            log.info("\n🔎 Step 3/8: Competitive Analysis")

            competitive_brief = self._step_analyze_competition(target)

            report["steps"]["competition"] = {"brief_length": len(competitive_brief)}



            # ── Step 3.5: Commercial Audit (Profitability Filter) ──

            log.info("\n💼 Step 3.5/8: Commercial Audit")

            audit_result = self._step_commercial_audit(target, competitive_brief)

            report["steps"]["commercial_audit"] = audit_result

            if not audit_result.get("pass"):

                log.warning(f"  ?AUDIT FAILED: {audit_result.get('reason')}")

                report["decisions"].append(f"ABORT: Commercial audit failed ({audit_result.get('score')}/10)")

                return self._finalize(report, cycle_start)

            log.info(f"  ?AUDIT PASSED: Score {audit_result.get('score')}/10 - {audit_result.get('reason')}")



            # ── Step 4: Build Product ──

            log.info("\n🏗?Step 4/8: Build Product")

            if dry_run:

                log.info("  [DRY RUN] Skipping build")

                product_path = None

                report["steps"]["build"] = {"dry_run": True}

            else:

                product_path = self._step_build(target, competitive_brief)

                report["steps"]["build"] = {"path": product_path, "success": product_path is not None}



            # ── Step 5: Web Scanner Quality Gate (v5.2, 学自Shannon) ──

            log.info("\n🔍 Step 5/8: Web Scanner Quality Gate")

            if product_path and not dry_run:

                try:

                    from titan_web_scanner import TitanWebScanner

                    scanner = TitanWebScanner()

                    scan_result = scanner.full_scan(product_path)

                    report["steps"]["web_scan"] = scan_result



                    struct_ok = scan_result.get("structure", {}).get("pass", False)

                    sec_issues = len(scan_result.get("security", {}).get("vulnerabilities", []))

                    log.info(f"  结构检? {'? if struct_ok else '?} | 安全漏洞: {sec_issues}")



                    if not struct_ok:

                        report["decisions"].append("WEB_SCAN: Structure check failed")

                except Exception as e:

                    log.warning(f"  Web Scanner异常: {e}")

                    report["steps"]["web_scan"] = {"error": str(e)}

            else:

                report["steps"]["web_scan"] = {"skipped": True}



            # ── Step 6: Quality Test ──

            log.info("\n🧪 Step 6/8: Quality Test")

            if product_path and not dry_run:

                qa_result = self._step_quality_test(product_path)

                report["steps"]["qa"] = qa_result



                if not qa_result.get("pass"):

                    report["decisions"].append(f"QA FAILED: {qa_result.get('score', 0)}/10 ?needs improvement")

                    # Try auto-fix

                    log.info("  🔧 Attempting auto-fix...")

                    product_path = self._step_improve(product_path, qa_result)

                    qa_result = self._step_quality_test(product_path)

                    report["steps"]["qa_retry"] = qa_result

            else:

                report["steps"]["qa"] = {"skipped": True}



            # ── Step 7: Deploy ──

            log.info("\n🚀 Step 7/8: Deploy")

            if product_path and not dry_run:

                deploy_url = self._step_deploy(product_path)

                report["steps"]["deploy"] = {"url": deploy_url}

            else:

                report["steps"]["deploy"] = {"skipped": True}



            # ── Step 8: Distribute ──

            log.info("\n📢 Step 8/8: Distribute")

            if not dry_run:

                distribution = self._step_distribute(target, product_path, deploy_url)

                report["steps"]["distribute"] = distribution

            else:

                report["steps"]["distribute"] = {"skipped": True}



            report["success"] = True

            report["decisions"].append("CYCLE COMPLETE")



            # ── Step 9: Verify Revenue ──

            log.info("\n💰 Step 9/9: Verify Revenue")

            try:

                rev_result = self._step_verify_revenue()

                if rev_result:

                    log.info(f"  💰 预估总收? ${rev_result.get('total', 0)}")

                report["steps"]["verify_revenue"] = rev_result

            except Exception as e:

                log.error(f"  ?Revenue verification error: {e}")

                report["steps"]["verify_revenue"] = {"error": str(e)}





        except Exception as e:

            log.error(f"?Cycle failed: {e}")

            report["error"] = str(e)

            report["decisions"].append(f"ERROR: {e}")



        # ── System 3: Meta-Reflection "Sleep Cycle" ──

        try:

            from titan_meta_reflector import TitanMetaReflector

            reflector = TitanMetaReflector()

            reflector.run_sleep_cycle()

        except Exception as e:

            log.warning(f"  ⚠️ Sleep cycle failed asynchronously: {e}")



        # ── Step 10: Persist Episodic Memory ──

        if self.memory_manager:

            status_str = "SUCCESS" if report["success"] else f"FAILED ({report.get('error', 'unknown error')})"

            summary = f"Cycle #{self.cycle_count} finished with status: {status_str}."

            if report["steps"].get("select"):

                 summary += f" Target tool: {report['steps']['select'].get('chosen')}."

            

            self.memory_manager.log_event("brain_cycle", summary, {

                "cycle_id": report["cycle_id"],

                "success": report["success"],

                "duration": report["duration_seconds"]

            })



        # ── Step 11: Soul Reflection & Reactive Learning ──

        try:

            from titan_soul import TitanSoul

            soul = TitanSoul()

            reflection = soul.reflect_on_result(report)

            log.info(f"👻 Soul Reflection: {reflection.get('message')}")

            

            if reflection.get("learning_required"):

                log.info("🔥 FRUSTRATION detected. Initiating Reactive Learning Loop...")

                error_msg = report.get("error", "unknown error")

                self._reactive_learning(error_msg)

        except Exception as e:

            log.warning(f"  ⚠️ Soul reflection or reactive learning failed: {e}")



        return self._finalize(report, cycle_start)



    # ══════════════════════════════════════════?

    # Reactive Learning Engine

    # ══════════════════════════════════════════?

    

    def _reactive_learning(self, error_context: str):

        """定向分析错误并去 GitHub 研学解决方案"""

        log.info(f"🔍 Analyzing error for targeted research: {error_context[:100]}")

        

        # 1. Use LLM to extract the core technical keyword/query

        try:

            from core_generators.llm_client import LLMClient

            client = LLMClient()

            prompt = f"Extract a 3-5 word GitHub search query to solve this technical error: {error_context}"

            query = client.generate(prompt, model="gpt-4o-mini").strip().replace('"', '')

            log.info(f"📚 Targeted Research Query: '{query}'")

            

            # 2. Invoke Scholar

            try:

                from github_scholar import GitHubScholar

                scholar = GitHubScholar()

                scholar.run(query=query, top_n=2)

            except Exception as e:

                log.warning(f"  Scholar research failed: {e}")

            

            # 3. Invoke Extractor

            try:

                from skill_extractor import SkillExtractor

                extractor = SkillExtractor()

                extractor.run_all()

            except Exception as e:

                log.warning(f"  Skill extraction failed: {e}")

            

            log.info("🎯 Reactive learning complete. Axioms updated via memory bank.")

        except Exception as e:

            log.error(f"Failed to execute reactive learning: {e}")



    # ══════════════════════════════════════════?

    # Step Implementations

    # ══════════════════════════════════════════?

        """Step 0: Evaluate ROI and pivot if panic threshold met."""

        try:

            from titan_pivot_manager import TitanPivotManager

            manager = TitanPivotManager()

            # Pass memory context to allow smarter pivot decisions based on history

            return manager.evaluate_and_pivot(context=memory_context)

        except Exception as e:

            log.warning(f"  ⚠️ Pivot Manager failed to evaluate: {e}")

            return {}



    def _step_discover(self, pivot_strategy: dict = None) -> list[dict]:

        """Step 1: Execute V6.5 Commercial Intuition Pipeline (Data + R-Agent)."""

        from titan_commercial_intuition import CommercialIntuitionEngine

        from titan_r_agent import RAgent

        

        # 1. Run Data-Driven Intuition Engine

        log.info("  ⚙️ Booting Commercial Intuition Engine (WTP + Cross-Ref) ...")

        intuition = CommercialIntuitionEngine()

        intuition.run()

        

        # 2. Feed validated data to R-Agent for Creative Wrapping

        log.info("  🧠 Engaging R-Agent to wrap niches into sellable products...")

        r_agent = RAgent()

        proposals = r_agent.generate_proposals()

        

        # Standardize format for the rest of the pipeline

        opportunities = []

        for p in proposals:

            opportunities.append({

                "keyword": p.get("name", "Unknown Product"),

                "differentiation": p.get("description", ""),

                "revenue_model": p.get("paywall_trigger", "Charge via UI block"),

                "opportunity_score": 9.9, # Override to max since we mathematically validated it

                "source": "r_agent_v6.5"

            })

            

        return opportunities



    def _step_select(self, opportunities: list[dict]) -> dict:

        """Step 2: Pick the best opportunity based on score and history."""

        # Filter out already-built keywords

        built = set(self.state.get("built_keywords", []))

        fresh = [o for o in opportunities if o.get("keyword", "").lower() not in built]



        if fresh:

            return fresh[0]  # Highest opportunity_score

        return opportunities[0]  # Fall back to best overall



    def _step_analyze_competition(self, target: dict) -> str:

        """Step 3: Get competitive analysis."""

        from competitor_scanner import CompetitorScanner

        scanner = CompetitorScanner()

        return scanner.get_build_brief(target.get("keyword", ""))



    def _step_commercial_audit(self, target: dict, competitive_brief: str) -> dict:

        """Step 3.5: Audit the commercial viability before building."""

        from core_generators.llm_client import LLMClient

        llm = LLMClient()

        

        keyword = target.get("keyword", "unknown tool")

        

        prompt = f"""You are a strict SaaS investor and monetization strategist.

Analyze this product idea: "{keyword}"

Context: {competitive_brief}



Evaluate if this is worth building based on willingness-to-pay and monetization potential.

Many simple tools (like "typing test", "stopwatch") have ZERO monetization moat. We want to avoid building garbage.



Score this from 1 to 10 on pure profitability potential (10 = can confidently charge money or get high CPM B2B ads).

Return a JSON object:

{{

  "score": (int 1-10),

  "pass": (boolean, must be true ONLY if score >= 7),

  "reason": (short 1-sentence explanation)

}}

"""

        try:

            import re

            result = llm.generate(prompt, is_json=True)

            match = re.search(r'\{.*\}', result.strip(), re.DOTALL)

            if match:

                result = match.group(0)

            data = json.loads(result)

            return {

                "score": data.get("score", 0),

                "pass": data.get("pass", False),

                "reason": data.get("reason", "Unknown")

            }

        except Exception as e:

            log.warning(f"Commercial audit failed to parse: {e}")

            return {"score": 0, "pass": False, "reason": "Failed to run audit. Aborting."}



    def _step_build(self, target: dict, competitive_brief: str) -> str | None:

        """Step 4: Build the product using enhanced AppBuilder."""

        from core_generators.app_builder import AppBuilder

        from titan_memory_bank import TitanMemoryBank

        from titan_meta_reflector import TitanMetaReflector

        

        bank = TitanMemoryBank()

        reflector = TitanMetaReflector()

        builder = AppBuilder()



        keyword = target.get("keyword", "unknown tool")

        revenue_model = target.get("revenue_model", "AdSense")

        differentiation = target.get("differentiation", "")

        

        # Grab strictly enforced knowledge axioms

        active_axioms = reflector.get_active_axioms()

        

        # ── Fast-Path Reflex Memory Check ──

        clone_data = bank.find_fast_path_clone(keyword)

        if clone_data:

            log.info(f"  ?Fast-Path Triggered! Cloning previous success: {clone_data['keyword']}")

            # We bypass the LLM and instantly write the cached code to a new app dir.

            import re

            

            # Simple word-replacement to adapt the cloned code to the new noun

            old_keyword = clone_data["keyword"]

            adapted_code = clone_data["code"].replace(old_keyword, keyword).replace(old_keyword.title(), keyword.title())

            

            # Create app directory structure manually as a fast path

            app_slug = re.sub(r'[^a-zA-Z0-9]', '-', keyword).strip('-').lower()

            product_dir = os.path.join(FORGE_DIR, "generated_apps", app_slug)

            src_dir = os.path.join(product_dir, "src", "app")

            os.makedirs(src_dir, exist_ok=True)

            

            # Write page.tsx

            page_path = os.path.join(src_dir, "page.tsx")

            with open(page_path, "w", encoding="utf-8") as f:

                f.write(adapted_code)

                

            # Write global.css (basic wrapper)

            css_path = os.path.join(src_dir, "globals.css")

            if not os.path.exists(css_path):

                with open(css_path, "w", encoding="utf-8") as f:

                    f.write("@tailwind base;\n@tailwind components;\n@tailwind utilities;\n")

                    

            log.info(f"  ?Reflex Clone written to: {product_dir}")

            return product_dir

            

        # ── Fallback to System 2 (Slow LLM Deliberation) ──



        # Enhanced idea with commercial requirements

        enhanced_idea = f"""Build a professional web tool for: "{keyword}".



COMPETITIVE INTELLIGENCE:

{competitive_brief}



COMMERCIAL REQUIREMENTS:

- Must include ad slot placement (Google AdSense compatible div)

- Must include share button (navigator.share API)

- Must include email capture or CTA

- Must include basic analytics tracking

- Revenue model: {revenue_model}

- Key differentiator: {differentiation}



SYSTEM 3 KNOWLEDGE AXIOMS (ABSOLUTE LAWS):

{active_axioms if active_axioms else "None established yet."}

You MUST obey these axioms strictly in your architecture.



QUALITY REQUIREMENTS:

- Mobile-first responsive design

- Touch event support

- Zero external dependencies (pure HTML/CSS/JS)

- Dark mode modern UI

- Loading time < 1 second

"""

        try:

            spec = builder.transform_idea(enhanced_idea)

            result = builder.generate_and_inject(spec)

            if result:

                # Track built keyword

                built = self.state.get("built_keywords", [])

                built.append(keyword.lower())

                self.state["built_keywords"] = built

                self._save_state()

                return result

        except Exception as e:

            log.error(f"  Build failed: {e}")



        return None



    def _step_quality_test(self, product_path: str) -> dict:

        """Step 6: Test the product."""

        from browser_qa import BrowserQA

        qa = BrowserQA()



        # Find the main HTML file

        if os.path.isdir(product_path):

            for root, dirs, files in os.walk(product_path):

                for f in files:

                    if f.endswith(".html"):

                        return qa.test(os.path.join(root, f))

        elif os.path.isfile(product_path):

            return qa.test(product_path)



        return {"pass": False, "score": 0, "issues": ["No HTML file found"]}



    def _step_improve(self, product_path: str, qa_result: dict) -> str:

        """Step 6b: Try to improve a failing product using the Roundtable Fixer."""

        issues = qa_result.get("issues", [])

        log.info(f"  Attempting Auto-Heal. Issues to fix: {len(issues)}")

        for issue in issues[:5]:

            log.info(f"    - {issue}")

            

        try:

            from titan_roundtable_fixer import TitanRoundtableFixer

            fixer = TitanRoundtableFixer()

            healed_path = fixer.heal_product(product_path, qa_result, max_rounds=2)

            return healed_path

        except Exception as e:

            log.error(f"  ?Roundtable Fixer failed critically: {e}")

            return product_path



    def _step_deploy(self, product_path: str) -> str | None:

        """Step 7: Deploy via TitanDeployer (Vercel ?static export fallback)."""

        try:

            from titan_deployer import TitanDeployer

            deployer = TitanDeployer()

            result = deployer.deploy(product_path)

            if result.get("success"):

                log.info(f"  ?Deployed: {result['url']} (method: {result['method']})")

                return result["url"]

            else:

                log.warning(f"  ⚠️ Deploy failed: {result.get('app_name')}")

                return None

        except Exception as e:

            log.warning(f"  ⚠️ Deploy failed: {e}")

            return None



    def _step_distribute(self, target: dict, product_path: str = None, deploy_url: str = None) -> dict:

        """Step 8: Auto-Distribute via Titan Publisher and Social Distributor."""

        import asyncio

        log.info("  Generating marketing assets and distributing to social media...")

        

        result = {"publisher": False, "social_distributor": False}

        tool_name = target.get("keyword", "New Tool")

        diff = target.get("differentiation", "Awesome UI and zero latency.")

        url = deploy_url or "https://shipmicro.com/tools"

        

        try:

            from titan_publisher import TitanPublisher

            publisher = TitanPublisher()

            marketing_assets = publisher.generate_marketing_package(tool_name, url, diff)

            log.info("  ?Marketing package generated.")

            result["publisher"] = True

            result["assets"] = len(marketing_assets)

        except Exception as e:

            log.warning(f"  ?Publisher failed: {e}")

            

        try:

            from social_distributor import run_social_distributor

            # Define the tool for the distributor

            tools_to_distribute = [{

                "name": tool_name.title(),

                "url": url,

                "description": diff

            }]

            

            log.info(f"  🚀 Launching Social Distributor for {tool_name}...")

            # Run the async distributor synchronously

            posts_generated = asyncio.run(run_social_distributor(tools=tools_to_distribute, auto=True))

            

            if posts_generated:

                log.info(f"  ?Social distribution complete. Generated {len(posts_generated)} posts.")

                result["social_distributor"] = True

        except Exception as e:

            log.warning(f"  ?Social Distributor failed: {e}")

            

        try:

            # Package the source code for sale!

            if product_path:

                from titan_source_packager import TitanSourcePackager

                packager = TitanSourcePackager()

                log.info(f"  📦 Packaging source code for sale...")

                pkg_result = packager.package_for_sale(tool_name.title(), product_path, diff)

                if pkg_result.get("success"):

                    log.info(f"  ?Source Code packaged at: {pkg_result['zip_path']}")

                    result["source_packaged"] = True

        except Exception as e:

            log.warning(f"  ?Source Packager failed: {e}")

            

        return result

        

    def _step_verify_revenue(self) -> dict:

        """Step 9: Verify and audit generated revenue from the fleet."""

        log.info("  Auditing fleet revenue generation...")

        try:

            from titan_revenue_verifier import TitanRevenueVerifier

            from titan_memory_bank import TitanMemoryBank

            

            verifier = TitanRevenueVerifier()

            result = verifier.audit_revenue()

            

            # Use this moment to cache any newly successful apps into the bank

            bank = TitanMemoryBank()

            bank.cache_successful_apps()

            

            return result

        except Exception as e:

            log.error(f"  ⚠️ Revenue verifier failed: {e}")

            return {}



    # ══════════════════════════════════════════?

    # State Management

    # ══════════════════════════════════════════?



    def _load_state(self) -> dict:

        try:

            if os.path.exists(BRAIN_STATE_FILE):

                with open(BRAIN_STATE_FILE, "r", encoding="utf-8") as f:

                    return json.load(f)

        except Exception:

            pass

        return {"total_cycles": 0, "built_keywords": [], "history": []}



    def _save_state(self):

        self.state["total_cycles"] = self.cycle_count

        with open(BRAIN_STATE_FILE, "w", encoding="utf-8") as f:

            json.dump(self.state, f, indent=2, ensure_ascii=False)



    def _finalize(self, report: dict, start_time: float) -> dict:

        report["duration_seconds"] = round(time.time() - start_time, 1)

        report["finished_at"] = datetime.now().isoformat()



        # Save to history

        history = self.state.get("history", [])

        history.append({

            "cycle_id": report["cycle_id"],

            "time": report["finished_at"],

            "success": report["success"],

            "duration": report["duration_seconds"],

        })

        self.state["history"] = history[-50:]  # Keep last 50

        self._save_state()



        # ── Write to executor_log.jsonl so dashboard shows current data ──

        try:

            log_dir = os.path.join(os.path.dirname(__file__), "logs")

            os.makedirs(log_dir, exist_ok=True)

            log_path = os.path.join(log_dir, "titan_executor.jsonl")

            steps = report.get("steps", {})

            task_names = list(steps.keys())

            outcome_parts = []

            for k, v in steps.items():

                if isinstance(v, dict):

                    if v.get("top_3"):

                        outcome_parts.append(f"\u626b\u63cf\u5b8c\u6210\uff0c\u53d1\u73b0{v.get('found',0)}\u4e2a\u4fe1\u53f7\uff0cTop5: {v.get('top_3', [])}")

                    elif v.get("chosen"):

                        outcome_parts.append(f"\u9009\u4e2d: {v['chosen']}")

                    elif v.get("skipped"):

                        pass

            outcome = "; ".join(outcome_parts) if outcome_parts else report.get("decisions", [""])[-1]

            succeeded = 1 if report["success"] else 0

            failed = 0 if report["success"] else 1

            entry = {

                "ts": report["finished_at"],

                "tasks": task_names[:5],

                "success": report["success"],

                "outcome": outcome[:120],

                "elapsed": report["duration_seconds"],

                "succeeded": succeeded,

                "failed": failed,

            }

            with open(log_path, "a", encoding="utf-8") as f:

                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        except Exception as e:

            log.warning(f"  \u26a0\ufe0f Failed to write executor log: {e}")



        # Print summary

        log.info(f"\n{'='*60}")

        status = "\u2705 SUCCESS" if report["success"] else "\u274c FAILED"

        log.info(f"\ud83e\udde0 Cycle #{self.cycle_count} \u2014 {status} ({report['duration_seconds']}s)")

        for decision in report.get("decisions", []):

            log.info(f"  \ud83d\udccb {decision}")

        log.info(f"{'='*60}\n")



        return report



    # ══════════════════════════════════════════?

    # QA-Only Mode (test existing products)

    # ══════════════════════════════════════════?



    def qa_existing(self) -> list[dict]:

        """Run QA on all existing tools and games."""

        from browser_qa import BrowserQA

        qa = BrowserQA()



        base = os.path.join(os.path.dirname(__file__), "shipmicro_site", "public")

        results = []



        for subdir in ["tools", "games"]:

            path = os.path.join(base, subdir)

            if os.path.exists(path):

                log.info(f"\n🧪 QA: {subdir}/")

                results.extend(qa.test_all_tools(path))



        return results





def _pulse_heart():

    """Write a heartbeat to heart_state.json so the dashboard stays alive."""

    try:

        hf = os.path.join(os.path.dirname(__file__), "heart_state.json")

        if os.path.exists(hf):

            with open(hf, "r", encoding="utf-8") as f:

                heart = json.load(f)

        else:

            heart = {"total_beats": 0, "recent_vitals": []}

        heart["total_beats"] = heart.get("total_beats", 0) + 1

        heart["last_saved"] = datetime.now().isoformat()

        with open(hf, "w", encoding="utf-8") as f:

            json.dump(heart, f, ensure_ascii=False, indent=2)

    except Exception as e:

        log.warning(f"Heartbeat pulse failed: {e}")





def main():

    parser = argparse.ArgumentParser(description="TITAN Engine v5.2 ?Autonomous Brain (Skill-Enhanced)")

    parser.add_argument("--cycle", action="store_true", help="Run one full cycle")

    parser.add_argument("--dry-run", action="store_true", help="Discover + analyze only, no build/deploy")

    parser.add_argument("--qa", action="store_true", help="QA test existing products")

    parser.add_argument("--discover", action="store_true", help="Run demand discovery only")

    parser.add_argument("--loop", type=int, default=0, help="Run N cycles with 1h interval")

    parser.add_argument("--forever", action="store_true", help="Run infinite cycles (never stop)")

    parser.add_argument("--sales-bot", action="store_true", help="Run Xianyu Auto-Sales Bot in background")

    parser.add_argument("--mount", action="store_true", help="Automatically discover and mount a new tool to ShipMicro Site")

    args = parser.parse_args()



    if args.sales_bot:

        try:

            from xianyu_auto_sales_bot import XianyuSalesBot

            log.info("🛒 Starting Xianyu Auto-Sales Bot in background thread...")

            bot = XianyuSalesBot()

            bot_thread = threading.Thread(target=bot.start_polling, daemon=True)

            bot_thread.start()

        except Exception as e:

            log.error(f"Failed to start Xianyu Sales Bot: {e}")



    brain = TitanBrain()



    if args.mount:

        try:

            from titan_tool_mounter import mount_new_tool

            log.info("🚀 Starting Titan Mounter Mode...")

            mount_new_tool()

        except Exception as e:

            log.error(f"Titan Mounter failed: {e}")

        return



    if args.qa:

        brain.qa_existing()

    elif args.discover:

        from demand_radar import DemandRadar

        radar = DemandRadar()

        signals = radar.scan()

        print(f"\n🔍 Top 10 Opportunities:")

        for i, s in enumerate(signals[:10], 1):

            print(f"  {i}. [{s.get('opportunity_score', 0):>8.0f}] {s['keyword']}")

    elif args.cycle or args.dry_run:

        _pulse_heart()

        brain.run_cycle(dry_run=args.dry_run)

    elif args.forever:

        cycle_num = 0

        log.info("♾️  TITAN Engine starting in FOREVER mode (Ctrl+C to stop)")

        while True:

            cycle_num += 1

            log.info(f"\n🔄 Forever Loop #{cycle_num}")

            _pulse_heart()

            

            # --- CIRCADIAN RHYTHM MANAGER ---

            current_hour = datetime.now().hour

            if 1 <= current_hour < 6:

                log.info("🌙 Nocturnal Phase Active (1 AM - 6 AM): Entering Self-Evolution Incubator.")

                try:

                    from titan_evolution import run_evolution_cycle

                    run_evolution_cycle()

                except Exception as e:

                    log.error(f"Evolution cycle crashed: {e}")

            else:

                # ☀?Daytime Phase (Normal Operation)

                try:

                    brain.run_cycle()

                except Exception as e:

                    log.error(f"Cycle #{cycle_num} crashed: {e}")

                    

            _pulse_heart()

            log.info("?Waiting 5 minutes before next cycle...")

            time.sleep(300)

    elif args.loop > 0:

        for i in range(args.loop):

            log.info(f"\n🔄 Loop {i+1}/{args.loop}")

            _pulse_heart()

            try:

                brain.run_cycle()

            except Exception as e:

                log.error(f"Loop {i+1} crashed: {e}")

            _pulse_heart()

            if i < args.loop - 1:

                log.info("?Waiting 1 hour before next cycle...")

                time.sleep(3600)

    else:

        # Default: dry run

        brain.run_cycle(dry_run=True)





if __name__ == "__main__":

    main()

