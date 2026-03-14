import sys
import argparse
import time
import os
import random
import math
from playwright.sync_api import sync_playwright

# Force UTF-8 encoding for Windows consoles to avoid emoji print crashes
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def ensure_profile_dir(profile_dir):
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)

# ─── Human Behavior Simulation ───
def human_sleep(base, variance=0.5):
    """Gaussian random sleep: base ± variance seconds, minimum 0.5s"""
    delay = max(0.5, random.gauss(base, base * variance))
    time.sleep(delay)
    return delay

def human_type(page, text, min_delay=30, max_delay=120):
    """Type text with variable per-character delay to mimic human typing."""
    for char in text:
        page.keyboard.type(char, delay=0)
        # Faster for common chars, slower for special/capital
        if char in ' \n':
            time.sleep(random.uniform(0.05, 0.15))
        elif char.isupper() or char in '!@#$%^&*()[]{}:':
            time.sleep(random.uniform(0.08, 0.18))
        else:
            time.sleep(random.uniform(min_delay / 1000, max_delay / 1000))

def simulate_reading(page, duration_base=3):
    """Simulate human reading behavior: random micro-scrolls and pauses."""
    steps = random.randint(2, 5)
    for _ in range(steps):
        scroll_px = random.randint(-30, 80)
        page.mouse.wheel(0, scroll_px)
        human_sleep(duration_base / steps, variance=0.6)

def login_to_platform(platform):
    """纯登录模式：只打开浏览器让用户手动登录，保存 Cookie 后退出"""
    profile_dir = f"./playwright_profiles/{platform}"
    ensure_profile_dir(profile_dir)
    
    urls = {
        "twitter": "https://x.com/login",
        "reddit": "https://www.reddit.com/login"
    }
    
    print(f"[Bot] Opening {platform} login page with persistent profile...")
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ],
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        page = browser.new_page()
        page.goto(urls.get(platform, urls["twitter"]), timeout=30000, wait_until="domcontentloaded")
        
        print("=" * 60)
        print("  Please log in manually in the browser window.")
        print("  After login is complete, come back here and press ENTER.")
        print("=" * 60)
        input(">>> Press ENTER after you have logged in successfully... ")
        
        print(f"[Bot] ✅ Cookie saved to {profile_dir}. You can now use headless mode!")
        browser.close()

def post_to_reddit(url, content, profile_dir="./playwright_profiles/reddit"):
    print(f"[Bot] Launching Playwright with persistent profile: {profile_dir}")
    ensure_profile_dir(profile_dir)
    
    with sync_playwright() as p:
        # headless=False for the FIRST TIME so the user can log in manually and save the cookie
        # After first login, you can change this to True
        is_headless = os.getenv("HEADLESS_MODE", "true").lower() == "true"
        
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=is_headless,
            # Stealth args to avoid detection
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        page = browser.new_page()
        
        print(f"[Bot] Navigating to target Reddit thread: {url}")
        try:
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(4) # Human delay
            
            print("[Bot] Looking for comment input box...")
            # Locator strategies for Reddit's various UIs
            editor = page.locator('shreddit-composer').locator('div[role="textbox"]')
            if editor.count() == 0:
                # Fallback for older UI
                editor = page.locator('div[role="textbox"][aria-label="Markdown editor"]')
            if editor.count() == 0:
                editor = page.locator('textarea[name="text"]')
                
            if editor.count() > 0:
                editor.first.scroll_into_view_if_needed()
                time.sleep(1)
                editor.first.click()
                time.sleep(1)
                
                print("[Bot] Typing organic payload...")
                editor.first.fill(content)
                time.sleep(2)
                
                print("[Bot] Clicking submit...")
                # Find the submit button inside the composer
                submit_btn = page.locator('shreddit-composer').locator('button[slot="submitButton"]')
                if submit_btn.count() == 0:
                    submit_btn = page.locator('button:has-text("Comment")')
                
                if submit_btn.count() > 0:
                    submit_btn.first.click()
                    print("[Bot] ✅ Comment physically clicked and submitted.")
                    time.sleep(4) # Wait for network request to finish
                else:
                    print("[Bot] ❌ Could not find the Submit/Comment button.")
            else:
                print("[Bot] ❌ Could not find comment editor. Are you logged in? Check cookie status.")
                
        except Exception as e:
            print(f"[Bot] ❌ Playwright automation encountered an error: {e}")
            
        finally:
            print("[Bot] Closing browser context.")
            browser.close()

