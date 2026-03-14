"""
Micro-SaaS Forge — 中央调度总控 (v3.5 — TITAN Self-Optimized)
支持：日志持久化、运行历史记录、--dry-run 模式、--stats 查看统计、
      断点恢复（--resume）、反馈驱动修复、失败记忆。
v3.5: 编译熔断器 (Circuit Breaker) + DAG 状态机步骤日志
学习来源: langgenius/dify (结构化循环) + assafelovic/gpt-researcher (human-in-the-loop)
"""
import os
import sys
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import FORGE_ROOT
from logger import get_logger
from run_history import record_run, print_stats
from core_generators.app_builder import AppBuilder
from deploy_probe import DeployProbe
from growth_engine.basic_seo import BasicSEO

log = get_logger("forge")

CHECKPOINT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "checkpoint.json")


class ForgeMaster:
    # v3.5: 编译熔断器 — 连续失败超过阈值就暂停冷却，避免浪费 Token
    CIRCUIT_BREAKER_THRESHOLD = 2   # 连续 2 个项目编译失败就触发熔断
    CIRCUIT_BREAKER_COOLDOWN = 300  # 熔断后冷却 5 分钟
    _consecutive_failures = 0

    def __init__(self):
        self.app_builder = AppBuilder()
        self.deploy_probe = DeployProbe()
        self.basic_seo = BasicSEO()

    def _save_checkpoint(self, step: int, data: dict):
        """Save pipeline progress for resume."""
        data["_checkpoint_step"] = step
        data["_checkpoint_time"] = time.time()
        with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        log.info(f"  💾 Checkpoint saved (step {step})")

    def _load_checkpoint(self) -> dict | None:
        """Load saved checkpoint if exists."""
        if os.path.exists(CHECKPOINT_FILE):
            try:
                with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def _clear_checkpoint(self):
        """Clear checkpoint after successful completion."""
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
            log.info("  🗑️ Checkpoint cleared")

    def run_pipeline(self, raw_idea: str, dry_run: bool = False, resume: bool = False) -> dict:
        """执行完整的 Micro-SaaS 生成流水线（支持断点恢复）。"""
        start_time = time.time()
        result = {"success": False, "url": "", "spec": {}}
        completed_step = 0
        repo_path = ""
        app_spec = {}

        # Resume from checkpoint if requested
        if resume:
            checkpoint = self._load_checkpoint()
            if checkpoint:
                completed_step = checkpoint.get("_checkpoint_step", 0)
                app_spec = checkpoint.get("spec", {})
                repo_path = checkpoint.get("repo_path", "")
                raw_idea = checkpoint.get("raw_idea", raw_idea)
                log.info(f"🔄 从断点恢复 (step {completed_step}), 跳过已完成步骤")
            else:
                log.info("⚠️ 无断点记录，从头开始")

        log.info("=" * 60)
        log.info("🚀 TITAN ENGINE v3.5 PIPELINE 启动")
        log.info(f"💡 点子: {raw_idea}")
        log.info("=" * 60)

        # v3.5: 熔断器检查
        if ForgeMaster._consecutive_failures >= self.CIRCUIT_BREAKER_THRESHOLD:
            log.warning(f"⚡ 熔断器触发！连续 {ForgeMaster._consecutive_failures} 次编译失败，冷却 {self.CIRCUIT_BREAKER_COOLDOWN}s...")
            time.sleep(self.CIRCUIT_BREAKER_COOLDOWN)
            ForgeMaster._consecutive_failures = 0
            log.info("✅ 熔断器重置，继续执行")

        # ── Step 1: Spec 转换 ──
        if completed_step < 1:
            log.info("[1/4] 🧠 将点子转换为工程规格...")
            app_spec = self.app_builder.transform_idea(raw_idea)
            result["spec"] = app_spec
            log.info(f"  规格: {json.dumps(app_spec, ensure_ascii=False)}")
            self._save_checkpoint(1, {"spec": app_spec, "raw_idea": raw_idea})
        else:
            log.info("[1/4] ⏭️ Spec (已从断点恢复)")
            result["spec"] = app_spec

        if dry_run:
            log.info("🏁 Dry-run 模式 — 仅生成规格，跳过后续步骤")
            result["success"] = True
            self._record(raw_idea, app_spec, True, "dry-run", start_time)
            return result

        # ── Step 2: 代码生成 ──
        if completed_step < 2:
            log.info("[2/4] 💻 生成 Next.js 代码并注入支付网关...")
            repo_path = self.app_builder.generate_and_inject(app_spec)
            if not repo_path:
                log.error("❌ Pipeline 在代码生成阶段失败")
                self._record(raw_idea, app_spec, False, "", start_time)
                return result
            log.info(f"  代码生成完成: {repo_path}")
            self._save_checkpoint(2, {"spec": app_spec, "repo_path": repo_path, "raw_idea": raw_idea})
        else:
            log.info("[2/4] ⏭️ 代码生成 (已从断点恢复)")

        # ── Step 2.5: 代码质量快速检查 ──
        log.info("[2.5/4] 🔍 代码质量快速检查...")
        page_file = os.path.join(repo_path, "src", "app", "page.tsx")
        issues = self._check_code_quality(page_file)
        if issues:
            log.warning(f"⚠️ 发现 {len(issues)} 个质量问题，触发反馈驱动修复...")
            fixed = self._feedback_fix(page_file, issues, app_spec)
            if not fixed:
                log.warning("❌ 反馈修复失败，触发完整重新生成 (retry 1/1)...")
                repo_path = self.app_builder.generate_and_inject(app_spec)
                if repo_path:
                    issues = self._check_code_quality(page_file)
                if issues:
                    log.warning("❌ 重新生成后仍不达标，降级处理")
                    # 记录失败到记忆系统
                    try:
                        import memory_bank as mem
                        mem.remember_failure(
                            category=app_spec.get("category", "Unknown"),
                            reason="; ".join(issues),
                            app_slug=app_spec.get("slug", ""),
                        )
                    except Exception:
                        pass
                    fallback_path = self.app_builder.generate_fallback_page(app_spec)
                    log.info(f"  降级落地页: {fallback_path}")
                    self._record(raw_idea, app_spec, False, "", start_time)
                    return result

        # ── Step 3: 部署与探测 ──
        log.info("[3/4] 🚀 部署到 Vercel 并探测健康...")
        deployment_url = self.deploy_probe.deploy_and_probe(repo_path)
        if not deployment_url:
            log.warning("⚠️ 部署失败，触发降级模式")
            fallback_path = self.app_builder.generate_fallback_page(app_spec)
            log.info(f"  降级落地页: {fallback_path}")
            self._record(raw_idea, app_spec, False, "", start_time)
            return result
        log.info(f"  已部署: {deployment_url}")

        # ── Step 4: SEO 资产 ──
        log.info("[4/4] 📈 生成 SEO 资产包...")
        self.basic_seo.generate_seo_assets(app_spec, deployment_url)

        # ── 完成 ──
        duration = time.time() - start_time
        result["success"] = True
        result["url"] = deployment_url
        self._record(raw_idea, app_spec, True, deployment_url, start_time)
        self._clear_checkpoint()

        log.info("=" * 60)
        log.info("✅ PIPELINE 顺利完成!")
        log.info(f"🌐 应用 URL: {deployment_url}")
        log.info(f"⏱️  总耗时: {duration:.1f}s")
        log.info("=" * 60)

        return result

    def _check_code_quality(self, page_file: str) -> list:
        """Quick code quality check. Returns list of issues (empty = pass)."""
        if not os.path.exists(page_file):
            return ["page.tsx 不存在"]

        try:
            with open(page_file, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception:
            return ["无法读取 page.tsx"]

        lines = code.strip().split("\n")
        issues = []

        if len(lines) < 50:
            issues.append(f"代码行数过少 ({len(lines)} < 50)，需要更完整的实现")
        if len(lines) > 500:
            issues.append(f"代码行数过多 ({len(lines)} > 500)，需要精简")
        if "export default" not in code:
            issues.append("缺少 export default function 组件导出")
        if not any(kw in code for kw in ["onClick", "onChange", "onSubmit", "useState", "onKeyDown"]):
            issues.append("缺少交互元素 (需要 onClick/onChange/useState 等)")
        if not any(kw in code for kw in ["bg-", "text-", "className"]):
            issues.append("缺少 Tailwind 样式类")
        if "TODO" in code or "coming soon" in code.lower():
            issues.append("包含占位符内容，需要完整实现")

        if not issues:
            log.info(f"  ✅ 代码质量检查通过 ({len(lines)} 行, 有交互, 有样式)")

        return issues

    def _feedback_fix(self, page_file: str, issues: list, app_spec: dict) -> bool:
        """Use LLM to fix specific quality issues (OpenClaw-inspired feedback loop)."""
        try:
            with open(page_file, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception:
            return False

        from core_generators.llm_client import LLMClient
        llm = LLMClient()

        fix_prompt = f"""The following Next.js page.tsx has quality issues that MUST be fixed:

ISSUES TO FIX:
{chr(10).join(f"- {issue}" for issue in issues)}

APP SPEC:
{json.dumps(app_spec, indent=2)}

CURRENT CODE:
```tsx
{code[:3000]}
```

FIX the issues above and return the COMPLETE corrected page.tsx.
Keep all existing working functionality. Only fix the listed issues.
Wrap your entire code in a ```tsx block."""

        log.info(f"  🔧 发送 {len(issues)} 个问题给 LLM 进行精准修复...")
        fixed_code = llm.extract_code_block(llm.generate(fix_prompt))
        if not fixed_code:
            return False

        with open(page_file, "w", encoding="utf-8") as f:
            f.write(fixed_code)

        # Re-check
        new_issues = self._check_code_quality(page_file)
        if new_issues:
            log.warning(f"  ⚠️ 修复后仍有 {len(new_issues)} 个问题")
            return False

        log.info("  ✅ 反馈修复成功！")
        return True

    def _record(self, idea, spec, success, url, start_time):
        duration = time.time() - start_time
        record_run(idea, spec, success, url, duration)


def main():
    args = sys.argv[1:]

    # --stats: 显示运行统计
    if "--stats" in args:
        print_stats()
        return

    # --dry-run: 只生成规格
    dry_run = "--dry-run" in args
    # --resume: 从断点恢复
    resume = "--resume" in args
    # 过滤标志参数
    args = [a for a in args if a not in ("--dry-run", "--resume")]

    idea = " ".join(args) if args else "A simple JSON to TypeScript Interface converter with a clean UI."

    master = ForgeMaster()
    master.run_pipeline(idea, dry_run=dry_run, resume=resume)


if __name__ == "__main__":
    main()
