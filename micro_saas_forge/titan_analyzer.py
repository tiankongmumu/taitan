import os
import sys
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "raw_data_global.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "curated_insights_global.json")

# Import the robust LLM client we already have in the project
sys.path.insert(0, BASE_DIR)
from core_generators.llm_client import LLMClient

SYSTEM_PROMPT = """You are a world-class Growth Hacker and Affiliate Marketing Expert based in Silicon Valley.
Your task is to analyze real user pain points from Reddit (e.g. r/SaaS, r/Entrepreneur) and match them perfectly with our curated list of high-commission Global SaaS Affiliate Programs.

INSTRUCTIONS:
1. Analyze the provided Reddit posts to identify the top 4-5 MOST SEVERE and COMMON business pain points.
2. For EACH identified pain point, select EXACTLY ONE tool from the provided `available_affiliate_products` that acts as the perfect solution.
3. If no tool in the list can solve a specific pain point, DISCARD that pain point. Do not force a match.
4. For every successful match, write a highly persuasive, conversion-optimized "Pitch Copy". 
   - The pitch must directly address the pain, provide emotional value, and subtly push the user to click the link.
   - Use a native, professional yet punchy tone (like an experienced indie hacker giving advice).

OUTPUT FORMAT:
You MUST return a strict JSON array (NO markdown wrapping, NO extra text) matching this EXACT schema:
[
  {
    "pain_point": "A concise 1-sentence summary of the core pain point.",
    "evidence": "A direct, impactful quote or summary from the Reddit posts proving this pain.",
    "solution_id": "The ID of the matched product",
    "solution_name": "The exact name of the matched product",
    "commission_rate": "The commission rate of the product",
    "affiliate_url": "The affiliate link of the product",
    "pitch_copy": "A 1-2 sentence high-converting pitch copy (Pain + Solution + Action).",
    "match_score": 95 // Your confidence in this match (0-100)
  }
]
ENSURE THE OUTPUT IS 100% VALID JSON. NO PREAMBLE. NO POSTSCRIPT. ENGLISH ONLY.
"""

def main():
    print("="*60)
    print("TITAN Engine - Titan Analyzer (Global Edition MVP)")
    print("="*60)
    
    if not os.path.exists(INPUT_FILE):
        logging.error(f"Input file not found: {INPUT_FILE}. Please run pipeline_crawler.py first.")
        return
        
    logging.info(f"Loading data from {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    reddit_posts = raw_data.get("reddit_posts", [])
    products = raw_data.get("affiliate_products", [])
    
    if not reddit_posts or not products:
        logging.error("Insufficient data to analyze.")
        return

    # Trim posts to fit nicely within context window 
    posts_subset = []
    for p in reddit_posts[:15]: # Take top 15
        posts_subset.append({
            "title": p.get("title"),
            "selftext": p.get("selftext", "")[:300], # Trucate text further
            "score": p.get("score")
        })
        
    payload = json.dumps({
        "reddit_pain_points": posts_subset,
        "available_affiliate_products": products
    }, ensure_ascii=False)
    
    user_prompt = f"Please perform the affinity matching analysis on the following dataset:\n\n{payload}"
    
    logging.info(f"Assembled data payload of length {len(payload)}. Initializing LLM Client...")
    
    llm = LLMClient()
    
    logging.info("Sending complex Global Few-Shot prompt to LLM...")
    
    # We want structured JSON back
    response = llm.generate(
        system_prompt=SYSTEM_PROMPT,
        prompt=user_prompt,
        is_json=True
    )
    
    if not response:
        logging.error("Failed to get response from LLM.")
        return
        
    # Clean the response just in case it's wrapped in markdown
    cleaned_json_str = response.strip()
    if cleaned_json_str.startswith("```json"):
        cleaned_json_str = cleaned_json_str[7:]
    if cleaned_json_str.endswith("```"):
        cleaned_json_str = cleaned_json_str[:-3]
    cleaned_json_str = cleaned_json_str.strip()
    
    try:
        curated_insights = json.loads(cleaned_json_str)
        logging.info(f"Successfully generated {len(curated_insights)} global curated insights from LLM.")
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(curated_insights, f, ensure_ascii=False, indent=2)
            
        print(f"\n✅ Created curated_insights_global.json with {len(curated_insights)} highly-targeted product recommendations!")
        
    except json.JSONDecodeError as e:
        logging.error(f"LLM did not return valid JSON. Error: {e}")
        logging.error(f"Raw response: {cleaned_json_str[:500]}...")

if __name__ == "__main__":
    main()
