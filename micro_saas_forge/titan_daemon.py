"""
╔══════════════════════════════════════════════════════════════╗
║  TITAN Daemon v1.0 — Always-On Scheduler & Service          ║
║  Replaces OpenClaw's cron system with native Python          ║
║                                                              ║
║  Capabilities:                                                ║
║  • APScheduler-based cron/interval/one-shot tasks            ║
║  • Subprocess isolation (each task runs in its own process)   ║
║  • Health HTTP endpoint (/health, /jobs)                      ║
║  • Structured JSON logging                                    ║
║  • Graceful shutdown with signal handling                     ║
║  • System service registration (Windows Task Scheduler)       ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import signal
import asyncio
import subprocess
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import io

# Force utf-8 encoding for standard output to prevent crash when printing emojis on Windows CMD
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Centralized config
sys.path.insert(0, os.path.dirname(__file__))
from titan_config import FORGE_DIR, LOG_DIR, TOOL_SCRIPTS

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
log = logging.getLogger("titan_daemon")
log.setLevel(logging.INFO)

_ch = logging.StreamHandler()
_ch.setFormatter(logging.Formatter("%(asctime)s [TITAN-DAEMON] %(levelname)s %(message)s", "%H:%M:%S"))
log.addHandler(_ch)

_log_file = LOG_DIR / "titan_daemon.jsonl"

class _JsonFmt(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "ts": datetime.now().isoformat(),
            "level": record.levelname,
            "msg": record.getMessage(),
        }, ensure_ascii=False)

_fh = logging.handlers.RotatingFileHandler(
    str(_log_file), maxBytes=5_000_000, backupCount=3, encoding="utf-8"
)
_fh.setFormatter(_JsonFmt())
log.addHandler(_fh)

# ---------------------------------------------------------------------------
# Job Registry — All scheduled tasks
# ---------------------------------------------------------------------------
JOBS = [
    {
        "id": "daily_forge",
        "name": "每日锻造 (Daily Forge)",
        "script": TOOL_SCRIPTS.get("codemint"),
        "trigger": "cron",
        "hour": 9,
        "minute": 0,
        "description": "生成、验证并发布新的微型工具",
    },
    {
        "id": "news_scraper",
        "name": "新闻爬取 (News Scraper)",
        "script": TOOL_SCRIPTS.get("news_scraper"),
        "trigger": "interval",
        "hours": 4,
        "description": "从HackerNews等平台爬取科技资讯",
    },
    {
        "id": "beast_mode",
        "name": "野兽模式 (Beast Mode)",
        "script": TOOL_SCRIPTS.get("beast_mode"),
        "trigger": "cron",
        "hour": 20,
        "minute": 0,
        "description": "全自动社交内容生成与分发",
    },
    {
        "id": "demand_radar",
        "name": "需求雷达 (Demand Radar)",
        "script": TOOL_SCRIPTS.get("demand_radar"),
        "trigger": "cron",
        "hour": 8,
        "minute": 0,
        "description": "多源需求信号扫描",
    },
    {
        "id": "quality_gate",
        "name": "质量门禁 (Quality Gate)",
        "script": TOOL_SCRIPTS.get("quality_gate"),
        "trigger": "cron",
        "hour": 10,
        "minute": 30,
        "description": "已有工具质量检测",
    },
    {
        "id": "twitter_nurturer",
        "name": "推特账号防封养号 (Twitter Nurturer)",
        "script": TOOL_SCRIPTS.get("nurturer_twitter"),
        "trigger": "interval",
        "hours": 6,
        "description": "自动刷无干预时间线和点赞，维持账号真实度",
    },
]

# ---------------------------------------------------------------------------
# Job Execution — subprocess isolation
# ---------------------------------------------------------------------------
_job_history = []
_MAX_HISTORY = 100

def run_job(job_id: str, script_path: Path):
    """Run a job as a subprocess. Isolated so one crash doesn't take down the daemon."""
    start = datetime.now()
    entry = {
        "job_id": job_id,
        "started_at": start.isoformat(),
        "status": "running",
    }
    log.info(f"🚀 Starting job: {job_id}")

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,  # 10 min max per job
            cwd=str(FORGE_DIR),
            env={**os.environ, "PYTHONPATH": str(FORGE_DIR)},
        )
        elapsed = (datetime.now() - start).total_seconds()
        entry["elapsed_seconds"] = round(elapsed, 1)

        if result.returncode == 0:
            entry["status"] = "success"
            log.info(f"✅ Job {job_id} completed in {elapsed:.1f}s")
        else:
            entry["status"] = "failed"
            entry["error"] = result.stderr[-500:] if result.stderr else "unknown"
            log.error(f"❌ Job {job_id} failed (exit {result.returncode}): {entry['error'][:200]}")

    except subprocess.TimeoutExpired:
        elapsed = (datetime.now() - start).total_seconds()
        entry["status"] = "timeout"
        entry["elapsed_seconds"] = round(elapsed, 1)
        log.error(f"⏰ Job {job_id} timed out after {elapsed:.1f}s")

    except Exception as e:
        entry["status"] = "error"
        entry["error"] = str(e)
        log.error(f"💥 Job {job_id} error: {e}")

    _job_history.append(entry)
    if len(_job_history) > _MAX_HISTORY:
        _job_history.pop(0)