def post_to_twitter(content, reply_content="", profile_dir="./playwright_profiles/twitter"):
    """使用 Playwright 物理模拟在 X (Twitter) 上发推文，并支持首评引流"""
    print(f"[Bot] Launching Playwright for Twitter with persistent profile: {profile_dir}")
    ensure_profile_dir(profile_dir)
    
    with sync_playwright() as p:
        is_headless = os.getenv("HEADLESS_MODE", "true").lower() == "true"
        
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=is_headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ],
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        page = browser.new_page()
        
        try:
            print("[Bot] Navigating to X (Twitter) home feed...")
            page.goto("https://x.com/home", timeout=30000, wait_until="domcontentloaded")
            time.sleep(6)
            
            # 检查是否已登录
            current_url = page.url
            if "login" in current_url or "i/flow" in current_url:
                print("[Bot] ❌ Not logged in! Run with --login-only first.")
                browser.close()
                return
            
            print("[Bot] Logged in successfully. Looking for compose area...")
            
            # 截图用于调试
            page.screenshot(path="debug_twitter_home.png")
            print("[Bot] Debug screenshot saved to debug_twitter_home.png")
            
            # 策略 1: 直接用键盘快捷键 N 打开发推对话框
            print("[Bot] Trying keyboard shortcut 'N' to open compose dialog...")
            page.keyboard.press("n")
            human_sleep(3)
            
            # 等待对话框中的文本框出现
            compose_selectors = [
                'div[data-testid="tweetTextarea_0"]',
                'div[role="textbox"][data-testid="tweetTextarea_0"]',
                'div[contenteditable="true"][role="textbox"]',
                'div[role="textbox"]',
            ]
            
            compose_box = None
            for selector in compose_selectors:
                try:
                    el = page.wait_for_selector(selector, timeout=5000)
                    if el:
                        compose_box = el
                        print(f"[Bot] Found compose box with selector: {selector}")
                        break
                except:
                    continue
                    
            if compose_box:
                compose_box.click()
                human_sleep(1.5)
                
                # Simulate reading the compose area before typing
                simulate_reading(page, duration_base=2)
                
                print(f"[Bot] Typing tweet content ({len(content)} chars)...")
                # Use humanized typing with variable speed
                human_type(page, content)
                human_sleep(2)
                
                # 截图确认内容已输入
                page.screenshot(path="debug_twitter_typed.png")
                
                print("[Bot] Clicking Post button...")
                post_selectors = [
                    'button[data-testid="tweetButton"]',
                    'button[data-testid="tweetButtonInline"]',
                ]
                
                posted = False
                for selector in post_selectors:
                    try:
                        btn = page.wait_for_selector(selector, timeout=5000)
                        if btn:
                            btn.click()
                            posted = True
                            print("[Bot] ✅ Tweet physically posted!")
                            human_sleep(8)
                            page.screenshot(path="debug_twitter_success.png")
                            print("[Bot] Success screenshot saved to debug_twitter_success.png")
                            
                            # Execute First Comment Drop if reply_content is provided
                            if reply_content:
                                print(f"[Bot] Initiating First Comment Drop: {reply_content[:50]}...")
                                human_sleep(4)  # Pause like a human composing a thought
                                simulate_reading(page, duration_base=2)  # Read the timeline
                                page.keyboard.press("r")
                                human_sleep(3)
                                human_type(page, reply_content)
                                human_sleep(2)
                                page.keyboard.press("Control+Enter")
                                human_sleep(8)
                                page.screenshot(path="debug_twitter_reply_success.png")
                                print("[Bot] ✅ First Comment Drop successful!")
                            
                            break
                    except:
                        continue
                        
                if not posted:
                    # 最后手段：用 Ctrl+Enter 提交
                    print("[Bot] Trying Ctrl+Enter to submit...")
                    page.keyboard.press("Control+Enter")
                    human_sleep(8)
                    page.screenshot(path="debug_twitter_fallback.png")
                    print("[Bot] ✅ Tweet submitted via keyboard shortcut.")
                    
                    if reply_content:
                        print(f"[Bot] Initiating First Comment Drop (Fallback): {reply_content[:50]}...")
                        human_sleep(4)
                        page.keyboard.press("r")
                        human_sleep(3)
                        human_type(page, reply_content)
                        human_sleep(2)
                        page.keyboard.press("Control+Enter")
                        human_sleep(8)
                        print("[Bot] ✅ First Comment Drop successful!")
            else:
                print("[Bot] ❌ Could not find tweet compose box after all attempts.")
                page.screenshot(path="debug_twitter_fail.png")
                print("[Bot] Failure screenshot saved to debug_twitter_fail.png")
                
        except Exception as e:
            print(f"[Bot] ❌ Twitter automation error: {e}")
            try:
                page.screenshot(path="debug_twitter_error.png")
            except:
                pass
            
        finally:
            print("[Bot] Closing browser context.")
            browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Titan Physical Web Automaton")
    parser.add_argument("--platform", required=True, choices=["reddit", "twitter"], help="Target platform")
    parser.add_argument("--url", required=False, help="Target URL (e.g. reddit post)")
    parser.add_argument("--content", required=False, default="", help="Text payload to post")
    parser.add_argument("--reply", required=False, default="", help="Text for First Comment Drop")
    parser.add_argument("--login-only", action="store_true", help="Only open browser for manual login, save cookies, then exit")
    args = parser.parse_args()
    
    if args.login_only:
        login_to_platform(args.platform)
    elif args.platform == "reddit":
        if not args.url:
            print("Error: --url is required for reddit")
            sys.exit(1)
        post_to_reddit(args.url, args.content)
    elif args.platform == "twitter":
        if not args.content:
            print("Error: --content is required for twitter")
            sys.exit(1)
        post_to_twitter(args.content, reply_content=args.reply)
