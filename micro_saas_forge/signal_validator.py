"""
TITAN Pipeline — Stage 2: Signal Validator
============================================
Validates and filters raw signals:
  - Deduplication (title similarity > 80%)
  - Quality filter (score < 5 or text too short → discard)
  - Language filter (keep English only)

Input:  demand_signals/raw_signals.json
Output: demand_signals/validated_signals.json
"""
import os
import sys
import json
import re
from typing import List, Dict

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger

log = get_logger("signal_validator")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNALS_DIR = os.path.join(BASE_DIR, "demand_signals")
INPUT_FILE = os.path.join(SIGNALS_DIR, "raw_signals.json")
OUTPUT_FILE = os.path.join(SIGNALS_DIR, "validated_signals.json")

# Thresholds
MIN_SCORE = 3           # Minimum upvotes/points to keep
MIN_TITLE_LEN = 10      # Minimum title length (chars)
SIMILARITY_THRESHOLD = 0.8  # Title similarity for dedup


def _normalize(text: str) -> str:
    """Normalize text for comparison."""
    return re.sub(r"[^a-z0-9\s]", "", text.lower().strip())


def _jaccard_similarity(a: str, b: str) -> float:
    """Compute Jaccard similarity between two strings (word-level)."""
    set_a = set(_normalize(a).split())
    set_b = set(_normalize(b).split())
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def _is_english(text: str) -> bool:
    """Quick heuristic: if >60% of characters are ASCII letters, treat as English."""
    if not text:
        return True  # Empty text is fine
    ascii_chars = sum(1 for c in text if c.isascii() and c.isalpha())
    total_alpha = sum(1 for c in text if c.isalpha())
    if total_alpha == 0:
        return True
    return ascii_chars / total_alpha > 0.6


def deduplicate(signals: List[Dict]) -> List[Dict]:
    """Remove near-duplicate signals based on title similarity."""
    if not signals:
        return []
    
    unique = [signals[0]]
    dupes = 0
    
    for signal in signals[1:]:
        is_dupe = False
        for existing in unique:
            sim = _jaccard_similarity(signal["title"], existing["title"])
            if sim >= SIMILARITY_THRESHOLD:
                is_dupe = True
                # Keep the one with higher score
                if signal.get("score", 0) > existing.get("score", 0):
                    unique.remove(existing)
                    unique.append(signal)
                dupes += 1
                break
        if not is_dupe:
            unique.append(signal)
    
    if dupes > 0:
        log.info(f"  🔄 Removed {dupes} duplicates")
    return unique


def filter_quality(signals: List[Dict]) -> List[Dict]:
    """Filter out low-quality signals."""
    filtered = []
    dropped = {"low_score": 0, "short_title": 0, "non_english": 0}
    
    for s in signals:
        # Score filter
        if s.get("score", 0) < MIN_SCORE:
            dropped["low_score"] += 1
            continue
        
        # Title length filter
        if len(s.get("title", "")) < MIN_TITLE_LEN:
            dropped["short_title"] += 1
            continue
        
        # Language filter
        if not _is_english(s.get("title", "")):
            dropped["non_english"] += 1
            continue
        
        filtered.append(s)
    
    for reason, count in dropped.items():
        if count > 0:
            log.info(f"  🗑️ Dropped {count} signals ({reason})")
    
    return filtered


def validate_signals(signals: List[Dict] = None) -> List[Dict]:
    """Run full validation pipeline on signals."""
    log.info("=" * 50)
    log.info("🔍 TITAN Signal Validator v5.0 — Starting")
    log.info("=" * 50)
    
    # Load from file if not provided
    if signals is None:
        if not os.path.exists(INPUT_FILE):
            log.error(f"Input file not found: {INPUT_FILE}")
            return []
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        signals = data.get("signals", data if isinstance(data, list) else [])
    
    log.info(f"📥 Input: {len(signals)} raw signals")
    
    # Step 1: Quality filter
    signals = filter_quality(signals)
    log.info(f"  → After quality filter: {len(signals)}")
    
    # Step 2: Deduplicate
    signals = deduplicate(signals)
    log.info(f"  → After dedup: {len(signals)}")
    
    # Step 3: Sort by score (highest first)
    signals.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    # Save
    output = {
        "metadata": {
            "validated_count": len(signals),
            "sources": list(set(s["source"] for s in signals))
        },
        "signals": signals
    }
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    log.info(f"✅ Validated {len(signals)} signals → {OUTPUT_FILE}")
    return signals


if __name__ == "__main__":
    validated = validate_signals()
    print(f"\n📊 Validated: {len(validated)} signals")
    for s in validated[:5]:
        print(f"  [{s['score']:>5}] [{s['source']}] {s['title'][:60]}")
