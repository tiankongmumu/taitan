"""
TITAN Deployer v1.0
自动部署构建成功的产品到 Vercel / Netlify / 静态托管
v1.0: 基础 Vercel CLI 部署 + 回退到静态导出
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

log = logging.getLogger("deployer")


class TitanDeployer:
    """自动部署管理器 — 支持 Vercel CLI + 静态导出"""

    DEPLOY_RECORD_FILE = os.path.join(os.path.dirname(__file__), "memory", "deployments.json")

    def deploy(self, app_path: str, method: str = "auto") -> dict:
        """部署应用到云端"""
        result = {
            "app_path": app_path,
            "app_name": os.path.basename(app_path),
            "method": method,
            "url": None,
            "success": False,
            "timestamp": datetime.now().isoformat(),
        }

        if method == "auto":
            # 优先尝试 Vercel，失败回退到静态导出
            for deploy_method in [self._deploy_vercel, self._deploy_static_export]:
                try:
                    url = deploy_method(app_path)
                    if url:
                        result["url"] = url
                        result["success"] = True
                        result["method"] = deploy_method.__name__.replace("_deploy_", "")
                        break
                except Exception as e:
                    log.warning(f"  {deploy_method.__name__} 失败: {e}")
        elif method == "vercel":
            result["url"] = self._deploy_vercel(app_path)
            result["success"] = result["url"] is not None
        elif method == "static":
            result["url"] = self._deploy_static_export(app_path)
            result["success"] = result["url"] is not None

        # 记录部署历史
        self._record_deployment(result)

        if result["success"]:
            log.info(f"  ✅ 部署成功: {result['url']}")
        else:
            log.warning(f"  ❌ 部署失败: {result['app_name']}")

        return result

    def _deploy_vercel(self, app_path: str) -> str | None:
        """通过 Vercel CLI 部署"""
        # 检查 Vercel CLI 是否可用
        try:
            check = subprocess.run(
                ["vercel", "--version"],
                capture_output=True, text=True, timeout=10, shell=True
            )
            if check.returncode != 0:
                log.warning("  Vercel CLI 未安装")
                return None
        except Exception:
            log.warning("  Vercel CLI 不可用")
            return None

        # 注入 vercel.json（如果不存在）
        vercel_json_path = os.path.join(app_path, "vercel.json")
        if not os.path.exists(vercel_json_path):
            vercel_config = {
                "framework": "nextjs",
                "buildCommand": "npm run build",
                "outputDirectory": ".next"
            }
            with open(vercel_json_path, "w", encoding="utf-8") as f:
                json.dump(vercel_config, f, indent=2)
            log.info("  注入 vercel.json (framework: nextjs)")

        # 获取 Vercel token
        vercel_token = os.environ.get("VERCEL_TOKEN", "")
        cmd = ["vercel", "--prod", "--yes"]
        if vercel_token:
            cmd.extend(["--token", vercel_token])

        # 执行部署 (生产模式, 自动确认)
        try:
            result = subprocess.run(
                cmd, cwd=app_path,
                capture_output=True, text=True,
                timeout=300, shell=True
            )
            log.info(f"  Vercel stdout: {result.stdout[:300]}")
            if result.stderr:
                log.info(f"  Vercel stderr: {result.stderr[:300]}")
            if result.returncode == 0:
                # 提取URL (通常是最后一行)
                lines = result.stdout.strip().split("\n")
                for line in reversed(lines):
                    line = line.strip()
                    if line.startswith("http"):
                        return line
                return lines[-1].strip() if lines else None
            else:
                log.warning(f"  Vercel部署失败 (exit {result.returncode}): {result.stderr[:300]}")
                return None
        except subprocess.TimeoutExpired:
            log.warning("  Vercel部署超时 (300s)")
            return None

    def _deploy_static_export(self, app_path: str) -> str | None:
        """
        Next.js 静态导出 — 生成到 out/ 目录
        可以上传到任何静态托管 (GitHub Pages, Cloudflare Pages, etc.)
        """
        try:
            out_dir = os.path.join(app_path, "out")

            # Step 1: 确保 next.config.mjs 包含 output: 'export'
            config_path = os.path.join(app_path, "next.config.mjs")
            config_injected = False
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config_content = f.read()
                if "output" not in config_content:
                    # 尝试多种替换模式
                    replacements = [
                        ("const nextConfig = {};", 'const nextConfig = { output: "export" };'),
                        ("const nextConfig = {", 'const nextConfig = { output: "export",'),
                    ]
                    for old, new in replacements:
                        if old in config_content:
                            config_content = config_content.replace(old, new)
                            config_injected = True
                            break
                    if not config_injected:
                        # Fallback: 添加到文件顶部后面
                        config_content = config_content.replace(
                            "/** @type {import('next').NextConfig} */",
                            '/** @type {import("next").NextConfig} */'
                        )
                        # 用正则替换
                        import re
                        config_content = re.sub(
                            r'const nextConfig\s*=\s*\{',
                            'const nextConfig = { output: "export",',
                            config_content, count=1
                        )
                        config_injected = True
                    with open(config_path, "w", encoding="utf-8") as f:
                        f.write(config_content)
                    log.info("  注入 output: 'export' 到 next.config.mjs")

            # Step 2: 重新构建（注入配置后必须rebuild）
            log.info("  正在构建静态导出...")
            build_result = subprocess.run(
                ["npm", "run", "build"],
                cwd=app_path,
                capture_output=True, text=True,
                timeout=180, shell=True
            )
            if build_result.returncode != 0:
                log.warning(f"  静态导出构建失败: {build_result.stderr[:300]}")
                return None

            # Step 3: 检查 out/ 是否生成
            if os.path.exists(out_dir):
                log.info(f"  ✅ 静态导出完成: {out_dir}")
                return f"file://{out_dir}"

            log.warning(f"  静态构建完成但 out/ 目录未生成")
            return None
        except Exception as e:
            log.warning(f"  静态导出失败: {e}")
            return None

    def _record_deployment(self, result: dict):
        """记录部署历史"""
        try:
            os.makedirs(os.path.dirname(self.DEPLOY_RECORD_FILE), exist_ok=True)
            records = []
            if os.path.exists(self.DEPLOY_RECORD_FILE):
                with open(self.DEPLOY_RECORD_FILE, "r", encoding="utf-8") as f:
                    records = json.load(f)
            records.append(result)
            records = records[-100:]  # 保留最近100条
            with open(self.DEPLOY_RECORD_FILE, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get_deployed_apps(self) -> list[dict]:
        """获取所有已部署的应用"""
        try:
            if os.path.exists(self.DEPLOY_RECORD_FILE):
                with open(self.DEPLOY_RECORD_FILE, "r", encoding="utf-8") as f:
                    records = json.load(f)
                return [r for r in records if r.get("success")]
        except Exception:
            pass
        return []

    def get_stats(self) -> dict:
        """获取部署统计"""
        records = self.get_deployed_apps()
        return {
            "total_deployments": len(records),
            "successful": len([r for r in records if r.get("success")]),
            "methods": list(set(r.get("method", "?") for r in records)),
            "latest": records[-1] if records else None,
        }


# CLI
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s", datefmt="%H:%M:%S")
    import argparse
    parser = argparse.ArgumentParser(description="TITAN Deployer v1.0")
    parser.add_argument("path", nargs="?", help="App path to deploy")
    parser.add_argument("--method", default="auto", choices=["auto", "vercel", "static"])
    parser.add_argument("--stats", action="store_true", help="Show deployment stats")
    args = parser.parse_args()

    deployer = TitanDeployer()

    if args.stats:
        stats = deployer.get_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    elif args.path:
        result = deployer.deploy(args.path, method=args.method)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Usage: python titan_deployer.py <app_path> [--method auto|vercel|static]")
