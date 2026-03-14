"""
ShipMicro Quality Gate — AI 评审员 (v3.5 — TITAN Self-Optimized)
功能: 对已生成的工具进行自动化质量评审，不合格的标记为下架
v3.5: 新增第6维度 "Architecture Quality" 评分
学习来源: infiniflow/ragflow (多租户配置) + botpress/botpress (任务层次)
"""
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from logger import get_logger

log = get_logger("quality")

# 质量分数阈值
THRESHOLD_SHIP = 7    # >= 7 分上线
THRESHOLD_IMPROVE = 5 # 5-6 分需改进
# < 5 分直接下架


def review_tool(llm: LLMClient, tool_info: dict) -> dict:
    """
    让 AI 评审一个已生成的工具，返回质量评分和建议。
    tool_info: {"name": "...", "slug": "...", "idea": "...", "app_path": "..."}
    """
    name = tool_info.get("name", tool_info.get("slug", "Unknown"))
    idea = tool_info.get("idea", "A developer micro-tool")

    # 尝试读取生成的 page.tsx 来评审代码质量
    code_snippet = ""
    app_path = tool_info.get("app_path", "")
    page_path = os.path.join(app_path, "src", "app", "page.tsx") if app_path else ""
    if page_path and os.path.exists(page_path):
        with open(page_path, "r", encoding="utf-8") as f:
            code_snippet = f.read()[:2000]  # 只取前 2000 字符

    prompt = f"""You are a senior product reviewer at ShipMicro.com.
You are reviewing a micro-tool before it goes live on the site.

Tool Name: {name}
Tool Description: {idea}
{"Code Preview (first 2000 chars):" + chr(10) + code_snippet if code_snippet else "No code available for review."}

Rate this tool on FIVE dimensions (each 1-10):

1. **Usefulness** (1-10): Does this solve a real, recurring developer pain point?
   - 1-3: Toy/demo, no practical value
   - 4-6: Somewhat useful but niche
   - 7-10: Developers would bookmark this

2. **UI Quality** (1-10): Based on the code, does the interface look professional?
   - 1-3: Ugly, broken, or confusing layout
   - 4-6: Functional but generic
   - 7-10: Clean, modern, delightful to use

3. **Completeness** (1-10): Does the tool fully deliver on its promise?
   - 1-3: Missing core functionality
   - 4-6: Works but has gaps
   - 7-10: Feature-complete for its scope

4. **Differentiation** (1-10): Is this different from what's already freely available?
   - 1-3: Dozens of identical free tools exist
   - 4-6: Exists but ours has a slight edge
   - 7-10: Unique angle or significantly better

5. **SEO Value** (1-10): Would developers search for this tool?
   - 1-3: No search demand
   - 4-6: Some long-tail searches
   - 7-10: High-volume developer search term

6. **Architecture Quality** (1-10): Does the code follow advanced engineering patterns?
   - 1-3: Monolithic, no separation of concerns, hardcoded values
   - 4-6: Basic structure but logic/UI are coupled
   - 7-10: Clean state management, error boundaries, component decoupling, config externalization

Output ONLY valid JSON:
{{
  "usefulness": <int>,
  "ui_quality": <int>,
  "completeness": <int>,
  "differentiation": <int>,
  "seo_value": <int>,
  "architecture": <int>,
  "overall": <float>,
  "verdict": "SHIP" | "IMPROVE" | "KILL",
  "reason": "<one-line explanation>",
  "suggestions": ["<improvement suggestion 1>", "<improvement suggestion 2>"]
}}

Rules:
- "overall" = average of all 6 scores
- "SHIP" if overall >= 7.0, "IMPROVE" if 5.0-6.9, "KILL" if < 5.0
- Be HONEST and HARSH. Don't rubber-stamp everything.
"""

    try:
        response = llm.generate(prompt)
        import re
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            review = json.loads(match.group())
            review["tool_name"] = name
            review["tool_slug"] = tool_info.get("slug", "")
            review["reviewed_at"] = datetime.now().isoformat()
            return review
    except Exception as e:
        log.warning(f"⚠️ 评审失败: {e}")

    return {
        "tool_name": name,
        "overall": 5.0,
        "verdict": "IMPROVE",
        "reason": "Review failed, defaulting to IMPROVE",
        "suggestions": ["Manual review needed"]
    }


def run_quality_gate(tools: list = None) -> dict:
    """
    对所有已生成的工具执行质量评审。
    返回: {"ship": [...], "improve": [...], "kill": [...]}
    """
    log.info("=" * 60)
    log.info("🔍 SHIPMICRO QUALITY GATE 启动")
    log.info("=" * 60)

    if not tools:
        # 从 history.json 读取
        history_path = os.path.join(os.path.dirname(__file__), "history.json")
        if os.path.exists(history_path):
            with open(history_path, "r", encoding="utf-8") as f:
                history = json.load(f)
            tools = [
                {
                    "name": h.get("app_name", h.get("slug", "")),
                    "slug": h.get("slug", ""),
                    "idea": h.get("idea", ""),
                    "app_path": os.path.join(os.path.dirname(__file__), "generated_apps", h.get("slug", ""))
                }
                for h in history
            ]
        else:
            log.warning("❌ 没有找到 history.json")
            return {"ship": [], "improve": [], "kill": []}

    llm = LLMClient()
    results = {"ship": [], "improve": [], "kill": []}

    for i, tool in enumerate(tools, 1):
        log.info(f"\n🔎 [{i}/{len(tools)}] 评审: {tool['name']}...")
        review = review_tool(llm, tool)

        verdict = review.get("verdict", "IMPROVE")
        overall = review.get("overall", 5.0)

        if verdict == "SHIP":
            emoji = "🟢"
            results["ship"].append(review)
        elif verdict == "IMPROVE":
            emoji = "🟡"
            results["improve"].append(review)
        else:
            emoji = "🔴"
            results["kill"].append(review)

        log.info(f"  {emoji} {verdict} (得分 {overall}/10) — {review.get('reason', '')}")

    # 总结
    log.info(f"\n{'='*60}")
    log.info(f"🏁 QUALITY GATE 评审完毕")
    log.info(f"  🟢 SHIP (上线): {len(results['ship'])} 个")
    log.info(f"  🟡 IMPROVE (需改进): {len(results['improve'])} 个")
    log.info(f"  🔴 KILL (下架): {len(results['kill'])} 个")
    log.info(f"{'='*60}")

    # 保存评审报告
    report_path = os.path.join(
        os.path.dirname(__file__), "logs",
        f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    )
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    log.info(f"📄 评审报告: {report_path}")

    return results


if __name__ == "__main__":
    results = run_quality_gate()
    if results["kill"]:
        print(f"\n⚠️ 以下 {len(results['kill'])} 个工具建议下架:")
        for r in results["kill"]:
            print(f"  🔴 {r['tool_name']} — {r.get('reason', '')}")
