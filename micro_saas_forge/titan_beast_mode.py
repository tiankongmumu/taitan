import os
import sys
import json
import time
from datetime import datetime
import io

# Force utf-8 encoding for standard output to prevent crash when printing emojis on Windows CMD
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add the core_generators to path for LLMClient
sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from logger import get_logger

log = get_logger("beast_mode")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSIGHTS_FILE = os.path.join(BASE_DIR, "curated_insights_global.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "social_posts")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# The URL where the user has deployed their SaaS Radar
# Users should replace this once they deploy to a custom domain
RADAR_URL = "https://shipmicrosite-9hkl1v000-tiankongmumus-projects.vercel.app"

def generate_reddit_post(llm: LLMClient, insight: dict) -> dict:
    """Generate a highly contextual Reddit post based on a specific pain point and tool match."""
    tool_name = insight.get('matched_product_name', 'a great tool')
    pain_point = insight.get('target_pain_point_summary', '')
    
    prompt = f"""You are a helpful, independent software developer and curator posting on Reddit (r/SaaS or r/Entrepreneur) in 2026.
You run a daily curated list of top tools that solve specific founder pain points. 
You are writing a helpful response/post addressing this exact pain point: "{pain_point}"

Your goal is to warmly recommend this specific tool: {tool_name}
And direct them to your full curated tech radar URL: {RADAR_URL}

RULES:
1. Tone: Highly genuine, helpful, fellow founder indie-hacker vibe. No corporate speak. NO emojis.
2. Start by acknowledging the agonizing problem ("Man, {pain_point} used to kill my workflow...")
3. Introduce the tool naturally as the best solution on your radar right now.
4. Provide the exact URL {RADAR_URL} naturally. Example: "I actually just built an AI radar that analyzes common founder pain points and curates exact tool matches. For your case, {tool_name} is currently ranking #1. You can check the full analysis here: {RADAR_URL}"
5. Keep it under 150 words.

Output Format:
TITLE: [Catchy, relatable title for a standalone post]
BODY:
[The post body]
"""

    try:
        response = llm.generate(prompt)
        lines = response.strip().split("\n")
        title = ""
        body_lines = []
        in_body = False
        for line in lines:
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
            elif line.startswith("BODY:"):
                in_body = True
            elif in_body:
                body_lines.append(line)
        return {
            "title": title or f"How to solve the {pain_point[:20]} problem",
            "body": "\n".join(body_lines).strip(),
            "target_subreddit": "r/SaaS or r/Entrepreneur"
        }
    except Exception as e:
        log.warning(f"Failed to generate Reddit post: {e}")
        return {
            "title": f"Found a great tool for {pain_point[:20]}",
            "body": f"If you struggle with {pain_point}, check out {tool_name}. I featured it on my daily SaaS radar here: {RADAR_URL}",
            "target_subreddit": "r/SaaS"
        }

def generate_x_post(llm: LLMClient, insights: list) -> str:
    """Generate a viral X/Twitter thread summarizing today's top tools."""
    tools_summary = ", ".join([i.get('matched_product_name', '') for i in insights[:3]])
    
    prompt = f"""Write a highly engaging, viral X (Twitter) tweet (under 260 characters).
You run 'ShipMicro', a daily AI-curated radar for the best SaaS tools for founders.
Today's top trending tools on your radar: {tools_summary}

RULES:
1. Tone: Sharp, high-value, visionary Silicon Valley indie hacker in 2026.
2. Hook them with the value (e.g. "Stop wasting hours on manual work.")
3. Mention the tools briefly.
4. NO URLs: Do NOT include any links or URLs in the tweet body. Instead, end with "Check the replies for the full radar link 👇" or "Link in bio".
5. Use 2-3 highly relevant hashtags: #buildinpublic #indiehackers #SaaS
6. Output ONLY the tweet text. NO introductory text.
"""
    try:
        tweet = llm.generate(prompt)
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
        return tweet.strip()
    except Exception as e:
        log.warning(f"Failed to generate X post: {e}")
        return f"Just updated the ShipMicro AI Radar! Top tools today: {tools_summary} \n\nCheck out the full curated list here: {RADAR_URL} \n\n#buildinpublic #indiehackers #SaaS"


def main():
    print("============================================================")
    print("🔥 TITAN ENGINE - BEAST MODE (Traffic & Monetization) 🔥")
    print("============================================================")
    
    if not os.path.exists(INSIGHTS_FILE):
        log.error("curated_insights_global.json not found! Run the autopilot pipeline first.")
        sys.exit(1)
        
    with open(INSIGHTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    insights = data if isinstance(data, list) else data.get("insights", [])
    if not insights:
        log.error("No insights found in the data file.")
        sys.exit(1)
        
    log.info(f"Loaded {len(insights)} high-converting insights. Warming up the LLM engines...")
    llm = LLMClient()
    
    generated_content = {
        "x_tweet_of_the_day": "",
        "reddit_guerrilla_posts": []
    }
    
    # 1. Generate the master Twitter Post
    log.info("Generating viral X/Twitter hook...")
    tweet = generate_x_post(llm, insights)
    generated_content["x_tweet_of_the_day"] = tweet
    
    # 2. Generate Reddit Posts for each specific insight
    log.info("Generating hyper-specific Reddit engagement posts...")
    for idx, insight in enumerate(insights):
        log.info(f"  -> Drafting Reddit post for pain point {idx+1}: {insight.get('matched_product_name', '')}")
        reddit_draft = generate_reddit_post(llm, insight)
        generated_content["reddit_guerrilla_posts"].append(reddit_draft)
        # Avoid hitting rate limits if there are many
        time.sleep(2)
        
    # 3. Save to File
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_meta = os.path.join(OUTPUT_DIR, f"beast_mode_payload_{timestamp}.json")
    
    with open(output_meta, "w", encoding="utf-8") as f:
        json.dump(generated_content, f, ensure_ascii=False, indent=2)
        
    print("\n" + "="*60)
    print("🏆 BEAST MODE PAYLOAD GENERATED SUCCESSFULLY 🏆")
    print("="*60)
    print(f"\n🐦 YOUR VIRAL TWEET (Copy & Paste to X):\n------------------------------------------------------------\n{tweet}\n------------------------------------------------------------")
    
    print("\n👽 YOUR GUERRILLA REDDIT REPLIES (Find matching posts and reply):\n")
    for i, post in enumerate(generated_content["reddit_guerrilla_posts"]):
        print(f"--- [Target: {post['target_subreddit']}] ---")
        print(f"TITLE/HOOK: {post['title']}")
        print(f"BODY:\n{post['body']}\n")
        
    print("\n🚀 Next steps: Copy and paste these to drive massive traffic to your affiliate links!")

if __name__ == "__main__":
    main()
