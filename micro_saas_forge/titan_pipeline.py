"""
TITAN Pipeline — Stage 7: Master Orchestrator
================================================
One-command execution of the full affiliate automation pipeline:

  1. Signal Collector   → Raw signals from Reddit/HN/PH
  2. Signal Validator    → Deduplicated + quality filtered
  3. Opportunity Scorer  → LLM-scored opportunities
  4. Affiliate Injector  → Pain-point ↔ product matches
  5. SEO Content Gen     → 600-800 word articles
  6. Auto Publisher      → Twitter/Reddit distribution content

Usage:
  python titan_pipeline.py               # Full run
  python titan_pipeline.py --dry-run     # Skip LLM calls, test flow
  python titan_pipeline.py --skip-collect # Skip data collection, reuse cached
"""
import os
import sys
import json
import time
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger

log = get_logger("titan_pipeline")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_FILE = os.path.join(BASE_DIR, "demand_signals", "daily_report.json")


class PipelineStage:
    """Represents one stage of the pipeline with timing and error tracking."""
    def __init__(self, name: str, func, skip: bool = False):
        self.name = name
        self.func = func
        self.skip = skip
        self.status = "pending"
        self.duration = 0
        self.output_count = 0
        self.error = None

    def run(self):
        if self.skip:
            self.status = "skipped"
            log.info(f"⏭️  [{self.name}] Skipped")
            return None
        
        log.info(f"▶️  [{self.name}] Starting...")
        start = time.time()
        try:
            result = self.func()
            self.duration = round(time.time() - start, 1)
            self.output_count = len(result) if isinstance(result, (list, dict)) else 0
            self.status = "success"
            log.info(f"✅ [{self.name}] Done in {self.duration}s → {self.output_count} items")
            return result
        except Exception as e:
            self.duration = round(time.time() - start, 1)
            self.status = "failed"
            self.error = str(e)
            log.error(f"❌ [{self.name}] Failed in {self.duration}s: {e}")
            return None


def run_pipeline(dry_run: bool = False, skip_collect: bool = False):
    """Execute the full TITAN affiliate automation pipeline."""
    
    print("=" * 60)
    print("🔥 TITAN AFFILIATE PIPELINE v5.0")
    print("=" * 60)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏷️  Mode: {'DRY RUN' if dry_run else 'PRODUCTION'}")
    print("=" * 60)
    
    pipeline_start = time.time()
    
    # Import stages lazily to catch import errors gracefully
    from signal_collector import collect_all_signals
    from signal_validator import validate_signals
    from opportunity_scorer import score_opportunities
    from affiliate_injector import inject_affiliates, ensure_products_file
    from seo_content_generator import generate_articles
    from auto_publisher import publish
    
    # Ensure affiliate products catalog exists
    ensure_products_file()
    
    # Define pipeline stages
    stages = [
        PipelineStage("1. Signal Collector", collect_all_signals, skip=skip_collect),
        PipelineStage("2. Signal Validator", validate_signals, skip=dry_run),
        PipelineStage("3. Opportunity Scorer", score_opportunities, skip=dry_run),
        PipelineStage("4. Affiliate Injector", inject_affiliates, skip=dry_run),
        PipelineStage("5. SEO Content Gen", generate_articles, skip=dry_run),
        PipelineStage("6. Auto Publisher", publish, skip=dry_run),
    ]
    
    # Execute pipeline
    results = {}
    for stage in stages:
        result = stage.run()
        results[stage.name] = result
        
        # If a critical stage fails, stop
        if stage.status == "failed" and stage.name in ["1. Signal Collector", "2. Signal Validator"]:
            log.error("🛑 Critical stage failed. Aborting pipeline.")
            break
    
    # Generate daily report
    total_time = round(time.time() - pipeline_start, 1)
    
    report = {
        "pipeline_run": {
            "timestamp": datetime.utcnow().isoformat(),
            "mode": "dry_run" if dry_run else "production",
            "total_duration_seconds": total_time,
        },
        "stages": [
            {
                "name": s.name,
                "status": s.status,
                "duration_seconds": s.duration,
                "output_count": s.output_count,
                "error": s.error
            }
            for s in stages
        ],
        "summary": {
            "total_stages": len(stages),
            "successful": sum(1 for s in stages if s.status == "success"),
            "failed": sum(1 for s in stages if s.status == "failed"),
            "skipped": sum(1 for s in stages if s.status == "skipped"),
        }
    }
    
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 PIPELINE EXECUTION REPORT")
    print("=" * 60)
    
    for s in stages:
        icon = {"success": "✅", "failed": "❌", "skipped": "⏭️", "pending": "⏳"}.get(s.status, "?")
        print(f"  {icon} {s.name:30s} {s.status:8s} {s.duration:5.1f}s  ({s.output_count} items)")
    
    print(f"\n  ⏱️  Total time: {total_time}s")
    print(f"  📊 Success: {report['summary']['successful']}/{report['summary']['total_stages']}")
    
    if report['summary']['failed'] == 0 and not dry_run:
        print("\n  🎉 PIPELINE COMPLETE — Check social_posts/ and content_output/ for your money-making content!")
    elif dry_run:
        print("\n  🏷️  DRY RUN complete — no LLM calls made. Run without --dry-run for full execution.")
    else:
        print(f"\n  ⚠️  {report['summary']['failed']} stage(s) failed. Check logs above.")
    
    print(f"  📄 Full report: {REPORT_FILE}")
    print("=" * 60)
    
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TITAN Affiliate Pipeline v5.0")
    parser.add_argument("--dry-run", action="store_true", help="Test flow without LLM calls")
    parser.add_argument("--skip-collect", action="store_true", help="Skip data collection, reuse cached signals")
    args = parser.parse_args()
    
    run_pipeline(dry_run=args.dry_run, skip_collect=args.skip_collect)
