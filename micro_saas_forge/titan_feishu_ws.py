"""
TITAN Engine — Feishu (飞书) Long Connection Listener
======================================================
Uses Feishu's WebSocket (Long Connection) to receive events without
needing a public IP or reverse proxy.

Requires: lark-oapi
"""
import os
import json
import logging
import lark_oapi as lark
from lark_oapi.api.im.v1 import P2ImMessageReceiveV1

import titan_config as config
import bot_commands as commands

# Configure logging
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger("feishu_ws")

# Load credentials from config
APP_ID = config.env("FEISHU_APP_ID")
APP_SECRET = config.env("FEISHU_APP_SECRET")

if not APP_ID or not APP_SECRET:
    log.error("❌ FEISHU_APP_ID or FEISHU_APP_SECRET not set in environment.")
    exit(1)

def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    """Handle message received events."""
    msg = data.event.message
    message_id = msg.message_id
    msg_type = msg.message_type
    
    if msg_type == "text":
        content_raw = msg.content
        content = json.loads(content_raw)
        text = content.get("text", "").strip()
        
        # Clean up @bot mentions
        # Note: If there's a specific bot name, it might need more precise stripping
        # but bot_commands.route already handles basic cleaning
        log.info(f"📨 Received message: '{text[:50]}' (ID: {message_id[:8]})")
        
        # Route to commands
        try:
            commands.route(message_id, text)
        except Exception as e:
            log.error(f"❌ Failed to route message: {e}")
    else:
        log.info(f"⏭ Ignored non-text message type: {msg_type}")

import asyncio

async def main():
    # Create event handler
    event_handler = lark.EventDispatcherHandler.builder("", "") \
        .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
        .build()

    # Create WS Client
    client = lark.ws.Client(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        event_handler=event_handler
    )
    
    log.info("🚀 Starting Feishu Long Connection (WebSocket)...")
    log.info("   Mode: Interactive command routing active.")
    
    # Start (this blocks)
    try:
        await client.start()
    except Exception as e:
        import traceback
        traceback.print_exc()
        log.error(f"❌ WebSocket Client failed: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
