"""
╔══════════════════════════════════════════════════════════════╗
║  TITAN Gateway v1.0 — WebSocket + HTTP Control Plane         ║
║  Replaces OpenClaw's Gateway with a lightweight Python       ║
║  equivalent focused on TITAN's actual needs                  ║
║                                                              ║
║  Features:                                                    ║
║  • HTTP API (health, metrics, jobs, send, forge, skills)     ║
║  • WebSocket for real-time dashboard & CLI connections        ║
║  • Unified entry point: one process runs everything          ║
╚══════════════════════════════════════════════════════════════╝

Requires: pip install aiohttp
"""

import os
import sys
import json
import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Set

log = logging.getLogger("titan_gateway")

sys.path.insert(0, os.path.dirname(__file__))
from titan_config import FORGE_DIR, LOG_DIR

# ---------------------------------------------------------------------------
# Metrics Collector
# ---------------------------------------------------------------------------
class Metrics:
    def __init__(self):
        self.start_time = datetime.now()
        self.requests_total = 0
        self.ws_connections = 0
        self.jobs_run = 0
        self.messages_sent = 0
        self.errors = 0

    def snapshot(self) -> dict:
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            "uptime_seconds": round(uptime),
            "uptime_human": f"{int(uptime//3600)}h {int((uptime%3600)//60)}m",
            "requests_total": self.requests_total,
            "ws_connections": self.ws_connections,
            "jobs_run": self.jobs_run,
            "messages_sent": self.messages_sent,
            "errors": self.errors,
            "started_at": self.start_time.isoformat(),
        }


