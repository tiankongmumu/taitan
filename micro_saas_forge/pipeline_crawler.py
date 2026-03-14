import os
import json
import logging
import requests
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "raw_data_global.json")

def fetch_reddit_posts(subreddit: str = "SaaS", limit: int = 20) -> List[Dict]:
    """Fetches top posts from a given Reddit subreddit."""
    logging.info(f"Fetching top {limit} posts from r/{subreddit}...")
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    
    # Reddit API requires a custom User-Agent to avoid 429 Too Many Requests
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 TitanEngine/2.0_Global'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        posts = []
        for child in data.get('data', {}).get('children', []):
            post_data = child.get('data', {})
            # Filter out pinned or sticky posts if necessary, though hot includes them
            if not post_data.get('stickied', False):
                posts.append({
                    "id": post_data.get('id'),
                    "title": post_data.get('title'),
                    "selftext": post_data.get('selftext', '')[:500], # Trucate text to save tokens
                    "url": f"https://www.reddit.com{post_data.get('permalink')}",
                    "score": post_data.get('score'),
                    "num_comments": post_data.get('num_comments')
                })
        logging.info(f"Successfully fetched {len(posts)} posts from Reddit.")
        return posts
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch Reddit data: {e}")
        return []

def get_mock_global_affiliate_products() -> List[Dict]:
    """Returns a mock list of high-commission GLOBAL affiliate SaaS products."""
    logging.info("Loading mock global affiliate products...")
    
    return [
        {
            "id": "prod_g01",
            "name": "Shopify (Global E-commerce Builder)",
            "solves_pain_point": "Hard to sell online, building ecommerce stores is too technical, payment gateway issues.",
            "commission_rate": "$150 per referral",
            "monthly_sales": "1M+",
            "affiliate_url": "YOUR_SHOPIFY_AFFILIATE_LINK_HERE", # ⬅️ Replace with real Shopify Affiliate Link
            "category": "E-commerce"
        },
        {
            "id": "prod_g02",
            "name": "Webflow (No-Code Website Builder)",
            "solves_pain_point": "WordPress is slow/bloated, need custom beautiful landing pages fast without coding.",
            "commission_rate": "50% for 12 months",
            "monthly_sales": "100k+",
            "affiliate_url": "YOUR_WEBFLOW_PARTNERSTACK_LINK_HERE", # ⬅️ Replace with real Webflow PartnerStack Link
            "category": "No-Code Builder"
        },
        {
            "id": "prod_g03",
            "name": "Jasper AI (AI Copywriter)",
            "solves_pain_point": "Writer's block, expensive content creators, SEO blog posts take too long to write.",
            "commission_rate": "30% recurring",
            "monthly_sales": "50k+",
            "affiliate_url": "YOUR_JASPER_PARTNERSTACK_LINK_HERE", # ⬅️ Replace with real Jasper PartnerStack Link
            "category": "AI/Marketing"
        },
        {
             "id": "prod_g04",
             "name": "Beehiiv (Newsletter Platform)",
             "solves_pain_point": "Substack lacks monetization options, Mailchimp is too expensive for big lists, want to grow a newsletter fast.",
             "commission_rate": "50% for 12 months",
             "monthly_sales": "20k+",
             "affiliate_url": "YOUR_BEEHIIV_PARTNERSTACK_LINK_HERE", # ⬅️ Replace with real Beehiiv PartnerStack Link
             "category": "Email Marketing"
        },
        {
             "id": "prod_g05",
             "name": "Gusto (Modern Payroll & HR)",
             "solves_pain_point": "Setting up payroll for remote teams is a nightmare, HR compliance is too complex for startups.",
             "commission_rate": "$100+ per signup",
             "monthly_sales": "300k+",
             "affiliate_url": "YOUR_GUSTO_PARTNERSTACK_LINK_HERE", # ⬅️ Replace with real Gusto PartnerStack Link
             "category": "HR/Payroll"
        },
        {
             "id": "prod_g06",
             "name": "Notion (Workspace & Productivity)",
             "solves_pain_point": "Team knowledge is scattered across Google Docs and Slack, project management is clunky.",
             "commission_rate": "50% of all new upgrades",
             "monthly_sales": "500k+",
             "affiliate_url": "YOUR_NOTION_PARTNERSTACK_LINK_HERE", # ⬅️ Replace with real Notion PartnerStack Link
             "category": "Productivity"
        }
    ]

def main():
    print("="*60)
    print("TITAN Engine - Pipeline Crawler (Global Edition MVP)")
    print("="*60)
    
    # 1. Fetch Reddit Data
    reddit_posts = fetch_reddit_posts(subreddit="SaaS", limit=20)
    entrepreneur_posts = fetch_reddit_posts(subreddit="Entrepreneur", limit=15)
    
    all_posts = reddit_posts + entrepreneur_posts
    
    # 2. Get Mock Global Affiliate Products
    affiliate_products = get_mock_global_affiliate_products()
    
    # 3. Assemble and Save
    combined_data = {
        "metadata": {
            "source1": "Reddit r/SaaS & r/Entrepreneur",
            "source2": "Mock Global Affiliate Products (US Market)",
            "post_count": len(all_posts),
            "product_count": len(affiliate_products)
        },
        "reddit_posts": all_posts,
        "affiliate_products": affiliate_products
    }
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)
        
    logging.info(f"Successfully saved combined data to {OUTPUT_FILE}")
    print(f"\n✅ Created raw_data_global.json with {len(all_posts)} posts and {len(affiliate_products)} US SaaS programs.")

if __name__ == "__main__":
    main()
