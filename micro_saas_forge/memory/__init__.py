"""
TITAN记忆系统
基于OpenClaw架构启发的记忆系统
"""

from .memory_bank import (
    MemoryBank,
    MemoryChunk,
    MemoryType,
    get_memory_bank
)

__version__ = "1.0.0"
__author__ = "TITAN Engine"
__description__ = "商业AI专用记忆系统"

print(f"🧠 TITAN记忆系统 v{__version__} 已加载")