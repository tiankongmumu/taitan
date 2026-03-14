"""
ShipMicro Tool Upgrader — 根据质量报告自动升级低分工具
流程: 质量体检 → 读取评审建议 → LLM 改写 page.tsx → 自愈编译 → 重新部署
"""
import os
import sys
import json
import time
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from core_generators.app_builder import AppBuilder
from deploy_probe import DeployProbe
from quality_gate import run_quality_gate, review_tool
from logger import get_logger

log = get_logger("upgrader")


def upgrade_tool(llm: LLMClient, tool_review: dict, app_path: str) -> bool:
    """根据质量评审报告升级一个工具的 page.tsx"""
    name = tool_review.get("tool_name", "Unknown")
    suggestions = tool_review.get("suggestions", [])
    reason = tool_review.get("reason", "")

    page_path = os.path.join(app_path, "src", "app", "page.tsx")
    if not os.path.exists(page_path):
        log.warning(f"  ⚠️ {name}: page.tsx 不存在，跳过")
        return False

    with open(page_path, "r", encoding="utf-8") as f:
        old_code = f.read()

    shipmicro_badge = '<a href="https://shipmicro.com" target="_blank" style="position:fixed;bottom:16px;right:16px;padding:6px 12px;background:#111;color:#888;border-radius:20px;font-size:12px;text-decoration:none;border:1px solid #333;z-index:999">🚢 ShipMicro</a>'

    prompt = f"""You are a senior React developer upgrading a Next.js micro-tool.

## Current Code (page.tsx):
```tsx
{old_code[:3000]}
```

## Quality Review Findings:
- Overall Score: {tool_review.get('overall', '?')}/10
- Verdict: {tool_review.get('verdict', '?')}
- Reason: {reason}
- Usefulness: {tool_review.get('usefulness', '?')}/10
- UI Quality: {tool_review.get('ui_quality', '?')}/10
- Completeness: {tool_review.get('completeness', '?')}/10
- Differentiation: {tool_review.get('differentiation', '?')}/10

## Required Improvements:
{chr(10).join(f"- {s}" for s in suggestions)}

## Upgrade Rules:
1. KEEP the existing functionality but IMPROVE it based on the suggestions above.
2. Make the UI significantly more polished (better colors, spacing, micro-animations).
3. Add real functionality where the original had mock/placeholder behavior.
4. This is a FREE tool — NO payment buttons, NO premium tiers.
5. Include this attribution at the bottom:
   <div dangerouslySetInnerHTML={{{{ __html: `{shipmicro_badge}` }}}} />
6. Use "use client"; if using React hooks.
7. Do NOT import external icon libraries. Use inline SVGs or emoji.
8. KEEP THE CODE UNDER 250 LINES.
9. Wrap your entire code in a ```tsx block.

Write the COMPLETE upgraded page.tsx:"""

    log.info(f"  🔧 LLM 正在升级 {name}...")
    upgraded_code = llm.extract_code_block(llm.generate(prompt))
    if not upgraded_code:
        log.warning(f"  ⚠️ LLM 升级失败")
        return False

    # 备份原始代码
    backup_path = page_path + ".bak"
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(old_code)

    # 写入升级后的代码
    with open(page_path, "w", encoding="utf-8") as f:
        f.write(upgraded_code)

    log.info(f"  ✅ 代码已升级 ({len(old_code)} → {len(upgraded_code)} chars)")
    return True


def rebuild_and_deploy(app_path: str, slug: str) -> bool:
    """编译并重新部署升级后的工具"""
    builder = AppBuilder()
    log.info(f"  🔨 编译升级后的 {slug}...")

    if not builder._self_heal_build(app_path):
        log.warning(f"  ❌ 编译失败，回滚代码")
        page_path = os.path.join(app_path, "src", "app", "page.tsx")
        backup_path = page_path + ".bak"
        if os.path.exists(backup_path):
            with open(backup_path, "r", encoding="utf-8") as f:
                original = f.read()
            with open(page_path, "w", encoding="utf-8") as f:
                f.write(original)
        return False

    probe = DeployProbe()
    url = probe.deploy_and_probe(app_path)
    if url:
        log.info(f"  🚀 重新部署成功: {url}")
        return True
    else:
        log.warning(f"  ⚠️ 部署失败")
        return False


