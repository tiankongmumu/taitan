"""
ShipMicro Skill Learner — 自动学习引擎 🧬
当系统在生产中遇到技能缺口时（编译失败、质量低分、新技术需求），
自动触发学习流程：识别缺口 → 研究方案 → 存储知识 → 下次应用。

核心理念：让 AI 团队从"只会做以前做过的事"进化为"遇到新问题能自学"。
"""
import os
import sys
import json
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger
from core_generators.llm_client import LLMClient

log = get_logger("skill_learner")

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")
SKILLS_FILE = os.path.join(KNOWLEDGE_DIR, "learned_skills.json")
GAP_LOG_FILE = os.path.join(KNOWLEDGE_DIR, "gap_log.json")


def _ensure_dir():
    os.makedirs(KNOWLEDGE_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════
# 1. 技能缺口检测 (Skill Gap Detection)
# ═══════════════════════════════════════════════════

# 常见的技能缺口模式 — 从错误信息中识别"我不会什么"
GAP_PATTERNS = {
    "state_management": [
        r"cannot read properties of undefined",
        r"too many re-renders",
        r"rendered more hooks than during the previous render",
    ],
    "typescript_generics": [
        r"type .+ is not assignable to type",
        r"argument of type .+ is not assignable to parameter",
        r"generic type .+ requires \d+ type argument",
    ],
    "nextjs_hydration": [
        r"hydration failed",
        r"text content does not match server-rendered html",
        r"there was an error while hydrating",
    ],
    "nextjs_routing": [
        r"module not found.*next/navigation",
        r"useRouter.*can only be used in a Client Component",
        r"generateStaticParams",
    ],
    "css_layout": [
        r"cannot read property.*style",
        r"tailwindcss.*unknown utility",
    ],
    "async_patterns": [
        r"objects are not valid as a react child.*promise",
        r"a]sync.*generator",
        r"unhandled promise rejection",
    ],
    "canvas_game": [
        r"canvas.*getContext",
        r"requestAnimationFrame",
        r"collision detection",
    ],
    "api_integration": [
        r"fetch failed",
        r"cors.*blocked",
        r"network error",
    ],
}


def detect_skill_gap(error_output: str) -> list[str]:
    """从错误信息中识别技能缺口类别"""
    gaps = []
    error_lower = error_output.lower()
    for skill_name, patterns in GAP_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, error_lower):
                if skill_name not in gaps:
                    gaps.append(skill_name)
                break
    return gaps


# ═══════════════════════════════════════════════════
# 2. 自动学习 (Auto-Study via LLM)
# ═══════════════════════════════════════════════════

