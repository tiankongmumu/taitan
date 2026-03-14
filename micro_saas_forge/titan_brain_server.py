"""
╔══════════════════════════════════════════════════════════════╗
║  TITAN Brain Server v2.0 — Production Hardened 🧠🦞          ║
║  OpenClaw's body, TITAN's mind.                              ║
║                                                              ║
║  v2.0 Upgrades:                                              ║
║  • Robust WebSocket with heartbeat & exponential reconnect   ║
║  • Tool Orchestrator with circuit breakers                   ║
║  • Conversation memory cap (prevents OOM)                    ║
║  • HTTP health endpoint (/health, /metrics)                  ║
║  • Structured JSON logging                                   ║
║  • Graceful signal handling                                  ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import asyncio
import signal
import time
import logging
import logging.handlers
from datetime import datetime, timedelta
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# ---------------------------------------------------------------------------
# Use centralized config
# ---------------------------------------------------------------------------
from titan_config import (
    FORGE_DIR, PROJECT_DIR,
    DEEPSEEK_API_KEY, DEEPSEEK_URL, DEEPSEEK_MODEL,
    QWEN_API_KEY, QWEN_URL, QWEN_MODEL,
    LLM_MAX_TOKENS, LLM_TEMPERATURE, LLM_TIMEOUT_SECONDS,
    BRAIN_MAX_HISTORY, BRAIN_HEALTH_PORT, BRAIN_LOG_FILE,
    WS_URL, WS_PING_INTERVAL, WS_PING_TIMEOUT,
    WS_RECONNECT_MIN, WS_RECONNECT_MAX, WS_RECONNECT_FACTOR,
    WS_MESSAGE_BUFFER,
    BEAST_MODE_HOUR, BEAST_MODE_MINUTE,
)
from tool_orchestrator import ToolOrchestrator

# ---------------------------------------------------------------------------
# Logging — dual output: console + JSONL file
# ---------------------------------------------------------------------------
log = logging.getLogger("titan_brain")
log.setLevel(logging.INFO)

# Console handler
_ch = logging.StreamHandler()
_ch.setFormatter(logging.Formatter("%(asctime)s [TITAN-BRAIN] %(levelname)s %(message)s", "%H:%M:%S"))
log.addHandler(_ch)

# File handler (JSONL for structured post-mortem)
class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "ts": datetime.now().isoformat(),
            "level": record.levelname,
            "msg": record.getMessage(),
            "module": record.module,
        }, ensure_ascii=False)

_fh = logging.handlers.RotatingFileHandler(
    str(BRAIN_LOG_FILE), maxBytes=5_000_000, backupCount=3, encoding="utf-8"
)
_fh.setFormatter(JsonFormatter())
log.addHandler(_fh)

# ---------------------------------------------------------------------------
# LLM Reasoning Engine
# ---------------------------------------------------------------------------
try:
    import requests as _req
except ImportError:
    _req = None

SYSTEM_PROMPT = """你是 TITAN Beast Mode 大脑 v2.0。你运行在 OpenClaw 框架之上，控制着所有的通信通道和本地工具。

你拥有以下能力（以 JSON tool_call 格式调用）：
1. news_scraper  — 爬取 HackerNews 获取热门 SaaS/AI 趋势
2. codemint      — 根据主题自动生成一个完整的微型 SaaS 工具（HTML/JS）
3. publisher     — 将生成的工具发布到小红书或 Reddit
4. browser       — 通过 OpenClaw 控制本地浏览器
5. reply         — 直接回复用户消息

