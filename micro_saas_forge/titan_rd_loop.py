"""
TITAN Engine v6.0 - Master R&D Loop
Implements the RAGEvoAgent architecture inspired by RD-Agent.
R-Agent generates proposals -> D-Agent writes code -> E-Agent evaluates -> Co-Optimize loop.
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(__file__))
from titan_r_agent import RAgent
from titan_d_agent import DAgent
from titan_e_agent import EAgent
from logger import get_logger

log = get_logger("titan_rd_loop")

MAX_EVO_LOOPS = 3

class RDEvolutionEngine:
    def __init__(self):
        self.r_agent = RAgent()
        self.d_agent = DAgent()
        self.e_agent = EAgent()
        
    def run(self, specific_proposal_file: str = None):
        log.info("🚀 TITAN v6.0 R&D Evolution Engine Starting...")
        
        if specific_proposal_file:
            with open(specific_proposal_file, "r", encoding="utf-8") as f:
                proposals = json.load(f)
            log.info(f"Loaded {len(proposals)} existing proposals from {specific_proposal_file}")
        else:
            proposals = self.r_agent.generate_proposals()
            
        if not proposals:
            log.error("No proposals available to process.")
            return
            
        for proposal in proposals:
            self._evolve_single_proposal(proposal)
            
    def _evolve_single_proposal(self, proposal: dict):
        app_id = proposal.get("id")
        log.info(f"\n=======================================================")
        log.info(f"🧬 Evolving Subject: {proposal.get('name')} [{app_id}]")
        log.info(f"=======================================================")
        
        current_feedback = None
        previous_api_code = None
        previous_page_code = None
        
        for evo_loop_id in range(1, MAX_EVO_LOOPS + 1):
            log.info(f"\n🔄 [Evo_Loop_{evo_loop_id}] Commencing Development...")
            
            # Step 1: D-Agent attempts to build/fix target
            success = self.d_agent.develop_proposal(
                proposal, 
                feedback=current_feedback, 
                previous_api_code=previous_api_code,
                previous_page_code=previous_page_code
            )
            
            if not success:
                log.error(f"❌ [Evo_Loop_{evo_loop_id}] D-Agent absolutely failed to structure the code. Aborting evolution for this proposal.")
                break
                
            # Read generated code to pass as context for next time
            api_path = os.path.join(os.path.dirname(__file__), "shipmicro_site", "src", "app", "api", app_id, "route.ts")
            page_path = os.path.join(os.path.dirname(__file__), "shipmicro_site", "src", "app", "tools", app_id, "page.tsx")
            try:
                with open(api_path, "r", encoding="utf-8") as f:
                    previous_api_code = f.read()
                with open(page_path, "r", encoding="utf-8") as f:
                    previous_page_code = f.read()
            except Exception:
                pass

            # Step 2: E-Agent evaluates the build
            log.info(f"\n⚖️ [Evo_Loop_{evo_loop_id}] Transferring to E-Agent for Evaluation...")
            passed, feedback = self.e_agent.evaluate(app_id, proposal)
            
            if passed:
                log.info(f"🎉 SUCCESS: [{app_id}] has passed rigorous E-Agent evaluation! Ready for production.")
                break
            else:
                log.warning(f"⚠️ FAILURE: Evaluation failed. Passing feedback to D-Agent for next evolution round.")
                current_feedback = feedback
                
        else:
            log.error(f"💀 Exhausted all {MAX_EVO_LOOPS} evolution loops for [{app_id}]. App remains unverified.")


if __name__ == "__main__":
    engine = RDEvolutionEngine()
    # We will pass the specific proposal file generated earlier
    if len(sys.argv) > 1:
        engine.run(specific_proposal_file=sys.argv[1])
    else:
        engine.run()
