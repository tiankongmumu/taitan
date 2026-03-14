"""
TITAN Engine v4.0 — 4-AI Roundtable Analysis
Sends the full TITAN codebase context to DeepSeek, Doubao, and Qwen independently.
Each AI analyzes the engine and provides upgrade recommendations.
"""
import os
import sys
import json
import time
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL,
    DOUBAO_API_KEY, DOUBAO_BASE_URL, DOUBAO_ENDPOINT,
    QWEN_API_KEY, QWEN_BASE_URL,
)
from titan_config import (
    GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL,
    MISTRAL_API_KEY, MISTRAL_BASE_URL, MISTRAL_MODEL,
    CEREBRAS_API_KEY, CEREBRAS_BASE_URL, CEREBRAS_MODEL,
    GITHUB_MODELS_TOKEN, GITHUB_MODELS_URL, GITHUB_MODELS_MODEL,
)

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "titan_roundtable_analysis.json")

# ── TITAN Engine codebase summary for analysis ──
TITAN_CONTEXT = """
# TITAN Engine v4.0 — Full Codebase Summary

## Architecture Overview
TITAN is an autonomous web product generation and monetization engine. It consists of:

### Core Modules
1. **titan_brain.py** (250 lines) — Autonomous loop controller
   - 7-step cycle: Discover → Select → Analyze → Build → QA → Deploy → Distribute
   - State persistence in brain_state.json
   - Keyword deduplication to avoid rebuilding
   - CLI: --cycle, --dry-run, --qa, --loop N, --discover

2. **demand_radar.py** (230 lines) — Demand discovery engine
   - Source 1: HackerNews API (top stories, filter for tool/product posts)
   - Source 2: LLM trend analysis (prompts LLM for 10 high-demand niches)
   - Source 3: Hardcoded keyword research DB (14 known opportunities)
   - Opportunity scoring: volume / competition^1.5
   - Outputs: demand_signals/signals.json

3. **competitor_scanner.py** (130 lines) — Competitive gap analysis
   - Uses LLM to simulate competitive research for a keyword
   - Identifies top 5 competitors, features, weaknesses
   - Finds 3-5 actionable competitive gaps
   - Generates build briefs for product_forge

4. **browser_qa.py** (300 lines) — 7-dimension quality testing
   - Structure (HTML validity)
   - SEO (title, meta, h1)
   - Mobile (viewport, touch, responsive)
   - Interactivity (JS, events, buttons)
   - Performance (file size, external deps)
   - Commercial readiness (ad slots, share, analytics, email capture, CTA)
   - Visual quality (CSS, animations, gradients, dark mode)
   - Weighted scoring, pass threshold: 7.0/10

5. **app_builder.py** (449 lines) — LLM code generator
   - Transforms text ideas into app specs
   - Uses LLM to generate Next.js or static HTML apps
   - Self-healing build (retries compilation up to 3x)
   - SEO metadata injection
   - Category-specific skill injection

6. **forge_master.py** (287 lines) — Pipeline orchestrator
   - idea → spec → build → quality check → feedback fix → deploy → SEO → record
   - Circuit breaker (2 failures → 5min cooldown)
   - Checkpoint/resume support

### Supporting Modules
- **llm_client.py** — Multi-model fallback (DeepSeek → Doubao → Qwen), retry, token tracking
- **basic_seo.py** — Blog article gen, launch posts, sitemap entries, dynamic meta
- **analytics_tracker.py** — localStorage-based tracking (NOT real analytics)
- **social_distributor.py** — Social posting (Reddit/HN)
- **news_scraper.py** — Tech news scraping
- **memory_bank.py** — Pattern/skill storage
- **skill_learner.py** — Learns from GitHub repos

8. **Cloud Relay & VPS Pipeline** (NEW)
   - US-based VPS execution to bypass IP-based bans.
   - Flask API for remote command execution.
   - Hot-Sync deployment tool for second-level code updates.

9. **Twitter Anti-Ban Matrix** (NEW)
   - Automated "First Comment Drop" strategy via Playwright.
   - Posts viral text first (no reach penalty), then auto-replies with marketing link.
   - Resident "Twitter Nurturer" bot for profile warming (doomscrolling/liking).

### Current Status (ShipMicro Suite)
- **Main Product**: [ShipMicro.com](https://shipmicro.com) — A suite of AI-powered "Pain-Point" SaaS tools.
- **The 5 Core Tools**:
  1. **AI Cover Letter Generator** (ATS-beating, DeepSeek V3 driven) - $9.90
  2. **Resume Optimizer** (ATS analysis & improvement) - $14.90
  3. **Debt Scam Shield** (AI audit of debt letters) - $14.99
  4. **MeetingNotes2CRM** (Meeting to CRM export) - $9.99
  5. **PitchDeckAI** (Pitch deck logic generator) - $9.90
- **Payments**: **PayPal FULLY INTEGRATED** via `api/checkout/route.ts`. Can process orders, capture payments, and unlock reports.
- **Infrastructure**: VPS Cloud Relay + Twitter Anti-Ban (First Comment Drop) + Twitter Nurturer is active and ready.

### Key Problems
1. **Conversion Gap**: Low conversion from Twitter impressions to PayPal checkout.
2. **Hook Quality**: Need viral hooks that appeal to job seekers, freelancers, and professionals.
3. **Product Depth**: Current tools generate reports/content; need to ensure "Aha!" moment happens before the paywall.
4. **Data Blindness**: Still using legacy analytics (localStorage), need to bridge to server-side events.
"""

