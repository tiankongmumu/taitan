"""
TITAN Engine — Bot Command Router
===================================
Parses user messages from Feishu and routes them to TITAN modules.
Supports slash commands and free-form AI chat.
"""
import os
import sys
import json
import re
import threading
from typing import Dict, Tuple, Optional

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger
from core_generators.llm_client import LLMClient
import feishu_client as feishu

log = get_logger("bot_commands")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNALS_DIR = os.path.join(BASE_DIR, "demand_signals")
SOCIAL_DIR = os.path.join(BASE_DIR, "social_posts")
CONTENT_DIR = os.path.join(BASE_DIR, "content_output")


# ─── Command Definitions ─────────────────────────────────

COMMANDS = {
    "/run":     "运行完整管线",
    "/status":  "查看管线状态",
    "/content": "查看最新生成内容",
    "/match":   "查看联盟匹配结果",
    "/xhs":     "查看小红书文案",
    "/zhihu":   "查看知乎回答",
    "/help":    "显示帮助信息",
}

# Chinese command aliases
CN_ALIASES = {
    "跑管线": "/run", "运行": "/run", "跑一次": "/run", "开始": "/run",
    "状态": "/status", "报告": "/status", "今日报告": "/status",
    "内容": "/content", "文章": "/content",
    "匹配": "/match", "产品": "/match",
    "小红书": "/xhs", "种草": "/xhs",
    "知乎": "/zhihu", "回答": "/zhihu",
    "帮助": "/help", "help": "/help",
}


def parse_command(text: str) -> Tuple[str, str]:
    """Parse user message into (command, args).
    Returns ('/chat', original_text) for free-form messages.
    """
    text = text.strip()

    # Direct slash command
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        if cmd in COMMANDS:
            return cmd, args
        return "/chat", text

    # Chinese alias matching
    for alias, cmd in CN_ALIASES.items():
        if alias in text:
            return cmd, text
    
    # Default: AI chat
    return "/chat", text


# ─── Command Handlers ────────────────────────────────────

def handle_help(message_id: str, args: str) -> None:
    """Show available commands."""
    lines = ["🤖 **TITAN Engine 指令列表**\n"]
    for cmd, desc in COMMANDS.items():
        lines.append(f"• `{cmd}` — {desc}")
    lines.append("\n💬 也可以直接用中文对话，例如：")
    lines.append('• "跑一次管线"')
    lines.append('• "给我看小红书文案"')
    lines.append('• "分析一下 AI 市场趋势"')

    feishu.reply_text(message_id, "\n".join(lines))


def handle_status(message_id: str, args: str) -> None:
    """Show pipeline status and latest results."""
    items = []

    # Check affiliate matches
    match_file = os.path.join(SIGNALS_DIR, "affiliate_matches.json")
    if os.path.exists(match_file):
        with open(match_file, "r", encoding="utf-8") as f:
            matches = json.load(f)
        items.append({"label": "联盟匹配", "value": f"{len(matches)} 条"})
        top = matches[0] if matches else {}
        if top:
            items.append({"label": "最佳匹配", "value": f"{top.get('product_name', '')} ({top.get('match_score', 0)}分)"})
    else:
        items.append({"label": "联盟匹配", "value": "❌ 尚未运行"})

    # Check content
    if os.path.exists(CONTENT_DIR):
        md_files = [f for f in os.listdir(CONTENT_DIR) if f.endswith(".md")]
        items.append({"label": "文章数量", "value": f"{len(md_files)} 篇"})

    # Check social posts
    latest = os.path.join(SOCIAL_DIR, "cn_payload_latest.json")
    if os.path.exists(latest):
        with open(latest, "r", encoding="utf-8") as f:
            payload = json.load(f)
        xhs_count = len(payload.get("xiaohongshu_posts", []))
        zhihu_count = len(payload.get("zhihu_answers", []))
        items.append({"label": "小红书", "value": f"{xhs_count} 条待发"})
        items.append({"label": "知乎", "value": f"{zhihu_count} 条待发"})
        items.append({"label": "生成时间", "value": payload.get("generated_at", "未知")[:19]})
    else:
        items.append({"label": "社交文案", "value": "❌ 尚未生成"})

    card = feishu.build_status_card("📊 TITAN 管线状态", items, "blue")
    feishu.reply_card(message_id, card)


def handle_match(message_id: str, args: str) -> None:
    """Show affiliate match results."""
    match_file = os.path.join(SIGNALS_DIR, "affiliate_matches.json")
    if not os.path.exists(match_file):
        feishu.reply_text(message_id, "❌ 尚无匹配数据。发送 /run 运行管线。")
        return

    with open(match_file, "r", encoding="utf-8") as f:
        matches = json.load(f)

    items = []
    for m in matches:
        items.append({
            "label": f"{m.get('product_name', '')} ({m.get('match_score', 0)}分)",
            "value": f"{m.get('pain_keyword', '')} → {m.get('target_platform', '通用')}"
        })

    card = feishu.build_status_card("💰 联盟匹配结果", items, "green")
    feishu.reply_card(message_id, card)


