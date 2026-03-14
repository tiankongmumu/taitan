import os
import sys
import json
import re

sys.path.insert(0, os.path.dirname(__file__))
from demand_radar import DemandRadar
from core_generators.llm_client import LLMClient
from logger import get_logger

log = get_logger("titan_mounter")

def mount_new_tool():
    log.info("🔍 Scaning demand for a new mounted tool...")
    radar = DemandRadar()
    opportunities = radar.get_top_opportunities(n=5)
    
    if not opportunities:
        log.warning("No opportunities found.")
        return
        
    target = opportunities[0]
    keyword = target.get("keyword", "unknown tool")
    log.info(f"🎯 Selected Opportunity: {keyword}")
    
    slug = re.sub(r'[^a-zA-Z0-9]', '-', keyword).strip('-').lower()
    
    prompt = f"""You are an elite Next.js and React developer.
Please build a functional, single-file Next.js page component (page.tsx) for a new tool: "{keyword}".

Requirements:
1. Use `"use client";` at the top.
2. The UI must be exceptionally beautiful, using Tailwind CSS, glassmorphism, nice gradients (e.g. `bg-gradient-to-br from-slate-900 to-slate-800`), and smooth transitions.
3. It must be a fully working utility. Write real logic using React hooks.
4. Export as `export default function ToolPage() {{...}}`
5. Do NOT use any external icon libraries. Use emojis.
6. Provide ONLY the final TypeScript/React code wrapped in a ```tsx code block.

Build a truly premium experience.
"""
    log.info(f"🧠 Generating code for {slug}...")
    llm = LLMClient()
    response = llm.generate(prompt)
    code = llm.extract_code_block(response)
    
    if not code:
        log.error("❌ Failed to generate code")
        return
        
    out_dir = os.path.join("d:\\Project\\1\\micro_saas_forge", "shipmicro_site", "src", "app", "tools", slug)
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "page.tsx")
    
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(code)
    log.info(f"✅ Code written to {out_file}")
    
    # Update data.ts using LLM or regex (Regex is faster here)
    data_file = os.path.join("d:\\Project\\1\\micro_saas_forge", "shipmicro_site", "src", "lib", "data.ts")
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            data_content = f.read()
            
        desc = getattr(target, 'desc', f"Awesome {keyword} tool")[:60]
        # Ask LLM for short Chinese name and desc for the registry
        info_prompt = f"Give me a JSON with two keys: 'nameCn' (Short Chinese name for tool '{keyword}', max 6 chars) and 'descCn' (One sentence Chinese description, max 20 chars)."
        try:
            info_resp = json.loads(llm.extract_code_block(llm.generate(info_prompt, is_json=True)) or '{}')
        except:
            info_resp = { "nameCn": keyword, "descCn": f"{keyword} 工具" }
            
        entry = f'    "{slug}": ["{keyword.title()}", "{desc}", "Utility", "✨", "{info_resp.get("nameCn", keyword)}", "{info_resp.get("descCn", desc)}"],\n'
        
        # Inject just before the closing brace of CURATED_TOOLS
        pattern = r"(const CURATED_TOOLS: Record<string, ToolEntry> = \{[\s\S]*?)(};)"
        new_content = re.sub(pattern, r"\1" + entry + r"\2", data_content)
        
        with open(data_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        log.info(f"✅ Registered {slug} in data.ts")

if __name__ == "__main__":
    mount_new_tool()
