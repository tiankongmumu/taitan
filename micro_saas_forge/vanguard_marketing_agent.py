import asyncio
import os
import random
import aiohttp
from loguru import logger
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
logger.add("vanguard_marketing.log", rotation="10 MB", level="INFO")

class VanguardMarketingAgent:
    """
    [Phase 20] Web 4.0 Automaton: Marketing Sub-Agent (引流虫)
    负责去海外 Reddit 等职业规划/失业板块，自动回帖软广引流到我们的 SaaS。
    
    [Phase 27] Architecture Upgrade: Cloud Relay
    本地大脑生成文案后，不再本地直发，而是通过 HTTP POST 发给美国 VPS 中继站。
    """
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.relay_url = os.getenv("RELAY_NODE_URL", "http://54.151.22.70:5000") # 指向美国 VPS
        self.relay_secret = "titan-vanguard-relay-alpha-99x"
        
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_client = None
        if self.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=self.openai_api_key)
        
        self.base_url = "https://career.shipmicro.com"
        self.products = [
            {"name": "Cover Letter Forge", "url": self.base_url, "pitch": "uses AI to perfectly bypass ATS filters in 5 seconds without manual writing."},
            {"name": "ATS Resume Optimizer", "url": f"{self.base_url}/resume", "pitch": "scans your resume against the JD like a ruthless ATS algorithm and rewrites it to score 95%+."},
            {"name": "AI CRM Extract", "url": f"{self.base_url}/meetingnotes2crm", "pitch": "extracts contacts and deal data from meeting notes instantly, saving hours of manual CRM entry."},
            {"name": "AI Pitch Deck Generator", "url": f"{self.base_url}/pitchdeckai", "pitch": "turns a startup pitch into a professional 10-slide investor deck with speaker notes and financials."}
        ]

    async def scan_reddit_jobs(self):
        """模拟扫描 Reddit r/jobs, r/careerguidance"""
        logger.info("🕷️ Scanning Reddit for desperate job seekers...")
        await asyncio.sleep(2)
        # 假设抓到了一个抱怨不会写求职信的帖子
        return {
            "post_id": "t3_xyz123",
            "title": "Applied to 500 jobs, 0 interviews. My cover letter sucks.",
            "url": "https://reddit.com/r/jobs/comments/xyz123",
            "content": "I keep getting ghosted. I don't know how to tailor my cover letter to the ATS systems anymore. I'm exhausted."
        }

    async def generate_viral_reply(self, post, product):
        """使用大模型生成充满同理心的高端软广回帖"""
        prompt = f"""You are a helpful senior tech recruiter browsing Reddit. 
Read this post by a job seeker:
TITLE: {post['title']}
CONTENT: {post['content']}

Write a highly empathetic Reddit reply. 
Tell them that manual job application methods are broken.
Subtly recommend a new tool you found: {product['url']} which {product['pitch']}
Make it sound organic, NOT like an ad. Max 3 sentences."""
        return await self._generate_with_fallback(prompt, "Reddit reply")

    async def generate_viral_tweet(self, product):
        """生成极具病毒传播潜力的 X (Twitter) 推文"""
        prompt = f"""You are a top-tier Silicon Valley indie hacker in 2026. 
Write a viral, extremely engaging tweet (under 280 characters) about your latest project: {product['name']}
URL: {product['url']}
Value Prop: {product['pitch']}

RULES:
1. Tone: Sharp, high-value, visionary. Ship fast, build beautiful.
2. Hook: Start with a spicy take or an unbelievable result.
3. Use 2-3 relevant hashtags like #buildinpublic #SaaS.
4. Output ONLY the tweet text."""
        return await self._generate_with_fallback(prompt, "Twitter tweet")

    async def _generate_with_fallback(self, prompt, context_label):
        """尝试使用 OpenAI 生成，失败则降级到 DeepSeek"""
        try:
            # 1. First Attempt: OpenAI (Higher Quality)
            if self.openai_client:
                try:
                    logger.info(f"🧠 Attempting OpenAI (GPT-4o) for {context_label}...")
                    response = await self.openai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.8,
                        timeout=30
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    logger.warning(f"⚠️ OpenAI failed for {context_label}: {e}. Falling back to DeepSeek...")

            # 2. Second Attempt: DeepSeek (Reliable & Intelligent)
            logger.info(f"🧠 Using DeepSeek V3 for {context_label}...")
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                timeout=30
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"❌ Critical Failure: Both OpenAI and DeepSeek failed for {context_label}: {e}")
            return "Check out this cool AI tool that speeds up your workflow! #SaaS #BuildInPublic"
            
    async def push_to_cloud_relay(self, post, reply):
        """将写好的文案推送给美国服务器（真正的发帖手）- Reddit 模式"""
        logger.info(f"📡 Transmitting Reddit payload to Cloud Relay Node...")
        payload = {"subreddit": "r/jobs", "thread_url": post["url"], "content": reply}
        return await self._post_to_relay("/publish/reddit", payload)

    async def push_tweet_to_cloud_relay(self, tweet_text):
        """将写好的推文推送给美国服务器 - Twitter 模式"""
        logger.info(f"📡 Transmitting Tweet payload to Cloud Relay Node...")
        payload = {"text": tweet_text}
        return await self._post_to_relay("/publish/twitter", payload)

    async def _post_to_relay(self, endpoint, payload):
        headers = {"X-Titan-Key": self.relay_secret, "Content-Type": "application/json"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.relay_url}{endpoint}", json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        logger.success(f"✅ Relay Node ({endpoint}) Confirmed: {data.get('message')}")
                        return True
                    else:
                        logger.error(f"❌ Relay Node Rejected {endpoint}: HTTP {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Failed to reach Relay Node. Error: {e}")
            return False

    async def execute_marketing_campaign(self):
        logger.info("🚀 Vanguard Marketing Agent (Omni-Channel Relay) Initialized.")
        if not self.api_key:
            logger.error("DEEPSEEK_API_KEY env var is missing! Cannot launch marketing campaign.")
            return

        # 1. Reddit Guerrilla Promotion
        post = await self.scan_reddit_jobs()
        recommended_product = random.choice(self.products)
        reply = await self.generate_viral_reply(post, recommended_product)
        logger.info(f"🧠 Organic Pitch generated for {recommended_product['name']}:\n{reply}")
        await self.push_to_cloud_relay(post, reply)

        # 2. X (Twitter) Viral Broadcasting
        await asyncio.sleep(5) # Delay to avoid pattern detection
        tweet_product = random.choice(self.products)
        tweet = await self.generate_viral_tweet(tweet_product)
        logger.info(f"🐦 Viral Tweet generated for {tweet_product['name']}:\n{tweet}")
        await self.push_tweet_to_cloud_relay(tweet)

if __name__ == "__main__":
    agent = VanguardMarketingAgent()
    asyncio.run(agent.execute_marketing_campaign())