def handle_xhs(message_id: str, args: str) -> None:
    """Show 小红书 content."""
    latest = os.path.join(SOCIAL_DIR, "cn_payload_latest.json")
    if not os.path.exists(latest):
        feishu.reply_text(message_id, "❌ 尚无小红书文案。发送 /run 运行管线。")
        return

    with open(latest, "r", encoding="utf-8") as f:
        payload = json.load(f)

    posts = payload.get("xiaohongshu_posts", [])
    if not posts:
        feishu.reply_text(message_id, "❌ 本次无小红书文案生成。")
        return

    for i, post in enumerate(posts, 1):
        title = post.get("title", f"笔记 {i}")
        body = post.get("body", "")[:300]
        content = f"**📕 笔记 {i}: {title}**\n\n{body}..."
        card = feishu.build_content_card(f"小红书文案 {i}/{len(posts)}", content)
        feishu.reply_card(message_id, card)


def handle_zhihu(message_id: str, args: str) -> None:
    """Show 知乎 answers."""
    latest = os.path.join(SOCIAL_DIR, "cn_payload_latest.json")
    if not os.path.exists(latest):
        feishu.reply_text(message_id, "❌ 尚无知乎文案。发送 /run 运行管线。")
        return

    with open(latest, "r", encoding="utf-8") as f:
        payload = json.load(f)

    answers = payload.get("zhihu_answers", [])
    if not answers:
        feishu.reply_text(message_id, "❌ 本次无知乎回答生成。")
        return

    for i, ans in enumerate(answers, 1):
        question = ans.get("question", "")
        answer = ans.get("answer", "")[:400]
        content = f"**❓ {question}**\n\n{answer}..."
        card = feishu.build_content_card(f"知乎回答 {i}/{len(answers)}", content)
        feishu.reply_card(message_id, card)


def handle_content(message_id: str, args: str) -> None:
    """Show latest generated articles."""
    index_file = os.path.join(CONTENT_DIR, "article_index.json")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            articles = json.load(f)
    elif os.path.exists(CONTENT_DIR):
        md_files = [f for f in os.listdir(CONTENT_DIR) if f.endswith(".md")]
        articles = [{"title": f.replace(".md", ""), "word_count": 0} for f in md_files]
    else:
        feishu.reply_text(message_id, "❌ 尚无文章。发送 /run 运行管线。")
        return

    items = []
    for a in articles:
        items.append({
            "label": a.get("title", "")[:40],
            "value": f"{a.get('word_count', '?')} 字 | {a.get('product', '通用')}"
        })

    card = feishu.build_status_card("📝 已生成文章", items, "purple")
    feishu.reply_card(message_id, card)


def handle_run(message_id: str, args: str) -> None:
    """Run the pipeline in background."""
    feishu.reply_text(message_id, "🚀 管线启动中... 预计 5-15 分钟完成。\n完成后会自动通知你。")

    def _run_pipeline():
        try:
            from titan_pipeline import run_pipeline
            result = run_pipeline(skip_collect="--skip-collect" not in args)
            
            # Send completion notification
            items = [
                {"label": "状态", "value": "✅ 完成"},
                {"label": "耗时", "value": f"{result.get('total_time', 0):.0f}s"},
                {"label": "错误", "value": str(result.get("errors", 0))}
            ]
            card = feishu.build_status_card("✅ 管线运行完成", items, "green")
            feishu.reply_card(message_id, card)
        except Exception as e:
            feishu.reply_text(message_id, f"❌ 管线运行失败: {str(e)[:200]}")

    thread = threading.Thread(target=_run_pipeline, daemon=True)
    thread.start()


def handle_chat(message_id: str, text: str) -> None:
    """Free-form AI chat — route to LLM."""
    try:
        llm = LLMClient()
        system = """你是 TITAN Engine 的 AI 助手，一个专注于 SaaS 市场分析和联盟营销的智能引擎。
你可以帮用户分析市场趋势、解答创业问题、提供营销建议。
回复简洁有力，像一个经验丰富的创业导师。
如果用户想操作管线，告诉他们可以发送 /help 查看指令。"""
        response = llm.generate(prompt=text, system_prompt=system)
        if response:
            feishu.reply_text(message_id, response.strip())
        else:
            feishu.reply_text(message_id, "🤔 抱歉，我暂时无法回复。请稍后再试。")
    except Exception as e:
        feishu.reply_text(message_id, f"⚠️ AI 回复异常: {str(e)[:100]}")


# ─── Router ──────────────────────────────────────────────

HANDLER_MAP = {
    "/help": handle_help,
    "/status": handle_status,
    "/match": handle_match,
    "/xhs": handle_xhs,
    "/zhihu": handle_zhihu,
    "/content": handle_content,
    "/run": handle_run,
    "/chat": handle_chat,
}


def route(message_id: str, text: str) -> None:
    """Route a message to the appropriate handler."""
    cmd, args = parse_command(text)
    handler = HANDLER_MAP.get(cmd, handle_chat)
    log.info(f"📨 Routing: '{text[:30]}...' → {cmd}")
    handler(message_id, args)


if __name__ == "__main__":
    # Test command parsing
    test_cases = [
        "/run", "/status", "跑一次管线", "给我看小红书文案",
        "帮我分析 AI 市场", "/help", "状态", "今天匹配了什么"
    ]
    for t in test_cases:
        cmd, args = parse_command(t)
        print(f"  '{t}' → cmd={cmd}, args='{args[:20]}'")
