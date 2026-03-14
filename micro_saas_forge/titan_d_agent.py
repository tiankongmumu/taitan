"""
TITAN Engine v6.0 - D-Agent (Development)
Implementation layer. Reads proposals from R-Agent and dynamically generates Next.js application code.
Generates:
1. src/app/api/{id}/route.ts
2. src/app/tools/{id}/page.tsx
"""
import os
import sys
import json
import re

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from logger import get_logger

log = get_logger("titan_d_agent")

SITE_DIR = os.path.join(os.path.dirname(__file__), "shipmicro_site")

class DAgent:
    def __init__(self):
        self.llm = LLMClient()
    
    def develop_proposal(self, proposal: dict, feedback: str = None, previous_api_code: str = None, previous_page_code: str = None) -> bool:
        app_id = proposal.get("id")
        log.info(f"🔨 TITAN D-Agent: Starting development for [{app_id}] {proposal.get('name')}")
        if feedback:
            log.warning(f"⚠️ Applying E-Agent Feedback: {feedback}")
        
        # Paths
        api_dir = os.path.join(SITE_DIR, "src", "app", "api", app_id)
        page_dir = os.path.join(SITE_DIR, "src", "app", "tools", app_id)
        os.makedirs(api_dir, exist_ok=True)
        os.makedirs(page_dir, exist_ok=True)
        
        # 1. Generate API Route
        api_code = self._generate_api_route(proposal, feedback, previous_api_code)
        if not api_code:
            return False
            
        # 2. Generate Page Component
        # We pass the api_code to the page generator so it knows what inputs the API expects.
        page_code = self._generate_pageComponent(proposal, api_code, feedback, previous_page_code)
        if not page_code:
            return False
            
        # Write to disk
        api_path = os.path.join(api_dir, "route.ts")
        page_path = os.path.join(page_dir, "page.tsx")
        
        with open(api_path, "w", encoding="utf-8") as f:
            f.write(api_code)
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(page_code)
            
        log.info(f"✅ D-Agent: Generated API route at {api_path}")
        log.info(f"✅ D-Agent: Generated Page component at {page_path}")
        
        # Register in lib/data.ts
        self._register_tool(proposal)
        
        return True
        
    def _generate_api_route(self, proposal: dict, feedback: str = None, previous_code: str = None) -> str:
        log.info(f"   🤖 D-Agent: Asking LLM to write route.ts...")
        feedback_prompt = f"\n⚠️ CRITICAL FEEDBACK FROM PREVIOUS RUN: {feedback}\nPrevious Code:\n```typescript\n{previous_code}\n```\nFIX THE ISSUES ABOVE!\n" if feedback and previous_code else ""
        
        prompt = f"""You are an expert Next.js backend developer.
Based on the following Viral Web App Proposal, write a Next.js App Router API route `route.ts`.

Proposal:
{json.dumps(proposal, ensure_ascii=False, indent=2)}{feedback_prompt}

Requirements:
1. It must be a POST request handler.
2. It should accept 2-3 input fields from the user body that are relevant to the proposal (e.g., if it's MBTI, accept `mbti` and `recent_bad_luck`).
3. It must construct a Prompt for DeepSeek API to generate the script based on the inputs and the `hook_question`.
4. Return the generated text as json: `{{ script: "..." }}`
5. Use fetch to call `https://api.deepseek.com/v1/chat/completions` using `process.env.DEEPSEEK_API_KEY`. (Model: deepseek-chat)
6. DO NOT use NextRequest, just use standard Request.

Return ONLY the TypeScript code block (```typescript...```). Do not explain.
"""
        response = self.llm.generate(prompt)
        return self._extract_code(response, "typescript")
        
    def _generate_pageComponent(self, proposal: dict, api_code: str, feedback: str = None, previous_code: str = None) -> str:
        log.info(f"   🤖 D-Agent: Asking LLM to write page.tsx...")
        feedback_prompt = f"\n⚠️ CRITICAL FEEDBACK FROM PREVIOUS RUN: {feedback}\nPrevious Code:\n```tsx\n{previous_code}\n```\nFIX THE ISSUES ABOVE!\n" if feedback and previous_code else ""
        
        prompt = f"""You are an expert React/Next.js frontend developer and UI/UX designer.
Based on the following Viral Web App Proposal and the Backend API code, write the Next.js `page.tsx` component.

Proposal:
{json.dumps(proposal, ensure_ascii=False, indent=2)}{feedback_prompt}

Backend API fields expected:
{api_code}

Requirements:
1. Use Tailwind CSS for a dark, cyberpunk, premium "{proposal.get('theme_color')}" theme.
2. Create standard React state for the inputs required by the API.
3. Build a beautiful form for the inputs.
4. Implement a typewriter effect to display the `result` string character by character (speed ~50ms).
5. CRITICAL VIRAL/PAYWALL LOGIC:
   - Wait until about 40% of the text is displayed (or roughly 80 characters).
   - Interrupt the typewriter effect immediately.
   - Show a popup/overlay "faux paywall" that halts the progress exactly at: "{proposal.get('paywall_trigger')}".
   - The paywall must say "微信支付 9.9 元解锁".
   - Create a `handlePay` function that just calls `alert('测试版：模拟支付成功');` then hides the paywall and RESUMES the typing effect from where it left off.
6. Return `export default function OraclePage() {{ ... }}`
7. Must be a Client Component (`"use client";` at top).
8. The header should link back to `/`.

Return ONLY the TSX code block (```tsx...```). Do not explain.
"""
        response = self.llm.generate(prompt)
        # fallback to typescript if tsx tag is missed
        code = self._extract_code(response, "tsx") 
        if not code:
            code = self._extract_code(response, "typescript")
        return code

    def _extract_code(self, text: str, lang: str) -> str:
        # Try finding ```lang ... ```
        pattern = re.compile(rf'```{lang}\n(.*?)```', re.DOTALL)
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
        # Fallback to general ``` ... ```
        pattern2 = re.compile(r'```(.*?\n)?(.*?)```', re.DOTALL)
        match2 = pattern2.search(text)
        if match2:
            return match2.group(2).strip()
        return text

    def _register_tool(self, proposal: dict):
        log.info(f"   ⚙️ D-Agent: Registering tool in src/lib/data.ts...")
        data_path = os.path.join(SITE_DIR, "src", "lib", "data.ts")
        if not os.path.exists(data_path):
            return
            
        with open(data_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        if f'"{proposal.get("id")}"' in content:
            log.info("Tool already registered.")
            return

        new_tool = f"""
    "{proposal.get('id')}": {{
        id: "{proposal.get('id')}",
        emoji: "🔮",
        title: "{proposal.get('name')}",
        description: "{proposal.get('description')}",
        category: "Entertainment",
        isPremium: false,
        translations: {{
            zh: {{
                title: "{proposal.get('name')}",
                description: "{proposal.get('description')}"
            }}
        }}
    }},"""
        
        # Inject right after `export const CURATED_TOOLS: Record<string, Tool> = {`
        marker = "export const CURATED_TOOLS: Record<string, Tool> = {"
        if marker in content:
            new_content = content.replace(marker, marker + new_tool)
            with open(data_path, "w", encoding="utf-8") as f:
                f.write(new_content)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        proposal_file = sys.argv[1]
        with open(proposal_file, "r", encoding="utf-8") as f:
            proposals = json.load(f)
        agent = DAgent()
        # Just develop the first one as a test
        agent.develop_proposal(proposals[0])
    else:
        print("Usage: python titan_d_agent.py <path_to_proposal_json>")
