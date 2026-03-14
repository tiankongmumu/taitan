"""
ShipMicro Daily Forge v2 — 精品工坊模式
策略：生成10个候选点子 → AI评分筛选 → 只有Top N进入生产线
"""
import os
import sys
import json
import time
import random
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from forge_master import ForgeMaster
from logger import get_logger

log = get_logger("daily")


def generate_candidate_ideas(llm: LLMClient, num_candidates=10) -> list:
    """让 AI 生成大量候选点子"""
    log.info(f"🧠 生成 {num_candidates} 个候选工具点子...")
    prompt = f"""You are a product manager at ShipMicro.com.
Today is {datetime.now().strftime('%Y-%m-%d')}.

Generate exactly {num_candidates} micro-tool ideas for developers. Each must be:
1. Tool: A single-purpose, browser-based utility. Game: A simple, highly addictive HTML5/React arcade game (e.g., Flappy Clone, 2048, Idle Clicker).
2. Solve a REAL daily pain point or provide quick fun. Everything runs entirely client-side (no backend).
3. Different from each other (cover different categories).

For EACH idea, provide:
- name: A short, catchy tool name
- description: One-line description of what it does
- category: One of [Code, Data, API, Design, Text, Security, DevOps, Productivity, Game]

Output ONLY a JSON array:
[{{"name": "...", "description": "...", "category": "..."}}]"""

    try:
        response = llm.generate(prompt)
        import re
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            ideas = json.loads(match.group())
            return ideas[:num_candidates]
    except Exception as e:
        log.warning(f"⚠️ 点子生成失败: {e}")

    return [
        {"name": "Regex Playground", "description": "Visual regex tester with real-time match highlighting", "category": "Code"},
        {"name": "Cron Translator", "description": "Convert cron expressions to human-readable text", "category": "DevOps"},
        {"name": "JWT Inspector", "description": "Decode and inspect JWT tokens with expiry warnings", "category": "Security"},
    ]


def score_ideas(llm: LLMClient, ideas: list) -> list:
    """让另一个 AI 对候选点子打分（0-10），筛选最优"""
    log.info(f"⚖️ AI 评审员对 {len(ideas)} 个候选点子打分...")

    ideas_text = "\n".join([f"{i+1}. [{d['category']}] {d['name']}: {d['description']}" for i, d in enumerate(ideas)])

    prompt = f"""You are a harsh, experienced product critic reviewing tool ideas for ShipMicro.com,
a site that ships FREE developer micro-tools.

Score each idea on THREE dimensions (each 0-10):
1. **Utility/Fun**: If it's a tool, how useful is it? If it's a Game category, how viral, fun, or addictive is it?
2. **Uniqueness**: How different is this from standard tutorials or freely available alternatives?
3. **SEO/Viral Potential**: Would people actively search for this tool, or share this game on social media?

Here are the {len(ideas)} candidate ideas:
{ideas_text}

Output ONLY a JSON array with scores for each idea (same order):
[{{"index": 0, "utility": 8, "uniqueness": 6, "seo": 7, "total": 21, "verdict": "SHIP"}}, ...]

Rules:
- "total" = utility + uniqueness + seo (max 30)
- "verdict": "SHIP" if total >= 20, "MAYBE" if 15-19, "KILL" if < 15
- Be HARSH. Most ideas should score 15-22. Only truly excellent ones get 25+.
- Generic, boring ideas (like "unit converter" or "calculator") must score below 15.
"""

    try:
        response = llm.generate(prompt)
        import re
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            scores = json.loads(match.group())
            # 合并分数到点子
            for s in scores:
                idx = s.get("index", 0)
                if idx < len(ideas):
                    ideas[idx]["score"] = s.get("total", 0)
                    ideas[idx]["verdict"] = s.get("verdict", "KILL")
                    ideas[idx]["utility"] = s.get("utility", 0)
                    ideas[idx]["uniqueness"] = s.get("uniqueness", 0)
                    ideas[idx]["seo"] = s.get("seo", 0)
            return ideas
    except Exception as e:
        log.warning(f"⚠️ 评分失败，给所有点子默认分数: {e}")
        for idea in ideas:
            idea["score"] = random.randint(15, 25)
            idea["verdict"] = "MAYBE"
    return ideas