# ---------------------------------------------------------------------------
# Gateway Server
# ---------------------------------------------------------------------------
class TitanGateway:
    """
    Unified control plane for the TITAN Engine.

    Start with:
        gateway = TitanGateway()
        await gateway.start(host="0.0.0.0", port=18790)
    """

    def __init__(self):
        self.metrics = Metrics()
        self._ws_clients: Set = set()
        self._app = None
        self._channels = None
        self._skills = None
        self._daemon = None

    def attach_channels(self, channels):
        """Attach TitanChannels for message routing."""
        self._channels = channels

    def attach_skills(self, skills):
        """Attach SkillRegistry for skill execution."""
        self._skills = skills

    async def start(self, host: str = "0.0.0.0", port: int = 18790):
        try:
            from aiohttp import web
        except ImportError:
            log.error("❌ aiohttp not installed. Run: pip install aiohttp")
            # Fallback: simple HTTP server
            await self._fallback_server(host, port)
            return

        app = web.Application()
        app.router.add_get("/", self._handle_root)
        app.router.add_get("/health", self._handle_health)
        app.router.add_get("/metrics", self._handle_metrics)
        app.router.add_get("/api/channels", self._handle_channels)
        app.router.add_get("/api/skills", self._handle_skills)
        app.router.add_post("/api/send", self._handle_send)
        app.router.add_post("/api/skill/run", self._handle_skill_run)
        app.router.add_get("/ws", self._handle_ws)

        self._app = app

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()

        log.info(f"🔌 TITAN Gateway running on http://{host}:{port}")
        log.info(f"   Health:  http://localhost:{port}/health")
        log.info(f"   Metrics: http://localhost:{port}/metrics")
        log.info(f"   WS:      ws://localhost:{port}/ws")

        # Keep running
        await asyncio.Event().wait()

    # ─── HTTP Handlers ────────────────────────────────────

    async def _handle_root(self, request):
        from aiohttp import web
        self.metrics.requests_total += 1
        return web.json_response({
            "name": "TITAN Gateway",
            "version": "1.0.0",
            "endpoints": ["/health", "/metrics", "/api/channels", "/api/skills", "/api/send", "/api/skill/run", "/ws"],
        })

    async def _handle_health(self, request):
        from aiohttp import web
        self.metrics.requests_total += 1
        return web.json_response({
            "status": "ok",
            "service": "titan-gateway",
            "version": "1.0.0",
            "uptime": self.metrics.snapshot()["uptime_human"],
            "ws_clients": len(self._ws_clients),
        })

    async def _handle_metrics(self, request):
        from aiohttp import web
        self.metrics.requests_total += 1
        return web.json_response(self.metrics.snapshot())

    async def _handle_channels(self, request):
        from aiohttp import web
        self.metrics.requests_total += 1
        if self._channels:
            return web.json_response(self._channels.status())
        return web.json_response({"error": "channels not attached"}, status=503)

    async def _handle_skills(self, request):
        from aiohttp import web
        self.metrics.requests_total += 1
        if self._skills:
            return web.json_response({"skills": self._skills.list_all()})
        return web.json_response({"error": "skills not attached"}, status=503)

    async def _handle_send(self, request):
        from aiohttp import web
        self.metrics.requests_total += 1
        try:
            body = await request.json()
            channel = body.get("channel", "")
            message = body.get("message", "")
            if not channel or not message:
                return web.json_response({"error": "missing channel or message"}, status=400)
            if self._channels:
                result = await self._channels.send(channel, message)
                self.metrics.messages_sent += 1
                return web.json_response(result)
            return web.json_response({"error": "channels not attached"}, status=503)
        except Exception as e:
            self.metrics.errors += 1
            return web.json_response({"error": str(e)}, status=500)

    async def _handle_skill_run(self, request):
        from aiohttp import web
        self.metrics.requests_total += 1
        try:
            body = await request.json()
            skill_name = body.get("skill", "")
            context = body.get("context", {})
            if not skill_name:
                return web.json_response({"error": "missing skill name"}, status=400)
            if self._skills:
                result = await self._skills.execute(skill_name, context)
                self.metrics.jobs_run += 1
                return web.json_response(result)
            return web.json_response({"error": "skills not attached"}, status=503)
        except Exception as e:
            self.metrics.errors += 1
            return web.json_response({"error": str(e)}, status=500)

    # ─── WebSocket Handler ────────────────────────────────

    async def _handle_ws(self, request):
        from aiohttp import web
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self._ws_clients.add(ws)
        self.metrics.ws_connections += 1
        log.info(f"🔗 WebSocket client connected (total: {len(self._ws_clients)})")

        # Send welcome
        await ws.send_json({
            "type": "welcome",
            "message": "Connected to TITAN Gateway v1.0",
            "metrics": self.metrics.snapshot(),
        })

        try:
            async for msg in ws:
                if msg.type == 1:  # TEXT
                    try:
                        data = json.loads(msg.data)
                        response = await self._handle_ws_message(data)
                        await ws.send_json(response)
                    except json.JSONDecodeError:
                        await ws.send_json({"error": "invalid JSON"})
                elif msg.type in (8, 256):  # CLOSE, ERROR
                    break
        finally:
            self._ws_clients.discard(ws)
            log.info(f"🔌 WebSocket client disconnected (remaining: {len(self._ws_clients)})")

        return ws

    async def _handle_ws_message(self, data: dict) -> dict:
        """Handle incoming WebSocket messages."""
        action = data.get("action", "")

        if action == "ping":
            return {"type": "pong", "ts": datetime.now().isoformat()}

        elif action == "status":
            return {"type": "status", "metrics": self.metrics.snapshot()}

        elif action == "send":
            channel = data.get("channel", "")
            message = data.get("message", "")
            if self._channels and channel and message:
                result = await self._channels.send(channel, message)
                self.metrics.messages_sent += 1
                return {"type": "send_result", "result": result}
            return {"type": "error", "message": "missing channel/message or channels not attached"}

        elif action == "skill":
            skill_name = data.get("skill", "")
            if self._skills and skill_name:
                result = await self._skills.execute(skill_name, data.get("context", {}))
                self.metrics.jobs_run += 1
                return {"type": "skill_result", "result": result}
            return {"type": "error", "message": "missing skill or skills not attached"}

        elif action == "skills_list":
            if self._skills:
                return {"type": "skills_list", "skills": self._skills.list_all()}
            return {"type": "error", "message": "skills not attached"}

        else:
            return {"type": "error", "message": f"unknown action: {action}"}

    async def broadcast(self, data: dict):
        """Broadcast a message to all connected WebSocket clients."""
        dead = set()
        for ws in self._ws_clients:
            try:
                await ws.send_json(data)
            except Exception:
                dead.add(ws)
        self._ws_clients -= dead

    # ─── Fallback HTTP Server ─────────────────────────────

    async def _fallback_server(self, host: str, port: int):
        """Simple fallback when aiohttp is not available."""
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import threading

        gw = self

        class FallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                gw.metrics.requests_total += 1
                if self.path == "/health":
                    self._json(200, {"status": "ok", "service": "titan-gateway-fallback"})
                elif self.path == "/metrics":
                    self._json(200, gw.metrics.snapshot())
                else:
                    self._json(200, {"name": "TITAN Gateway (fallback)", "tip": "Install aiohttp for full features"})

            def _json(self, code, data):
                body = json.dumps(data, ensure_ascii=False).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        server = HTTPServer((host, port), FallbackHandler)
        log.info(f"🔌 TITAN Gateway (fallback) on http://{host}:{port}")
        server.serve_forever()


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
async def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
                        datefmt="%H:%M:%S")

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 18790

    gateway = TitanGateway()

    # Auto-attach channels if available
    try:
        from titan_channels import TitanChannels
        channels = TitanChannels()
        gateway.attach_channels(channels)
        log.info(f"📱 Channels attached: {channels.available}")
    except Exception as e:
        log.warning(f"⚠️  Could not attach channels: {e}")

    # Auto-attach skills if available
    try:
        from titan_skills import SkillRegistry
        skills = SkillRegistry()
        gateway.attach_skills(skills)
        log.info(f"🔧 Skills attached: {[s['name'] for s in skills.list_all()]}")
    except Exception as e:
        log.warning(f"⚠️  Could not attach skills: {e}")

    await gateway.start(port=port)


if __name__ == "__main__":
    asyncio.run(main())
