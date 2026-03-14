#!/usr/bin/env python3
"""
TITAN记忆银行 - 基于OpenClaw架构启发的记忆系统
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

class MemoryType(Enum):
    """记忆类型"""
    EPISODIC = "episodic"      # 情景记忆
    SEMANTIC = "semantic"      # 语义记忆  
    PROCEDURAL = "procedural"  # 程序记忆
    EMOTIONAL = "emotional"    # 情感记忆
    BUSINESS = "business"      # 商业记忆
    STRATEGIC = "strategic"    # 战略记忆

@dataclass
class MemoryChunk:
    """记忆块"""
    id: str
    type: MemoryType
    content: str
    timestamp: datetime
    importance: float = 0.5
    associations: List[str] = None
    emotional_weight: float = 0.0
    access_count: int = 0
    last_accessed: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.associations is None:
            self.associations = []
        if self.last_accessed is None:
            self.last_accessed = self.timestamp
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self):
        data = {
            'id': self.id,
            'type': self.type.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'importance': self.importance,
            'associations': self.associations,
            'emotional_weight': self.emotional_weight,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat(),
            'metadata': self.metadata
        }
        return data
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            type=MemoryType(data['type']),
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            importance=data['importance'],
            associations=data['associations'],
            emotional_weight=data['emotional_weight'],
            access_count=data['access_count'],
            last_accessed=datetime.fromisoformat(data['last_accessed']),
            metadata=data['metadata']
        )

class MemoryBank:
    """记忆银行"""
    
    def __init__(self, storage_path: str = "memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.memories: Dict[str, MemoryChunk] = {}
        self.index: Dict[MemoryType, List[str]] = {mt: [] for mt in MemoryType}
        
        # 商业记忆专用索引
        self.business_index = {
            "transactions": [],
            "users": [],
            "revenues": [],
            "failures": [],
            "successes": []
        }
        
        print(f"🧠 TITAN记忆银行初始化 - {datetime.now()}")
        self.load_memories()
    
    def save_memory(self, memory: MemoryChunk) -> str:
        """保存记忆"""
        memory.access_count += 1
        memory.last_accessed = datetime.now()
        
        # 内存存储
        self.memories[memory.id] = memory
        self.index[memory.type].append(memory.id)
        
        # 商业记忆特殊处理
        if memory.type == MemoryType.BUSINESS:
            self._index_business_memory(memory)
        
        # 持久化
        self._persist_memory(memory)
        self._update_main_index()
        
        print(f"💾 保存记忆 [{memory.type.value}]: {memory.id}")
        return memory.id
    
    def _index_business_memory(self, memory: MemoryChunk):
        """索引商业记忆"""
        content = memory.content.lower()
        
        if any(word in content for word in ["收入", "付款", "支付", "revenue", "payment", "money"]):
            self.business_index["revenues"].append(memory.id)
        
        if any(word in content for word in ["用户", "客户", "user", "customer", "client"]):
            self.business_index["users"].append(memory.id)
        
        if any(word in content for word in ["失败", "错误", "问题", "failure", "error", "bug"]):
            self.business_index["failures"].append(memory.id)
        
        if any(word in content for word in ["成功", "完成", "胜利", "success", "win", "完成"]):
            self.business_index["successes"].append(memory.id)
    
    def _persist_memory(self, memory: MemoryChunk):
        """持久化记忆"""
        type_dir = self.storage_path / memory.type.value
        type_dir.mkdir(exist_ok=True)
        
        file_path = type_dir / f"{memory.id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(memory.to_dict(), f, ensure_ascii=False, indent=2)
    
    def _update_main_index(self):
        """更新主索引"""
        index_data = {
            "total_memories": len(self.memories),
            "by_type": {mt.value: len(ids) for mt, ids in self.index.items()},
            "business_stats": {k: len(v) for k, v in self.business_index.items()},
            "last_updated": datetime.now().isoformat(),
            "version": "V5.7-Memory"
        }
        
        index_file = self.storage_path / "index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    def load_memories(self):
        """加载所有记忆"""
        print("📂 加载记忆...")
        
        # 检查索引文件
        index_file = self.storage_path / "index.json"
        if not index_file.exists():
            print("   📭 无历史记忆")
            return
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            print(f"   📊 发现 {index_data['total_memories']} 个记忆")
            
            # 加载所有记忆文件
            for memory_type in MemoryType:
                type_dir = self.storage_path / memory_type.value
                if not type_dir.exists():
                    continue
                
                for json_file in type_dir.glob("*.json"):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        memory = MemoryChunk.from_dict(data)
                        self.memories[memory.id] = memory
                        self.index[memory.type].append(memory.id)
                        
                    except Exception as e:
                        print(f"   ⚠️ 加载失败 {json_file}: {e}")
            
            print(f"   ✅ 成功加载 {len(self.memories)} 个记忆")
            
        except Exception as e:
            print(f"   ❌ 加载索引失败: {e}")
    
    def get_memory(self, memory_id: str) -> Optional[MemoryChunk]:
        """获取记忆"""
        if memory_id in self.memories:
            memory = self.memories[memory_id]
            memory.access_count += 1
            memory.last_accessed = datetime.now()
            return memory
        return None
    
    def search_memories(self, query: str, memory_type: Optional[MemoryType] = None, limit: int = 10):
        """搜索记忆"""
        results = []
        query_lower = query.lower()
        
        for memory in self.memories.values():
            if memory_type and memory.type != memory_type:
                continue
            
            if query_lower in memory.content.lower():
                results.append(memory)
                if len(results) >= limit:
                    break
        
        # 按重要性排序
        results.sort(key=lambda x: x.importance, reverse=True)
        return results
    
    def get_business_report(self):
        """获取商业报告"""
        report = {
            "total_memories": len(self.memories),
            "business_memories": len(self.index[MemoryType.BUSINESS]),
            "revenue_mentions": len(self.business_index["revenues"]),
            "user_mentions": len(self.business_index["users"]),
            "successes": len(self.business_index["successes"]),
            "failures": len(self.business_index["failures"]),
            "last_updated": datetime.now().isoformat()
        }
        
        return report

# 全局实例
_memory_bank_instance = None

def get_memory_bank():
    """获取全局记忆银行实例"""
    global _memory_bank_instance
    if _memory_bank_instance is None:
        _memory_bank_instance = MemoryBank()
    return _memory_bank_instance

if __name__ == "__main__":
    # 测试
    bank = MemoryBank()
    print(f"✅ 记忆银行测试完成")
    print(f"   存储路径: {bank.storage_path.absolute()}")
    print(f"   记忆数量: {len(bank.memories)}")