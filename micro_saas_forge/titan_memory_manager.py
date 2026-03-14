"""
TITAN Memory Manager (The Hippocampus) 🧠
Manages Episodic (Event Stream) and Semantic (RAG) memory tiers.
Enables coherent long-term memory across cycles.
"""

import os
import json
from datetime import datetime
from pathlib import Path
import logging

# Ensure absolute paths for local imports
sys_path = os.path.dirname(os.path.abspath(__file__))
if sys_path not in sys.path:
    import sys
    sys.path.insert(0, sys_path)

from titan_config import FORGE_DIR, LOG_DIR

log = logging.getLogger("memory_manager")

class TitanMemoryManager:
    def __init__(self):
        self.memory_dir = Path(FORGE_DIR) / "memory"
        self.memory_dir.mkdir(exist_ok=True)
        
        self.event_stream_file = self.memory_dir / "titan_event_stream.jsonl"
        self.identity_file = self.memory_dir / "titan_identity.json"
        
    def log_event(self, category: str, summary: str, details: dict = None):
        """记录一个『情节记忆』时间片段 (Episodic Memory)"""
        event = {
            "ts": datetime.now().isoformat(),
            "category": category, # e.g., 'deployment', 'scholarship', 'failure'
            "summary": summary,
            "details": details or {},
        }
        
        try:
            with open(self.event_stream_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
            log.info(f"🧠 Recorded episodic memory: {summary}")
        except Exception as e:
            log.error(f"Failed to log episodic memory: {e}")

    def get_recent_events(self, limit: int = 10) -> list[dict]:
        """获取最近发生的事件片段"""
        if not self.event_stream_file.exists():
            return []
            
        events = []
        try:
            with open(self.event_stream_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    events.append(json.loads(line))
        except Exception as e:
            log.error(f"Failed to read events: {e}")
            
        return events

    def update_identity(self, goals: list[str], personality: str = None):
        """更新泰坦的『同一性』缓存，确保跨周期目标一致性"""
        identity = {
            "updated_at": datetime.now().isoformat(),
            "active_goals": goals,
            "personality_traits": personality or "Analytical, Ambitious, Autonomous",
        }
        
        try:
            with open(self.identity_file, "w", encoding="utf-8") as f:
                json.dump(identity, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log.error(f"Failed to update identity: {e}")

    def get_context_for_brain(self) -> str:
        """为 Brain 周期生成记忆上下文片段"""
        events = self.get_recent_events(5)
        if not events:
            return "No recent episodic memories."
            
        context = "RECENT EPISODIC MEMORIES (Last 5 events):\n"
        for e in events:
            context += f"- [{e['ts'][:16]}] {e['category'].upper()}: {e['summary']}\n"
            
        return context

if __name__ == "__main__":
    # Test
    manager = TitanMemoryManager()
    manager.log_event("initialization", "Memory Core v1.0 activated.")
    print(manager.get_context_for_brain())
