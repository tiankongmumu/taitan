"""
TITAN Engine v6.0 - R-Agent (Research / Hypothesis Generator)
Scans market trends and generates 3 distinct monetization Proposal Hooks for the 'Emotion Printing Press' matrix.
"""
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from logger import get_logger

log = get_logger("titan_r_agent")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "r_agent_proposals")

class RAgent:
    def __init__(self):
        self.llm = LLMClient()
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def generate_proposals(self) -> list[dict]:
        log.info("🔍 TITAN R-Agent: Requesting Market Trend Validation...")
        
        # V6.5 Upgrade: Ingest mathematically proven keywords from Commercial Intuition Engine
        intuition_file = os.path.join(os.path.dirname(__file__), "validated_commercial_proposals.json")
        validated_keywords = []
        
        if os.path.exists(intuition_file):
            with open(intuition_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                proposals = data.get("top_proposals", [])
                for p in proposals[:3]:  # Take the top 3 highest WTP niches
                    source_tag = "[闲鱼已验证]" if p.get("source") == "xianyu_proven" else "[全球需求大]"
                    validated_keywords.append(f"{source_tag} {p.get('keyword')} (预计售价: {p.get('avg_unit_price_rmb', 9.9)}元)")
                    
        if not validated_keywords:
            log.warning("⚠️ No validated intuition data found. Falling back to default arbitrage keywords.")
            validated_keywords = ["抖音去水印工具", "PDF全自动解密脚本", "小红书营销配图生成"]

        trending_display = "\n".join([f"- {kw}" for kw in validated_keywords])

        prompt = f"""You are the master brain of a matrix of highly viral WeChat/Xiaohongshu Web Apps ("The Emotion Printing Press") and Xianyu Arbitrage Scripts.
Your goal is to take the following MATHEMATICALLY PROVEN high-demand niches and invent 3 DISTINCT, highly targeted commercial web apps or scripts to monopolize them.

These niches have already passed our Willingness-to-Pay (WTP) engine. Do NOT invent new niches. Just wrap these niches into sellable products.

Proven Niches for today:
{trending_display}

For EACH concept, provide:
1. `id`: A unique short English identifier (e.g., "dy-watermark-pro", "pdf-unlocker").
2. `name`: The viral Chinese name of the app (e.g., "全网无水印解析终极版").
3. `description`: A 1-sentence description of what it does.
4. `target_audience`: The specific demographic who will pay for this.
5. `hook_question`: The marketing hook for Xianyu/Xiaohongshu (e.g., "做影视剪辑天天求人去水印？").
6. `paywall_trigger`: EXACTLY how we charge money (e.g., "软件本体免费发送，内置机器码激活授权收费9.9元/月").
7. `theme_color`: The primary Tailwind CSS color for the UI (e.g., "rose", "blue").

You MUST return the exact output in a valid JSON array format. Do not return markdown formatted json. Just straight JSON.
Example output:
[
  {{
    "id": "mbti-villain",
    "name": "MBTI 反派人格鉴定",
    "description": "基于MBTI分析你灵魂深处的黑暗面和适合演的影视剧大反派。",
    "target_audience": "热衷MBTI的00后、对现状不满的年轻人",
    "hook_question": "撕下面具，你究竟是哪个反派？",
    "paywall_trigger": "在显示你的最终反派归宿和专属腹黑武器前卡住",
    "theme_color": "red"
  }}
]"""

        log.info("🤖 R-Agent: Asking LLM to generate 3 unique monetization proposals...")
        response = self.llm.generate(prompt, system_prompt="You are a ruthless viral marketing genius.")
        
        proposals = []
        try:
            # Extract JSON block if it's there
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
                
            proposals = json.loads(json_str)
        except Exception as e:
            log.error(f"Failed to parse LLM response into JSON. Error: {e}")
            log.error(f"Raw Response: {response}")
            return []
            
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(OUTPUT_DIR, f"proposal_{timestamp}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(proposals, f, ensure_ascii=False, indent=2)
            
        log.info(f"✅ R-Agent: Generated {len(proposals)} proposals saved to {filename}")
        for p in proposals:
            log.info(f"   💡 Proposal: {p.get('name')} ({p.get('id')})")
            
        return proposals

if __name__ == "__main__":
    agent = RAgent()
    agent.generate_proposals()
