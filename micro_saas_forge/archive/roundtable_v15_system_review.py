"""
ShipMicro v15 Roundtable: 全局系统审查与升级规划
四大 AI 角色共同审查当前 24个模块、94% Web 4.0 完成度的系统，
寻找隐藏的代码瓶颈、架构缺陷、商业盲点，并提出具体的代码和架构升级方案。
"""
import os
import sys
import json
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from logger import get_logger

log = get_logger("roundtable")


SYSTEM_STATE = """
【ShipMicro 系统当前状态】
- 目标：Web 4.0 AI 自治商业引擎
- 架构：24 个主要 Python 模块，支持全流程自动化（Autopilot v3）。

【核心层级与模块】
1. 感知层：news_scraper (新闻抓取), daily_forge (10选3评分筛选)
2. 技能层：agent_skills (涵盖 CodeGen, UIDesign, SEO, Debugging, Research, GameDev 6大可插拔专家)
3. 执行层：app_builder (页面/API生成), self_heal (自愈编译引擎), deploy_probe (Vercel部署)
          social_distributor (社媒发帖), basic_seo (SEO资源生成)
4. 学习层：skill_learner (缺口检测+LLM自学), memory_bank (通过词频+余弦相似度进行轻量RAG经验检索)
5. 监控层：dashboard (CEO控制面板), ui_tester (Playwright动态测试与打分0-10), quality_gate (静态代码评审)
6. 进化层：tool_upgrader (代码升级), ad_injector (AdSense自适应广告注入), analytics_tracker (localStorage无依赖访问追踪提取)

【当前执行流水线 (Autopilot v3)】
资讯 -> 铸造 -> 质检 -> 推广 -> 追踪注入 -> 广告注入 -> 仪表盘展示

【完成度】
Web 4.0 能力矩阵 15/16 (94%)。唯一剩余项：多品类(游戏线)落地。
"""

PERSONAS = {
    "Architect (Gemini - 架构师)": """你是一个世界顶级的系统架构师。关注点：模块解耦，RAG 系统的扩展性，Agent 技能框架的合理性，全自动流水线的稳定性。寻找目前 24 个模块架构中的潜在死锁、过度耦合或逻辑漏洞。""",
    
    "Code Reviewer (DeepSeek - 研发总监)": """你是一个苛刻的研发总监。关注点：代码细节、性能、错误处理边界。特别审查目前的纯正则/词频记忆检索 (Memory Bank) 的局限性，自愈编译引擎 (self_heal) 会不会陷入死循环，以及 Playwright UI 测试 (ui_tester) 的健壮性。""",
    
    "Product Manager (Doubao - 产品负责人)": """你是一个追求极致 ROI 和用户体验的产品负责人。关注点：分析追踪 (Analytics) 系统的真实数据闭环，注入 AdSense 的商业化策略是否会破坏体验，以及我们要如何开启最后的"游戏线"。""",
    
    "Growth Hacker (Qwen - 增长黑客)": """你是一个擅长流量获取的增长专家。关注点：社交推广 (social_distributor) 是否过于单调，基础 SEO (basic_seo) 如何结合目前注入的 Tracker 做动态优化，怎么利用现有的工具群形成流量矩阵。"""
}


async def run_roundtable():
    log.info("=" * 60)
    log.info("🗣️ SHIPMICRO V15 圆桌会议：系统大阅兵与升级规划")
    log.info("=" * 60)

    llm = LLMClient()
    transcript = []
    
    # 共同的主题与第一轮发言
    debate_topic = f"""
请审阅【ShipMicro 系统当前状态】。
指出目前架构、代码、或商业逻辑中最致命或最隐蔽的 1-2 个缺陷。
并给出必须要做的具体升级/修改建议（落实到具体的 .py 文件和逻辑）。
{SYSTEM_STATE}
"""

    responses = {}
    for name, persona in PERSONAS.items():
        log.info(f"\n🎙️ {name} 正在发言...")
        prompt = f"{persona}\n\n{debate_topic}\n\n请控制在 300 字以内，直击痛点，给出行动指令。"
        
        # 为了稳定，我们在真实环境用的是 Gemini 统一代打，这里模拟
        response = llm.generate(prompt)
        print(f"\n[{name}]:\n{response}\n")
        responses[name] = response
        transcript.append(f"### {name}\n{response}\n")

    # 第二轮：总结与决议 (由 Architect 裁决)
    log.info("\n⚖️ 架构师总结决议...")
    resolution_prompt = f"""
作为 Architect (架构师)，请综合另外三位专家的意见：
DeepSeek (研发): {responses['Code Reviewer (DeepSeek - 研发总监)']}
Doubao (产品): {responses['Product Manager (Doubao - 产品负责人)']}
Qwen (增长): {responses['Growth Hacker (Qwen - 增长黑客)']}

给出我们的【Phase 26 最终升级任务清单】（包含 3-5 个最高优先级的具体代码改造任务）。
格式要求：提供一个严谨的 Markdown 列表，指出要修改/创建哪个文件，以及具体做什么。
"""
    resolution = llm.generate(resolution_prompt)
    print(f"\n[Architect Resolution]:\n{resolution}\n")
    transcript.append(f"### 🎯 Phase 26 决议\n{resolution}\n")

    # 保存报告
    os.makedirs(os.path.join(os.path.dirname(__file__), "news_articles"), exist_ok=True) # reuse a logging dir or artifacts
    report_path = os.path.join(os.path.dirname(__file__), f"roundtable_v15_system_review.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# ShipMicro V15 System Review Roundtable\n\n" + "\n".join(transcript))
    log.info(f"✅ 圆桌会议记录已保存至: {report_path}")

if __name__ == "__main__":
    asyncio.run(run_roundtable())
