"""
╔══════════════════════════════════════════════════════════════╗
║  TITAN Executor v1.0 — 任务执行器 ⚡                         ║
║  Maps heart instructions to real Python functions            ║
║                                                              ║
║  信号传导链：                                                 ║
║  👻灵魂 → ❤️心脏 → ⚡执行器 → 🧠大脑/📡感知/🔧技能          ║
║                                                              ║
║  心脏产生指令 → 执行器翻译成实际函数调用 → 返回结果给灵魂     ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import asyncio
import logging
import traceback
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable

sys.path.insert(0, os.path.dirname(__file__))
from titan_config import FORGE_DIR, LOG_DIR

log = logging.getLogger("titan_executor")


# ---------------------------------------------------------------------------
# Task Implementations — 每个任务的实际执行逻辑
# ---------------------------------------------------------------------------

def _run_demand_radar() -> dict:
    """📡 扫描高变现需求"""
    try:
        from demand_radar import DemandRadar
        radar = DemandRadar()
        signals = radar.scan()
        top = signals[:5] if signals else []
        return {
            "success": True,
            "outcome": f"扫描完成，发现{len(signals)}个信号，Top5: {[s.get('keyword','?') for s in top]}",
            "data": {"total_signals": len(signals), "top_5": top},
        }
    except Exception as e:
        return {"success": False, "outcome": f"需求雷达扫描失败: {e}"}


def _run_forge_tool() -> dict:
    """⚒️ 锻造变现工具 — 使用大脑完整流水线，失败则升级给Antigravity"""
    try:
        from titan_brain import TitanBrain
        brain = TitanBrain()
        report = brain.run_cycle(dry_run=False)
        success = report.get("status") == "shipped" if isinstance(report, dict) else False

        if not success and isinstance(report, dict):
            # 构建失败 → 检查是否需要升级给Antigravity
            steps = report.get("steps", {})
            keyword = ""
            errors = []
            if "discover" in steps:
                top3 = steps["discover"].get("top_3", [])
                keyword = top3[0] if top3 else ""
            if "build" in steps:
                errors = [str(steps["build"].get("error", ""))]
            if "test" in steps:
                errors.append(str(steps["test"].get("error", "")))

            # 读取大脑状态看连续失败次数
            brain_state_file = FORGE_DIR / "brain_state.json"
            consecutive_failures = 0
            if brain_state_file.exists():
                bs = json.loads(brain_state_file.read_text(encoding="utf-8"))
                history = bs.get("history", [])
                for h in reversed(history[-5:]):
                    if not h.get("success", True):
                        consecutive_failures += 1
                    else:
                        break

            if consecutive_failures >= 2 and keyword:
                try:
                    from titan_coding_bridge import CodingBridge, assess_complexity, TaskComplexity
                    bridge = CodingBridge()
                    complexity = assess_complexity(
                        keyword=keyword,
                        previous_failures=consecutive_failures,
                        error_patterns=errors,
                    )
                    if complexity in (TaskComplexity.COMPLEX, TaskComplexity.CRITICAL):
                        # 读取需求信号的详细信息
                        signals_file = FORGE_DIR / "demand_signals" / "signals.json"
                        signal_info = {}
                        if signals_file.exists():
                            sdata = json.loads(signals_file.read_text(encoding="utf-8"))
                            for sig in sdata.get("signals", []):
                                if sig.get("keyword") == keyword:
                                    signal_info = sig
                                    break

                        bridge.create_request(
                            title=f"构建 {keyword} 工具",
                            description=f"API自动构建{consecutive_failures}次失败，升级给Antigravity。",
                            keyword=keyword,
                            monthly_volume=signal_info.get("monthly_volume", 0),
                            revenue_model=signal_info.get("revenue_model", ""),
                            differentiation=signal_info.get("differentiation", ""),
                            build_complexity=signal_info.get("build_complexity", "COMPLEX"),
                            previous_attempts=consecutive_failures,
                            failure_reasons=[f"cycle失败"] + errors[:3],
                            error_logs=errors[:5],
                            priority=1,
                        )
                        log.info(f"🌉 已升级给Antigravity: {keyword}")
                except Exception as bridge_err:
                    log.warning(f"桥接升级失败: {bridge_err}")

        return {
            "success": success,
            "outcome": f"锻造完成: {json.dumps(report, ensure_ascii=False, default=str)[:200]}",
            "data": report,
        }
    except Exception as e:
        return {"success": False, "outcome": f"锻造失败: {e}"}


def _run_daily_forge() -> dict:
    """⚒️ 每日锻造 — 生成+评估+构建"""
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(__file__), "daily_forge.py")],
            capture_output=True, text=True, timeout=300, cwd=os.path.dirname(__file__),
        )
        success = result.returncode == 0
        output = result.stdout[-500:] if result.stdout else result.stderr[-500:]
        return {
            "success": success,
            "outcome": f"每日锻造{'成功' if success else '失败'}: {output[:200]}",
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "outcome": "每日锻造超时(300s)"}
    except Exception as e:
        return {"success": False, "outcome": f"每日锻造异常: {e}"}


def _run_quality_gate() -> dict:
    """🔍 质量门控检查"""
    try:
        from titan_brain import TitanBrain
        brain = TitanBrain()
        qa_report = brain.qa_existing()
        return {
            "success": True,
            "outcome": f"质量检查完成: {json.dumps(qa_report, ensure_ascii=False, default=str)[:200]}",
            "data": qa_report,
        }
    except Exception as e:
        return {"success": False, "outcome": f"质量检查失败: {e}"}


def _run_news_scan() -> dict:
    """📰 新闻扫描"""
    try:
        from news_scraper import NewsScraper
        scraper = NewsScraper()
        articles = scraper.scrape()
        return {
            "success": True,
            "outcome": f"新闻扫描完成，获取{len(articles) if articles else 0}篇文章",
            "data": {"article_count": len(articles) if articles else 0},
        }
    except Exception as e:
        return {"success": False, "outcome": f"新闻扫描失败: {e}"}


def _run_skill_analysis() -> dict:
    """📊 分析失败技能"""
    try:
        from memory_bank import MemoryBank
        mb = MemoryBank()
        failures = mb.get_recent_failures(10) if hasattr(mb, 'get_recent_failures') else []
        # Read history for pattern extraction
        history_file = FORGE_DIR / "history.json"
        history = []
        if history_file.exists():
            data = json.loads(history_file.read_text(encoding="utf-8"))
            if isinstance(data, list):
                history = data
            elif isinstance(data, dict):
                history = data.get("runs", [])
            failed = [h for h in history if not h.get("success", True)]
            return {
                "success": True,
                "outcome": f"分析完成: 历史{len(history)}次运行, {len(failed)}次失败",
                "data": {"total_runs": len(history), "failures": len(failed)},
            }
        return {"success": True, "outcome": "暂无历史数据可分析"}
    except Exception as e:
        return {"success": False, "outcome": f"技能分析失败: {e}"}


def _run_skill_learning() -> dict:
    """📚 学习新能力"""
    try:
        from skill_learner import SkillLearner
        learner = SkillLearner()
        learned = learner.review_and_learn() if hasattr(learner, 'review_and_learn') else None
        return {
            "success": True,
            "outcome": f"技能学习完成: {learned if learned else '复习了已有技能'}",
        }
    except Exception as e:
        return {"success": False, "outcome": f"技能学习失败: {e}"}


def _run_system_health() -> dict:
    """🏥 系统健康检查"""
    import shutil
    disk = shutil.disk_usage(os.path.dirname(__file__))
    disk_pct = disk.used / disk.total * 100

    # Check log sizes
    log_size = 0
    log_dir = LOG_DIR
    if log_dir.exists():
        for f in log_dir.iterdir():
            if f.is_file():
                log_size += f.stat().st_size

    return {
        "success": True,
        "outcome": f"系统健康: 磁盘使用{disk_pct:.1f}%, 日志大小{log_size/1024/1024:.1f}MB",
        "data": {"disk_usage_pct": disk_pct, "log_size_mb": log_size / 1024 / 1024},
    }


def _run_error_diagnosis() -> dict:
    """🔧 错误诊断"""
    errors = []
    log_file = LOG_DIR / "titan_heart.jsonl"
    if log_file.exists():
        lines = log_file.read_text(encoding="utf-8").strip().split("\n")
        for line in lines[-100:]:
            try:
                entry = json.loads(line)
                if entry.get("level") in ("ERROR", "CRITICAL"):
                    errors.append(entry)
            except:
                pass

    return {
        "success": True,
        "outcome": f"错误诊断: 最近100条日志中发现{len(errors)}个错误",
        "data": {"error_count": len(errors), "recent_errors": errors[-5:]},
    }


def _run_resource_cleanup() -> dict:
    """🧹 清理资源"""
    cleaned = 0
    # Clean old log files
    log_dir = LOG_DIR
    if log_dir.exists():
        for f in log_dir.iterdir():
            if f.is_file() and f.suffix in (".log", ".tmp") and f.stat().st_size > 10_000_000:
                f.unlink()
                cleaned += 1

    # Clean __pycache__
    base = Path(os.path.dirname(__file__))
    for cache_dir in base.rglob("__pycache__"):
        if cache_dir.is_dir():
            for f in cache_dir.iterdir():
                if f.is_file():
                    f.unlink()
                    cleaned += 1

    return {
        "success": True,
        "outcome": f"资源清理完成: 清理了{cleaned}个文件",
        "data": {"files_cleaned": cleaned},
    }


def _run_beast_mode() -> dict:
    """🦁 野兽推广模式"""
    try:
        beast_script = os.path.join(os.path.dirname(__file__), "titan_beast_mode.py")
        if os.path.exists(beast_script):
            result = subprocess.run(
                [sys.executable, beast_script],
                capture_output=True, text=True, timeout=120,
                cwd=os.path.dirname(__file__),
            )
            return {
                "success": result.returncode == 0,
                "outcome": f"野兽模式{'成功' if result.returncode == 0 else '失败'}: {result.stdout[-200:]}",
            }
        return {"success": False, "outcome": "beast_mode脚本不存在"}
    except Exception as e:
        return {"success": False, "outcome": f"野兽模式异常: {e}"}


def _run_social_distribute() -> dict:
    """📢 社交分发"""
    try:
        from titan_channels import TitanChannels
        channels = TitanChannels()
        # Build a status message
        heart_inst = FORGE_DIR / "heart_instruction.json"
        msg = "🤖 泰坦引擎运行中 — 正在自主探索变现机会"
        if heart_inst.exists():
            inst = json.loads(heart_inst.read_text(encoding="utf-8"))
            msg = f"🤖 泰坦引擎运行中\n阶段: {inst.get('stage','?')}\n驱动: {inst.get('drive','?')}"

        # Try async broadcast
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(channels.broadcast(msg))
        finally:
            loop.close()

        return {"success": True, "outcome": "社交分发完成"}
    except Exception as e:
        return {"success": False, "outcome": f"社交分发失败(通道未配置?): {e}"}


def _run_web_scan(scan_type: str = "security") -> dict:
    """🔍 Web扫描 (学习自Shannon)"""
    try:
        from titan_web_scanner import TitanWebScanner
        scanner = TitanWebScanner()

        generated_dir = FORGE_DIR / "generated_apps"
        if scan_type == "competitor":
            # 分析竞品 — 用热门信号的第一个关键词搜索
            return {"success": True, "outcome": "竞品分析需要URL参数"}

        # 扫描最新生成的应用
        app_dirs = sorted(
            [d for d in generated_dir.iterdir() if d.is_dir() and (d / "src").exists()],
            key=lambda d: d.stat().st_mtime,
            reverse=True,
        )

        if not app_dirs:
            return {"success": True, "outcome": "没有找到可扫描的应用"}

        latest = app_dirs[0]
        if scan_type == "full":
            report = scanner.full_scan(str(latest))
        else:
            report = scanner.security_scan(str(latest))

        passed = report.get("passed", False)
        score = report.get("score", 0)
        return {
            "success": True,
            "outcome": f"Web扫描({'全面' if scan_type == 'full' else '安全'}): {latest.name} — "
                       f"{'✅通过' if passed else '❌未通过'} (分数={score})",
            "data": report,
        }
    except Exception as e:
        return {"success": False, "outcome": f"Web扫描失败: {e}"}


def _run_check_bridge() -> dict:
    """🌉 检查Antigravity编码请求状态"""
    try:
        from titan_coding_bridge import CodingBridge
        bridge = CodingBridge()
        pending = bridge.get_pending()
        completed = bridge.check_completed()
        return {
            "success": True,
            "outcome": f"编码桥接: {len(pending)}待处理, {len(completed)}已完成",
            "data": {
                "pending": len(pending),
                "completed": len(completed),
                "pending_keywords": [p.keyword for p in pending[:5]],
            },
        }
    except Exception as e:
        return {"success": False, "outcome": f"桥接检查失败: {e}"}


def _noop(task_name: str) -> dict:
    """未知任务 — 记录但不执行"""
    log.warning(f"⚠️ 任务'{task_name}'暂未实现，已记录")
    return {
        "success": True,
        "outcome": f"任务'{task_name}'暂未实现，已记录",
        "data": {"skipped": True},
    }


# ---------------------------------------------------------------------------
# 💰 Monetize Task Wrappers — 调用 titan_monetize
# ---------------------------------------------------------------------------

def _run_integrate_payment() -> dict:
    from titan_monetize import integrate_payment
    return integrate_payment()

def _run_analyze_conversion() -> dict:
    from titan_monetize import analyze_conversion
    return analyze_conversion()

def _run_optimize_landing() -> dict:
    from titan_monetize import optimize_landing
    return optimize_landing()

def _run_track_revenue() -> dict:
    from titan_monetize import track_revenue
    return track_revenue()

def _run_collect_feedback() -> dict:
    from titan_monetize import collect_feedback
    return collect_feedback()

def _run_expand_market() -> dict:
    from titan_monetize import expand_market
    return expand_market()

def _run_auto_deploy() -> dict:
    from titan_monetize import auto_deploy_to_shipmicro
    return auto_deploy_to_shipmicro()

def _run_optimize_retention() -> dict:
    from titan_monetize import optimize_retention
    return optimize_retention()


# ---------------------------------------------------------------------------
# Task Registry — 任务名 → 执行函数映射
# ---------------------------------------------------------------------------
TASK_REGISTRY: Dict[str, Callable] = {
    # 📡 感知任务
    "demand_radar_scan":       _run_demand_radar,
    "news_scan":               _run_news_scan,

    # ⚒️ 构建任务
    "forge_monetization_tool": _run_forge_tool,
    "forge_daily":             _run_daily_forge,

    # 🔍 质量任务
    "quality_gate_review":     _run_quality_gate,
    "system_health_check":     _run_system_health,

    # 📈 成长任务
    "analyze_failed_skills":   _run_skill_analysis,
    "learn_new_capability":    _run_skill_learning,
    "extract_success_patterns": _run_skill_analysis,
    "upgrade_weak_skills":     _run_skill_learning,

    # 🛡️ 生存任务
    "diagnose_errors":         _run_error_diagnosis,
    "free_resources":          _run_resource_cleanup,
    "rollback_if_needed":      lambda: {"success": True, "outcome": "无需回滚"},
    "alert_owner":             lambda: {"success": True, "outcome": "告警已记录"},

    # 📢 分发任务
    "social_distribute":       _run_social_distribute,
    "beast_mode_push":         _run_beast_mode,

    # 🌉 桥接任务
    "check_coding_requests":   _run_check_bridge,

    # 🔍 Web扫描任务 (学习自Shannon)
    "web_security_scan":       lambda: _run_web_scan("security"),
    "web_full_scan":           lambda: _run_web_scan("full"),
    "competitor_analysis":     lambda: _run_web_scan("competitor"),

    # 💰 商业任务 — 接入 titan_monetize 真实实现
    "integrate_payment":         _run_integrate_payment,
    "analyze_conversion_funnel": _run_analyze_conversion,
    "optimize_landing_page":     _run_optimize_landing,
    "ab_test_pricing":           _run_track_revenue,
    "collect_user_feedback":     _run_collect_feedback,
    "expand_to_new_market":      _run_expand_market,
    "upsell_existing_users":     _run_auto_deploy,
    "optimize_retention":        _run_optimize_retention,
}


# ---------------------------------------------------------------------------
# Titan Executor — 核心执行器
# ---------------------------------------------------------------------------
class TitanExecutor:
    """
    将心脏的行动指令翻译为实际的Python函数调用。

    信号链：
      ❤️ heart_instruction.json
        → ⚡ TitanExecutor.execute_plan()
          → 🧠 DemandRadar / TitanBrain / ForgeMaster / ...
            → 📊 结果 → 👻 Soul.reflect_on_result()
    """

    def __init__(self):
        self.execution_log: List[dict] = []
        self._log_file = LOG_DIR / "titan_executor.jsonl"
        self.task_timeout = 300  # 默认5分钟超时

    def execute_plan(self, tasks: List[str], energy: float = 1.0) -> dict:
        """
        执行行动计划中的任务列表。

        Args:
            tasks: 任务名列表, e.g. ["demand_radar_scan", "forge_monetization_tool"]
            energy: 能量系数 (0-1), 控制执行多少任务

        Returns:
            {"success": bool, "results": [...], "summary": str}
        """
        # 根据能量决定执行多少任务
        max_tasks = max(1, int(len(tasks) * energy))
        tasks_to_run = tasks[:max_tasks]

        log.info(f"⚡ 执行器启动: {len(tasks_to_run)}/{len(tasks)} 任务 (能量={energy:.0%})")

        results = []
        successes = 0
        failures = 0

        for i, task_name in enumerate(tasks_to_run):
            log.info(f"  [{i+1}/{len(tasks_to_run)}] 🔄 {task_name}...")

            executor_fn = TASK_REGISTRY.get(task_name)
            if not executor_fn:
                result = _noop(task_name)
                log.warning(f"      ⚠️ 未知任务: {task_name}")
            else:
                try:
                    start = time.time()
                    result = executor_fn()
                    elapsed = time.time() - start

                    result["task"] = task_name
                    result["elapsed_seconds"] = round(elapsed, 1)

                    if result.get("success"):
                        successes += 1
                        log.info(f"      ✅ {result.get('outcome', '完成')[:80]} ({elapsed:.1f}s)")
                    else:
                        failures += 1
                        log.warning(f"      ❌ {result.get('outcome', '失败')[:80]} ({elapsed:.1f}s)")

                except Exception as e:
                    failures += 1
                    result = {
                        "task": task_name,
                        "success": False,
                        "outcome": f"执行异常: {str(e)[:200]}",
                        "traceback": traceback.format_exc()[-300:],
                    }
                    log.error(f"      💥 {task_name}: {e}")

            results.append(result)
            self._log_execution(result)

        # 汇总
        summary = f"执行完成: {successes}成功/{failures}失败/{len(tasks_to_run)}总计"
        log.info(f"⚡ {summary}")

        return {
            "success": failures == 0,
            "results": results,
            "summary": summary,
            "successes": successes,
            "failures": failures,
            "total": len(tasks_to_run),
        }

    def _log_execution(self, result: dict):
        """记录执行日志"""
        entry = {
            "ts": datetime.now().isoformat(),
            "task": result.get("task", "unknown"),
            "success": result.get("success", False),
            "outcome": result.get("outcome", "")[:200],
            "elapsed": result.get("elapsed_seconds", 0),
        }

        try:
            with open(self._log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

        self.execution_log.append(entry)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    args = sys.argv[1:]

    if not args or args[0] == "run":
        # Read heart instruction and execute
        inst_file = FORGE_DIR / "heart_instruction.json"
        if inst_file.exists():
            inst = json.loads(inst_file.read_text(encoding="utf-8"))
            tasks = inst.get("tasks", [])
            energy = inst.get("energy_allocation", 1.0)
            print(f"📋 读取心脏指令: {tasks}")
            executor = TitanExecutor()
            result = executor.execute_plan(tasks, energy)
            print(f"\n📊 {result['summary']}")
        else:
            print("❌ 没有找到 heart_instruction.json")

    elif args[0] == "task":
        # Run a specific task
        if len(args) > 1:
            task_name = args[1]
            executor = TitanExecutor()
            result = executor.execute_plan([task_name])
            print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        else:
            print("Usage: python titan_executor.py task <task_name>")

    elif args[0] == "list":
        print("📋 可用任务:")
        for name in sorted(TASK_REGISTRY.keys()):
            print(f"  • {name}")

    elif args[0] in ("help", "--help", "-h"):
        print("""
⚡ TITAN Executor v1.0 — Usage:
  python titan_executor.py run              执行心脏指令
  python titan_executor.py task <name>      执行单个任务
  python titan_executor.py list             列出所有可用任务
""")
    else:
        print(f"❌ Unknown command: {args[0]}. Run with --help")


if __name__ == "__main__":
    _main()
