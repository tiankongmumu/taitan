"""
ShipMicro Memory Bank v2 — Web 4.0 系统记忆体 (Quality-Weighted RAG)
Roundtable Upgrade 1: 质量加权检索 + 失败经验过滤 + 成功概率评分。

变更点 (vs v1):
- remember_fix 新增 fix_verified 字段（修复后编译是否成功）
- recall_fix 使用 quality_weighted_score = similarity * success_weight
- 负面经验（fix_verified=False）被降权而非完全排除
- 模板检索时按 quality_score 加权排序
- 新增 n-gram 匹配增强检索精度
"""
import os
import re
import json
import math
from datetime import datetime
from collections import Counter
from logger import get_logger

log = get_logger("memory")

MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory")
EXPERIENCES_FILE = os.path.join(MEMORY_DIR, "experiences.json")
TEMPLATES_FILE = os.path.join(MEMORY_DIR, "successful_templates.json")


def _ensure_dir():
    os.makedirs(MEMORY_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════
# 关键词提取 & 相似度计算 v2 (加入 n-gram)
# ═══════════════════════════════════════════════════

STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "in", "on", "at", "to", "for", "of", "with", "by", "from", "as",
    "into", "through", "during", "before", "after", "above", "below",
    "and", "but", "or", "nor", "not", "so", "yet", "both", "either",
    "neither", "each", "every", "all", "any", "few", "more", "most",
    "other", "some", "such", "no", "only", "own", "same", "than",
    "this", "that", "it", "its", "if", "then", "else", "when",
    "error", "warning", "info", "line", "file", "src", "app", "page",
    "tsx", "jsx", "next", "react", "import", "export", "default",
    "function", "return", "const", "let", "var", "type", "interface",
}


def extract_keywords(text: str) -> list[str]:
    """从文本中提取有意义的关键词（小写，去停用词，去短词）"""
    tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]{2,}', text.lower())
    unigrams = [t for t in tokens if t not in STOP_WORDS and len(t) > 2]
    # v2: 加入 bigram 以捕获 "does not exist" 等短语模式
    bigrams = []
    for i in range(len(tokens) - 1):
        bg = f"{tokens[i]}_{tokens[i+1]}"
        if tokens[i] not in STOP_WORDS or tokens[i+1] not in STOP_WORDS:
            bigrams.append(bg)
    return unigrams + bigrams[:10]  # 限制 bigram 数量