ANALYSIS_PROMPT = """You are a global SaaS growth expert and conversion copywriter. Analyze the recent changes to the **ShipMicro** suite.

**Your mission: Resolve the Domain vs. Promotion Mismatch.**

**Background Context:**
We recently redesigned our root domain (`www.shipmicro.com`) into a generic "5-in-1 SaaS Aggregation Portal". We moved our most popular "Cover Letter Generator" tool to the sub-route `/cover-letter`.

**The Crisis:**
Our main promotional URLs and external marketing channels have historically pushed users to `www.shipmicro.com` with the specific promise of "Generate a Cover Letter". Now, when users click these links, they land on a generic 5-tool portal, causing a severe messaging mismatch ("decoupling") and likely high bounce rates.

**Please answer the following:**
1. **Strategic Assessment:** Was it a mistake to turn the root domain into a generic portal when the primary traffic driver is the Cover Letter tool? 
2. **Immediate Technical Fixes (Pick the best path):**
   - Option A: Revert `www.shipmicro.com` to be the Cover Letter tool, and move the generic portal to a sub-domain (e.g., `tools.shipmicro.com`) or sub-route (`/tools`).
   - Option B: Use Next.js Middleware/Redirects to route traffic based on UTM parameters or Referrer.
   - Option C: Redesign the root page to hero the Cover Letter heavily but keep the other 4 tools as minor up-sells.
3. **Marketing Alignment:** How do we unify our Twitter automation (`beast_mode_distribute.py`), our SEO Content Farm (`seo_content_farm.py`), and our landing pages so that the "Promise" precisely matches the "Destination"?
4. **Final Recommendation:** Give a concrete, step-by-step action plan to execute in the next 1 hour to fix this leak.

Respond in Chinese (中文). Brutal honesty required. No theoretical fluff - give me the highest conversion technical architecture."""


def call_model(name, url, api_key, model, prompt, timeout=120):
    """Call a single LLM model."""
    print(f"\n{'='*50}")
    print(f"🤖 Calling {name}...")
    print(f"{'='*50}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a senior tech architect and startup strategist. Respond in Chinese."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 4000,
        "temperature": 0.3,
    }

    for attempt in range(3):
        try:
            start = time.time()
            res = requests.post(url, headers=headers, json=data, timeout=timeout)
            res.raise_for_status()
            content = res.json()["choices"][0]["message"]["content"]
            elapsed = round(time.time() - start, 1)
            print(f"✅ {name}: {len(content)} chars in {elapsed}s")
            return {
                "model": name,
                "response": content,
                "chars": len(content),
                "time_seconds": elapsed,
                "success": True,
            }
        except Exception as e:
            print(f"⚠️ {name} attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(2 ** (attempt + 1))

    return {"model": name, "response": "", "success": False, "error": "All retries failed"}


def run_roundtable():
    """Run the 4-AI roundtable analysis."""
    print("\n" + "=" * 60)
    print(f"🧠 TITAN ENGINE v4.0 — 7-AI ROUNDTABLE ANALYSIS")
    print("=" * 60)

    results = []

    # AI 1: DeepSeek
    if DEEPSEEK_API_KEY:
        r = call_model("DeepSeek", DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, "deepseek-chat", ANALYSIS_PROMPT, timeout=60)
        results.append(r)

    # AI 2: Doubao
    if DOUBAO_API_KEY:
        r = call_model("Doubao", DOUBAO_BASE_URL, DOUBAO_API_KEY, DOUBAO_ENDPOINT, ANALYSIS_PROMPT, timeout=120)
        results.append(r)

    # AI 3: Qwen
    if QWEN_API_KEY:
        r = call_model("Qwen", QWEN_BASE_URL, QWEN_API_KEY, "qwen-max", ANALYSIS_PROMPT, timeout=120)
        results.append(r)

    # AI 4: Groq (Free - 超快推理)
    if GROQ_API_KEY:
        r = call_model("Groq (Llama 3.3 70B)", GROQ_BASE_URL, GROQ_API_KEY, GROQ_MODEL, ANALYSIS_PROMPT, timeout=60)
        results.append(r)

    # AI 5: Mistral (Free - 10亿 tokens/月)
    if MISTRAL_API_KEY:
        r = call_model("Mistral", MISTRAL_BASE_URL, MISTRAL_API_KEY, MISTRAL_MODEL, ANALYSIS_PROMPT, timeout=120)
        results.append(r)

    # AI 6: Cerebras (Free - 超快推理)
    if CEREBRAS_API_KEY:
        r = call_model("Cerebras", CEREBRAS_BASE_URL, CEREBRAS_API_KEY, CEREBRAS_MODEL, ANALYSIS_PROMPT, timeout=60)
        results.append(r)

    # AI 7: GitHub Models (Free - GPT-4o)
    if GITHUB_MODELS_TOKEN:
        r = call_model("GitHub Models (GPT-4o)", GITHUB_MODELS_URL, GITHUB_MODELS_TOKEN, GITHUB_MODELS_MODEL, ANALYSIS_PROMPT, timeout=120)
        results.append(r)

    # Save results
    output = {
        "roundtable_time": datetime.now().isoformat(),
        "models_called": len(results),
        "successful": sum(1 for r in results if r.get("success")),
        "results": results,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Print summaries
    print("\n" + "=" * 60)
    print("📋 ROUNDTABLE RESULTS")
    print("=" * 60)
    for r in results:
        if r.get("success"):
            print(f"\n{'─'*50}")
            print(f"🤖 {r['model']} ({r.get('chars', 0)} chars, {r.get('time_seconds', 0)}s)")
            print(f"{'─'*50}")
            print(r["response"][:2000])
            if len(r["response"]) > 2000:
                print(f"\n... [{len(r['response']) - 2000} more chars]")
        else:
            print(f"\n❌ {r['model']}: FAILED")

    print(f"\n📁 Full results saved to: {OUTPUT_FILE}")
    return results


if __name__ == "__main__":
    run_roundtable()
