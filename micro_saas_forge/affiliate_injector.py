"""
TITAN Pipeline — Stage 4: Affiliate Injector
===============================================
Matches scored opportunities to affiliate products and generates
high-converting pitch copy for each match.

Input:  demand_signals/scored_opportunities.json + affiliate_products.json
Output: demand_signals/affiliate_matches.json
"""
import os
import sys
import json
from typing import List, Dict

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger
from core_generators.llm_client import LLMClient

log = get_logger("affiliate_injector")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNALS_DIR = os.path.join(BASE_DIR, "demand_signals")
PRODUCTS_FILE = os.path.join(BASE_DIR, "affiliate_products.json")
CN_PRODUCTS_FILE = os.path.join(BASE_DIR, "cn_affiliate_products.json")
INPUT_FILE = os.path.join(SIGNALS_DIR, "scored_opportunities.json")
OUTPUT_FILE = os.path.join(SIGNALS_DIR, "affiliate_matches.json")

SYSTEM_PROMPT = """You are a world-class affiliate marketing copywriter fluent in both English and Chinese.
Given a list of user pain points (with scores) and a catalog of affiliate products,
create the BEST possible match between each pain point and a product.

For each match, write:
1. "pain_keyword": The opportunity keyword
2. "pain_summary": One sentence about the pain
3. "product_id": ID of the best matching product
4. "product_name": Name of the matched product
5. "affiliate_url": The affiliate URL from the catalog
6. "commission": The commission rate
7. "pitch_copy": A 2-3 sentence HIGH-CONVERTING pitch in CHINESE (中文) that naturally addresses the pain and recommends the product. Sound like a helpful tech blogger sharing real experience, NOT an ad.
8. "pitch_copy_en": Same pitch in English (for international channels)
9. "match_score": 0-100 confidence in this match
10. "target_platform": Best Chinese platform to promote this (小红书/知乎/公众号/闲鱼)

RULES:
- Only match if the product GENUINELY solves the pain. Don't force matches.
- If no product fits, skip that pain point entirely.
- pitch_copy must feel organic, empathetic, and actionable.
- Prefer Chinese domestic products when they solve the pain equally well.

Return a valid JSON array. NO markdown wrapping."""


def load_products(locale: str = "all") -> List[Dict]:
    """Load affiliate product catalog (global + CN)."""
    products = []
    
    # Load global products
    if locale in ("all", "global") and os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            products.extend(json.load(f))
    
    # Load CN products
    if locale in ("all", "cn") and os.path.exists(CN_PRODUCTS_FILE):
        with open(CN_PRODUCTS_FILE, "r", encoding="utf-8") as f:
            products.extend(json.load(f))
    
    if not products:
        log.warning("No product files found, using defaults")
        return _default_products()
    
    log.info(f"📦 Loaded {len(products)} products (locale={locale})")
    return products


