"""
TITAN Engine v3.0: GitHub Scholar (前哨站)
负责自动检索 GitHub Top AI/Agent 项目，并下载核心文件 (README, prompts, agents)。
"""
import os
import time
import json
import base64
import requests
import random
from config import FORGE_ROOT
from logger import get_logger

log = get_logger("scholar")

# 存储下载的原始文件
RAW_DATA_DIR = os.path.join(FORGE_ROOT, "github_raw_data")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

class GitHubScholar:
    def __init__(self):
        self.api_base = "https://api.github.com"
        self.token = self._get_github_token()
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
            log.info("GitHub Token 已加载，享有高频限制。")
        else:
            log.warning("未检测到 GITHUB_TOKEN，使用受限的公共 API 限额 (可能导致 403 限流)。")

    def _get_github_token(self):
        val = os.environ.get("GITHUB_TOKEN")
        if val: return val
        env_path = os.path.join(FORGE_ROOT, ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GITHUB_TOKEN="):
                        return line.split("=", 1)[1].strip()
        return None

    def search_top_repos(self, limit: int = 10, query="topic:agent+stars:>5000", domain="agent") -> list[dict]:
        """按特定条件搜索顶级项目"""
        log.info(f"🔍 正在检索 GitHub Top {limit} 项目 ({domain})...")
        url = f"{self.api_base}/search/repositories?q={query}&sort=stars&order=desc&per_page={limit}"
        
        try:
            r = requests.get(url, headers=self.headers)
            r.raise_for_status()
            items = r.json().get("items", [])
            repos = [{"full_name": item["full_name"], "stars": item["stargazers_count"], "url": item["html_url"], "branch": item.get("default_branch", "main"), "domain": domain} for item in items]
            log.info(f"✅ 检索成功！共找到 {len(repos)} 个项目。")
            return repos
        except Exception as e:
            log.error(f"❌ 检索失败: {e}")
            if "API rate limit" in str(e):
                log.warning("请在 .env 中配置 GITHUB_TOKEN 以提升限额。")
            return []

    def get_repo_tree(self, full_name: str, branch: str) -> list[str]:
        """获取项目文件树列表"""
        url = f"{self.api_base}/repos/{full_name}/git/trees/{branch}?recursive=1"
        try:
            r = requests.get(url, headers=self.headers)
            r.raise_for_status()
            tree = r.json().get("tree", [])
            # 返回所有是 file (blob) 的路径
            return [item["path"] for item in tree if item["type"] == "blob"]
        except Exception as e:
            log.warning(f"  ⚠️ 获取文件树出错 ({full_name}): {e}")
            if 'r' in locals() and hasattr(r, 'text'):
                log.warning(f"  ⚠️ 响应: {r.text[:200]}")
            # 可能是分支名不对或项目太大
            return []

    def download_file(self, full_name: str, branch: str, filepath: str) -> str | None:
        """从此仓库下载单个文件内容"""
        # 使用 raw.githubusercontent 速度更快，也不占普通 API 限制 (没有 token 也能下)
        url = f"https://raw.githubusercontent.com/{full_name}/{branch}/{filepath}"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                return r.text
        except Exception:
            pass
        return None

    def fetch_core_files(self, repo: dict):
        """爬取核心文件 (README, 架构, prompt/agent 相关的代码)"""
        full_name = repo["full_name"]
        safe_name = full_name.replace("/", "_")
        repo_dir = os.path.join(RAW_DATA_DIR, safe_name)
        
        if os.path.exists(repo_dir):
            log.info(f"⏭️ {full_name} 已经存在，跳过...")
            return

        log.info(f"📥 正在解析 {full_name} (⭐ {repo['stars']})...")
        tree_paths = self.get_repo_tree(full_name, repo["branch"])
        if not tree_paths:
            log.warning(f"⚠️ 无法获取 {full_name} 的文件树")
            return

        domain = repo.get("domain", "agent")
        # 筛选感兴趣的文件
        target_files = []
        # 1. README
        readmes = [p for p in tree_paths if p.lower() in ("readme.md", "architecture.md", "design.md")]
        if readmes:
            target_files.append(readmes[0]) # 拿第一个

        # 2. 根据 domain 获取核心代码
        interesting = []
        for p in tree_paths:
            pl = p.lower()
            if "test" in pl or "docs" in pl or "example" in pl:  # 排除测试和文档
                continue
                
            if domain == "agent":
                if pl.endswith((".py", ".ts", ".js")):
                    if any(k in pl for k in ["prompt", "agent", "memory", "llm", "chain", "workflow"]):
                        if "app" not in pl:
                            interesting.append(p)
            elif domain == "frontend":
                if pl.endswith(("package.json", ".tsx", ".vue", ".ts", "index.js", "app.js")):
                    interesting.append(p)
            elif domain == "backend":
                if pl.endswith(("main.go", "app.py", "pom.xml", ".java", ".py", ".go", ".ts")):
                    if any(k in pl for k in ["controller", "service", "route", "model", "config"]):
                        interesting.append(p)
            elif domain == "game-engine":
                if pl.endswith(("cmakelists.txt", ".cs", ".cpp", ".h", ".ts", "premake5.lua")):
                    interesting.append(p)
        
        # 限制最多随机挑选 3 个核心代码文件，避免下载过多
        random.shuffle(interesting)
        target_files.extend(interesting[:3])

        if not target_files:
            log.info(f"  无感兴趣的内部文件。")
            return

        os.makedirs(repo_dir, exist_ok=True)
        # 记录 meta 数据
        with open(os.path.join(repo_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(repo, f, ensure_ascii=False, indent=2)

        # 下载文件
        for fpath in target_files:
            content = self.download_file(full_name, repo["branch"], fpath)
            if content:
                # 只保留前 500 行，避免文件过大把后面的 LLM 撑爆
                lines = content.split("\n")[:500]
                truncated = "\n".join(lines)
                
                safe_fpath = fpath.replace("/", "_").replace("\\", "_")
                with open(os.path.join(repo_dir, safe_fpath), "w", encoding="utf-8") as f:
                    f.write(truncated)
                log.info(f"  📄 Saved {fpath}")
            
            # API 限速保护
            time.sleep(0.5)

    def run(self, top_n: int = 5, query: str = "topic:agent+stars:>5000", domain: str = "agent"):
        repos = self.search_top_repos(limit=top_n, query=query, domain=domain)
        for repo in repos:
            self.fetch_core_files(repo)
            time.sleep(2) # 休息一下
        
        log.info("=" * 60)
        log.info("✅ GitHub 前哨站检索完毕！")
        log.info(f"数据存放于: {RAW_DATA_DIR}")
        log.info("=" * 60)

if __name__ == "__main__":
    scholar = GitHubScholar()
    scholar.run(top_n=100) # 扩容至前 100 大项目
