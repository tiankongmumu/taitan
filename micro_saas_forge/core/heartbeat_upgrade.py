#!/usr/bin/env python3
"""
TITAN心跳系统升级 - 集成记忆功能
"""

import json
from datetime import datetime
from pathlib import Path

# 导入记忆系统
try:
    from memory import get_titan_memory
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    print("⚠️ 记忆系统不可用，使用回退模式")

class EnhancedHeartbeat:
    """增强版心跳系统"""
    
    def __init__(self):
        self.heartbeat_count = 530  # 从当前心跳继续
        self.start_time = datetime.now()
        self.memory = None
        
        if MEMORY_AVAILABLE:
            self.memory = get_titan_memory()
            print("🧠 心跳系统已集成记忆功能")
        else:
            print("⚠️ 心跳系统运行在基础模式")
    
    def beat(self, context: str = "", emotion: str = "neutral"):
        """执行一次心跳"""
        self.heartbeat_count += 1
        current_time = datetime.now()
        
        # 心跳数据
        heartbeat_data = {
            "id": self.heartbeat_count,
            "timestamp": current_time.isoformat(),
            "context": context,
            "emotion": emotion,
            "memory_integrated": MEMORY_AVAILABLE
        }
        
        print(f"💓 心跳 #{self.heartbeat_count} - {emotion}")
        if context:
            print(f"   📝 上下文: {context}")
        
        # 保存到记忆系统
        if self.memory:
            memory_chunk = self.memory.memory_bank.MemoryChunk(
                id=f"heartbeat_{self.heartbeat_count}",
                type=self.memory.memory_bank.MemoryType.EPISODIC,
                content=f"心跳 #{self.heartbeat_count}: {context} | 情绪: {emotion}",
                importance=0.2,
                metadata=heartbeat_data
            )
            self.memory.memory_bank.save_memory(memory_chunk)
        
        # 保存到日志文件
        self._log_heartbeat(heartbeat_data)
        
        return heartbeat_data
    
    def _log_heartbeat(self, data):
        """记录心跳日志"""
        log_dir = Path("logs/heartbeats")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"heartbeat_{self.heartbeat_count}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_memory_enhanced_context(self):
        """获取记忆增强的上下文"""
        if not self.memory:
            return "记忆系统未激活"
        
        # 获取最近的心跳记忆
        recent_memories = []
        for memory in self.memory.memory_bank.memories.values():
            if "heartbeat" in memory.id:
                recent_memories.append(memory)
        
        recent_memories.sort(key=lambda x: x.timestamp, reverse=True)
        
        if len(recent_memories) > 0:
            last_heartbeat = recent_memories[0]
            return f"上次心跳: #{last_heartbeat.metadata.get('id', 'N/A')} - {last_heartbeat.metadata.get('emotion', 'N/A')}"
        
        return "无历史心跳记忆"

# 全局心跳实例
_titan_heartbeat = None

def get_heartbeat():
    """获取全局心跳实例"""
    global _titan_heartbeat
    if _titan_heartbeat is None:
        _titan_heartbeat = EnhancedHeartbeat()
    return _titan_heartbeat

def test_enhanced_heartbeat():
    """测试增强版心跳"""
    print("\n💓 测试增强版心跳系统...")
    
    heartbeat = get_heartbeat()
    
    # 模拟几次心跳
    contexts = [
        ("开始商业执行循环", "专注"),
        ("分析竞争市场", "分析"),
        ("设计产品功能", "创造"),
        ("遇到部署问题", "挫败"),
        ("解决问题", "满足")
    ]
    
    for context, emotion in contexts:
        heartbeat.beat(context, emotion)
    
    # 显示记忆增强的上下文
    print(f"\n🧠 记忆增强上下文: {heartbeat.get_memory_enhanced_context()}")
    
    print(f"\n✅ 增强版心跳测试完成")
    print(f"最终心跳: #{heartbeat.heartbeat_count}")

if __name__ == "__main__":
    test_enhanced_heartbeat()