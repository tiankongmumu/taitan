"""
TITAN Engine — Bot Server (飞书 Webhook)
=========================================
Flask server that receives Feishu webhook events and routes them
to TITAN bot commands.

Usage:
  python titan_bot_server.py                    # Start on port 9000
  python titan_bot_server.py --port 8080        # Custom port
  python titan_bot_server.py --tunnel            # Auto-start ngrok tunnel

Env vars needed:
  FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_VERIFICATION_TOKEN
"""
import os
import sys
import json
import argparse
import hashlib
import threading
from typing import Set

# Flask import with helpful error
try:
    from flask import Flask, request, jsonify
except ImportError:
    print("❌ Flask not installed. Run: pip install flask")
    sys.exit(1)

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger
import feishu_client as feishu
import bot_commands as commands

log = get_logger("bot_server")

app = Flask(__name__)

# Deduplicate events (Feishu may send duplicates)
_processed_events: Set[str] = set()
_MAX_CACHE = 1000


def _dedup(event_id: str) -> bool:
    """Return True if already processed."""
    if event_id in _processed_events:
        return True
    _processed_events.add(event_id)
    if len(_processed_events) > _MAX_CACHE:
        # Trim oldest half
        to_remove = list(_processed_events)[:_MAX_CACHE // 2]
        for r in to_remove:
            _processed_events.discard(r)
    return False


@app.route("/", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "engine": "TITAN Bot Server v5.0",
        "feishu_configured": bool(os.environ.get("FEISHU_APP_ID")),
    })


@app.route("/webhook/feishu", methods=["POST"])
def feishu_webhook():
    """Main Feishu event callback endpoint."""
    body = request.get_json(force=True)

    # Step 1: URL verification (challenge-response)
    challenge = feishu.verify_event(body)
    if challenge is not None:
        log.info(f"🔐 URL verification challenge received")
        return jsonify({"challenge": challenge})

    # Step 2: Extract event
    header = body.get("header", {})
    event = body.get("event", {})
    event_id = header.get("event_id", "")
    event_type = header.get("event_type", "")

    # Deduplicate
    if event_id and _dedup(event_id):
        log.info(f"⏭ Skipped duplicate event: {event_id[:16]}")
        return jsonify({"code": 0})

    log.info(f"📨 Event: {event_type} | ID: {event_id[:16]}")

    # Step 3: Handle message events
    if event_type == "im.message.receive_v1":
        message = event.get("message", {})
        msg_type = message.get("message_type", "")
        message_id = message.get("message_id", "")
        
        # Only handle text messages
        if msg_type == "text":
            content = json.loads(message.get("content", "{}"))
            text = content.get("text", "").strip()

            if not text:
                return jsonify({"code": 0})

            # Remove @bot mention prefix
            text = text.lstrip("@_user_1 ").strip()
            if not text:
                text = "/help"

            log.info(f"💬 Message: '{text[:50]}' | ID: {message_id[:16]}")

            # Route in background to avoid 3s timeout
            thread = threading.Thread(
                target=commands.route,
                args=(message_id, text),
                daemon=True
            )
            thread.start()

        return jsonify({"code": 0})

    # Other events: log and ignore
    log.info(f"  ℹ Unhandled event type: {event_type}")
    return jsonify({"code": 0})


@app.route("/webhook/test", methods=["POST"])
def test_webhook():
    """Test endpoint for local development (no Feishu needed).
    POST {"text": "你的消息"}
    """
    body = request.get_json(force=True)
    text = body.get("text", "")
    if not text:
        return jsonify({"error": "missing 'text' field"})

    cmd, args = commands.parse_command(text)
    log.info(f"🧪 Test: '{text}' → cmd={cmd}")

    # For test mode, just return parsed info + file data
    result = {"command": cmd, "args": args}

    if cmd == "/status":
        match_file = os.path.join(commands.SIGNALS_DIR, "affiliate_matches.json")
        if os.path.exists(match_file):
            with open(match_file, "r", encoding="utf-8") as f:
                result["matches"] = json.load(f)

    elif cmd == "/xhs":
        latest = os.path.join(commands.SOCIAL_DIR, "cn_payload_latest.json")
        if os.path.exists(latest):
            with open(latest, "r", encoding="utf-8") as f:
                payload = json.load(f)
            result["xiaohongshu_posts"] = payload.get("xiaohongshu_posts", [])

    elif cmd == "/zhihu":
        latest = os.path.join(commands.SOCIAL_DIR, "cn_payload_latest.json")
        if os.path.exists(latest):
            with open(latest, "r", encoding="utf-8") as f:
                payload = json.load(f)
            result["zhihu_answers"] = payload.get("zhihu_answers", [])

    return jsonify(result)


def main():
    parser = argparse.ArgumentParser(description="TITAN Bot Server")
    parser.add_argument("--port", type=int, default=9000, help="Server port")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    args = parser.parse_args()

    print(f"""
╔══════════════════════════════════════════╗
║   🤖 TITAN Bot Server v5.0              ║
║   Port: {args.port:<33}║
║   Webhook: /webhook/feishu               ║
║   Test:    /webhook/test                 ║
║   Health:  /                             ║
╚══════════════════════════════════════════╝
""")

    # Check config
    if not os.environ.get("FEISHU_APP_ID"):
        print("⚠️  FEISHU_APP_ID not set. Set env vars or use /webhook/test endpoint.\n")

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