回复格式必须是严格的 JSON：
{"tool": "reply|news_scraper|codemint|publisher|browser", "args": {...}}
链式调用返回 JSON 数组：
[{"tool": "news_scraper", "args": {}}, {"tool": "codemint", "args": {"topic": "..."}}]
永远使用中文回复。"""


def _call_llm(messages: list) -> str:
    if _req is None:
        return json.dumps({"tool": "reply", "args": {"content": "（离线模式）requests 未安装。"}})

    api_key = DEEPSEEK_API_KEY or QWEN_API_KEY
    model = DEEPSEEK_MODEL if DEEPSEEK_API_KEY else QWEN_MODEL
    url = DEEPSEEK_URL if DEEPSEEK_API_KEY else QWEN_URL

    try:
        r = _req.post(url, headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }, json={
            "model": model,
            "messages": messages,
            "max_tokens": LLM_MAX_TOKENS,
            "temperature": LLM_TEMPERATURE,
        }, timeout=LLM_TIMEOUT_SECONDS)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        log.error(f"LLM call failed: {e}")
        return json.dumps({"tool": "reply", "args": {"content": f"⚠️ LLM 推理出错: {e}"}})


# ---------------------------------------------------------------------------
# TitanBrain — with memory cap
# ---------------------------------------------------------------------------
class TitanBrain:
    """The cognitive core with bounded conversation memory."""

    def __init__(self):
        self.conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.total_thoughts = 0

    def think(self, user_message: str) -> list:
        self.conversation_history.append({"role": "user", "content": user_message})
        self._trim_history()

        raw = _call_llm(self.conversation_history)
        self.conversation_history.append({"role": "assistant", "content": raw})
        self.total_thoughts += 1

        log.info(f"LLM response (thought #{self.total_thoughts}): {raw[:150]}...")
        return self._parse_actions(raw)

    def _trim_history(self):
        """Keep only the system prompt + last N messages to prevent OOM."""
        if len(self.conversation_history) > BRAIN_MAX_HISTORY + 1:
            system = self.conversation_history[0]
            recent = self.conversation_history[-(BRAIN_MAX_HISTORY):]
            self.conversation_history = [system] + recent
            log.info(f"🧹 Memory trimmed to {len(self.conversation_history)} messages")

    @staticmethod
    def _parse_actions(raw: str) -> list:
        try:
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = "\n".join(cleaned.split("\n")[1:])
            if cleaned.endswith("```"):
                cleaned = "\n".join(cleaned.split("\n")[:-1])
            cleaned = cleaned.strip()
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                return [parsed]
            elif isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass
        return [{"tool": "reply", "args": {"content": raw}}]

    def get_status(self) -> dict:
        return {
            "total_thoughts": self.total_thoughts,
            "history_length": len(self.conversation_history),
            "max_history": BRAIN_MAX_HISTORY,
        }


# ---------------------------------------------------------------------------
# Tool Executor — bridges TITAN's Python scripts
# ---------------------------------------------------------------------------
class ToolExecutor:
    @staticmethod
    async def execute(tool_name: str, args: dict) -> str:
        log.info(f"⚡ Executing tool: {tool_name}")
        executors = {
            "news_scraper": ToolExecutor._run_news_scraper,
            "codemint":     ToolExecutor._run_codemint,
            "publisher":    ToolExecutor._run_publisher,
            "browser":      ToolExecutor._run_browser,
            "reply":        ToolExecutor._passthrough_reply,
        }
        fn = executors.get(tool_name)
        if fn is None:
            return f"❌ Unknown tool: {tool_name}"
        return await fn(args)

    @staticmethod
    async def _passthrough_reply(args): return args.get("content", "")

    @staticmethod
    async def _run_news_scraper(args):
        return f"📰 News Scraper:\n{await _run_subprocess(['python', str(FORGE_DIR / 'news_scraper.py')])}"

    @staticmethod
    async def _run_codemint(args):
        topic = args.get("topic", "AI productivity tool")
        return f"🔨 CodeMint ({topic}):\n{await _run_subprocess(['python', str(FORGE_DIR / 'daily_forge.py')], {'FORGE_TOPIC': topic})}"

    @staticmethod
    async def _run_publisher(args):
        p = args.get("platform", "xhs")
        script = "reddit_publisher.py" if p == "reddit" else "xhs_publisher_async.py"
        return f"📢 Published to {p}:\n{await _run_subprocess(['python', str(FORGE_DIR / script)])}"

    @staticmethod
    async def _run_browser(args):
        return f"🌐 Browser: open {args.get('url', 'shipmicro.com')} (via OpenClaw Node)"


async def _run_subprocess(cmd, env_extra=None):
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            env=env, cwd=str(FORGE_DIR))
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
        out = stdout.decode("utf-8", errors="replace")
        if stderr:
            out += "\n[stderr] " + stderr.decode("utf-8", errors="replace")
        return out[:1500]
    except asyncio.TimeoutError:
        return "⏰ Subprocess timed out."
    except Exception as e:
        return f"Error: {e}"


# ---------------------------------------------------------------------------
# Robust WebSocket Connector (v2.0 upgrade)
# ---------------------------------------------------------------------------
class ConnectionState:
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    RECONNECTING = "RECONNECTING"


class RobustWSConnector:
    """
    Production-grade WebSocket connector with:
    - Heartbeat ping/pong
    - Exponential backoff reconnect
    - Outbound message buffer during reconnection
    - Connection state machine
    """

    def __init__(self, brain: TitanBrain, orchestrator: ToolOrchestrator):
        self.brain = brain
        self.orchestrator = orchestrator
        self.ws = None
        self.state = ConnectionState.DISCONNECTED
        self.reconnect_delay = WS_RECONNECT_MIN
        self.message_buffer = asyncio.Queue(maxsize=WS_MESSAGE_BUFFER)
        self._ping_task = None
        self._uptime_start = None
        self.total_messages_in = 0
        self.total_messages_out = 0

    async def run(self):
        log.info(f"🧠 TITAN Brain Server v2.0 starting...")
        log.info(f"   Gateway: {WS_URL}")
        log.info(f"   LLM: {'DeepSeek' if DEEPSEEK_API_KEY else 'Qwen' if QWEN_API_KEY else 'OFFLINE'}")

        while True:
            try:
                await self._connect_and_serve()
            except Exception as e:
                self.state = ConnectionState.RECONNECTING
                log.warning(f"Connection lost: {e}. Reconnecting in {self.reconnect_delay}s...")
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay = min(self.reconnect_delay * WS_RECONNECT_FACTOR, WS_RECONNECT_MAX)

    async def _connect_and_serve(self):
        try:
            import websockets
        except ImportError:
            log.warning("websockets not installed. Running STANDALONE mode.")
            await self._standalone_mode()
            return

        self.state = ConnectionState.CONNECTING
        try:
            async with websockets.connect(
                WS_URL, extra_headers={"Sec-WebSocket-Protocol": "openclaw-node"}
            ) as ws:
                self.ws = ws
                self.state = ConnectionState.CONNECTED
                self.reconnect_delay = WS_RECONNECT_MIN  # Reset backoff on success
                self._uptime_start = datetime.now()
                log.info("✅ Neural link established with OpenClaw Gateway!")

                await ws.send(json.dumps({
                    "type": "node.hello",
                    "payload": {
                        "id": "titan_brain",
                        "name": "TITAN Engine Brain v2.0",
                        "version": "2.0",
                        "capabilities": ["brain", "cognitive", "beast_mode",
                                         "news_scraper", "codemint", "publisher"],
                    }
                }))

                # Start heartbeat
                self._ping_task = asyncio.create_task(self._heartbeat(ws))
                # Flush any buffered messages
                asyncio.create_task(self._flush_buffer(ws))

                async for message in ws:
                    await self._handle_event(ws, message)

        except (ConnectionRefusedError, OSError):
            log.warning("Gateway unavailable. Falling back to standalone.")
            await self._standalone_mode()

    async def _heartbeat(self, ws):
        """Send periodic pings to detect dead connections."""
        while True:
            try:
                await asyncio.sleep(WS_PING_INTERVAL)
                pong = await ws.ping()
                await asyncio.wait_for(pong, timeout=WS_PING_TIMEOUT)
                log.debug("💓 Heartbeat OK")
            except Exception:
                log.warning("💔 Heartbeat failed! Connection may be dead.")
                await ws.close()
                break

    async def _flush_buffer(self, ws):
        """Send any messages that were buffered during reconnection."""
        while not self.message_buffer.empty():
            msg = self.message_buffer.get_nowait()
            await ws.send(msg)
            self.total_messages_out += 1
            log.info(f"📤 Flushed buffered message")

    async def _send(self, ws, data: dict):
        """Send a message, buffering if disconnected."""
        msg = json.dumps(data)
        if self.state == ConnectionState.CONNECTED and ws and ws.open:
            await ws.send(msg)
            self.total_messages_out += 1
        else:
            try:
                self.message_buffer.put_nowait(msg)
                log.info("📦 Message buffered (WS disconnected)")
            except asyncio.QueueFull:
                log.warning("⚠️ Message buffer full, dropping message")

    async def _handle_event(self, ws, raw_message: str):
        try:
            data = json.loads(raw_message)
        except json.JSONDecodeError:
            return

        event_type = data.get("type", "unknown")
        self.total_messages_in += 1

        if event_type in ("message.inbound", "session.message"):
            payload = data.get("payload", {})
            user_text = payload.get("content") or payload.get("text") or ""
            sender = payload.get("from") or payload.get("senderId") or "unknown"
            channel = payload.get("channel", "cli")
            log.info(f"💬 [{channel}] {sender}: {user_text}")

            # THINK
            actions = self.brain.think(user_text)

            # ACT (through orchestrator with circuit breakers)
            results = []
            for action in actions:
                tool = action.get("tool", "reply")
                args = action.get("args", {})
                result = await self.orchestrator.submit(tool, args)
                results.append(result)

            # RESPOND
            final = "\n\n".join(results)
            await self._send(ws, {
                "type": "message.outbound",
                "payload": {"to": sender, "channel": channel, "content": f"🧠 TITAN:\n{final}"}
            })

        elif event_type == "ping":
            await self._send(ws, {"type": "pong"})

    async def _standalone_mode(self):
        log.info("=" * 50)
        log.info("🧠 TITAN Brain v2.0 — STANDALONE MODE")
        log.info("   Type commands below. Ctrl+C to exit.")
        log.info("=" * 50)

        loop = asyncio.get_event_loop()
        while True:
            try:
                user_input = await loop.run_in_executor(None, lambda: input("\n[You] > "))
                if not user_input.strip():
                    continue
                actions = self.brain.think(user_input)
                for action in actions:
                    result = await self.orchestrator.submit(
                        action.get("tool", "reply"), action.get("args", {}))
                    print(f"\n🧠 [{action.get('tool')}] {result}")
            except (EOFError, KeyboardInterrupt):
                break

    def get_status(self) -> dict:
        uptime = str(datetime.now() - self._uptime_start) if self._uptime_start else "N/A"
        return {
            "state": self.state,
            "uptime": uptime,
            "reconnect_delay": self.reconnect_delay,
            "messages_in": self.total_messages_in,
            "messages_out": self.total_messages_out,
            "buffer_size": self.message_buffer.qsize(),
        }


# ---------------------------------------------------------------------------
# HTTP Health Endpoint (runs in a thread)
# ---------------------------------------------------------------------------
_global_status = {}

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "version": "2.0"}).encode())
        elif self.path == "/metrics":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(_global_status, default=str, ensure_ascii=False).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress HTTP logs


def _start_health_server():
    try:
        server = HTTPServer(("0.0.0.0", BRAIN_HEALTH_PORT), HealthHandler)
        log.info(f"🏥 Health endpoint: http://localhost:{BRAIN_HEALTH_PORT}/health")
        server.serve_forever()
    except OSError as e:
        log.warning(f"Health server failed to start: {e}")


# ---------------------------------------------------------------------------
# Beast Mode Scheduler
# ---------------------------------------------------------------------------
class BeastModeScheduler:
    def __init__(self, brain: TitanBrain, orchestrator: ToolOrchestrator):
        self.brain = brain
        self.orchestrator = orchestrator

    async def run_daily_pipeline(self):
        log.info("🔥 BEAST MODE ACTIVATED")
        steps = [
            {"tool": "news_scraper", "args": {}},
            {"tool": "codemint", "args": {"topic": "auto-selected"}},
            {"tool": "publisher", "args": {"platform": "xhs"}},
        ]
        results = []
        for step in steps:
            result = await self.orchestrator.submit(step["tool"], step["args"])
            results.append(f"[{step['tool']}] {result[:200]}")
            log.info(result[:200])
        return "\n".join(results)

    async def schedule_loop(self):
        while True:
            now = datetime.now()
            target = now.replace(hour=BEAST_MODE_HOUR, minute=BEAST_MODE_MINUTE, second=0)
            if now >= target:
                target += timedelta(days=1)
            wait = (target - now).total_seconds()
            log.info(f"⏰ Beast Mode at {target:%Y-%m-%d %H:%M} (in {wait/3600:.1f}h)")
            await asyncio.sleep(wait)
            await self.run_daily_pipeline()


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
async def main():
    global _global_status

    # Start health server in background thread
    health_thread = threading.Thread(target=_start_health_server, daemon=True)
    health_thread.start()

    brain = TitanBrain()
    executor = ToolExecutor()
    orchestrator = ToolOrchestrator(executor_fn=executor.execute)
    await orchestrator.start()

    connector = RobustWSConnector(brain, orchestrator)
    scheduler = BeastModeScheduler(brain, orchestrator)

    # Periodically update global status for health endpoint
    async def update_metrics():
        while True:
            _global_status = {
                "timestamp": datetime.now().isoformat(),
                "brain": brain.get_status(),
                "connection": connector.get_status(),
                "orchestrator": orchestrator.get_health(),
            }
            await asyncio.sleep(5)

    await asyncio.gather(
        connector.run(),
        scheduler.schedule_loop(),
        update_metrics(),
    )


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════╗
    ║     🧠 TITAN Brain Server v2.0                   ║
    ║     Production Hardened 🦞                        ║
    ╠══════════════════════════════════════════════════╣
    ║  ✅ Robust WebSocket (heartbeat + reconnect)      ║
    ║  ✅ Circuit Breakers (per-tool fault isolation)    ║
    ║  ✅ Memory Cap (OOM prevention)                   ║
    ║  ✅ Health Endpoint (http://localhost:8080)        ║
    ╚══════════════════════════════════════════════════╝
    """)

    # Graceful shutdown
    def _shutdown(sig, frame):
        print("\n[TITAN] Graceful shutdown initiated... 🧠💤")
        sys.exit(0)
    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    asyncio.run(main())
