import os
import sys
import json

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from logger import get_logger

log = get_logger("titan_roundtable_s10")

def run_reality_check():
    llm = LLMClient()
    
    prompt = """你是3位顶级的商业操盘手和流量黑客。
目前项目的现状：
我们之前试图做“情绪印钞机”（做类似于“MBTI测算”、“前世牛马判官”的 Next.js 网页，然后弹窗收 9.9元）。
但刚才主理人（用户）一针见血地指出：**“现在这种赚钱方案完全是自嗨，根本行不通！”**

请进行一场无情的、残酷的、且极度务实的圆桌会议。

**Persona 1: 流量老镰刀 (极其务实，只看ROI和流量来源)**
立刻痛批之前的方案为什么是“程序员的自嗨”（如：没有自带流量池、小红书/微信封杀外链极速）。然后提出一个**不写代码或者少写代码，直接利用现成大平台（闲鱼、淘宝、小红书）公域流量的“套利/卖货”自动化方案**。

**Persona 2: B2B 软件出海客 (专注解决真实业务痛点)**
痛批 B2C 搞搞笑测试是死路。提出一个面向“有钱人”（如：跨境电商卖家、自媒体工作室、闲鱼商家）的**B2B自动化工具**。这些人愿意为了“省时间”付月费。

**Persona 3: 架构师 (TITAN Engine 主脑)**
总结上述两人的方案，结合目前 TITAN 已经写好的库（如 `xianyu_auto_sales_bot.py`, `xhs_auto_publisher.py` 等现成组件），选出**最快能见钱（TimeToMoney最短）、最不依赖运气的【国内暴利 1号工程 绝对务实版】**。

必须以 JSON 数组的形式输出对话，格式：
[
  { "speaker": "流量老镰刀", "dialogue": "..." },
  ...,
  { "speaker": "架构师", "FINAL_DECISION": "结论", "action_plan": ["步骤1", "步骤2"] }
]

不要输出任何 Markdown 格式，只输出合法的 JSON 字符串。
"""

    log.info("🔥 组织残酷现实商业圆桌会议，痛批之前的自嗨战略...")
    response = llm.generate(prompt, system_prompt="残酷的商业现实主义者。不要自嗨，只要能赚钱的真理。")
    
    output_file = os.path.join(os.path.dirname(__file__), "titan_roundtable_s10_reality.json")
    try:
        # 清理响应，提取JSON
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            json_str = response.strip()
            
        data = json.loads(json_str)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        log.info(f"✅ 圆桌会议结束，记录保存在: {output_file}")
        
    except Exception as e:
        log.error(f"解析 JSON 失败: {e}\nRaw Response:\n{response}")

if __name__ == "__main__":
    run_reality_check()
