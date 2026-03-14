import asyncio
import os
import json
from datetime import datetime
from loguru import logger
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
logger.add("titan_demand_scout.log", rotation="10 MB", level="INFO")

class ProactiveDemandScout:
    """
    [Phase 28] Automaton: Proactive Demand Scout (主动侦察兵)
    当引擎算力闲置且预算充足时运行。
    自动去全球创业论坛、ProductHunt、Reddit r/SaaS 挖掘微型 SaaS 需求。
    """
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        self.output_file = "new_saas_proposals.json"

    async def scrape_raw_demand_signals(self):
        """模拟定向爬取海外高质量论坛数据 (e.g. Reddit, X/Twitter, IndieHackers)"""
        logger.info("📡 Scouting Web for 'I'd pay for this' signals...")
        await asyncio.sleep(2)
        import random
        # Expanded signal pool — each run picks 3 random demand signals
        all_signals = [
            {"platform": "X (Twitter)", "upvotes": 1205, "content": "Building pitch decks is the worst part of fundraising. If an AI could just read my 1-pager Notion doc and output a nicely formatted 10-slide deck with standard startup metrics, you'd have my money."},
            {"platform": "Reddit - r/freelance", "upvotes": 678, "content": "I spend 2 hours every week converting client invoices from PDF into spreadsheets. Would love a tool that auto-extracts line items, totals, and dates into a clean CSV."},
            {"platform": "Reddit - r/startups", "upvotes": 321, "content": "We need a simple tool that takes our GitHub changelog commits and auto-generates a beautiful customer-facing changelog newsletter we can email out."},
            {"platform": "IndieHackers", "upvotes": 540, "content": "I'd pay good money for a tool that watches my competitors' pricing pages and alerts me when they change prices or features. Competitor price monitoring is a huge gap."},
            {"platform": "Reddit - r/CustomerSuccess", "upvotes": 199, "content": "Wish there was a tool that takes raw support tickets and auto-tags them with sentiment, urgency, and product area. Would save our team hours of triage work."},
            {"platform": "X (Twitter)", "upvotes": 892, "content": "Why is there no good tool to convert a Loom video transcript into a professional SOW (Statement of Work) document? Freelancers would pay $10 each time."},
            {"platform": "Reddit - r/Entrepreneur", "upvotes": 445, "content": "I need something that reads my Stripe dashboard data and generates a beautiful investor-ready revenue report with MRR, churn, and growth charts."},
            {"platform": "IndieHackers", "upvotes": 367, "content": "A tool that takes my raw blog post draft and optimizes it for SEO — suggesting better titles, meta descriptions, internal links, and keyword density. I'd pay $5/post."},
            {"platform": "Reddit - r/webdev", "upvotes": 723, "content": "Is there a tool that converts Figma design tokens (colors, spacing, typography) into a ready-to-use CSS/Tailwind config file? Would save hours of manual setup."},
            {"platform": "Reddit - r/SaaS", "upvotes": 89, "content": "We need a massive ERP system for our trucking business."},
            {"platform": "X (Twitter)", "upvotes": 1100, "content": "Just spent 3 hours writing cold outreach emails. AI should be able to take a LinkedIn profile URL and generate a hyper-personalized cold email in seconds."},
            {"platform": "Reddit - r/sales", "upvotes": 556, "content": "I wish there was a tool that could analyze my sales call transcript and automatically generate a follow-up email with the key points discussed and next steps."},
        ]
        return random.sample(all_signals, 3)

    async def analyze_and_filter_opportunities(self, posts):
        """利用高智商模型过滤掉极其复杂的项目，精选出 Next.js + API 能一天做完的 Micro-SaaS"""
        prompt = f"""You are the Titan Engine's Demand Assessor. 
Analyze the following raw internet posts where users express a pain point or willingness to pay.
Posts: {json.dumps(posts)}

Filter objective: We are looking for ONE highly profitable Micro-SaaS idea that we can build as a new feature block in our Next.js architecture within 24 hours.

Rejection criteria:
- Requires heavy backend state management (like an ERP, CRM, social network).
- Requires custom hardware or highly specialized, inaccessible data.
- Low willingness to pay.

Acceptance criteria:
- Single-purpose utility (transforms data A to data B).
- High perceived value by business users or job seekers.
- Can be powered completely by LLM APIs behind the scenes + a simple React UI stringing it together.
- Perfect for a $9.99 one-time payment or small recurring.

Select the BEST idea, and output ONLY a JSON object:
{{
    "idea_name": "Name of the micro-SaaS tool",
    "target_audience": "Who buys this?",
    "pain_point": "What it solves",
    "solution_architecture": "How we build it using Next.js + DeepSeek API",
    "monetization": "Pricing strategy",
    "estimated_dev_time_hours": 12,
    "confidence_score": 95
}}
"""
        logger.info("🧠 Brain is analyzing signals and filtering out low-ROI / high-barrier ideas...")
        try:
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            result = json.loads(response.choices[0].message.content)
            result["discovered_at"] = datetime.now().isoformat()
            return result
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return None

    def save_proposal(self, proposal):
        proposals = []
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    proposals = json.load(f)
            except Exception:
                pass
                
        proposals.append(proposal)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(proposals, f, ensure_ascii=False, indent=4)
        logger.info(f"💾 Opportunity proposal saved to {self.output_file}.")

    async def execute_scout_mission(self):
        logger.info("🚀 Launching Proactive Demand Scout.")
        if not self.api_key:
            logger.error("API Key missing.")
            return

        raw_data = await self.scrape_raw_demand_signals()
        proposal = await self.analyze_and_filter_opportunities(raw_data)
        
        if proposal:
            logger.success(f"💎 Acquired high-conviction SaaS idea: {proposal.get('idea_name')}")
            logger.info(f"Target: {proposal.get('target_audience')} | Pain: {proposal.get('pain_point')}")
            self.save_proposal(proposal)
        else:
            logger.warning("No suitable ideas found in this scouting run.")

if __name__ == "__main__":
    scout = ProactiveDemandScout()
    asyncio.run(scout.execute_scout_mission())
