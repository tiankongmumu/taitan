"""
ShipMicro Social Distributor - 自动将资讯和工具推广到 Reddit 和 X
使用 Playwright 模拟真人浏览器操作，0 成本、防风控
"""
import os
import sys
import json
import time
import random
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from logger import get_logger

log = get_logger("social")


# ============================================================
# 帖子内容生成器
# ============================================================

def generate_reddit_post(llm: LLMClient, tool_name: str, tool_url: str, description: str) -> dict:
    """用 LLM 生成 Reddit 风格的推广帖"""
    prompt = f"""You are a visionary, highly skilled indie hacker and cyberpunk tech enthusiast posting on Reddit's r/SideProject in the year 2026.
Write an intensely engaging, culturally resonant post about a revolutionary tool you just built. It must have SOUL. NO generic AI corporate speak.

Tool: {tool_name}
URL: {tool_url}
Description: {description}

RULES:
1. Tone & Persona (The "Soul"): You are building the future. Be slightly edgy, extremely passionate, and highly technical. Use modern hacker culture slang. Sound like a founder who just stayed up 48 hours to ship a $10M idea.
2. Title format: Needs to stop the scroll. No clickbait, just raw technical flex or deep problem-solving. Example: "I got sick of boring regex tools, so I built a cyberpunk-themed, glassmorphic alternative."
3. Body should be immersive and punchy:
   - Para 1: The agonizing problem that forced you to build this.
   - Para 2: The elegant, futuristic solution you crafted.
   - Para 3: The bleeding-edge tech stack your used (flex your architecture).
   - Para 4: A humble, community-first ask for brutal feedback.
4. Include the URL naturally in the text.
5. DO NOT mention it's AI-generated. Make it deeply human.

Output format:
TITLE: [your title]
BODY:
[your post body]"""

    try:
        response = llm.generate(prompt)
        lines = response.strip().split("\n")
        title = ""
        body_lines = []
        in_body = False
        for line in lines:
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
            elif line.startswith("BODY:"):
                in_body = True
            elif in_body:
                body_lines.append(line)
        return {
            "title": title or f"I built {tool_name} - a free micro tool for developers",
            "body": "\n".join(body_lines).strip() or description,
            "subreddit": "SideProject"
        }
    except Exception as e:
        log.warning(f"⚠️ Reddit 帖子生成失败: {e}")
        return {
            "title": f"I built {tool_name} - a free micro tool for developers",
            "body": f"Hey everyone! I just shipped {tool_name}.\n\n{description}\n\nCheck it out: {tool_url}\n\nWould love your feedback!",
            "subreddit": "SideProject"
        }


def generate_x_post(llm: LLMClient, tool_name: str, tool_url: str, description: str) -> str:
    """用 LLM 生成 X (Twitter) 风格的推文"""
    prompt = f"""Write a viral, extremely engaging tweet (under 260 characters) about a futuristic dev tool called "{tool_name}".
What it does: {description}

RULES:
1. Tone (The "Soul"): You are a top-tier Silicon Valley indie hacker in 2026. Ship fast, build beautiful things, and have edge. Sound highly passionate and drop immediate value. No corporate jargon. 
2. NO URLs: Do NOT include any links or URLs in the tweet. Instead, add a phrase like "Link in bio" or "Check the first reply 👇" at the end.
3. Use 2-3 hashtags: #buildinpublic #indiehacker #nextjs #devtools

Make it sound like a real visionary developer sharing their latest masterpiece.
Output ONLY the tweet text, nothing else."""

    try:
        tweet = llm.generate(prompt)
        # 确保不超过 280 字符
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
        return tweet.strip()
    except Exception:
        return f"🚀 Just shipped {tool_name}! {description[:100]}...\n\n{tool_url}\n\n#buildinpublic #devtools"


# ============================================================
# Playwright 自动化发帖
# ============================================================

async def post_to_reddit(page, post: dict, credentials: dict):
    """使用 Playwright 在 Reddit 上发帖"""
    log.info(f"🔵 Reddit: 发帖到 r/{post['subreddit']}...")

    try:
        # 1. 登录
        await page.goto("https://www.reddit.com/login", wait_until="networkidle")
        await page.fill('input[name="username"]', credentials.get("reddit_username", ""))
        await page.fill('input[name="password"]', credentials.get("reddit_password", ""))
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(3000)

        # 2. 导航到提交页面
        await page.goto(
            f"https://www.reddit.com/r/{post['subreddit']}/submit",
            wait_until="networkidle"
        )
        await page.wait_for_timeout(2000)

        # 3. 填写标题和正文
        title_input = page.locator('[name="title"], [placeholder*="Title"]').first
        await title_input.fill(post["title"])

        body_input = page.locator('[role="textbox"], textarea').first
        await body_input.fill(post["body"])

        await page.wait_for_timeout(1000)

        # 4. 提交
        submit_btn = page.locator('button:has-text("Post"), button:has-text("Submit")').first
        await submit_btn.click()
        await page.wait_for_timeout(3000)

        log.info(f"  ✅ Reddit 发帖成功: {post['title'][:50]}")
        return True
    except Exception as e:
        log.warning(f"  ❌ Reddit 发帖失败: {e}")
        return False


