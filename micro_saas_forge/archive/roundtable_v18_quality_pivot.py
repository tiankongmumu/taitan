"""
ShipMicro Roundtable v18 — Quality-First Pivot Strategy
主题：停止批量生产，双线并进 (Path A: 游戏广告变现 + Path B: 精品工具打磨)
参与者：商业化总监 (CBO)、游戏体验总监 (GXO)、工具质量首席 (CQO)、TITAN 引擎架构师 (Architect)
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from logger import get_logger

log = get_logger("roundtable_v18")

class RoundtableV18QualityPivot:
    def __init__(self):
        self.llm = LLMClient()

    def run_roundtable(self):
        log.info("=" * 60)
        log.info("🎤 ROUNDTABLE V18: QUALITY-FIRST PIVOT")
        log.info("=" * 60)

        transcript = []

        context = """
### 现状 (TITAN v3.5 冷酷评估结论)
- ShipMicro 目前拥有 48 个免费工具 + 47 个小游戏，但收入 = 0
- 0 个 Premium 工具 → 用户无理由付费
- 0 流量 → 无 SEO、无社交运营
- 赛道竞品全是免费开源 (IT-Tools 70+, CyberChef 300+)
- TITAN v3.5 拥有 127 个从 GitHub 学习的架构模式
- 所有工具均为 AI 生成 (<350行)，质量约 6/10

### Boss 决策
1. 停止批量生产
2. 同时执行 Path A (游戏广告变现) + Path B (精品工具打磨)
3. TITAN 引擎以 ShipMicro 作为验证场，持续优化
4. 重点提高每个游戏和工具的质量
"""

        # === Phase 1: 商业化总监 — 广告变现方案 ===
        log.info("\n🗣️ Phase 1: CBO — 广告变现整体方案")
        cbo_prompt = f"""{context}
You are the Chief Business Officer (CBO). Respond in Chinese.
ShipMicro has 47 browser games. The Boss wants to monetize via ads.

Questions to answer:
1. 最适合小游戏站的广告类型是什么？(Banner / Interstitial / Rewarded Video?)
2. Google AdSense vs 其他广告平台, 哪个更适合？门槛是什么？
3. 预估: 如果达到 1000 DAU, 月收入大概多少?
4. 我们最需要优先做什么才能开始赚第一分钱?

请给出简洁、可执行的方案 (150字以内)。
"""
        cbo_resp = self.llm.generate(cbo_prompt, system_prompt="你是一位有丰富互联网变现经验的商业化总监。请给出专业但简洁的建议。")
        log.info(f"\n[CBO 商业化总监]:\n{cbo_resp}")
        transcript.append(f"## 🎯 商业化总监 (CBO)\n{cbo_resp}")

        # === Phase 2: 游戏体验总监 — 如何提升游戏质量 ===
        log.info("\n🗣️ Phase 2: GXO — 游戏质量提升方案")
        gxo_prompt = f"""{context}
Previous input from CBO: {cbo_resp}

You are the Game Experience Officer (GXO). Respond in Chinese.
我们的 47 个游戏目前是 AI 一次性生成的，每个 <350 行，质量大约 6/10。

Questions to answer:
1. 从 47 个游戏中，选出最有留存价值的 TOP 5 (应该优先打磨哪些类型？)
2. 一个"可以留住用户"的小游戏，最低需要什么功能？(排行榜？关卡？音效？)
3. 如何用 TITAN v3.5 的学习模式来提升游戏质量？(引擎学了 Godot/Bevy/Cocos 的模式)
4. 给出一个"优秀休闲小游戏"的质量标杆 (从 6/10 提升到 8/10 需要什么？)

请给出简洁方案 (200字以内)。
"""
        gxo_resp = self.llm.generate(gxo_prompt, system_prompt="你是一位资深游戏体验设计总监，精通休闲游戏留存机制。")
        log.info(f"\n[GXO 游戏体验总监]:\n{gxo_resp}")
        transcript.append(f"## 🎮 游戏体验总监 (GXO)\n{gxo_resp}")

        # === Phase 3: 工具质量首席 — 如何打磨精品工具 ===
        log.info("\n🗣️ Phase 3: CQO — 工具质量提升方案")
        cqo_prompt = f"""{context}
