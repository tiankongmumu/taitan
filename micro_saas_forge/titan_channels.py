"""
╔══════════════════════════════════════════════════════════════╗
║  TITAN Channels v1.0 — Unified Multi-Channel Messaging       ║
║  Replaces OpenClaw's 22-channel system with focused Python   ║
║                                                              ║
║  Supported channels:                                          ║
║  • 飞书 (Feishu)    — P0, wraps existing feishu_client.py    ║
║  • Telegram Bot     — P1, python-telegram-bot / requests     ║
║  • Discord Bot      — P2, discord.py / requests webhook      ║
║  • 企业微信 Webhook — P2, simple HTTP POST                    ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List

sys.path.insert(0, os.path.dirname(__file__))
from titan_config import FORGE_DIR

log = logging.getLogger("titan_channels")

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, "")  or default

# Channel credentials from environment
FEISHU_APP_ID       = _env("FEISHU_APP_ID")
FEISHU_APP_SECRET   = _env("FEISHU_APP_SECRET")
TELEGRAM_BOT_TOKEN  = _env("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID    = _env("TELEGRAM_CHAT_ID")
DISCORD_WEBHOOK_URL = _env("DISCORD_WEBHOOK_URL")
WECOM_WEBHOOK_URL   = _env("WECOM_WEBHOOK_URL")


# ---------------------------------------------------------------------------
# Channel Base Class
# ---------------------------------------------------------------------------
class Channel:
    """Base class for all messaging channels."""
    name: str = "base"
    enabled: bool = False

    async def send(self, message: str, **kwargs) -> dict:
        raise NotImplementedError

    async def send_card(self, title: str, body: str, url: str = "", **kwargs) -> dict:
        """Send a rich card message. Falls back to plain text."""
        return await self.send(f"**{title}**\n{body}\n{url}")

    def status(self) -> dict:
        return {"channel": self.name, "enabled": self.enabled}


# ---------------------------------------------------------------------------
# Feishu Channel
# ---------------------------------------------------------------------------
class FeishuChannel(Channel):
    name = "feishu"

    def __init__(self):
        self.enabled = bool(FEISHU_APP_ID and FEISHU_APP_SECRET)
        if self.enabled:
            try:
                import feishu_client
                self._client = feishu_client
            except ImportError:
                self.enabled = False
                log.warning("⚠️  feishu_client.py not importable")

    async def send(self, message: str, chat_id: str = "", **kwargs) -> dict:
        if not self.enabled:
            return {"ok": False, "error": "feishu not configured"}
        try:
            result = self._client.send_text(chat_id, message)
            return {"ok": True, "result": result}
        except Exception as e:
            log.error(f"Feishu send error: {e}")
            return {"ok": False, "error": str(e)}

    async def send_card(self, title: str, body: str, url: str = "", chat_id: str = "", **kwargs) -> dict:
        if not self.enabled:
            return {"ok": False, "error": "feishu not configured"}
        try:
            card = self._client.build_content_card(title, body, url)
            result = self._client.send_card(chat_id, card)
            return {"ok": True, "result": result}
        except Exception as e:
            log.error(f"Feishu card error: {e}")
            return {"ok": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Telegram Channel
# ---------------------------------------------------------------------------
class TelegramChannel(Channel):
    name = "telegram"

    def __init__(self):
        self.enabled = bool(TELEGRAM_BOT_TOKEN)
        self.base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}" if self.enabled else ""

    async def send(self, message: str, chat_id: str = "", **kwargs) -> dict:
        if not self.enabled:
            return {"ok": False, "error": "telegram not configured"}

        target = chat_id or TELEGRAM_CHAT_ID
        if not target:
            return {"ok": False, "error": "no chat_id specified"}

        try:
            import requests
            resp = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": target,
                    "text": message,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False,
                },
                timeout=10,
            )
            data = resp.json()
            return {"ok": data.get("ok", False), "result": data}
        except Exception as e:
            log.error(f"Telegram send error: {e}")
            return {"ok": False, "error": str(e)}

    async def send_card(self, title: str, body: str, url: str = "", **kwargs) -> dict:
        text = f"*{title}*\n\n{body}"
        if url:
            text += f"\n\n🔗 [查看详情]({url})"
        return await self.send(text, **kwargs)

    async def get_updates(self, offset: int = 0) -> list:
        """Fetch new messages (for polling-based listening)."""
        if not self.enabled:
            return []
        try:
            import requests
            resp = requests.get(
                f"{self.base_url}/getUpdates",
                params={"offset": offset, "timeout": 30, "limit": 10},
                timeout=35,
            )
            data = resp.json()
            return data.get("result", [])
        except Exception as e:
            log.error(f"Telegram getUpdates error: {e}")
            return []


# ---------------------------------------------------------------------------
# Discord Channel (Webhook-based, no bot required)
# ---------------------------------------------------------------------------
class DiscordChannel(Channel):
    name = "discord"

    def __init__(self):
        self.enabled = bool(DISCORD_WEBHOOK_URL)

    async def send(self, message: str, **kwargs) -> dict:
        if not self.enabled:
            return {"ok": False, "error": "discord not configured"}
        try:
            import requests
            resp = requests.post(
                DISCORD_WEBHOOK_URL,
                json={"content": message[:2000]},  # Discord limit
                timeout=10,
            )
            return {"ok": resp.status_code in (200, 204), "status": resp.status_code}
        except Exception as e:
            log.error(f"Discord send error: {e}")
            return {"ok": False, "error": str(e)}

    async def send_card(self, title: str, body: str, url: str = "", **kwargs) -> dict:
        embed = {
            "title": title,
            "description": body[:4096],
            "color": 0x7c3aed,  # Purple
            "timestamp": datetime.utcnow().isoformat(),
        }
        if url:
            embed["url"] = url
        try:
            import requests
            resp = requests.post(
                DISCORD_WEBHOOK_URL,
                json={"embeds": [embed]},
                timeout=10,
            )
            return {"ok": resp.status_code in (200, 204), "status": resp.status_code}
        except Exception as e:
            log.error(f"Discord card error: {e}")
            return {"ok": False, "error": str(e)}


# ---------------------------------------------------------------------------
# 企业微信 Channel (Webhook)
# ---------------------------------------------------------------------------
class WeComChannel(Channel):
    name = "wecom"

    def __init__(self):
        self.enabled = bool(WECOM_WEBHOOK_URL)

    async def send(self, message: str, **kwargs) -> dict:
        if not self.enabled:
            return {"ok": False, "error": "wecom not configured"}
        try:
            import requests
            resp = requests.post(
                WECOM_WEBHOOK_URL,
                json={
                    "msgtype": "text",
                    "text": {"content": message},
                },
                timeout=10,
            )
            data = resp.json()
            return {"ok": data.get("errcode") == 0, "result": data}
        except Exception as e:
            log.error(f"WeCom send error: {e}")
            return {"ok": False, "error": str(e)}

    async def send_card(self, title: str, body: str, url: str = "", **kwargs) -> dict:
        if not self.enabled:
            return {"ok": False, "error": "wecom not configured"}
        try:
            import requests
            card = {
                "msgtype": "markdown",
                "markdown": {
                    "content": f"## {title}\n{body}" + (f"\n[查看详情]({url})" if url else ""),
                },
            }
            resp = requests.post(WECOM_WEBHOOK_URL, json=card, timeout=10)
            data = resp.json()
            return {"ok": data.get("errcode") == 0, "result": data}
        except Exception as e:
            log.error(f"WeCom card error: {e}")
            return {"ok": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Unified Channel Router
# ---------------------------------------------------------------------------
class TitanChannels:
    """
    Unified messaging router — send to any channel with one call.

    Usage:
        channels = TitanChannels()
        await channels.send("feishu", "Hello from TITAN!")
        await channels.broadcast("System alert: something happened")
    """

    def __init__(self):
        self._channels: Dict[str, Channel] = {
            "feishu": FeishuChannel(),
            "telegram": TelegramChannel(),
            "discord": DiscordChannel(),
            "wecom": WeComChannel(),
        }
        self._listeners: List[Callable] = []

    @property
    def available(self) -> List[str]:
        return [name for name, ch in self._channels.items() if ch.enabled]

    def status(self) -> dict:
        return {
            name: ch.status()
            for name, ch in self._channels.items()
        }

    async def send(self, channel: str, message: str, **kwargs) -> dict:
        """Send a message to a specific channel."""
        ch = self._channels.get(channel)
        if not ch:
            return {"ok": False, "error": f"Unknown channel: {channel}"}
        if not ch.enabled:
            return {"ok": False, "error": f"Channel {channel} not configured"}
        return await ch.send(message, **kwargs)

    async def send_card(self, channel: str, title: str, body: str, url: str = "", **kwargs) -> dict:
        """Send a rich card to a specific channel."""
        ch = self._channels.get(channel)
        if not ch:
            return {"ok": False, "error": f"Unknown channel: {channel}"}
        if not ch.enabled:
            return {"ok": False, "error": f"Channel {channel} not configured"}
        return await ch.send_card(title, body, url, **kwargs)

    async def broadcast(self, message: str, **kwargs) -> Dict[str, dict]:
        """Send a message to ALL enabled channels."""
        results = {}
        for name, ch in self._channels.items():
            if ch.enabled:
                results[name] = await ch.send(message, **kwargs)
        return results

    async def broadcast_card(self, title: str, body: str, url: str = "", **kwargs) -> Dict[str, dict]:
        """Send a rich card to ALL enabled channels."""
        results = {}
        for name, ch in self._channels.items():
            if ch.enabled:
                results[name] = await ch.send_card(title, body, url, **kwargs)
        return results

    def on_message(self, callback: Callable):
        """Register a listener for incoming messages (polling-based)."""
        self._listeners.append(callback)

    async def poll_loop(self, interval: int = 5):
        """Poll Telegram for incoming messages and dispatch to listeners."""
        tg = self._channels.get("telegram")
        if not isinstance(tg, TelegramChannel) or not tg.enabled:
            log.warning("⚠️  Telegram not configured, polling disabled")
            return

        offset = 0
        log.info("📡 Starting Telegram polling loop...")
        while True:
            updates = await tg.get_updates(offset)
            for update in updates:
                offset = update.get("update_id", 0) + 1
                msg = update.get("message", {})
                text = msg.get("text", "")
                sender = msg.get("from", {}).get("first_name", "unknown")
                chat_id = str(msg.get("chat", {}).get("id", ""))

                log.info(f"📨 [{sender}] {text[:50]}")
                for cb in self._listeners:
                    try:
                        await cb(text=text, sender=sender, chat_id=chat_id, channel="telegram")
                    except Exception as e:
                        log.error(f"Listener error: {e}")

            await asyncio.sleep(interval)


# ---------------------------------------------------------------------------
# CLI / Test
# ---------------------------------------------------------------------------
async def _test():
    channels = TitanChannels()
    print("=" * 50)
    print("🧠 TITAN Channels v1.0 — Status")
    print("=" * 50)
    for name, info in channels.status().items():
        status = "✅ 已配置" if info["enabled"] else "❌ 未配置"
        print(f"  {name:12s} {status}")
    print(f"\n可用通道: {channels.available}")

    if channels.available:
        print(f"\n发送测试消息到: {channels.available[0]} ...")
        result = await channels.send(channels.available[0], "🧠 TITAN Engine v3.0 — 通道测试成功！")
        print(f"  结果: {result}")


if __name__ == "__main__":
    asyncio.run(_test())
