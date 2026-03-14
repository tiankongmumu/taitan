"""
TITAN Pipeline — Stage 6: Auto Publisher (CN Edition)
======================================================
Generates distribution content for Chinese social platforms:
  - 小红书 种草笔记
  - 知乎 回答/文章
  - 公众号 文章
  - 微博 短文

Input:  demand_signals/affiliate_matches.json
Output: social_posts/cn_payload_*.json
"""
import os
import sys
import json
import time
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger
from core_generators.llm_client import LLMClient

log = get_logger("auto_publisher")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNALS_DIR = os.path.join(BASE_DIR, "demand_signals")
INPUT_FILE = os.path.join(SIGNALS_DIR, "affiliate_matches.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "social_posts")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_xiaohongshu(llm: LLMClient, match: Dict) -> Dict:
    """Generate a 小红书 style product recommendation note."""
    pain = match.get("pain_summary", match.get("pain_keyword", ""))
    product = match.get("product_name", "")
    url = match.get("affiliate_url", "")

    prompt = f"""写一篇小红书风格的种草笔记。

痛点：{pain}
推荐工具：{product}
链接：{url}

要求：
1. 标题要抓眼球，30字以内，加 emoji（参考：绝了！/破防了/后悔没早用/吐血整理）
2. 正文 200-300 字，口语化，用短句
3. 多用 emoji 分隔段落（🔥💡✅📌🎯）
4. 先说痛点（让人共鸣）→ 再说发现了什么好东西 → 具体怎么用 → 效果
5. 结尾加标签 #效率工具 #AI推荐 #打工人必备
6. 语气像在和闺蜜/好友分享，不要硬广

输出格式：
标题：xxx
正文：xxx"""

    response = llm.generate(prompt=prompt, system_prompt="你是一位拥有10万粉丝的小红书科技博主。")

    if not response:
        return {"title": f"后悔没早用！{product}真的太好了", "body": f"最近发现了{product}，解决了{pain}。推荐链接：{url}", "platform": "小红书"}

    lines = response.strip().split("\n")
    title = ""
    body_lines = []
    in_body = False
    for line in lines:
        if line.startswith("标题：") or line.startswith("标题:"):
            title = line.split("：", 1)[-1].split(":", 1)[-1].strip()
        elif line.startswith("正文：") or line.startswith("正文:"):
            in_body = True
            rest = line.split("：", 1)[-1].split(":", 1)[-1].strip()
            if rest:
                body_lines.append(rest)
        elif in_body:
            body_lines.append(line)

    return {
        "title": title or f"🔥 {product} — 效率翻倍神器",
        "body": "\n".join(body_lines).strip() or response,
        "platform": "小红书"
    }


def generate_zhihu(llm: LLMClient, match: Dict) -> Dict:
    """Generate a 知乎 style answer/article."""
    pain = match.get("pain_summary", match.get("pain_keyword", ""))
    product = match.get("product_name", "")
    url = match.get("affiliate_url", "")

    prompt = f"""写一段知乎风格的回答（300-400字）。

假设问题是："有什么好用的工具可以解决「{pain}」？"
推荐工具：{product}
链接：{url}

要求：
1. 开头先表示理解提问者的痛苦
2. 然后分享自己的亲身经历
3. 推荐工具时说清楚「为什么好用」「怎么用」
4. 数据或具体场景让回答更有说服力
5. 结尾自然带上链接
6. 语气：理性分析 + 个人体验，像一个认真的知乎答主

直接输出回答内容，不需要格式标记。"""

    response = llm.generate(prompt=prompt, system_prompt="你是一位在知乎有5万关注的科技领域答主。")

    return {
        "question": f"有什么好用的工具可以解决「{pain[:30]}」？",
        "answer": response.strip() if response else f"推荐试试 {product}，专门解决这个问题的。链接：{url}",
        "platform": "知乎"
    }


def generate_weibo(llm: LLMClient, matches: List[Dict]) -> str:
    """Generate a Weibo-style short post."""
    tools = "、".join([m.get("product_name", "") for m in matches[:3]])
    prompt = f"""写一条微博（140字以内）。

你是一个科技博主，要推荐今天发现的好工具：{tools}
语气轻松有趣，加 emoji，加 #话题标签#

直接输出微博内容。"""

    response = llm.generate(prompt=prompt, system_prompt="你是一位活跃的科技微博博主。")
    return response.strip() if response else f"今日好工具推荐：{tools} 🔥 #效率工具# #AI推荐#"


def publish(matches: List[Dict] = None) -> Dict:
    """Generate all Chinese distribution content."""
    log.info("=" * 50)
    log.info("📢 TITAN Auto Publisher v5.0 CN — Starting")
    log.info("=" * 50)

    # Load matches
    if matches is None:
        if not os.path.exists(INPUT_FILE):
            log.error(f"Input not found: {INPUT_FILE}")
            return {}
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            matches = json.load(f)

    log.info(f"📥 Input: {len(matches)} affiliate matches")
    llm = LLMClient()

    payload = {
        "generated_at": datetime.utcnow().isoformat(),
        "weibo": "",
        "xiaohongshu_posts": [],
        "zhihu_answers": [],
        "match_count": len(matches)
    }

    # 1. Weibo short post
    log.info("📱 生成微博...")
    payload["weibo"] = generate_weibo(llm, matches)

    # 2. 小红书 posts (top 3)
    log.info("📕 生成小红书种草笔记...")
    for i, match in enumerate(matches[:3], 1):
        log.info(f"  [{i}/3] {match.get('pain_keyword', '')}")
        post = generate_xiaohongshu(llm, match)
        payload["xiaohongshu_posts"].append(post)
        time.sleep(1)

    # 3. 知乎 answers (top 2)
    log.info("💡 生成知乎回答...")
    for i, match in enumerate(matches[:2], 1):
        log.info(f"  [{i}/2] {match.get('pain_keyword', '')}")
        answer = generate_zhihu(llm, match)
        payload["zhihu_answers"].append(answer)
        time.sleep(1)

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"cn_payload_{timestamp}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    latest_file = os.path.join(OUTPUT_DIR, "cn_payload_latest.json")
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    log.info(f"✅ Published → {output_file}")
    return payload


if __name__ == "__main__":
    result = publish()
    print(f"\n📱 微博:\n{result.get('weibo', '')}\n")
    for post in result.get("xiaohongshu_posts", []):
        print(f"📕 [小红书] {post['title']}")
    for ans in result.get("zhihu_answers", []):
        print(f"💡 [知乎] {ans['question']}")