def _default_products() -> List[Dict]:
    """Default affiliate product catalog."""
    return [
        {
            "id": "shopify",
            "name": "Shopify",
            "solves": "E-commerce, online stores, selling online",
            "commission": "$150 per referral",
            "affiliate_url": "https://www.shopify.com/?ref=shipmicro",
            "category": "E-commerce"
        },
        {
            "id": "webflow",
            "name": "Webflow",
            "solves": "No-code website building, landing pages, portfolio sites",
            "commission": "50% for 12 months",
            "affiliate_url": "https://webflow.grsm.io/shipmicro",
            "category": "No-Code"
        },
        {
            "id": "jasper",
            "name": "Jasper AI",
            "solves": "AI copywriting, content creation, blog writing, marketing copy",
            "commission": "30% recurring",
            "affiliate_url": "https://jasper.ai/?ref=shipmicro",
            "category": "AI/Content"
        },
        {
            "id": "beehiiv",
            "name": "Beehiiv",
            "solves": "Newsletter platform, email marketing, audience building",
            "commission": "50% for 12 months",
            "affiliate_url": "https://www.beehiiv.com/?via=shipmicro",
            "category": "Email Marketing"
        },
        {
            "id": "notion",
            "name": "Notion",
            "solves": "Team productivity, project management, knowledge base, wikis",
            "commission": "50% of upgrades",
            "affiliate_url": "https://affiliate.notion.so/shipmicro",
            "category": "Productivity"
        },
        {
            "id": "nordvpn",
            "name": "NordVPN",
            "solves": "Online privacy, VPN, data security, remote work security",
            "commission": "$10-40 per signup",
            "affiliate_url": "https://go.nordvpn.net/aff_c?offer_id=15&aff_id=shipmicro",
            "category": "Security"
        },
        {
            "id": "surfer",
            "name": "Surfer SEO",
            "solves": "SEO optimization, content ranking, keyword research",
            "commission": "25% recurring",
            "affiliate_url": "https://surferseo.com/?via=shipmicro",
            "category": "SEO"
        },
        {
            "id": "hostinger",
            "name": "Hostinger",
            "solves": "Web hosting, domain names, WordPress hosting",
            "commission": "60% per sale",
            "affiliate_url": "https://www.hostinger.com/?ref=shipmicro",
            "category": "Hosting"
        }
    ]


def inject_affiliates(opportunities: List[Dict] = None) -> List[Dict]:
    """Match opportunities to affiliate products and generate pitch copy."""
    log.info("=" * 50)
    log.info("💰 TITAN Affiliate Injector v5.0 — Starting")
    log.info("=" * 50)
    
    # Load opportunities
    if opportunities is None:
        if not os.path.exists(INPUT_FILE):
            log.error(f"Input not found: {INPUT_FILE}")
            return []
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            opportunities = json.load(f)
    
    # Load products
    products = load_products()
    log.info(f"📥 Input: {len(opportunities)} opportunities, {len(products)} products")
    
    # Prepare LLM payload
    payload = json.dumps({
        "pain_points": [
            {"keyword": o.get("keyword", ""), "pain": o.get("pain_summary", ""), "score": o.get("opportunity_score", 0)}
            for o in opportunities[:10]
        ],
        "affiliate_products": [
            {"id": p["id"], "name": p["name"], "solves": p["solves"], "commission": p["commission"], "affiliate_url": p["affiliate_url"]}
            for p in products
        ]
    }, ensure_ascii=False)
    
    user_prompt = f"Match these pain points to the best affiliate products:\n\n{payload}"
    
    log.info("🧠 Sending to LLM for matching...")
    llm = LLMClient()
    response = llm.generate(prompt=user_prompt, system_prompt=SYSTEM_PROMPT, is_json=True)
    
    if not response:
        log.error("LLM returned empty response")
        return []
    
    # Parse
    text = response.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1:
        text = text[start:end + 1]
    
    try:
        matches = json.loads(text.strip())
    except json.JSONDecodeError as e:
        log.error(f"Failed to parse LLM response: {e}")
        return []
    
    # Filter out weak matches
    strong_matches = [m for m in matches if m.get("match_score", 0) >= 60]
    strong_matches.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    
    # Save
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(strong_matches, f, ensure_ascii=False, indent=2)
    
    log.info(f"✅ Generated {len(strong_matches)} affiliate matches → {OUTPUT_FILE}")
    return strong_matches


# Also save default products if file doesn't exist
def ensure_products_file():
    """Create default products file if it doesn't exist."""
    if not os.path.exists(PRODUCTS_FILE):
        products = _default_products()
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        log.info(f"📦 Created default {PRODUCTS_FILE} with {len(products)} products")


if __name__ == "__main__":
    ensure_products_file()
    matches = inject_affiliates()
    print(f"\n💰 Affiliate Matches:")
    for m in matches:
        print(f"  [{m.get('match_score', 0)}] {m.get('pain_keyword', '')} → {m.get('product_name', '')}")
        print(f"      {m.get('pitch_copy', '')[:80]}...")