def select_top_ideas(ideas: list, top_n=3) -> list:
    """按分数排序，只取 Top N 个「SHIP」级别的点子"""
    scored = [i for i in ideas if "score" in i]
    scored.sort(key=lambda x: x["score"], reverse=True)

    log.info(f"\n📊 候选点子评分排行榜:")
    for i, idea in enumerate(scored):
        emoji = "🟢" if idea.get("verdict") == "SHIP" else ("🟡" if idea.get("verdict") == "MAYBE" else "🔴")
        log.info(f"  {emoji} #{i+1} [{idea['score']}/30] {idea['name']} — {idea.get('verdict', '?')}")
        log.info(f"       实用:{idea.get('utility','?')} 差异:{idea.get('uniqueness','?')} SEO:{idea.get('seo','?')}")

    # 只取 SHIP 或 MAYBE 级别的前 N 个
    selected = [i for i in scored if i.get("verdict") in ("SHIP", "MAYBE")][:top_n]

    if not selected:
        log.warning("⚠️ 没有点子通过筛选！取分数最高的 1 个保底")
        selected = scored[:1]

    log.info(f"\n✅ 精选 {len(selected)} 个点子进入生产线：")
    for s in selected:
        log.info(f"  🏆 {s['name']} (得分 {s['score']}/30)")

    return selected


def run_daily_forge(num_tools=3, dry_run=False):
    """精品工坊模式：生成10个候选 → AI评分 → 取Top N → 铸造部署"""
    log.info("=" * 60)
    log.info("🏭 SHIPMICRO DAILY FORGE v2 (精品工坊模式)")
    log.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log.info(f"🎯 目标: 从 10 个候选中精选 {num_tools} 个精品工具")
    if dry_run:
        log.info("⚠️ DRY RUN 模式 — 只评分筛选，不实际部署")
    log.info("=" * 60)

    start = time.time()
    llm = LLMClient()

    # 1. 生成 10 个候选点子
    candidates = generate_candidate_ideas(llm, num_candidates=10)
    log.info(f"💡 已生成 {len(candidates)} 个候选点子")

    # 2. AI 评分筛选
    scored = score_ideas(llm, candidates)

    # 3. 精选 Top N
    selected = select_top_ideas(scored, top_n=num_tools)

    if dry_run:
        elapsed = time.time() - start
        log.info(f"\n🏁 DRY RUN 完成 ({elapsed:.1f}s)。精选了 {len(selected)} 个点子。")
        return selected

    # 4. 铸造精选工具
    results = []
    for i, idea in enumerate(selected, 1):
        log.info(f"\n{'='*40}")
        log.info(f"🔨 [{i}/{len(selected)}] 铸造精品: {idea['name']} (得分 {idea.get('score', '?')}/30)")
        log.info(f"{'='*40}")
        try:
            forge = ForgeMaster()
            idea_text = f"{idea['name']}: {idea['description']}"
            success = forge.run_pipeline(idea_text)
            results.append({"idea": idea, "success": success})
            if success:
                log.info(f"  ✅ 精品铸造成功!")
            else:
                log.warning(f"  ❌ 铸造失败")
        except Exception as e:
            log.error(f"  💥 异常: {e}")
            results.append({"idea": idea, "success": False, "error": str(e)})

        if i < len(selected):
            log.info("⏳ 冷却 5 秒...")
            time.sleep(5)

    # 5. 总结
    elapsed = time.time() - start
    success_count = sum(1 for r in results if r["success"])
    log.info(f"\n{'='*60}")
    log.info(f"🏁 精品工坊完成!")
    log.info(f"  📊 候选: {len(candidates)} → 精选: {len(selected)} → 成功: {success_count}")
    log.info(f"  ⏱️ 耗时: {elapsed:.1f}s")
    log.info(f"{'='*60}")

    # 保存日志
    os.makedirs(os.path.join(os.path.dirname(__file__), "logs"), exist_ok=True)
    log_path = os.path.join(os.path.dirname(__file__), "logs", f"daily_{datetime.now().strftime('%Y%m%d')}.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().isoformat(),
            "mode": "quality_workshop",
            "candidates": candidates,
            "selected": selected,
            "results": [{"idea_name": r["idea"]["name"], "score": r["idea"].get("score"), "success": r["success"]} for r in results],
            "duration": elapsed
        }, f, ensure_ascii=False, indent=2)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ShipMicro Daily Forge v2 (精品工坊)")
    parser.add_argument("--count", type=int, default=3, help="每日精选工具数量")
    parser.add_argument("--dry-run", action="store_true", help="仅评分筛选，不部署")
    args = parser.parse_args()
    run_daily_forge(num_tools=args.count, dry_run=args.dry_run)
