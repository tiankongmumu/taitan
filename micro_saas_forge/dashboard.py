"""
ShipMicro CEO Dashboard — 系统全局监控仪表盘
一键查看：系统健康、工具统计、质量报告、记忆库、部署历史。
"""
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger

log = get_logger("dashboard")

BASE_DIR = os.path.dirname(__file__)


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_history():
    return load_json(os.path.join(BASE_DIR, "history.json")) or []


def get_memory_stats():
    exp = load_json(os.path.join(BASE_DIR, "memory", "experiences.json")) or []
    tpl = load_json(os.path.join(BASE_DIR, "memory", "successful_templates.json")) or []
    return {"fix_experiences": len(exp), "successful_templates": len(tpl)}


def get_latest_quality_report():
    log_dir = os.path.join(BASE_DIR, "logs")
    if not os.path.isdir(log_dir):
        return None
    files = [f for f in os.listdir(log_dir) if f.startswith("quality_report") and f.endswith(".json")]
    if not files:
        return None
    latest = sorted(files)[-1]
    return load_json(os.path.join(log_dir, latest))


def get_generated_apps():
    apps_dir = os.path.join(BASE_DIR, "generated_apps")
    if not os.path.isdir(apps_dir):
        return []
    return [d for d in os.listdir(apps_dir) if os.path.isdir(os.path.join(apps_dir, d)) and not d.endswith("_fallback")]


def get_news_count():
    news_dir = os.path.join(BASE_DIR, "news_articles")
    if not os.path.isdir(news_dir):
        return 0
    return len([f for f in os.listdir(news_dir) if f.endswith(".json")])


def count_social_posts():
    sp_dir = os.path.join(BASE_DIR, "social_posts")
    if not os.path.isdir(sp_dir):
        return 0
    return len([f for f in os.listdir(sp_dir) if f.endswith(".json")])


def run_dashboard():
    """运行CEO仪表盘"""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " 🚢 SHIPMICRO CEO DASHBOARD ".center(58) + "║")
    print("║" + f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}".center(58) + "║")
    print("╚" + "═" * 58 + "╝")

    # ── 系统健康 ──
    history = get_history()
    apps = get_generated_apps()
    mem = get_memory_stats()

    print(f"\n{'─'*30} 系统健康 {'─'*30}")
    print(f"  🛠️  已部署工具:    {len(apps)}")
    print(f"  📋  历史记录条目:  {len(history)}")
    print(f"  🧠  修复经验记忆:  {mem['fix_experiences']}")
    print(f"  🧠  成功模板记忆:  {mem['successful_templates']}")
    print(f"  📰  新闻文章:      {get_news_count()}")
    print(f"  📢  社交帖子:      {count_social_posts()}")

    # ── 工具列表 ──
    print(f"\n{'─'*30} 工具列表 {'─'*30}")
    if apps:
        for i, app in enumerate(sorted(apps), 1):
            # 检查是否已部署（有 .vercel 目录或部署历史）
            app_path = os.path.join(BASE_DIR, "generated_apps", app)
            has_vercel = os.path.exists(os.path.join(app_path, ".vercel"))
            status = "🟢 已部署" if has_vercel else "🟡 本地"
            print(f"  {i:2d}. {status}  {app}")
    else:
        print("  (暂无工具)")

    # ── 质量报告 ──
    print(f"\n{'─'*30} 最新质量报告 {'─'*30}")
    qr = get_latest_quality_report()
    if qr:
        ship = qr.get("ship", [])
        improve = qr.get("improve", [])
        kill = qr.get("kill", [])
        print(f"  🟢 SHIP (可直接上线):  {len(ship)}")
        print(f"  🟡 IMPROVE (需改进):   {len(improve)}")
        print(f"  🔴 KILL (应下架):      {len(kill)}")
        if improve:
            print(f"\n  需改进的工具:")
            for t in sorted(improve, key=lambda x: x.get("overall", 0)):
                print(f"    {'⭐' * max(1, int(t.get('overall', 0) / 2))} {t.get('overall', '?')}/10 — {t.get('tool_name', '?')}")
    else:
        print("  (尚无质量报告, 运行 `python quality_gate.py` 生成)")

    # ── 记忆库摘要 ──
    print(f"\n{'─'*30} 记忆库 {'─'*30}")
    exp = load_json(os.path.join(BASE_DIR, "memory", "experiences.json")) or []
    if exp:
        print(f"  最近的修复经验:")
        for e in exp[-3:]:
            print(f"    🔧 [{e.get('app_slug', '?')}] {e.get('error_snippet', '')[:60]}...")
    else:
        print("  (记忆库为空 — 下次铸造工具时会自动积累)")

    # ── 能力矩阵 ──
    print(f"\n{'─'*30} 能力矩阵 {'─'*30}")
    capabilities = [
        ("LLM 代码生成", True), ("自愈编译引擎", True), ("Vercel 自动部署", True),
        ("AI 评分选题 (10→3)", True), ("AI 质量评审", True),
        ("系统记忆体 (RAG)", True), ("新闻抓取", True), ("社交推广生成", True),
        ("全流程自动化", True), ("CEO 仪表盘", True),
        ("用户行为追踪", True), ("AdSense 广告注入", True),
        ("自动化 UI 测试", True), ("多品类 (游戏线)", False),
        ("API 开放平台", False), ("异常告警通知", False),
    ]
    for name, done in capabilities:
        print(f"  {'✅' if done else '⬜'} {name}")

    done_count = sum(1 for _, d in capabilities if d)
    total = len(capabilities)
    pct = int(done_count / total * 100)
    bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
    print(f"\n  Web 4.0 完成度: [{bar}] {pct}% ({done_count}/{total})")

    print(f"\n{'═'*60}")
    print("  💡 快速命令:")
    print("    python shipmicro_autopilot.py --count 3    # 日常生产")
    print("    python quality_gate.py                     # 质量体检")
    print("    python tool_upgrader.py --max 3            # 自动升级")
    print("    python dashboard.py                        # 本仪表盘")
    print(f"{'═'*60}\n")


if __name__ == "__main__":
    run_dashboard()
