import os
import sys
import argparse
from datetime import datetime

# Add core_generators to path to use LLMClient
sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from logger import get_logger

log = get_logger("article_forge")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "seo_articles")

# The user's Aliyun Ambassador Link (Fallback if not provided in CLI)
DEFAULT_ALIYUN_LINK = "https://www.aliyun.com/minisite/goods?userCode=YOUR_CODE_HERE"

def generate_seo_article(llm: LLMClient, topic: str, affiliate_link: str) -> str:
    """Uses the LLM to write a high-converting, 2000+ word tech tutorial."""
    
    prompt = f"""You are a senior DevOps engineer and highly influential tech blogger on Zhihu (知乎) and Juejin (掘金) in 2026.
Your goal is to write a comprehensive, "babysitter-level" (保姆级) technical tutorial that ranks #1 on search engines.

TOPIC: "{topic}"

**CRITICAL MONETIZATION RULE:**
You MUST heavily promote this specific Aliyun server link as the *absolute prerequisite* for this tutorial: {affiliate_link}
This is not an ad at the end. This is a mandatory step in the environment setup.

**ARTICLE STRUCTURE:**
1. **Catchy Title**: Irresistible title (e.g., "[2026最新] 零基础保姆教程：带你用不到百元搭建顶级...")
2. **The Hook (引言)**: 1-2 paragraphs addressing the exact pain point. Why is this topic so hot right now? What are the common struggles?
3. **Environment Prep (核心引流区)**: 
   - State clearly: "To run this properly, local laptops won't work due to [Memory/Network/Firewall limits]. We need a cloud server."
   - Strongly recommend: "I highly recommend the Aliyun Lightweight App Server for beginners. It's stable, cheap, and perfect for this."
   - Provide the EXACT clickable link in Markdown: `[👉 点击这里领取新人专属特惠服务器通道]({affiliate_link})`
   - Add a subtle FOMO: "Use this specific channel to get the lowest price. Don't buy the standard retail ones, they are a ripoff."
4. **Step-by-Step Implementation (硬核实操)**:
   - Provide actual dummy Docker commands or bash scripts relevant to the topic.
   - Use Markdown code blocks.
   - Make it look incredibly professional and authoritative.
5. **Conclusion & Q&A**: Wrap up nicely, congratulating them on their new setup.

**TONE:** Helpful, authoritative, slightly cynical about bad tech, deeply encouraging to beginners. Written entirely in Simplified Chinese (简体中文).

Return ONLY the raw Markdown content. No conversational intro.
"""

    log.info(f"Generating 2000+ word SEO tutorial for topic: '{topic}'...")
    try:
        content = llm.generate(prompt)
        return content.strip()
    except Exception as e:
        log.error(f"Failed to generate article: {e}")
        return f"# Failed to generate article\n\nError: {e}"

def main():
    print("============================================================")
    print("🚀 TITAN ENGINE - ALIYUN ARTICLE FORGE (SEO Cannon) 🚀")
    print("============================================================")
    
    parser = argparse.ArgumentParser(description="Generate SEO-optimized tech tutorials with Aliyun Affiliate hooks.")
    parser.add_argument("--topic", type=str, required=True, help="The technical topic/keyword (e.g., '部署 DeepSeek')")
    parser.add_argument("--link", type=str, default=DEFAULT_ALIYUN_LINK, help="Your Aliyun Ambassador short link")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    llm = LLMClient()
    
    article_markdown = generate_seo_article(llm, args.topic, args.link)
    
    # Generate a safe filename
    safe_topic = "".join(c for c in args.topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_topic = safe_topic.replace(' ', '_').lower()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"aliyun_seo_{safe_topic}_{timestamp}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(article_markdown)
        
    print("\n" + "="*60)
    print("🏆 SEO ARTICLE GENERATED SUCCESSFULLY 🏆")
    print("="*60)
    print(f"Topic: {args.topic}")
    print(f"Injected Affiliate Link: {args.link}")
    print(f"Saved to: {filepath}\n")
    print("Next Steps:")
    print("1. Review the generated markdown.")
    print("2. Copy and paste it to Zhihu, CSDN, Juejin, or your personal blog.")
    print("3. Watch the passive Aliyun commissions roll in!")

if __name__ == "__main__":
    main()