def _load_skills() -> list[dict]:
    if os.path.exists(SKILLS_FILE):
        with open(SKILLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_skills(data: list[dict]):
    _ensure_dir()
    with open(SKILLS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_gap_log() -> list[dict]:
    if os.path.exists(GAP_LOG_FILE):
        with open(GAP_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_gap_log(data: list[dict]):
    _ensure_dir()
    with open(GAP_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def has_skill(skill_name: str) -> bool:
    """检查是否已学过某项技能"""
    skills = _load_skills()
    return any(s["skill_name"] == skill_name for s in skills)


def study_skill(skill_name: str, context: str = "") -> dict:
    """
    自动学习一项新技能：
    - 调用 LLM 生成关于该技能的"速成教程"
    - 包含：常见错误、正确代码模式、最佳实践
    - 存入 knowledge_base
    """
    if has_skill(skill_name):
        log.info(f"🧬 技能 '{skill_name}' 已学过，跳过")
        skills = _load_skills()
        return next(s for s in skills if s["skill_name"] == skill_name)

    log.info(f"🧬 开始自学技能: {skill_name}...")

    llm = LLMClient()
    study_prompt = f"""
You are an expert developer creating a REFERENCE CARD for a junior developer.
Topic: "{skill_name}" in Next.js / React / TypeScript projects.

Context of why we need this skill:
{context[:500] if context else "General knowledge needed for web app development."}

Create a concise reference card with:

1. **Common Mistakes** (3 most frequent errors and why they happen)
2. **Correct Patterns** (3 code snippets showing the RIGHT way to do it)
3. **Quick Fix Checklist** (5 actionable steps to fix issues related to this)

Rules:
- Be EXTREMELY concise. Max 300 words.
- Code examples must be complete and copy-pasteable.
- Focus on Next.js 14+ App Router patterns.
- Wrap code in ```tsx blocks.
"""
    response = llm.generate(study_prompt)

    if not response:
        log.error(f"  ❌ 学习失败: LLM 未返回内容")
        return {}

    skill_entry = {
        "skill_name": skill_name,
        "knowledge": response,
        "context": context[:200],
        "learned_at": datetime.now().isoformat(),
        "times_applied": 0,
    }

    skills = _load_skills()
    skills.append(skill_entry)
    # 保留最多 50 项技能
    if len(skills) > 50:
        skills = skills[-50:]
    _save_skills(skills)

    log.info(f"  ✅ 技能 '{skill_name}' 学习完成 ({len(response)} 字)")
    return skill_entry


def auto_learn_from_error(error_output: str, app_slug: str = "") -> list[dict]:
    """
    完整的自动学习流程：
    1. 检测技能缺口
    2. 对每个缺口，检查是否已学过
    3. 未学过的，调用 LLM 自学
    4. 记录学习日志
    """
    gaps = detect_skill_gap(error_output)
    if not gaps:
        return []

    log.info(f"🧬 检测到 {len(gaps)} 个技能缺口: {gaps}")

    # 记录到缺口日志
    gap_log = _load_gap_log()
    gap_log.append({
        "gaps": gaps,
        "error_snippet": error_output[:300],
        "app_slug": app_slug,
        "timestamp": datetime.now().isoformat(),
    })
    if len(gap_log) > 100:
        gap_log = gap_log[-100:]
    _save_gap_log(gap_log)

    learned = []
    for gap in gaps:
        skill = study_skill(gap, context=error_output[:500])
        if skill:
            learned.append(skill)

    return learned


# ═══════════════════════════════════════════════════
# 3. 知识注入 (Knowledge Injection)
# ═══════════════════════════════════════════════════

def get_relevant_skills(task_description: str, error_output: str = "") -> str:
    """
    根据任务描述和/或错误信息，检索相关的已学技能，
    返回可直接注入到 LLM prompt 中的知识文本。
    """
    skills = _load_skills()
    if not skills:
        return ""

    # 方法1：如果有错误信息，按缺口类别匹配
    if error_output:
        gaps = detect_skill_gap(error_output)
        matched = [s for s in skills if s["skill_name"] in gaps]
        if matched:
            # 更新应用次数
            for s in skills:
                if s["skill_name"] in gaps:
                    s["times_applied"] = s.get("times_applied", 0) + 1
            _save_skills(skills)

            knowledge_text = "\n\n## 🧬 Learned Skills (from Auto-Study):\n"
            for s in matched:
                knowledge_text += f"\n### Skill: {s['skill_name']}\n{s['knowledge'][:600]}\n"
            log.info(f"🧬 注入 {len(matched)} 项已学技能到 prompt")
            return knowledge_text

    # 方法2：按关键词模糊匹配
    from memory_bank import extract_keywords, compute_similarity
    task_kw = extract_keywords(task_description + " " + error_output)
    if not task_kw:
        return ""

    scored = []
    for s in skills:
        skill_kw = extract_keywords(s.get("knowledge", "") + " " + s.get("skill_name", ""))
        sim = compute_similarity(task_kw, skill_kw)
        if sim > 0.1:
            scored.append((sim, s))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:2]

    if not top:
        return ""

    knowledge_text = "\n\n## 🧬 Relevant Learned Skills:\n"
    for _, s in top:
        knowledge_text += f"\n### {s['skill_name']}\n{s['knowledge'][:400]}\n"
        # 更新应用次数
        for sk in skills:
            if sk["skill_name"] == s["skill_name"]:
                sk["times_applied"] = sk.get("times_applied", 0) + 1
        _save_skills(skills)

    log.info(f"🧬 注入 {len(top)} 项相关技能到 prompt")
    return knowledge_text


# ═══════════════════════════════════════════════════
# 4. 📊 Analytics Feedback Loop (Roundtable Upgrade 3)
# ═══════════════════════════════════════════════════

def analytics_feedback() -> dict:
    """
    从 ui_tester 和 analytics_tracker 的数据中提取反馈信号，
    转化为技能调优权重，驱动 daily_forge 的选题评分。
    """
    base = os.path.dirname(__file__)
    signals = {"tool_performance": {}, "skill_gaps_trend": {}, "forge_weight_adjustments": {}}

    # 1. 读取 UI 测试报告 — 哪些类型的工具 UI 表现好/差
    logs_dir = os.path.join(base, "logs")
    if os.path.isdir(logs_dir):
        report_files = sorted([f for f in os.listdir(logs_dir) if f.startswith("ui_test_report")])
        if report_files:
            latest = os.path.join(logs_dir, report_files[-1])
            with open(latest, "r", encoding="utf-8") as f:
                ui_results = json.load(f)
            for r in ui_results:
                slug = r.get("slug", "")
                score = r.get("ui_score", 0)
                signals["tool_performance"][slug] = {
                    "ui_score": score,
                    "status": r.get("status", "UNKNOWN"),
                    "interactive": r.get("checks", {}).get("has_interactive", False),
                }

    # 2. 分析技能缺口趋势 — 哪些缺口反复出现
    gap_log = _load_gap_log()
    if gap_log:
        from collections import Counter
        recent_gaps = []
        for entry in gap_log[-20:]:  # 最近 20 条
            recent_gaps.extend(entry.get("gaps", []))
        gap_counts = Counter(recent_gaps)
        signals["skill_gaps_trend"] = dict(gap_counts.most_common(5))

    # 3. 生成 forge 权重调整建议
    # 如果某个技能缺口频率 > 3, 说明我们不擅长这类工具，应降低相关类型的选题权重
    for gap_name, count in signals.get("skill_gaps_trend", {}).items():
        if count >= 3:
            signals["forge_weight_adjustments"][gap_name] = {
                "action": "reduce_weight",
                "reason": f"技能缺口 '{gap_name}' 出现 {count} 次, 需先学会再做",
                "weight_multiplier": 0.5,
            }

    # 如果某些工具 UI score > 8, 说明我们擅长这类工具，应增加权重
    high_performers = [s for s, d in signals["tool_performance"].items() if d.get("ui_score", 0) >= 8]
    if high_performers:
        signals["forge_weight_adjustments"]["high_quality_tools"] = {
            "action": "increase_weight",
            "tools": high_performers,
            "reason": f"{len(high_performers)} 个工具 UI 评分 >= 8, 擅长领域",
            "weight_multiplier": 1.3,
        }

    # 保存信号文件供 daily_forge 读取
    signals_path = os.path.join(base, "analytics_data", "forge_signals.json")
    os.makedirs(os.path.dirname(signals_path), exist_ok=True)
    with open(signals_path, "w", encoding="utf-8") as f:
        json.dump(signals, f, ensure_ascii=False, indent=2)

    log.info(f"📊 Analytics Feedback: 生成 {len(signals['forge_weight_adjustments'])} 条选题调weight信号")
    return signals


# ═══════════════════════════════════════════════════
# 5. 技能统计
# ═══════════════════════════════════════════════════

def get_skill_stats() -> dict:
    """返回技能库统计"""
    skills = _load_skills()
    gap_log = _load_gap_log()
    return {
        "total_skills": len(skills),
        "total_gap_events": len(gap_log),
        "skills": [
            {"name": s["skill_name"], "applied": s.get("times_applied", 0), "learned": s["learned_at"]}
            for s in skills
        ],
        "top_gaps": _get_top_gaps(gap_log),
    }


def _get_top_gaps(gap_log: list[dict]) -> dict:
    """统计最常见的技能缺口"""
    from collections import Counter
    all_gaps = []
    for entry in gap_log:
        all_gaps.extend(entry.get("gaps", []))
    return dict(Counter(all_gaps).most_common(5))


# ═══════════════════════════════════════════════════
# 自测
# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    print("🧬 Skill Learner 自测")

    # 1. 测试缺口检测
    test_error = "Error: Hydration failed because the initial UI does not match what was rendered on the server."
    gaps = detect_skill_gap(test_error)
    print(f"  缺口检测: {gaps}")
    assert "nextjs_hydration" in gaps, "应该检测到 nextjs_hydration 缺口"

    # 2. 测试多重缺口
    test_error2 = "Type 'string' is not assignable to type 'number'. Also: Hydration failed."
    gaps2 = detect_skill_gap(test_error2)
    print(f"  多重缺口: {gaps2}")
    assert len(gaps2) >= 2, "应该检测到至少2个缺口"

    # 3. 测试无缺口
    gaps3 = detect_skill_gap("Everything works fine!")
    print(f"  无缺口: {gaps3}")
    assert len(gaps3) == 0

    print(f"  统计: {json.dumps(get_skill_stats(), indent=2, default=str)}")
    print("✅ 自测通过")
