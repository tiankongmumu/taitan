"""
TITAN Publisher 📢
Automated Marketing & Distribution Module.
Acts as an AI Marketing Agency that generates SEO articles and multi-channel social media posts for newly deployed tools.
"""

import os
import sys
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logger import get_logger
from core_generators.llm_client import LLMClient
from config import GENERATED_APPS_DIR, FORGE_ROOT

log = get_logger("publisher")

MARKETING_OUTPUT_DIR = os.path.join(FORGE_ROOT, "marketing_assets")

class TitanPublisher:
    def __init__(self):
        self.llm = LLMClient()
        os.makedirs(MARKETING_OUTPUT_DIR, exist_ok=True)
        
    def generate_marketing_package(self, tool_keyword: str, tool_url: str, differentiation: str) -> dict:
        """
        Generates a complete marketing package for a new tool.
        Includes: SEO Blog post, Twitter Thread, Reddit Post, Xiaohongshu copy.
        """
        log.info(f"📢 TITAN Publisher: Generating marketing package for '{tool_keyword}'...")
        
        results = {
            "seo_blog": self._generate_seo_blog(tool_keyword, tool_url, differentiation),
            "twitter": self._generate_twitter_thread(tool_keyword, tool_url, differentiation),
            "reddit": self._generate_reddit_post(tool_keyword, tool_url, differentiation),
            "xiaohongshu": self._generate_xhs_copy(tool_keyword, tool_url, differentiation)
        }
        
        self._save_assets(tool_keyword, results)
        return results
        
    def _generate_seo_blog(self, keyword: str, url: str, diff: str) -> str:
        log.info("  ✍️ Drafting SEO Blog article...")
        prompt = f"""You are an elite SEO content writer.
We just built a new web tool: "{keyword}". 
Its unique selling point is: {diff}
Its live URL is: {url}

Write a highly engaging, SEO-optimized 1000-word tutorial/article that targets the long-tail keywords around "{keyword}".
The post MUST:
1. Have an eye-catching H1 title.
2. Explain the problem clearly (why developers/users struggle with this).
3. Offer concrete, actionable advice or a tutorial.
4. Seamlessly introduce our new tool ({url}) as the ultimate solution.
5. Provide code snippets or real-world examples if applicable.
6. Use Markdown formatting (##, ###, bullet points, bold).
"""
        response = self.llm.generate(prompt, system_prompt="You rank #1 on Google for everything you write. Provide pure markdown content.")
        return response

    def _generate_twitter_thread(self, keyword: str, url: str, diff: str) -> str:
        log.info("  🐦 Drafting Twitter/X Thread...")
        prompt = f"""You are a viral tech founder on Twitter/X building in public.
We just shipped a new tool: "{keyword}".
Differentiator: {diff}
Link: {url}

Write a viral Twitter thread (3-5 tweets max).
Tone: Energetic, builder-in-public, slightly provocative but deeply helpful.
Structure:
Tweet 1: The Hook. State a painful problem everyone hates. Mention we just "shipped a solution". Include Link.
Tweet 2: Why existing solutions suck.
Tweet 3: How our tool ({keyword}) changes this (mention the differentiator).
Tweet 4: Call to action. Tell them it's live, ask for feedback. Link again.
"""
        response = self.llm.generate(prompt)
        return response

    def _generate_reddit_post(self, keyword: str, url: str, diff: str) -> str:
        log.info("  👽 Drafting Reddit Post...")
        prompt = f"""You are an authentic, non-spammy developer posting in r/SideProject or r/webdev on Reddit.
We built: "{keyword}"
Differentiator: {diff}
Link: {url}

Write a Reddit post.
The Reddit community hates marketing speak. The tone MUST be: humble, technical, sharing a genuine problem we solved for ourselves.
Start with "I built..." or "I was so frustrated with... so I made..."
Explain the tech stack or the logic briefly to show you are a real dev.
Include the link naturally. Ask for brutal feedback.
"""
        response = self.llm.generate(prompt)
        return response

    def _generate_xhs_copy(self, keyword: str, url: str, diff: str) -> str:
        log.info("  📕 Drafting Xiaohongshu (小红书) Copy...")
        prompt = f"""你是一个深谙小红书流量密码的效率工具/程序员博主。
我们刚发布了一个新工具："{keyword}"
它的核心亮点是：{diff}
网址：{url}

写一篇小红书种草文案。
要求：
1. 吸引眼球的爆款标题（带上适合的Emoji，比如🔥、💥、简直了）。
2. 口语化，用词要“惊艳”、“效率神器”、“打工人必备”、“封神”。
3. 痛点代入，直接点出不用这个工具会有多麻烦。
4. 列出 3 个不容拒绝的优点。
5. 结尾加上适当的 Tag（例如 #效率工具 #程序员 #神器 #生产力工具）。
"""
        response = self.llm.generate(prompt)
        return response

    def _save_assets(self, keyword: str, assets: dict):
        """Saves the generated content to disk."""
        safe_name = keyword.lower().replace(" ", "_").replace("/", "").strip()
        timestamp = int(time.time())
        folder_path = os.path.join(MARKETING_OUTPUT_DIR, f"{safe_name}_{timestamp}")
        os.makedirs(folder_path, exist_ok=True)
        
        with open(os.path.join(folder_path, "seo_blog.md"), "w", encoding="utf-8") as f:
            f.write(assets["seo_blog"])
            
        with open(os.path.join(folder_path, "social_media.txt"), "w", encoding="utf-8") as f:
            f.write("=== TWITTER THREAD ===\n")
            f.write(assets["twitter"])
            f.write("\n\n=== REDDIT POST ===\n")
            f.write(assets["reddit"])
            f.write("\n\n=== 小红书文案 ===\n")
            f.write(assets["xiaohongshu"])
            
        log.info(f"✅ Marketing assets saved to: {folder_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        kw = sys.argv[1]
    else:
        kw = "SQL Query Optimizer"
        
    pub = TitanPublisher()
    pub.generate_marketing_package(kw, "https://shipmicro.com/tools/sql-opt", "Zero latency, runs locally in browser via WASM")
