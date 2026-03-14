"""
TITAN Pipeline — Stage 3: Opportunity Scorer
==============================================
Uses LLM to deeply analyze validated signals and score each one:
  - market_size (1-10)
  - competition (1-10, higher = more competitive)
  - urgency (1-10, how badly people need a solution)
  - opportunity_score = urgency * 0.4 + market_size * 0.35 + (10 - competition) * 0.25

Input:  demand_signals/validated_signals.json
Output: demand_signals/scored_opportunities.json
"""
import os
import sys
import json
from typing import List, Dict

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger
from core_generators.llm_client import LLMClient

log = get_logger("opportunity_scorer")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNALS_DIR = os.path.join(BASE_DIR, "demand_signals")
INPUT_FILE = os.path.join(SIGNALS_DIR, "validated_signals.json")
OUTPUT_FILE = os.path.join(SIGNALS_DIR, "scored_opportunities.json")

SYSTEM_PROMPT = """You are a world-class SaaS market analyst.
Analyze the following batch of signals (Reddit posts, HN stories, etc.) and identify the TOP 10 most commercially viable pain points.

For each pain point, provide:
1. "keyword": A concise 3-5 word label for this opportunity (e.g. "AI invoice processing")
2. "pain_summary": One sentence describing the core pain
3. "market_size": 1-10 score (10 = massive TAM)
4. "competition": 1-10 score (10 = very crowded, 1 = blue ocean)
5. "urgency": 1-10 score (10 = people desperately need this NOW)
6. "evidence": A direct quote or reference from the signals
7. "target_audience": Who specifically would pay for this

Return a valid JSON array. NO markdown wrapping. NO extra text."""


def _extract_json(text: str) -> list:
    """Extract JSON array from LLM response."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    # Find the array
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1:
        text = text[start:end + 1]
    
    return json.loads(text)


def score_opportunities(signals: List[Dict] = None) -> List[Dict]:
    """Score validated signals using LLM analysis."""
    log.info("=" * 50)
    log.info("📊 TITAN Opportunity Scorer v5.0 — Starting")
    log.info("=" * 50)
    
    # Load from file if not provided
    if signals is None:
        if not os.path.exists(INPUT_FILE):
            log.error(f"Input not found: {INPUT_FILE}")
            return []
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        signals = data.get("signals", data if isinstance(data, list) else [])
    
    log.info(f"📥 Input: {len(signals)} validated signals")
    
    # Prepare payload for LLM (top 30 by score)
    top_signals = sorted(signals, key=lambda x: x.get("score", 0), reverse=True)[:30]
    payload = json.dumps([
        {"title": s["title"], "text": s.get("text", "")[:200], "score": s.get("score", 0), "source": s["source"]}
        for s in top_signals
    ], ensure_ascii=False)
    
    user_prompt = f"Analyze these {len(top_signals)} signals and identify the top 10 opportunities:\n\n{payload}"
    
    log.info("🧠 Sending to LLM for analysis...")
    llm = LLMClient()
    response = llm.generate(prompt=user_prompt, system_prompt=SYSTEM_PROMPT, is_json=True)
    
    if not response:
        log.error("LLM returned empty response")
        return []
    
    try:
        opportunities = _extract_json(response)
    except json.JSONDecodeError as e:
        log.error(f"Failed to parse LLM JSON: {e}")
        log.error(f"Raw: {response[:300]}")
        return []
    
    # Calculate composite score
    for opp in opportunities:
        m = opp.get("market_size", 5)
        c = opp.get("competition", 5)
        u = opp.get("urgency", 5)
        opp["opportunity_score"] = round(u * 0.4 + m * 0.35 + (10 - c) * 0.25, 2)
    
    # Sort by score
    opportunities.sort(key=lambda x: x.get("opportunity_score", 0), reverse=True)
    
    # Save
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(opportunities, f, ensure_ascii=False, indent=2)
    
    log.info(f"✅ Scored {len(opportunities)} opportunities → {OUTPUT_FILE}")
    return opportunities


if __name__ == "__main__":
    opps = score_opportunities()
    print(f"\n🏆 Top Opportunities:")
    for i, o in enumerate(opps[:5], 1):
        print(f"  {i}. [{o['opportunity_score']:.1f}] {o['keyword']}")
        print(f"     Mkt:{o['market_size']} Comp:{o['competition']} Urg:{o['urgency']}")