# ---------------------------------------------------------------------------
# Health HTTP Server
# ---------------------------------------------------------------------------
HEALTH_PORT = 8079

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self._json_response(200, {
                "status": "ok",
                "service": "titan-daemon",
                "uptime_since": _start_time.isoformat(),
                "jobs_registered": len(JOBS),
            })
        elif self.path == "/jobs":
            self._json_response(200, {
                "registered": [
                    {"id": j["id"], "name": j["name"], "trigger": j["trigger"], "description": j["description"]}
                    for j in JOBS
                ],
                "recent_history": _job_history[-20:],
            })
        elif self.path == "/run" or self.path.startswith("/run/"):
            # Manual trigger: /run/job_id
            job_id = self.path.split("/")[-1] if "/" in self.path[1:] else ""
            job = next((j for j in JOBS if j["id"] == job_id), None)
            if job and job.get("script") and Path(job["script"]).exists():
                threading.Thread(target=run_job, args=(job_id, job["script"]), daemon=True).start()
                self._json_response(200, {"status": "triggered", "job_id": job_id})
            else:
                self._json_response(404, {"error": f"Job '{job_id}' not found"})
        else:
            self._json_response(404, {"error": "not found"})

    def _json_response(self, code, data):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # Suppress default HTTP logging


def start_health_server():
    server = HTTPServer(("0.0.0.0", HEALTH_PORT), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    log.info(f"🏥 Health endpoint: http://localhost:{HEALTH_PORT}/health")
    log.info(f"📋 Jobs endpoint:   http://localhost:{HEALTH_PORT}/jobs")
    log.info(f"▶️  Manual trigger:  http://localhost:{HEALTH_PORT}/run/<job_id>")
    return server


# ---------------------------------------------------------------------------
# Scheduler — APScheduler or fallback asyncio
# ---------------------------------------------------------------------------
_start_time = datetime.now()

def _create_scheduler():
    """Create scheduler using APScheduler if available, else fallback to simple asyncio loop."""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        from apscheduler.triggers.interval import IntervalTrigger

        scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

        for job in JOBS:
            script = job.get("script")
            if not script or not Path(script).exists():
                log.warning(f"⚠️  Skipping job {job['id']}: script not found at {script}")
                continue

            if job["trigger"] == "cron":
                trigger = CronTrigger(
                    hour=job.get("hour", 9),
                    minute=job.get("minute", 0),
                    timezone="Asia/Shanghai",
                )
            elif job["trigger"] == "interval":
                trigger = IntervalTrigger(
                    hours=job.get("hours", 4),
                    timezone="Asia/Shanghai",
                )
            else:
                log.warning(f"⚠️  Unknown trigger type for {job['id']}: {job['trigger']}")
                continue

            scheduler.add_job(
                run_job,
                trigger=trigger,
                args=[job["id"], Path(script)],
                id=job["id"],
                name=job["name"],
                replace_existing=True,
                misfire_grace_time=300,
            )
            log.info(f"📅 Registered: {job['name']} ({job['trigger']})")

        return scheduler

    except ImportError:
        log.warning("⚠️  APScheduler not installed. Using fallback asyncio scheduler.")
        log.warning("   Install with: pip install apscheduler")
        return None


async def _fallback_loop():
    """Simple fallback scheduler when APScheduler isn't available."""
    import time as _time

    log.info("🔄 Running fallback scheduler loop (checks every 60s)")
    last_run = {}

    while True:
        now = datetime.now()
        for job in JOBS:
            script = job.get("script")
            if not script or not Path(script).exists():
                continue

            should_run = False
            jid = job["id"]

            if job["trigger"] == "cron":
                target_hour = job.get("hour", 9)
                target_min = job.get("minute", 0)
                if now.hour == target_hour and now.minute == target_min:
                    if jid not in last_run or (now - last_run[jid]).total_seconds() > 120:
                        should_run = True
            elif job["trigger"] == "interval":
                interval_h = job.get("hours", 4)
                if jid not in last_run or (now - last_run[jid]).total_seconds() > interval_h * 3600:
                    should_run = True

            if should_run:
                last_run[jid] = now
                threading.Thread(target=run_job, args=(jid, Path(script)), daemon=True).start()

        await asyncio.sleep(60)


# ---------------------------------------------------------------------------
# Windows Service Registration
# ---------------------------------------------------------------------------
def register_windows_service():
    """Register TITAN Daemon as a Windows Task Scheduler task (runs at login)."""
    import platform
    if platform.system() != "Windows":
        log.info("ℹ️  Not Windows — skipping service registration")
        return False

    python_exe = sys.executable
    script_path = Path(__file__).resolve()
    task_name = "TitanDaemon"

    cmd = (
        f'schtasks /Create /SC ONLOGON /TN "{task_name}" '
        f'/TR "\\"{python_exe}\\" \\"{script_path}\\"" '
        f'/RL HIGHEST /F'
    )

    log.info(f"📝 Registering Windows Task: {task_name}")
    log.info(f"   Command: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            log.info(f"✅ Windows Task '{task_name}' registered successfully (runs at login)")
            return True
        else:
            log.error(f"❌ Failed to register: {result.stderr}")
            return False
    except Exception as e:
        log.error(f"❌ Service registration error: {e}")
        return False


def unregister_windows_service():
    """Remove TITAN Daemon from Windows Task Scheduler."""
    cmd = 'schtasks /Delete /TN "TitanDaemon" /F'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            log.info("✅ Windows Task 'TitanDaemon' removed")
        else:
            log.warning(f"⚠️  Could not remove task: {result.stderr}")
    except Exception as e:
        log.error(f"❌ Error: {e}")


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("🧠 TITAN DAEMON v1.0 — Always-On Scheduler")
    print("=" * 60)

    # Handle CLI commands
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "install":
            register_windows_service()
            return
        elif cmd == "uninstall":
            unregister_windows_service()
            return
        elif cmd == "run":
            # Run a specific job immediately
            job_id = sys.argv[2] if len(sys.argv) > 2 else None
            if job_id:
                job = next((j for j in JOBS if j["id"] == job_id), None)
                if job and job.get("script"):
                    run_job(job_id, Path(job["script"]))
                else:
                    print(f"❌ Job '{job_id}' not found. Available: {[j['id'] for j in JOBS]}")
            else:
                print(f"Available jobs: {[j['id'] for j in JOBS]}")
            return
        elif cmd == "list":
            print("\n📋 Registered Jobs:")
            for j in JOBS:
                script_ok = "✅" if j.get("script") and Path(j["script"]).exists() else "❌"
                trigger = f"cron {j.get('hour', '?')}:{j.get('minute', '?'):02d}" if j["trigger"] == "cron" else f"every {j.get('hours', '?')}h"
                print(f"  {script_ok} {j['id']:20s} | {trigger:15s} | {j['name']}")
            return
        elif cmd in ("help", "--help", "-h"):
            print("""
Usage: python titan_daemon.py [command]

Commands:
  (none)      Start the daemon (foreground)
  install     Register as Windows startup task
  uninstall   Remove Windows startup task
  run <id>    Run a specific job immediately
  list        List all registered jobs
  help        Show this help
""")
            return

    # Start health server
    health_server = start_health_server()

    # Create scheduler
    scheduler = _create_scheduler()

    # Graceful shutdown
    shutdown_event = asyncio.Event() if scheduler is None else None

    def handle_signal(sig, frame):
        log.info(f"🛑 Received signal {sig}, shutting down...")
        if scheduler:
            scheduler.shutdown(wait=False)
        if shutdown_event:
            shutdown_event.set()
        health_server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Print status
    print(f"\n📅 Registered {len(JOBS)} jobs:")
    for j in JOBS:
        script_ok = "✅" if j.get("script") and Path(j["script"]).exists() else "⚠️"
        trigger = f"cron {j.get('hour', '?')}:{j.get('minute', '?'):02d}" if j["trigger"] == "cron" else f"every {j.get('hours', '?')}h"
        print(f"  {script_ok} {j['id']:20s} | {trigger:15s} | {j['name']}")

    print(f"\n🏥 Health: http://localhost:{HEALTH_PORT}/health")
    print(f"📋 Jobs:   http://localhost:{HEALTH_PORT}/jobs")
    print(f"▶️  Run:    http://localhost:{HEALTH_PORT}/run/<job_id>")
    print("\n🟢 TITAN Daemon running. Press Ctrl+C to stop.\n")

    if scheduler:
        scheduler.start()
        try:
            # Keep the main thread alive
            signal.pause() if hasattr(signal, 'pause') else asyncio.get_event_loop().run_forever()
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
    else:
        # Fallback: use asyncio
        asyncio.run(_fallback_loop())


if __name__ == "__main__":
    main()
