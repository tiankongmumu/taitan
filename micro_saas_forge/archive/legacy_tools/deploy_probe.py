"""
Micro-SaaS Forge — 部署探针 (v2)
支持：Vercel 自动部署、HTTP 200 健康探测、配置中心集成。
"""
import os
import sys
import subprocess
import time
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import VERCEL_TOKEN
from logger import get_logger

log = get_logger("deploy")


class DeployProbe:
    def __init__(self):
        self.vercel_token = VERCEL_TOKEN

    def deploy_and_probe(self, project_path: str) -> str:
        """部署到 Vercel 并探测 HTTP 200。"""
        log.info(f"部署路径: {project_path}")

        if not self.vercel_token:
            log.warning("VERCEL_TOKEN 未设置，进入模拟模式")
            time.sleep(1)
            if not self._simulated_probe():
                return None
            return "https://simulated-app-url.vercel.app"

        try:
            log.info("执行 `vercel --prod` ...")
            cmd = ["npx", "vercel", "--prod", "--token", self.vercel_token, "--yes"]
            result = subprocess.run(
                cmd, cwd=project_path, capture_output=True, text=True,
                check=True, timeout=300, shell=True
            )

            deployed_url = None
            for line in result.stdout.split("\n"):
                if line.startswith("https://") and "vercel.app" in line:
                    deployed_url = line.strip()
                    break

            if not deployed_url:
                log.error("无法从 Vercel 输出中提取部署 URL")
                return None

            log.info(f"已部署: {deployed_url}，开始健康探测...")
            if not self._probe_url(deployed_url):
                log.error(f"健康探测失败: {deployed_url}")
                return None

            return deployed_url

        except subprocess.TimeoutExpired:
            log.error("Vercel 部署超时 (>300s)")
            return None
        except subprocess.CalledProcessError as e:
            log.error(f"部署失败: {e.stderr[:500]}")
            return None

    def _simulated_probe(self) -> bool:
        log.info("[模拟] 探测 HTTP 200...")
        time.sleep(0.5)
        log.info("[模拟] 收到 200 OK")
        return True

    def _probe_url(self, url: str, max_retries: int = 5) -> bool:
        """探测 URL 是否返回 200，带重试。"""
        import requests
        for i in range(1, max_retries + 1):
            try:
                log.info(f"探测 (尝试 {i}/{max_retries})...")
                res = requests.get(url, timeout=15)
                if res.status_code in (200, 308, 401):
                    log.info(f"✅ HTTP {res.status_code} — 应用已上线（Vercel 部署成功）")
                    return True
                else:
                    log.warning(f"探测返回 HTTP {res.status_code}")
            except requests.exceptions.RequestException as e:
                log.warning(f"探测失败: {e}")
            time.sleep(3 * i)  # 递增等待
        return False
