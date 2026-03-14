import time
from github_scholar import GitHubScholar
from logger import get_logger

log = get_logger("domain_scholar")

def run_domain_crawls():
    scholar = GitHubScholar()
    
    tasks = [
        # Frontend frameworks
        {"domain": "frontend", "query": "topic:frontend-framework+stars:>10000", "top_n": 10},
        # Backend frameworks
        {"domain": "backend", "query": "topic:backend-framework+stars:>10000", "top_n": 10},
        # Game engines
        {"domain": "game-engine", "query": "topic:game-engine+stars:>5000", "top_n": 10}
    ]
    
    for t in tasks:
        log.info(f"🚀 开始采集专题: {t['domain']} (Top {t['top_n']})")
        scholar.run(top_n=t['top_n'], query=t['query'], domain=t['domain'])
        time.sleep(5)
        
    log.info("🎉 所有扩展专题采集完毕！请运行 skill_extractor.py 进行知识提炼。")

if __name__ == "__main__":
    run_domain_crawls()
