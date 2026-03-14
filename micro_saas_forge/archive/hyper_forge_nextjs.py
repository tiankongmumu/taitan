"""
Hyper Forge: The Full-Stack Next.js Generator
==============================================
This script breaks the "Architecture Lock".
Instead of generating a single HTML file, it autonomously scaffolds, writes,
and deploys a completely independent full-stack Next.js application.
"""
import os
import sys
import json
import time
import subprocess

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from logger import get_logger

log = get_logger("hyper_forge")

DEPLOYMENTS_DIR = os.path.join(os.path.dirname(__file__), "deployments")

def run_cmd(cmd, cwd=None):
    log.info(f"⚙️ 执行命令: {cmd}")
    process = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
    for line in process.stdout:
        print(f"  | {line.strip()}")
    process.wait()
    return process.returncode == 0

def parse_llm_json(response_text: str) -> dict:
    try:
        # try to find json block
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = response_text.strip()
        return json.loads(json_str)
    except Exception as e:
        log.error(f"Failed to parse JSON from LLM: {e}")
        return json.loads(response_text[response_text.find("{"):response_text.rfind("}")+1])

def brainstorm_fullstack_app(llm: LLMClient):
    prompt = """You are a visionary Tech Founder. Pitch a highly viral, ultra-modern Micro-SaaS idea that requires a full-stack Next.js architecture (e.g., APIs, complex state, interactivity). 
Do NOT suggest simple forms or static tools. Think tools with "SOUL": "Visual Node-Based Logic Editor", "Real-time AI Sentiment Dashboard", "Interactive 3D CSS Pattern Generator", "AI-Powered Data Visualization Sandbox".
Reply in precise JSON format:
{
  "slug": "ai-data-sandbox",
  "name": "AI Data Sandbox",
  "description": "Upload a CSV and explore beautiful, interactive D3.js/Recharts data visualizations automatically powered by AI.",
  "category": "Data & Visualization",
  "core_features": ["Drag & Drop Upload", "Interactive Charts", "AI Insight Generation"]
}"""
    log.info("🧠 [Agent: PM] 开始构思全栈微型 SaaS 商业蓝图...")
    res_text = llm.generate(prompt)
    res = parse_llm_json(res_text)
    log.info(f"✅ 构思完成: {res.get('name', 'Unknown')} ({res.get('slug', 'unknown-slug')})")
    return res

def plan_architecture(llm: LLMClient, app_info: dict):
    prompt = f"""You are the Lead Architect. We are building a Next.js (App Router, Tailwind, TS) project named '{app_info['name']}'.
Description: {app_info['description']}
Features: {app_info['core_features']}

We have already scaffolded the base Next.js app.
List the exact files we need to CREATE OR OVERWRITE to build this MVP. Keep it minimal to 3-5 critical files max to ensure it works.
Always include `src/app/page.tsx` as the main UI. If you need an API, add `src/app/api/action/route.ts`.
Reply in JSON format:
{{
  "files": [
    {{
      "filepath": "src/app/page.tsx",
      "purpose": "The main landing page and interactive UI."
    }},
    {{
      "filepath": "src/app/api/process/route.ts",
      "purpose": "The backend API endpoint to process the request."
    }}
  ]
}}"""
    log.info("📐 [Agent: Architect] 正在设计代码架构图纸...")
    res_text = llm.generate(prompt)
    res = parse_llm_json(res_text)
    if "files" not in res:
        res["files"] = [{"filepath": "src/app/page.tsx", "purpose": "Main UI"}]
    log.info(f"✅ 架构设计完毕，需生成 {len(res['files'])} 个核心文件。")
    return res["files"]

def write_file_code(llm: LLMClient, app_info: dict, all_files: list, target_file: dict):
    filepath = target_file["filepath"]
    purpose = target_file["purpose"]
    
    prompt = f"""You are a Senior Full-Stack Next.js Developer.
Project Name: {app_info['name']}
Description: {app_info['description']}
File to write: `{filepath}`
Purpose of this file: {purpose}
Global architecture planned: {[f['filepath'] for f in all_files]}

REQUIREMENTS:
1. SOULFUL AESTHETICS: Write Production-Ready code with a premium Dark Mode design (`bg-gray-950`, `text-white`). Use glassmorphism (`backdrop-blur-xl`, `bg-white/5`), glowing shadows, and micro-animations (`hover:scale-105`, `transition-all`).
2. ROBUSTNESS: Handle loading states (loading spinners/skeletons) and edge cases beautifully. Ensure the UI feels alive and responsive.
3. REACT/NEXT.JS: If it's a TSX file, use 'use client' ONLY if using React hooks. Do not import external icon libraries; use inline SVG or emojis.
4. If it's an API route (route.ts), write the modern Next.js App Router API format (export async function POST(req) ...).
5. Return ONLY valid code. NO markdown formatting blocks like ```tsx. Just raw code. Do not explain anything."""

    log.info(f"👨‍💻 [Agent: Coder] 正在全力编写 {filepath} ...")
    code = llm.generate(prompt)
    code = code.replace("```tsx", "").replace("```ts", "").replace("```javascript", "").replace("```", "").strip()
    return code

def run_hyper_forge():
    log.info("\n" + "🚀"*30)
    log.info("🔥 HYPER FORGE 启动: 全栈架构破壁者")
    log.info("🚀"*30 + "\n")
    
    os.makedirs(DEPLOYMENTS_DIR, exist_ok=True)
    llm = LLMClient()
    
    # 1. Brainstorm
    app_info = brainstorm_fullstack_app(llm)
    slug = app_info["slug"]
    project_path = os.path.join(DEPLOYMENTS_DIR, slug)
    
    # 2. Scaffold Next.js App
    if not os.path.exists(project_path):
        log.info(f"📦 [Agent: DevOps] 正在初始化独立的 Next.js 代码库: {slug}")
        create_cmd = f"npx -y create-next-app@latest {slug} --typescript --tailwind --eslint --app --src-dir --import-alias \"@/*\" --use-npm"
        success = run_cmd(create_cmd, cwd=DEPLOYMENTS_DIR)
        if not success:
            log.error("❌ 初始化 Next.js 失败！")
            return False
    else:
        log.info(f"⚠️ [Agent: DevOps] 发现已存在项目库 {slug}，将在原基础上覆写。")
        
    # 3. Architecture
    files_to_write = plan_architecture(llm, app_info)
    
    # 4. Coding
    for file_meta in files_to_write:
        filepath = file_meta["filepath"]
        full_path = os.path.join(project_path, filepath)
        # Ensure directories exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        code = write_file_code(llm, app_info, files_to_write, file_meta)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(code)
        log.info(f"💾 [Agent: Coder] {filepath} 物理写入完成。")
        time.sleep(1) # Prevent API rate limits
        
    log.info(f"🎉 [Agent: DevOps] 全栈应用 {app_info['name']} 代码生成完毕！路径: {project_path}")
    log.info("💡 下一步: 可以通过 Vercel CLI 自动部署该独立应用。由于此属高阶资源消耗操作，第一阶段演示到此结束。")
    return True

if __name__ == "__main__":
    run_hyper_forge()
