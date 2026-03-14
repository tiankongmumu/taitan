import asyncio
import os
import json
import re
from loguru import logger
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
logger.add("titan_code_forge.log", rotation="10 MB", level="INFO")

class ProactiveCodeForge:
    """
    [Phase 28] Automaton: Proactive Code Forge (全自动造物主)
    接收 Demand Scout 挖到的商业痛点，直接通过大模型编写出独立的 React (Next.js) 页面，
    并自动写入现有的 vanguard-cover-letter SaaS 架构中。
    """
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        self.proposals_file = "new_saas_proposals.json"
        self.saas_root_dir = r"d:\Project\1\vanguard-cover-letter\src\app"

    def get_latest_proposal(self):
        if not os.path.exists(self.proposals_file):
            logger.warning("No proposals found.")
            return None
        with open(self.proposals_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data and len(data) > 0:
                return data[-1] # 提取最新鲜的商业灵感
        return None

    async def generate_react_code(self, proposal):
        logger.info(f"🧠 Generating Next.js scaffold for: {proposal['idea_name']}")
        prompt = f"""You are the Titan Engine's Code Forge (Expert Next.js Developer).
Your task is to build a high-converting, beautiful landing/tool page for a newly discovered Micro-SaaS tool.

Business Context:
- Product Name: {proposal['idea_name']}
- Target Audience: {proposal['target_audience']}
- Problem Solved: {proposal['pain_point']}
- Monetization: {proposal['monetization']}

Critical Next.js App Router Rules (QA Checklist):
1. If the component uses ANY React hooks (useState, useEffect) or interactive event listeners (onClick, onChange), the very first line of the code MUST be exactly: "use client";
2. Only output valid, fully self-contained TSX code.
3. Do not include markdown wrappers (like ```tsx).
4. Use Tailwind CSS carefully and use only lucide-react standard icons.

Requirements:
1. Write a SINGLE valid React file (Next.js App Router `page.tsx`). Must be `export default function Page() {{...}}`
2. Include a hero section and an interactive mock area for the tool.
3. Add a compelling Pricing/CTA section.
"""
        try:
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            raw_code = response.choices[0].message.content
            raw_code = re.sub(r'```[a-z]*\n?', '', raw_code)
            raw_code = re.sub(r'```', '', raw_code)
            return raw_code.strip()
        except Exception as e:
            logger.error(f"Failed to generate code: {e}")
            return None

    def perform_quality_assurance_check(self, code):
        """质量门禁扫描 (AQA): 防止框架级基础语法错误直接崩盘"""
        logger.info("🛡️ Performing Automated Quality Assurance (AQA) on forged code...")
        corrected_code = code
        
        # 常见致命错误 1：用了钩子但没有 "use client"
        uses_hooks = bool(re.search(r'use(State|Effect|Memo|Callback|Ref|Context)\b', code))
        uses_interactivity = bool(re.search(r'on(Click|Change|Submit)\b', code))
        
        if (uses_hooks or uses_interactivity) and not code.startswith('"use client"'):
            logger.warning("⚠️ QA Alert: Missing 'use client' directive for an interactive component. Injecting automatically.")
            # 强行在开头注入
            if corrected_code.startswith("'use client'"):
                corrected_code = '"use client";\n' + corrected_code[12:]
            else:
                corrected_code = '"use client";\n\n' + corrected_code
                
        # 常见致命错误 2：文件末尾少写大括号
        if "export default function" in corrected_code and not corrected_code.strip().endswith(("}", ");", ">")):
            logger.error("🛑 QA FAILED: The generated component appears to be truncated or syntactically invalid.")
            return None
            
        logger.success("✅ QA Passed. The forged code meets minimum compilation standards.")
        return corrected_code

    async def build_and_inject(self):
        logger.info("🚀 Launching Proactive Code Forge.")
        proposal = self.get_latest_proposal()
        if not proposal:
            logger.error("No raw materials to work with. Run titan_demand_scout.py first.")
            return

        slug = re.sub(r'[^a-zA-Z0-9-]', '-', proposal['idea_name'].lower())
        slug = re.sub(r'-+', '-', slug).strip('-')
        
        target_dir = os.path.join(self.saas_root_dir, slug)
        
        if os.path.exists(target_dir):
            logger.warning(f"SaaS Module '{slug}' already exists in project. Skipping.")
            return
            
        raw_code = await self.generate_react_code(proposal)
        if not raw_code:
            return
            
        # 强制执行质检流程
        verified_code = self.perform_quality_assurance_check(raw_code)
        if not verified_code:
            logger.error("SaaS Module creation aborted due to QA failure.")
            return
            
        logger.info(f"🏗️ Forging new SaaS module directory: {target_dir}")
        os.makedirs(target_dir, exist_ok=True)
        
        file_path = os.path.join(target_dir, "page.tsx")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(verified_code)
            
        logger.success(f"✅ Auto-Evolved new SaaS module successfully injected at: {target_dir}")

if __name__ == "__main__":
    forge = ProactiveCodeForge()
    asyncio.run(forge.build_and_inject())