def run_upgrade_cycle(min_score=7.0, max_upgrades=5, deploy=True):
    """完整的体检+升级流程"""
    log.info("=" * 60)
    log.info("🏥 SHIPMICRO 工具体检 & 升级中心")
    log.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log.info(f"🎯 目标: 升级所有得分 < {min_score} 的工具 (最多 {max_upgrades} 个)")
    log.info("=" * 60)

    start = time.time()

    # 1. 运行质量体检
    log.info("\n🔍 Step 1: 运行质量体检...")
    qr = run_quality_gate()

    # 2. 收集需要升级的工具
    needs_upgrade = qr.get("improve", []) + qr.get("kill", [])
    needs_upgrade.sort(key=lambda x: x.get("overall", 0))  # 最差的优先升级

    if not needs_upgrade:
        log.info("🎉 所有工具都达标，无需升级！")
        return {"upgraded": 0, "total": 0}

    log.info(f"\n📋 {len(needs_upgrade)} 个工具需要升级:")
    for r in needs_upgrade:
        log.info(f"  {'🔴' if r.get('verdict') == 'KILL' else '🟡'} {r.get('tool_name', '?')} — {r.get('overall', '?')}/10 — {r.get('reason', '')[:60]}")

    # 3. 逐个升级
    llm = LLMClient()
    upgraded = []
    to_upgrade = needs_upgrade[:max_upgrades]

    for i, review in enumerate(to_upgrade, 1):
        slug = review.get("tool_slug", "")
        name = review.get("tool_name", slug)
        app_path = os.path.join(os.path.dirname(__file__), "generated_apps", slug)

        log.info(f"\n{'='*40}")
        log.info(f"🔧 [{i}/{len(to_upgrade)}] 升级: {name} (当前 {review.get('overall', '?')}/10)")
        log.info(f"{'='*40}")

        if not os.path.exists(app_path):
            log.warning(f"  ⚠️ 应用目录不存在: {app_path}，跳过")
            continue

        # 升级代码
        success = upgrade_tool(llm, review, app_path)
        if not success:
            continue

        # 编译 + 部署
        if deploy:
            deployed = rebuild_and_deploy(app_path, slug)
            if deployed:
                # 升级后重新评审
                log.info(f"  🔍 重新评审升级后的工具...")
                new_review = review_tool(llm, {
                    "name": name, "slug": slug,
                    "idea": review.get("reason", ""),
                    "app_path": app_path
                })
                new_score = new_review.get("overall", 0)
                old_score = review.get("overall", 0)
                delta = new_score - old_score

                emoji = "📈" if delta > 0 else ("📉" if delta < 0 else "➡️")
                log.info(f"  {emoji} 分数变化: {old_score} → {new_score} ({'+' if delta > 0 else ''}{delta:.1f})")
                upgraded.append({"name": name, "slug": slug, "old": old_score, "new": new_score})
        else:
            log.info(f"  ⏭️ 跳过部署（dry-run 模式）")
            upgraded.append({"name": name, "slug": slug, "old": review.get("overall", 0), "new": "?"})

        if i < len(to_upgrade):
            log.info("  ⏳ 冷却 5 秒...")
            time.sleep(5)

    # 4. 总结
    elapsed = time.time() - start
    log.info(f"\n{'='*60}")
    log.info(f"🏁 升级完毕!")
    log.info(f"  📊 需升级: {len(needs_upgrade)} → 已处理: {len(upgraded)}")
    log.info(f"  ⏱️ 耗时: {elapsed / 60:.1f} 分钟")
    for u in upgraded:
        log.info(f"  {'📈' if u['new'] != '?' and u['new'] > u['old'] else '🔧'} {u['name']}: {u['old']} → {u['new']}")
    log.info(f"{'='*60}")

    # 保存升级报告
    os.makedirs(os.path.join(os.path.dirname(__file__), "logs"), exist_ok=True)
    report_path = os.path.join(os.path.dirname(__file__), "logs",
        f"upgrade_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({"upgraded": upgraded, "elapsed": elapsed}, f, ensure_ascii=False, indent=2)

    return {"upgraded": len(upgraded), "total": len(needs_upgrade)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ShipMicro 工具体检 & 升级")
    parser.add_argument("--max", type=int, default=5, help="最多升级几个工具 (默认5)")
    parser.add_argument("--threshold", type=float, default=7.0, help="升级阈值 (默认7.0)")
    parser.add_argument("--no-deploy", action="store_true", help="只升级代码，不编译部署")
    args = parser.parse_args()

    run_upgrade_cycle(min_score=args.threshold, max_upgrades=args.max, deploy=not args.no_deploy)
