"""
ShipMicro Autopilot v3 — Web 4.0 全自治流水线
Pipeline: 资讯 → 精品铸造 → 质量体检 → 社交推广 → 追踪注入 → 广告注入 → CEO仪表盘
"""
import os
import sys
import time
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger

log = get_logger("autopilot")


def run_autopilot(tool_count=3, skip_news=False, skip_forge=False, skip_quality=False, skip_social=False, dry_run=False):
    log.info("=" * 60)
    log.info("🚢 SHIPMICRO AUTOPILOT v3 (Web 4.0 自治引擎)")
    log.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log.info(f"🎯 Pipeline: 资讯 → 铸造(10选{tool_count}) → 质检 → 推广 → 追踪 → 广告 → 仪表盘")
    if dry_run:
        log.info("⚠️  DRY RUN 模式")
    log.info("=" * 60)

    start = time.time()
    results = {"news": None, "forge": None, "quality": None, "social": None}

    # ═══════════════════════════════════════════════
    # STEP 1: 资讯抓取
    # ═══════════════════════════════════════════════
    if not skip_news:
        log.info("\n📰 [1/7] 资讯抓取引擎启动...")
        try:
            from news_scraper import run_news_scraper
            articles = run_news_scraper(max_articles=6)
            results["news"] = f"✅ 生成 {len(articles)} 篇资讯"
        except Exception as e:
            results["news"] = f"❌ 失败: {e}"
            log.error(f"资讯抓取失败: {e}")
    else:
        results["news"] = "⏭️ 已跳过"

    # ═══════════════════════════════════════════════
    # STEP 2: 精品铸造（10选N）
    # ═══════════════════════════════════════════════
    if not skip_forge:
        log.info(f"\n🏭 [2/7] 精品铸造引擎启动 (10 选 {tool_count})...")
        try:
            from daily_forge import run_daily_forge
            forge_results = run_daily_forge(num_tools=tool_count, dry_run=dry_run)
            if dry_run:
                results["forge"] = f"✅ DRY RUN: 精选了 {len(forge_results)} 个点子"
            else:
                success = sum(1 for r in forge_results if r.get("success"))
                results["forge"] = f"✅ 铸造 {success}/{len(forge_results)} 个精品工具"
        except Exception as e:
            results["forge"] = f"❌ 失败: {e}"
            log.error(f"工具铸造失败: {e}")
    else:
        results["forge"] = "⏭️ 已跳过"

    # ═══════════════════════════════════════════════
    # STEP 3: 质量体检
    # ═══════════════════════════════════════════════
    if not skip_quality and not dry_run:
        log.info("\n🔍 [3/7] AI 质量评审启动...")
        try:
            from quality_gate import run_quality_gate
            qr = run_quality_gate()
            ship = len(qr.get("ship", []))
            improve = len(qr.get("improve", []))
            kill = len(qr.get("kill", []))
            results["quality"] = f"✅ SHIP:{ship} IMPROVE:{improve} KILL:{kill}"
            if kill > 0:
                log.warning(f"⚠️ {kill} 个工具被建议下架！")
                for k in qr["kill"]:
                    log.warning(f"  🔴 {k.get('tool_name', '?')} — {k.get('reason', '')}")
        except Exception as e:
            results["quality"] = f"❌ 失败: {e}"
            log.error(f"质量体检失败: {e}")
    else:
        results["quality"] = "⏭️ 已跳过" if skip_quality else "⏭️ DRY RUN 跳过"

    # ═══════════════════════════════════════════════
    # STEP 4: 社交推广
    # ═══════════════════════════════════════════════
    if not skip_social and not dry_run:
        log.info("\n📢 [4/7] 社交推广引擎启动...")
        try:
            import asyncio
            from social_distributor import run_social_distributor
            posts = asyncio.run(run_social_distributor())
            if posts:
                results["social"] = f"✅ 生成 {len(posts)} 套推广帖"
            else:
                results["social"] = "⚠️ 无可推广的工具"
        except Exception as e:
            results["social"] = f"❌ 失败: {e}"
            log.error(f"社交推广失败: {e}")
    else:
        results["social"] = "⏭️ 已跳过" if skip_social else "⏭️ DRY RUN 跳过"

    # ═══════════════════════════════════════════════
    # STEP 5: 📊 分析追踪注入 (NEW in v3)
    # ═══════════════════════════════════════════════
    if not dry_run:
        log.info("\n📊 [5/7] 分析追踪代码注入...")
        try:
            from analytics_tracker import inject_analytics_into_page
            apps_dir = os.path.join(os.path.dirname(__file__), "generated_apps")
            if os.path.isdir(apps_dir):
                injected = 0
                for app_name in os.listdir(apps_dir):
                    app_path = os.path.join(apps_dir, app_name)
                    page_path = os.path.join(app_path, "src", "app", "page.tsx")
                    if os.path.exists(page_path):
                        if inject_analytics_into_page(page_path, app_name):
                            injected += 1
                results["analytics"] = f"✅ {injected} 个工具已注入追踪"
        except Exception as e:
            results["analytics"] = f"❌ 失败: {e}"
            log.error(f"追踪注入失败: {e}")
    else:
        results["analytics"] = "⏭️ DRY RUN 跳过"

    # ═══════════════════════════════════════════════
    # STEP 6: 💰 广告代码注入 (NEW in v3)
    # ═══════════════════════════════════════════════
    if not dry_run:
        log.info("\n💰 [6/7] AdSense 广告注入...")
        try:
            from ad_injector import inject_ads_into_all
            inject_ads_into_all()
            results["ads"] = "✅ 广告已注入"
        except Exception as e:
            results["ads"] = f"❌ 失败: {e}"
            log.error(f"广告注入失败: {e}")
    else:
        results["ads"] = "⏭️ DRY RUN 跳过"

    # ═══════════════════════════════════════════════
    # STEP 7: 📊 CEO 仪表盘 (NEW in v3)
    # ═══════════════════════════════════════════════
    log.info("\n📊 [7/7] CEO 仪表盘...")
    try:
        from dashboard import run_dashboard
        run_dashboard()
        results["dashboard"] = "✅ 已输出"
    except Exception as e:
        results["dashboard"] = f"❌ 失败: {e}"

    # ═══════════════════════════════════════════════
    # 总结报告
    # ═══════════════════════════════════════════════
    elapsed = time.time() - start
    log.info(f"\n{'='*60}")
    log.info("🏁 SHIPMICRO AUTOPILOT v3 执行完毕")
    log.info(f"⏱️  总耗时: {elapsed / 60:.1f} 分钟")
    log.info(f"📰 资讯: {results.get('news', '-')}")
    log.info(f"🏭 铸造: {results.get('forge', '-')}")
    log.info(f"🔍 质检: {results.get('quality', '-')}")
    log.info(f"📢 推广: {results.get('social', '-')}")
    log.info(f"📊 追踪: {results.get('analytics', '-')}")
    log.info(f"💰 广告: {results.get('ads', '-')}")
    log.info(f"📊 仪表: {results.get('dashboard', '-')}")
    log.info("=" * 60)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ShipMicro Autopilot v3 (Web 4.0 自治引擎)")
    parser.add_argument("--count", type=int, default=3, help="每日精选工具数量 (默认3)")
    parser.add_argument("--dry-run", action="store_true", help="仅评分筛选，不实际部署")
    parser.add_argument("--skip-news", action="store_true", help="跳过资讯抓取")
    parser.add_argument("--skip-forge", action="store_true", help="跳过工具铸造")
    parser.add_argument("--skip-quality", action="store_true", help="跳过质量体检")
    parser.add_argument("--skip-social", action="store_true", help="跳过社交推广")
    args = parser.parse_args()

    run_autopilot(
        tool_count=args.count,
        skip_news=args.skip_news,
        skip_forge=args.skip_forge,
        skip_quality=args.skip_quality,
        skip_social=args.skip_social,
        dry_run=args.dry_run
    )
