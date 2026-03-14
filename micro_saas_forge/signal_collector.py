"""
TITAN Pipeline — Stage 1: Signal Collector
============================================
Collects raw business/pain-point signals from multiple data sources:
  - Reddit (r/SaaS, r/Entrepreneur, r/startups)
  - HackerNews (top stories)
  - ProductHunt (trending)

Output: List[RawSignal] saved to demand_signals/raw_signals.json
"""
import os
import sys
import json
import time
import requests
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger

log = get_logger("signal_collector")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "demand_signals")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "raw_signals.json")
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TitanEngine/5.0"
}
REQUEST_TIMEOUT = 15


# ============================================================
# Data Source: Reddit
# ============================================================
def fetch_reddit(subreddit: str, limit: int = 20) -> List[Dict]:
    """Fetch hot posts from a Reddit subreddit."""
    log.info(f"📡 Reddit r/{subreddit} top {limit}...")
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        posts = []
        for child in r.json().get("data", {}).get("children", []):
            d = child.get("data", {})
            if d.get("stickied"):
                continue
            posts.append({
                "source": f"reddit/r/{subreddit}",
                "title": d.get("title", ""),
                "text": (d.get("selftext", "") or "")[:500],
                "score": d.get("score", 0),
                "comments": d.get("num_comments", 0),
                "url": f"https://www.reddit.com{d.get('permalink', '')}",
                "timestamp": datetime.utcfromtimestamp(d.get("created_utc", 0)).isoformat()
            })
        log.info(f"  ✅ Got {len(posts)} posts from r/{subreddit}")
        return posts
    except Exception as e:
        log.warning(f"  ❌ Reddit r/{subreddit} failed: {e}")
        return []


# ============================================================
# Data Source: HackerNews
# ============================================================
def fetch_hackernews(limit: int = 15) -> List[Dict]:
    """Fetch top stories from HackerNews."""
    log.info(f"📡 HackerNews top {limit}...")
    try:
        r = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        story_ids = r.json()[:limit]
        posts = []
        for sid in story_ids:
            try:
                sr = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=10)
                s = sr.json()
                if s and s.get("type") == "story":
                    posts.append({
                        "source": "hackernews",
                        "title": s.get("title", ""),
                        "text": "",
                        "score": s.get("score", 0),
                        "comments": s.get("descendants", 0),
                        "url": s.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                        "timestamp": datetime.utcfromtimestamp(s.get("time", 0)).isoformat()
                    })
            except Exception:
                continue
            time.sleep(0.1)  # Be nice to HN API
        log.info(f"  ✅ Got {len(posts)} stories from HN")
        return posts
    except Exception as e:
        log.warning(f"  ❌ HackerNews failed: {e}")
        return []


# ============================================================
# Data Source: ProductHunt (via unofficial endpoint)
# ============================================================
def fetch_producthunt(limit: int = 10) -> List[Dict]:
    """Fetch trending products from ProductHunt (front page scrape)."""
    log.info(f"📡 ProductHunt trending {limit}...")
    try:
        # Use the unofficial API endpoint
        url = "https://www.producthunt.com/frontend/graphql"
        query = {
            "operationName": "HomePage",
            "variables": {"featured": True},
            "query": "query HomePage($featured: Boolean) { posts(featured: $featured, first: 10) { edges { node { id name tagline votesCount url } } } }"
        }
        r = requests.post(url, json=query, headers={**HEADERS, "Content-Type": "application/json"}, timeout=REQUEST_TIMEOUT)
        if r.status_code != 200:
            log.info("  ⚠️ ProductHunt API unavailable, skipping")
            return []
        data = r.json()
        edges = data.get("data", {}).get("posts", {}).get("edges", [])
        posts = []
        for edge in edges[:limit]:
            node = edge.get("node", {})
            posts.append({
                "source": "producthunt",
                "title": node.get("name", ""),
                "text": node.get("tagline", ""),
                "score": node.get("votesCount", 0),
                "comments": 0,
                "url": node.get("url", ""),
                "timestamp": datetime.utcnow().isoformat()
            })
        log.info(f"  ✅ Got {len(posts)} products from PH")
        return posts
    except Exception as e:
        log.warning(f"  ❌ ProductHunt failed: {e}")
        return []


# ============================================================
# Main Collector
# ============================================================
def collect_all_signals() -> List[Dict]:
    """Run all data source collectors and return unified RawSignal list."""
    log.info("=" * 50)
    log.info("🚀 TITAN Signal Collector v5.0 — Starting")
    log.info("=" * 50)

    all_signals = []

    # Reddit sources
    for sub in ["SaaS", "Entrepreneur", "startups"]:
        signals = fetch_reddit(sub, limit=20)
        all_signals.extend(signals)
        time.sleep(1)  # Rate limit

    # HackerNews
    all_signals.extend(fetch_hackernews(limit=15))

    # ProductHunt
    all_signals.extend(fetch_producthunt(limit=10))

    # Save
    output = {
        "metadata": {
            "collected_at": datetime.utcnow().isoformat(),
            "total_signals": len(all_signals),
            "sources": list(set(s["source"] for s in all_signals))
        },
        "signals": all_signals
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    log.info(f"✅ Collected {len(all_signals)} raw signals → {OUTPUT_FILE}")
    return all_signals


if __name__ == "__main__":
    signals = collect_all_signals()
    print(f"\n📊 Summary: {len(signals)} signals from {len(set(s['source'] for s in signals))} sources")
    for s in sorted(signals, key=lambda x: x["score"], reverse=True)[:5]:
        print(f"  [{s['score']:>5}] [{s['source']}] {s['title'][:60]}")
