"""News Scraper Skill — wraps the existing news_scraper.py as a standardized TITAN Skill."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from titan_skills import TitanSkill


class NewsScraperSkill(TitanSkill):
    name = "news_scraper"
    description = "从 HackerNews/GitHub Trending 爬取科技资讯"
    triggers = ["cron:0 */4 * * *", "manual", "message:新闻"]
    version = "1.0"

    async def execute(self, context: dict) -> dict:
        try:
            from news_scraper import main as scrape_main
            scrape_main()
            return {"status": "success", "message": "新闻爬取完成"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
