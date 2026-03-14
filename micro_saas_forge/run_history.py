"""
Micro-SaaS Forge — 运行历史记录
每次 pipeline 执行后记录结果，方便追溯和统计。
"""
import json
import os
from datetime import datetime
from config import HISTORY_FILE


def record_run(idea: str, spec: dict, success: bool, url: str, duration_s: float):
    """追加一条运行记录到 history.json。"""
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []

    entry = {
        "timestamp": datetime.now().isoformat(),
        "idea": idea,
        "app_name": spec.get("name", "Unknown"),
        "slug": spec.get("slug", "unknown"),
        "success": success,
        "deployment_url": url,
        "duration_seconds": round(duration_s, 2),
    }
    history.append(entry)

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    return entry


def get_history() -> list:
    """读取全部运行历史。"""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def print_stats():
    """打印运行统计。"""
    history = get_history()
    if not history:
        print("暂无运行记录。")
        return

    total = len(history)
    success = sum(1 for h in history if h["success"])
    avg_time = sum(h["duration_seconds"] for h in history) / total

    print(f"\n📊 Forge 运行统计")
    print(f"   总运行次数: {total}")
    print(f"   成功率: {success}/{total} ({success/total*100:.0f}%)")
    print(f"   平均耗时: {avg_time:.1f}s")
    print(f"   最近一次: {history[-1]['app_name']} ({'✅' if history[-1]['success'] else '❌'})")
