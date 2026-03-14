import os
import sys
import time
import random
import argparse
from playwright.sync_api import sync_playwright
import logging

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Ensure logs are visible
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [NURTURER] - %(message)s')
log = logging.getLogger("nurturer")

def ensure_profile_dir(profile_dir):
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)

def simulate_human_reading(page, duration_sec):
    """模拟人类在推特时间线上的浏览行为：无规律滚动、停顿阅读"""
    log.info(f"⏳ Start doomscrolling for ~{duration_sec} seconds...")
    start_time = time.time()
    
    while time.time() - start_time < duration_sec:
        # 决定向下滚动的像素数
        scroll_amount = random.randint(300, 900)
        
        # 物理滚动
        page.mouse.wheel(0, scroll_amount)
        log.info(f"  👇 Scrolled down {scroll_amount}px")
        
        # 偶尔往回滚一下 (10% 概率)
        if random.random() < 0.1:
            back_scroll = random.randint(100, 300)
            page.mouse.wheel(0, -back_scroll)
            log.info(f"  👆 Scrolled slightly up {back_scroll}px")

        # 停顿阅读当前推文
        wait_time = random.uniform(2.0, 8.0)
        
        # 偶尔遇到“长文”或者“视频”停留很久 (5% 概率)
        if random.random() < 0.05:
            wait_time += random.uniform(10.0, 20.0)
            log.info(f"  👁️ Found interesting tweet, deep reading for {wait_time:.1f}s")
            
        time.sleep(wait_time)

def try_random_like(page):
    """尝试以很低的概率随机点赞当前屏幕上的一个推文"""
    try:
        # 查找屏幕内可见的、未点赞的心形按钮
        # Twitter's like button aria-label is usually "Like" when not liked, and "Liked" when liked
        like_buttons = page.locator('div[data-testid="like"]')
        
        count = like_buttons.count()
        if count > 0:
            # 随机挑一个点赞
            target_idx = random.randint(0, count - 1)
            target = like_buttons.nth(target_idx)
            
            # 只有 5% 的绝对概率点赞
            if random.random() < 0.05:
                # 移动鼠标过去
                target.scroll_into_view_if_needed()
                time.sleep(random.uniform(0.5, 1.5))
                target.click()
                log.info("  ❤️ Liked a random tweet to build account history!")
                time.sleep(random.uniform(1.0, 3.0))
    except Exception as e:
        log.warning(f"  ⚠️ Could not like: {e}")

def nurture_twitter(duration_minutes=5, profile_dir="./playwright_profiles/twitter"):
    """执行推特养号主干流程"""
    ensure_profile_dir(profile_dir)
    log.info(f"🚀 Launching Nurturer with profile: {profile_dir}")
    
    total_seconds = duration_minutes * 60
    
    with sync_playwright() as p:
        # 获取环境变量，决定是否静默模式运行
        is_headless = os.getenv("HEADLESS_MODE", "true").lower() == "true"
        
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=is_headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ],
            viewport={"width": random.randint(1100, 1400), "height": random.randint(700, 900)},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        
        try:
            page = browser.new_page()
            
            log.info("Navigating to X (Twitter) home feed...")
            page.goto("https://x.com/home", timeout=30000, wait_until="domcontentloaded")
            time.sleep(random.uniform(5.0, 8.0))
            
            current_url = page.url
            if "login" in current_url or "i/flow" in current_url:
                log.error("❌ Not logged in! Please run: python playwright_bot.py --platform twitter --login-only")
                browser.close()
                return

            log.info("✅ Login verified. Injecting virtual human...")
            
            start_time = time.time()
            
            # 主循环：滚动、停顿、低概率互动
            while time.time() - start_time < total_seconds:
                # 每次进行 10-30 秒的连续浏览
                chunk_duration = random.randint(10, 30)
                simulate_human_reading(page, chunk_duration)
                
                # 尝试极低概率点赞
                try_random_like(page)
                
                # 随机跳转到 Explore 页面逛逛 (20% 概率)
                if random.random() < 0.2:
                    log.info("  🧭 Going to Explore tab to check trends...")
                    page.goto("https://x.com/explore", wait_until="domcontentloaded")
                    time.sleep(random.uniform(3.0, 6.0))
                    simulate_human_reading(page, random.randint(15, 40))
                    
                    log.info("  🏠 Going back to Home feed...")
                    page.goto("https://x.com/home", wait_until="domcontentloaded")
                    time.sleep(random.uniform(3.0, 5.0))
                    
        except Exception as e:
            log.error(f"💥 Nurture session crashed: {e}")
            try:
                page.screenshot(path="debug_nurturer_crash.png")
            except:
                pass
        finally:
            log.info(f"🛑 Nurturing session complete. Duration: {(time.time() - start_time) / 60:.1f} mins.")
            time.sleep(1) # Let background requests flush
            browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TITAN: Twitter Account Nurturer (Anti-Ban)")
    parser.add_argument("--duration", type=int, default=5, help="Duration to run the nurture script in minutes (default: 5)")
    args = parser.parse_args()
    
    log.info(f"=== Starting Twitter Nurturing Session ({args.duration} mins) ===")
    nurture_twitter(duration_minutes=args.duration)