async def post_to_x(page, tweet: str, credentials: dict):
    """使用 Playwright 在 X (Twitter) 上发推"""
    log.info(f"🐦 X: 发推...")

    try:
        # 1. 登录
        await page.goto("https://twitter.com/i/flow/login", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        username_input = page.locator('input[autocomplete="username"]').first
        await username_input.fill(credentials.get("x_username", ""))
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(2000)

        password_input = page.locator('input[type="password"]').first
        await password_input.fill(credentials.get("x_password", ""))
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(3000)

        # 2. 发推
        await page.goto("https://twitter.com/compose/tweet", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        tweet_box = page.locator('[data-testid="tweetTextarea_0"]').first
        await tweet_box.fill(tweet)
        await page.wait_for_timeout(1000)

        post_btn = page.locator('[data-testid="tweetButton"]').first
        await post_btn.click()
        await page.wait_for_timeout(3000)

        log.info(f"  ✅ X 发推成功: {tweet[:50]}...")
        return True
    except Exception as e:
        log.warning(f"  ❌ X 发推失败: {e}")
        return False


# ============================================================
# 主流程
# ============================================================

def get_latest_items_from_db(limit=3):
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), "shipmicro_site", "prisma", "dev.db")
    if not os.path.exists(db_path):
        log.warning(f"❌ 找不到数据库: {db_path}")
        return []
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        # 获取最新添加的内容
        cur.execute("SELECT slug, title, description, category FROM ContentItem ORDER BY createdAt DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        
        tools = []
        for r in rows:
            prefix = "arcade" if r["category"] in ["Tap", "Dodge", "Memory", "Pattern", "Math", "Typing", "Reaction", "Classic"] else "tools"
            tools.append({
                "name": r["title"],
                "url": f"https://www.shipmicro.com/{prefix}/{r['slug']}",
                "description": r["description"] or f"A cool {r['category']} app"
            })
        conn.close()
        return tools
    except Exception as e:
        log.error(f"❌ 读取数据库失败: {e}")
        return []

async def run_social_distributor(tools: list = None, credentials: dict = None, auto: bool = False):
    """
    执行社交分发流程。
    tools: [{"name": "Tool Name", "url": "https://...", "description": "..."}]
    credentials: {"reddit_username": "", "reddit_password": "", "x_username": "", "x_password": ""}
    """
    log.info("=" * 60)
    log.info("📢 SHIPMICRO SOCIAL DISTRIBUTOR 启动")
    log.info("=" * 60)

    if not tools:
        # 从本地 Prisma SQLite 数据库读取最新内容
        log.info("🔍 正在从数据库读取最新发布的内容...")
        tools = get_latest_items_from_db(limit=3)

    if not tools:
        log.warning("❌ 没有找到可推广的工具，退出")
        return

    if not credentials:
        # 尝试从环境变量或 .env 读取
        credentials = {
            "reddit_username": os.environ.get("REDDIT_USERNAME", ""),
            "reddit_password": os.environ.get("REDDIT_PASSWORD", ""),
            "x_username": os.environ.get("X_USERNAME", ""),
            "x_password": os.environ.get("X_PASSWORD", ""),
        }

    llm = LLMClient()

    # 生成帖子内容（不需要 Playwright，纯 LLM）
    posts = []
    for tool in tools:
        log.info(f"\n📝 生成推广内容: {tool['name']}...")
        reddit_post = generate_reddit_post(llm, tool["name"], tool["url"], tool["description"])
        x_tweet = generate_x_post(llm, tool["name"], tool["url"], tool["description"])
        posts.append({
            "tool": tool,
            "reddit": reddit_post,
            "x_tweet": x_tweet
        })

    # 保存生成的帖子内容到本地（即使不发布也可以手动使用）
    output_dir = os.path.join(os.path.dirname(__file__), "social_posts")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"posts_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    log.info(f"\n💾 帖子内容已保存至: {output_path}")

    # 如果有凭据，尝试自动发帖
    has_reddit = credentials.get("reddit_username") and credentials.get("reddit_password")
    has_x = credentials.get("x_username") and credentials.get("x_password")

    if has_reddit or has_x:
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )

                for post_data in posts:
                    if has_reddit:
                        page = await context.new_page()
                        await post_to_reddit(page, post_data["reddit"], credentials)
                        await page.close()
                        # 随机等待 30-90 秒，模拟真人行为
                        wait_time = random.randint(30, 90)
                        log.info(f"⏳ 冷却 {wait_time}s (防风控)...")
                        await asyncio.sleep(wait_time)

                    if has_x:
                        page = await context.new_page()
                        await post_to_x(page, post_data["x_tweet"], credentials)
                        await page.close()
                        wait_time = random.randint(30, 90)
                        log.info(f"⏳ 冷却 {wait_time}s (防风控)...")
                        await asyncio.sleep(wait_time)

                await browser.close()
        except ImportError:
            log.warning("⚠️ Playwright 未安装。请运行: pip install playwright && playwright install chromium")
        except Exception as e:
            log.error(f"💥 自动发帖异常: {e}")
    else:
        log.info("\n📋 未配置社交媒体凭据，帖子内容已保存，您可以手动复制发布。")
        log.info("   若要自动发帖，请在 .env 中配置:")
        log.info("   REDDIT_USERNAME=xxx")
        log.info("   REDDIT_PASSWORD=xxx")
        log.info("   X_USERNAME=xxx")
        log.info("   X_PASSWORD=xxx")

    # 输出预览
    try:
        print("\n" + "=" * 60)
        print("📋 生成的推广内容预览:")
        print("=" * 60)
        for post_data in posts:
            tool = post_data["tool"]
            print(f"\n🔧 工具: {tool['name']}")
            print(f"📌 Reddit r/{post_data['reddit']['subreddit']}:")
            print(f"   标题: {post_data['reddit']['title']}")
            print(f"   正文前100字: {post_data['reddit']['body'][:100]}...")
            print(f"🐦 X 推文:")
            print(f"   {post_data['x_tweet']}")
            print("-" * 40)
    except UnicodeEncodeError:
        pass # Ignore print errors on Windows console

    return posts


