"""
TITAN Engine — Feishu (飞书) Bot Client
========================================
Handles all communication with Feishu Open Platform API:
  - Event verification (challenge-response)
  - Receiving messages from users
  - Sending text/card/rich-text replies
  - Token management (tenant_access_token)

Requires: FEISHU_APP_ID + FEISHU_APP_SECRET in environment or titan_config.
"""
import os
import sys
import json
import time
import hashlib
import hmac
import requests
from typing import Dict, Optional

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger

log = get_logger("feishu_client")

# ─── Config ───────────────────────────────────────────────
FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
FEISHU_VERIFICATION_TOKEN = os.environ.get("FEISHU_VERIFICATION_TOKEN", "")
FEISHU_ENCRYPT_KEY = os.environ.get("FEISHU_ENCRYPT_KEY", "")

BASE_URL = "https://open.feishu.cn/open-apis"

# Token cache
_token_cache = {"token": "", "expires": 0}


def get_tenant_access_token() -> str:
    """Get or refresh tenant_access_token."""
    now = time.time()
    if _token_cache["token"] and _token_cache["expires"] > now:
        return _token_cache["token"]

    url = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }, timeout=10)

    data = resp.json()
    if data.get("code") == 0:
        token = data["tenant_access_token"]
        expire = data.get("expire", 7200)
        _token_cache["token"] = token
        _token_cache["expires"] = now + expire - 300  # 5min buffer
        log.info(f"🔑 Got tenant_access_token (expires in {expire}s)")
        return token
    else:
        log.error(f"Failed to get token: {data}")
        return ""


def _headers() -> Dict:
    """Build authorization headers."""
    return {
        "Authorization": f"Bearer {get_tenant_access_token()}",
        "Content-Type": "application/json; charset=utf-8"
    }


# ─── Send Messages ───────────────────────────────────────

def send_text(chat_id: str, text: str, msg_type: str = "open_id") -> bool:
    """Send a plain text message to a user or chat."""
    url = f"{BASE_URL}/im/v1/messages?receive_id_type={msg_type}"
    body = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    try:
        resp = requests.post(url, headers=_headers(), json=body, timeout=10)
        data = resp.json()
        if data.get("code") == 0:
            log.info(f"📤 Sent text to {chat_id[:10]}...")
            return True
        else:
            log.error(f"Send failed: {data.get('msg', '')}")
            return False
    except Exception as e:
        log.error(f"Send error: {e}")
        return False


def reply_text(message_id: str, text: str) -> bool:
    """Reply to a specific message."""
    url = f"{BASE_URL}/im/v1/messages/{message_id}/reply"
    body = {
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    try:
        resp = requests.post(url, headers=_headers(), json=body, timeout=10)
        data = resp.json()
        if data.get("code") == 0:
            log.info(f"↩️ Replied to {message_id[:10]}...")
            return True
        else:
            log.error(f"Reply failed: {data.get('msg', '')}")
            return False
    except Exception as e:
        log.error(f"Reply error: {e}")
        return False


def send_card(chat_id: str, card: Dict, msg_type: str = "open_id") -> bool:
    """Send an interactive card message."""
    url = f"{BASE_URL}/im/v1/messages?receive_id_type={msg_type}"
    body = {
        "receive_id": chat_id,
        "msg_type": "interactive",
        "content": json.dumps(card)
    }
    try:
        resp = requests.post(url, headers=_headers(), json=body, timeout=10)
        data = resp.json()
        if data.get("code") == 0:
            log.info(f"🃏 Sent card to {chat_id[:10]}...")
            return True
        else:
            log.error(f"Card send failed: {data.get('msg', '')}")
            return False
    except Exception as e:
        log.error(f"Card error: {e}")
        return False


def reply_card(message_id: str, card: Dict) -> bool:
    """Reply with an interactive card."""
    url = f"{BASE_URL}/im/v1/messages/{message_id}/reply"
    body = {
        "msg_type": "interactive",
        "content": json.dumps(card)
    }
    try:
        resp = requests.post(url, headers=_headers(), json=body, timeout=10)
        return resp.json().get("code") == 0
    except Exception as e:
        log.error(f"Card reply error: {e}")
        return False


# ─── Card Builders ────────────────────────────────────────

def build_status_card(title: str, items: list, color: str = "blue") -> Dict:
    """Build a status report card.
    Args:
        title: Card header title
        items: List of {"label": "...", "value": "..."} dicts
        color: Header color (blue/green/red/orange)
    """
    elements = []
    for item in items:
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**{item['label']}**：{item['value']}"
            }
        })
    elements.append({"tag": "hr"})
    elements.append({
        "tag": "note",
        "elements": [{"tag": "plain_text", "content": "🤖 TITAN Engine v5.0"}]
    })

    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "template": color
        },
        "elements": elements
    }


def build_content_card(title: str, content_text: str, url: str = "") -> Dict:
    """Build a content preview card with optional link."""
    elements = [
        {
            "tag": "div",
            "text": {"tag": "lark_md", "content": content_text}
        }
    ]
    if url:
        elements.append({
            "tag": "action",
            "actions": [{
                "tag": "button",
                "text": {"tag": "plain_text", "content": "查看完整内容"},
                "url": url,
                "type": "primary"
            }]
        })
    elements.append({
        "tag": "note",
        "elements": [{"tag": "plain_text", "content": "🤖 TITAN Engine v5.0"}]
    })

    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "template": "purple"
        },
        "elements": elements
    }


# ─── Event Verification ──────────────────────────────────

def verify_event(body: Dict) -> Optional[str]:
    """Handle Feishu event verification (challenge-response).
    Returns challenge string if this is a verification request, None otherwise.
    """
    if body.get("type") == "url_verification":
        return body.get("challenge", "")
    return None


def verify_signature(timestamp: str, nonce: str, body: str, signature: str) -> bool:
    """Verify event callback signature."""
    if not FEISHU_ENCRYPT_KEY:
        return True  # Skip if no encrypt key configured

    bytes_b = (timestamp + nonce + FEISHU_ENCRYPT_KEY).encode("utf-8")
    bytes_b1 = body.encode("utf-8")
    h = hashlib.sha256(bytes_b + bytes_b1)
    return h.hexdigest() == signature


if __name__ == "__main__":
    print("✅ Feishu client module loaded")
    print(f"   App ID configured: {'✅' if FEISHU_APP_ID else '❌'}")
    print(f"   App Secret configured: {'✅' if FEISHU_APP_SECRET else '❌'}")