Previous inputs:
CBO: {cbo_resp}
GXO: {gxo_resp}

You are the Chief Quality Officer (CQO) for developer tools. Respond in Chinese.
我们有 48 个开发者工具，全部免费，质量参差不齐。

Questions to answer:
1. 从 48 个工具中，哪 3-5 个有最高 SEO 搜索量、值得重点打磨？
2. 一个"足以让开发者收藏"的工具，最低需要什么？(对比 DevUtils, SmallDev)
3. 哪些工具应该设为 Premium ($9/月)？标准是什么？
4. 如何利用 TITAN v3.5 的 127 个学习模式来系统性提高工具质量？

请给出简洁方案 (200字以内)。
"""
        cqo_resp = self.llm.generate(cqo_prompt, system_prompt="你是一位对代码质量有极致追求的工具质量首席官。")
        log.info(f"\n[CQO 工具质量首席]:\n{cqo_resp}")
        transcript.append(f"## 🛠️ 工具质量首席 (CQO)\n{cqo_resp}")

        # === Phase 4: TITAN 架构师 — 技术实施路线图 ===
        log.info("\n🗣️ Phase 4: Architect — 技术实施路线图")
        arch_prompt = f"""{context}
All previous inputs:
CBO: {cbo_resp}
GXO: {gxo_resp}
CQO: {cqo_resp}

You are the TITAN Engine Lead Architect. Respond in Chinese.
你需要综合以上所有讨论，制定一个可执行的技术实施路线图。

你需要输出:
1. 【本周任务 (Week 1)】: 最重要的 3 件事，能够最快产生收入或提升质量
2. 【第二周 (Week 2)】: 紧随其后的 3 件事
3. 【质量提升引擎改造】: TITAN v3.5 需要新增哪些模块来支撑"精品模式"（而非批量模式）
4. 【成功指标】: 30 天后，我们如何衡量这次转型是否成功？

请格式化为 markdown 列表 (200字以内)。
"""
        arch_resp = self.llm.generate(arch_prompt, system_prompt="你是 TITAN v3.5 引擎首席架构师，精通系统架构和工程管理。")
        log.info(f"\n[TITAN Architect 架构师]:\n{arch_resp}")
        transcript.append(f"## ⚙️ TITAN 架构师\n{arch_resp}")

        # === Final: CEO 裁决 ===
        log.info("\n🗣️ Final Phase: CEO AI — 最终裁决")
        ceo_prompt = f"""
All roundtable inputs:
CBO: {cbo_resp}
GXO: {gxo_resp}
CQO: {cqo_resp}
Architect: {arch_resp}

You are the CEO AI. Respond in Chinese.
综合以上所有讨论，输出最终的执行决议：

格式要求:
### 🔴 立即执行 (今天)
- [ ] 任务 1
- [ ] 任务 2
- [ ] 任务 3

### 🟡 本周完成
- [ ] 任务 4
- [ ] 任务 5
- [ ] 任务 6

### 🟢 30 天目标
- 目标 1
- 目标 2

必须简洁，每个任务一行，总共不超过 150 字。
"""
        ceo_resp = self.llm.generate(ceo_prompt, system_prompt="你是一位果断的 CEO。只给出最终决策，不做多余解释。")
        log.info(f"\n[CEO AI 最终裁决]:\n{ceo_resp}")
        transcript.append(f"## 👑 CEO AI 最终裁决\n{ceo_resp}")

        # Save report
        report_path = os.path.join(os.path.dirname(__file__), "roundtable_v18_quality_pivot.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# ShipMicro Roundtable v18: Quality-First Pivot\n\n")
            f.write(f"**日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("**议题**: 停止批量生产，Path A (游戏广告) + Path B (精品工具) 双线并进\n\n")
            f.write("---\n\n")
            f.write("\n\n---\n\n".join(transcript))
        log.info(f"\n📝 圆桌会议记录: {report_path}")
        return report_path

if __name__ == "__main__":
    rt = RoundtableV18QualityPivot()
    rt.run_roundtable()
"""
Created roundtable v18 script for quality-first pivot discussion.
"""