def compute_similarity(kw_a: list[str], kw_b: list[str]) -> float:
    """计算两组关键词的余弦相似度 (0.0 ~ 1.0)"""
    if not kw_a or not kw_b:
        return 0.0
    ca, cb = Counter(kw_a), Counter(kw_b)
    all_words = set(ca.keys()) | set(cb.keys())
    dot = sum(ca.get(w, 0) * cb.get(w, 0) for w in all_words)
    mag_a = math.sqrt(sum(v * v for v in ca.values()))
    mag_b = math.sqrt(sum(v * v for v in cb.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


# ═══════════════════════════════════════════════════
# 经验存储 v2（编译错误 + 修复方案 + 质量评分）
# ═══════════════════════════════════════════════════

def _load_experiences() -> list[dict]:
    if os.path.exists(EXPERIENCES_FILE):
        with open(EXPERIENCES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_experiences(data: list[dict]):
    _ensure_dir()
    with open(EXPERIENCES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def remember_fix(error_output: str, old_code: str, fixed_code: str,
                 app_slug: str = "", fix_verified: bool = True):
    """记住一次 Bug 修复经历（v2: 新增 fix_verified 验证标记）"""
    exp = _load_experiences()
    keywords = extract_keywords(error_output)

    entry = {
        "type": "build_fix",
        "error_snippet": error_output[:500],
        "keywords": keywords[:30],
        "old_code_snippet": old_code[:300],
        "fixed_code_snippet": fixed_code[:500],
        "app_slug": app_slug,
        "fix_verified": fix_verified,     # v2: 修复后编译是否真的成功了
        "apply_count": 0,                 # v2: 被引用次数
        "timestamp": datetime.now().isoformat(),
    }
    exp.append(entry)

    if len(exp) > 200:
        exp = exp[-200:]

    _save_experiences(exp)
    tag = "✅已验证" if fix_verified else "⚠️未验证"
    log.info(f"🧠 记忆存储: 新增修复经验 [{tag}] ({len(keywords)} 关键词), 总数: {len(exp)}")


def recall_fix(error_output: str, top_k: int = 3) -> list[dict]:
    """v2: 质量加权检索 — 验证过的修复优先，未验证的降权"""
    exp = _load_experiences()
    if not exp:
        return []

    query_kw = extract_keywords(error_output)
    if not query_kw:
        return []

    scored = []
    for e in exp:
        if e.get("type") != "build_fix":
            continue
        sim = compute_similarity(query_kw, e.get("keywords", []))
        if sim > 0.12:
            # v2: 质量加权
            verified = e.get("fix_verified", True)
            apply_count = e.get("apply_count", 0)
            # 验证过的经验得 1.0 权重，未验证的降到 0.3
            quality_weight = 1.0 if verified else 0.3
            # 被多次引用的经验额外加分（说明有效）
            popularity_bonus = min(apply_count * 0.05, 0.2)
            final_score = sim * quality_weight + popularity_bonus
            scored.append((final_score, e))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = [e for _, e in scored[:top_k]]

    # v2: 更新被引用次数
    if results:
        all_exp = _load_experiences()
        result_timestamps = {r.get("timestamp") for r in results}
        for e in all_exp:
            if e.get("timestamp") in result_timestamps:
                e["apply_count"] = e.get("apply_count", 0) + 1
        _save_experiences(all_exp)
        log.info(f"🧠 记忆检索v2: 找到 {len(results)} 条 (最高加权分: {scored[0][0]:.2f}, "
                 f"验证率: {sum(1 for r in results if r.get('fix_verified', True))}/{len(results)})")
    else:
        log.info("🧠 记忆检索v2: 未找到相关修复经验 (新问题)")

    return results


# ═══════════════════════════════════════════════════
# 成功模板存储 v2（质量分加权排序）
# ═══════════════════════════════════════════════════

def _load_templates() -> list[dict]:
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_templates(data: list[dict]):
    _ensure_dir()
    with open(TEMPLATES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def remember_success(app_desc: str, page_code: str, app_slug: str = "",
                     quality_score: float = 0, ui_score: float = 0):
    """v2: 同时记录 quality_score 和 ui_score"""
    templates = _load_templates()
    keywords = extract_keywords(app_desc)

    entry = {
        "type": "successful_template",
        "description": app_desc[:200],
        "keywords": keywords[:30],
        "code_snippet": page_code[:800],
        "app_slug": app_slug,
        "quality_score": quality_score,
        "ui_score": ui_score,            # v2: UI 测试得分 (0-10)
        "reference_count": 0,            # v2: 被引用次数
        "timestamp": datetime.now().isoformat(),
    }
    templates.append(entry)

    if len(templates) > 100:
        templates = templates[-100:]

    _save_templates(templates)
    log.info(f"🧠 记忆存储: 新增成功模板 '{app_slug}' (质量:{quality_score} UI:{ui_score}), 总数: {len(templates)}")


def recall_template(app_desc: str, top_k: int = 2) -> list[dict]:
    """v2: 质量分加权检索 — 高 quality_score 和 ui_score 的模板优先"""
    templates = _load_templates()
    if not templates:
        return []

    query_kw = extract_keywords(app_desc)
    if not query_kw:
        return []

    scored = []
    for t in templates:
        sim = compute_similarity(query_kw, t.get("keywords", []))
        if sim > 0.1:
            # v2: 质量加权排序
            qs = t.get("quality_score", 5) / 10.0       # 归一化到 0-1
            us = t.get("ui_score", 5) / 10.0
            quality_bonus = (qs + us) / 2 * 0.3          # 最多加 0.3
            final_score = sim + quality_bonus
            scored.append((final_score, t))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = [t for _, t in scored[:top_k]]

    if results:
        log.info(f"🧠 模板检索v2: 找到 {len(results)} 个 (最高加权分: {scored[0][0]:.2f})")

    return results

# ═══════════════════════════════════════════════════
# 失败记忆 (TITAN v2.0 — OpenClaw-inspired)
# ═══════════════════════════════════════════════════

FAILURES_FILE = os.path.join(MEMORY_DIR, "failures.json")

def _load_failures() -> list[dict]:
    if os.path.exists(FAILURES_FILE):
        try:
            with open(FAILURES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def _save_failures(data: list[dict]):
    _ensure_dir()
    with open(FAILURES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def remember_failure(category: str = "", reason: str = "", app_slug: str = ""):
    """记住一次生成失败（存储失败原因 + 类别，用于未来回避）"""
    failures = _load_failures()
    entry = {
        "category": category,
        "reason": reason[:300],
        "app_slug": app_slug,
        "timestamp": datetime.now().isoformat(),
    }
    failures.append(entry)
    if len(failures) > 100:
        failures = failures[-100:]
    _save_failures(failures)
    log.info(f"🧠 失败记忆存储: [{category}] {reason[:60]}... (总数: {len(failures)})")

def recall_failures(category: str = "", top_k: int = 3) -> list[dict]:
    """检索某类别的失败记忆，返回最近的失败原因"""
    failures = _load_failures()
    if not failures:
        return []
    if category:
        failures = [f for f in failures if f.get("category", "") == category]
    # 返回最近的 top_k 个
    return failures[-top_k:]


# ═══════════════════════════════════════════════════
# 架构模式学习 (TITAN v3.0 — Scholar 记忆提取)
# ═══════════════════════════════════════════════════

PATTERNS_FILE = os.path.join(MEMORY_DIR, "architectural_patterns.json")

def _load_patterns() -> list[dict]:
    if os.path.exists(PATTERNS_FILE):
        try:
            with open(PATTERNS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def _save_patterns(data: list[dict]):
    _ensure_dir()
    with open(PATTERNS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def remember_pattern(category: str, source_repo: str, description: str, prompt_fragment: str):
    """保存从 GitHub 自动学习到的优秀设计模式 (Skill Prompt)"""
    patterns = _load_patterns()
    entry = {
        "category": category,
        "source_repo": source_repo,
        "description": description[:500],
        "prompt_fragment": prompt_fragment,
        "timestamp": datetime.now().isoformat()
    }
    
    # 简单的覆盖逻辑：同样来源和类别的模式直接覆盖，避免重复
    patterns = [p for p in patterns if not (p.get("category") == category and p.get("source_repo") == source_repo)]
    patterns.append(entry)
    
    if len(patterns) > 500: # 扩容到 500
        patterns = patterns[-500:]
        
    _save_patterns(patterns)
    log.info(f"🧠 学会新技能 [{category}] 源自 {source_repo} (总技能数: {len(patterns)})")

def recall_pattern(category: str, top_k: int = 3, context: str = "") -> list[dict]:
    """v3.5: 关键词相似度加权召回 — 不再仅按 category 精确匹配，
    而是用 compute_similarity 对 description 做模糊匹配，优先召回最相关的模式。
    学习来源: deepset-ai/haystack (可序列化状态) + agentscope-ai/agentscope (向量存储)
    """
    patterns = _load_patterns()
    if not patterns:
        return []
        
    # 第一道筛子: category 匹配（宽泛匹配）
    if category and category != "Unknown":
        matched = [p for p in patterns if category.lower() in p.get("category", "").lower() or p.get("category", "") in ("Agent", "General", "Prompt")]
    else:
        matched = patterns
    
    if not matched:
        matched = patterns  # 如果没有匹配的，回退到全量
        
    # 第二道筛子: 如果有 context，用关键词相似度排序
    if context:
        context_kw = extract_keywords(context)
        for p in matched:
            desc_kw = extract_keywords(p.get("description", "") + " " + p.get("prompt_fragment", ""))
            p["_relevance"] = compute_similarity(context_kw, desc_kw)
        matched.sort(key=lambda x: x.get("_relevance", 0), reverse=True)
    else:
        # 无 context 时按时间排序（最新优先）
        matched.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # 清理临时字段
    result = matched[:top_k]
    for r in result:
        r.pop("_relevance", None)
    return result

def recall_multi_domain(domains: list[str], top_k_per_domain: int = 1, context: str = "") -> list[dict]:
    """v3.5: 跨域融合召回 — 一次从多个 category 中各取最相关模式，实现知识交叉注入。"""
    results = []
    seen_repos = set()
    for domain in domains:
        patterns = recall_pattern(domain, top_k=top_k_per_domain, context=context)
        for p in patterns:
            repo = p.get("source_repo", "")
            if repo not in seen_repos:
                results.append(p)
                seen_repos.add(repo)
    return results

# ═══════════════════════════════════════════════════
# 统计 & 诊断 v2
# ═══════════════════════════════════════════════════

def get_memory_stats() -> dict:
    exp = _load_experiences()
    templates = _load_templates()
    verified = sum(1 for e in exp if e.get("fix_verified", True))
    return {
        "total_fix_experiences": len(exp),
        "verified_fixes": verified,
        "unverified_fixes": len(exp) - verified,
        "total_successful_templates": len(templates),
        "avg_quality_score": sum(t.get("quality_score", 0) for t in templates) / max(len(templates), 1),
        "memory_dir": MEMORY_DIR,
    }


if __name__ == "__main__":
    print("🧠 Memory Bank v2 自测")
    print(f"  统计: {json.dumps(get_memory_stats(), indent=2)}")

    remember_fix(
        "Type error: Property 'value' does not exist on type 'EventTarget'",
        "const val = e.target.value;",
        "const val = (e.target as HTMLInputElement).value;",
        "test-app", fix_verified=True
    )
    remember_fix(
        "Property 'value' does not exist on type 'EventTarget'",
        "const x = e.target.value;",
        "// bad fix that didn't work",
        "test-app-bad", fix_verified=False
    )

    results = recall_fix("Property value does not exist on type EventTarget")
    print(f"  检索到 {len(results)} 条经验")
    for r in results:
        v = "✅" if r.get("fix_verified", True) else "⚠️"
        print(f"    {v} {r['error_snippet'][:50]}...")
    assert results[0].get("fix_verified", True), "验证过的修复应排在第一位"
    print("✅ v2 自测通过 (验证过的修复优先)")
