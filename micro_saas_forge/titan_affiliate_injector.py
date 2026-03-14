"""
TITAN Affiliate Injector 🎯
Selects the most relevant affiliate program for a given tool and generates a React widget snippet.
"""

import os
import sys
import json
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logger import get_logger
from core_generators.llm_client import LLMClient
from titan_affiliate_catalog import AFFILIATE_PROGRAMS

log = get_logger("affiliate")

class TitanAffiliateInjector:
    def __init__(self):
        self.llm = LLMClient()
        
    def get_affiliate_widget(self, keyword: str, differentiation: str) -> str:
        """
        Returns a JSX snippet containing the tailored affiliate advertisement.
        """
        log.info(f"🎯 Matching affiliate program for '{keyword}'...")
        
        selected_adj = self._match_program(keyword, differentiation)
        
        # Build the JSX Widget
        widget_code = f"""
{{/* 💰 TITAN AFFILIATE INJECTOR 💰 */}}
<div className="my-8 p-4 sm:p-6 rounded-2xl border border-violet-500/20 bg-gradient-to-r from-violet-500/5 to-cyan-500/5 relative overflow-hidden group">
  <div className="absolute top-0 right-0 px-3 py-1 bg-violet-500/20 rounded-bl-xl text-[10px] text-violet-300 font-bold uppercase tracking-wider">
    {selected_adj.get('badge_text', 'Sponsored')}
  </div>
  <div className="flex items-start gap-4">
    <div className="text-3xl sm:text-4xl group-hover:scale-110 transition-transform">
      {selected_adj.get('icon', '🔥')}
    </div>
    <div>
      <h4 className="text-sm font-bold text-white mb-1 group-hover:text-cyan-300 transition-colors">
        {selected_adj.get('name')}
      </h4>
      <p className="text-xs text-gray-400 mb-3 leading-relaxed">
        {selected_adj.get('ad_copy')}
      </p>
      <a 
        href="{selected_adj.get('link')}" 
        target="_blank" 
        rel="noopener noreferrer"
        className="inline-block px-4 py-1.5 rounded-full bg-white/10 text-white text-xs font-bold hover:bg-white/20 transition-colors border border-white/5"
      >
        了解更多 →
      </a>
    </div>
  </div>
</div>
"""
        log.info(f"  ✅ Selected partner: {selected_adj['name']}")
        return widget_code

    def _match_program(self, keyword: str, diff: str) -> dict:
        """Fast keyword-based matching — no LLM needed."""
        combined = (keyword + " " + diff).lower()
        best_score = -1
        best_program = AFFILIATE_PROGRAMS[-1]  # default: shipmicro
        
        for program in AFFILIATE_PROGRAMS:
            score = sum(1 for tag in program["tags"] if tag in combined)
            # Boost by partial word match
            for tag in program["tags"]:
                for word in combined.split():
                    if tag in word or word in tag:
                        score += 0.5
            if score > best_score:
                best_score = score
                best_program = program
        
        return best_program

if __name__ == "__main__":
    injector = TitanAffiliateInjector()
    print(injector.get_affiliate_widget("SQL Optimizer", "Fast local WASM"))