# ============================================================
# v2: Social Engagement Matrix (Roundtable Upgrade 5)
# ============================================================

def generate_auto_replies(llm: LLMClient, tool_name: str, comments: list[str]) -> list[str]:
    """用 LLM 生成社交媒体评论的自动回复（增长黑客策略）"""
    if not comments:
        return []

    prompt = f"""You are the developer of {tool_name}, replying to comments on your Reddit/X post.
For each comment below, write a brief, genuine reply (max 50 words each).
Be helpful, humble, and encourage interaction.

Comments:
{chr(10).join(f'{i+1}. {c}' for i, c in enumerate(comments[:5]))}

Output format:
1. [your reply]
2. [your reply]
...
"""
    try:
        response = llm.generate(prompt)
        replies = []
        for line in response.strip().split("\n"):
            if line.strip() and line[0].isdigit():
                reply = line.split(".", 1)[-1].strip()
                if reply:
                    replies.append(reply)
        return replies
    except Exception as e:
        log.warning(f"⚠️ 自动回复生成失败: {e}")
        return []


def generate_engagement_report(tools: list = None) -> dict:
    """生成社交推广效果报告（供 analytics_feedback 读取）"""
    output_dir = os.path.join(os.path.dirname(__file__), "social_posts")
    if not os.path.isdir(output_dir):
        return {"status": "no_data", "posts": 0}

    post_files = sorted([f for f in os.listdir(output_dir) if f.startswith("posts_")])
    total_posts = 0
    platforms = {"reddit": 0, "x": 0}
    for pf in post_files:
        path = os.path.join(output_dir, pf)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        total_posts += len(data)
        for p in data:
            if p.get("reddit"):
                platforms["reddit"] += 1
            if p.get("x_tweet"):
                platforms["x"] += 1

    report = {
        "total_post_batches": len(post_files),
        "total_posts": total_posts,
        "platforms": platforms,
        "latest_batch": post_files[-1] if post_files else None,
    }

    report_path = os.path.join(output_dir, "engagement_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    log.info(f"📊 Social Engagement Report: {total_posts} posts across {len(post_files)} batches")
    return report


if __name__ == "__main__":
    import asyncio
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", action="store_true", help="Auto run from orchestrator")
    args = parser.parse_args()
    asyncio.run(run_social_distributor(auto=args.auto))

