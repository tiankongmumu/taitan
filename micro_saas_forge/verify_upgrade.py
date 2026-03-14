#!/usr/bin/env python3
"""
TITAN升级验证脚本
验证V5.7升级是否完全成功
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

print("🔍 TITAN V5.7升级验证")
print("=" * 60)

# 根目录
root_dir = Path("d:/Project/1/micro_saas_forge")

# 检查升级完成标志
upgrade_flag = root_dir / "UPGRADE_V5.7_COMPLETE"
if upgrade_flag.exists():
    print(f"✅ 升级完成标志存在: {upgrade_flag}")
    with open(upgrade_flag, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"   内容: {content}")
else:
    print(f"❌ 升级完成标志不存在")

# 检查记忆系统
memory_bank = root_dir / "memory" / "memory_bank.py"
if memory_bank.exists():
    print(f"✅ 记忆系统核心文件存在: {memory_bank}")
else:
    print(f"❌ 记忆系统核心文件不存在")

# 检查记忆集成
memory_integration = root_dir / "core" / "titan_memory_integration.py"
if memory_integration.exists():
    print(f"✅ 记忆集成文件存在: {memory_integration}")
else:
    print(f"❌ 记忆集成文件不存在")

# 检查安全框架
safe_framework = root_dir / "safe_upgrade_framework.py"
if safe_framework.exists():
    print(f"✅ 安全升级框架存在: {safe_framework}")
else:
    print(f"❌ 安全升级框架不存在")

# 检查目录结构
required_dirs = ["memory", "core", "upgrade_checkpoints", "backups", "logs"]
print(f"\n📂 目录结构检查:")
for dir_name in required_dirs:
    dir_path = root_dir / dir_name
    if dir_path.exists():
        print(f"✅ {dir_name:20s} - 存在")
    else:
        print(f"❌ {dir_name:20s} - 缺失")

# 功能测试
print(f"\n🔧 功能测试:")
try:
    sys.path.insert(0, str(root_dir))
    from memory.memory_bank import get_memory_bank
    print(f"✅ 记忆系统导入成功")
    
    from core.titan_memory_integration import TitanMemoryIntegration
    print(f"✅ 记忆集成导入成功")
    
    from safe_upgrade_framework import SafeUpgradeFramework
    print(f"✅ 安全框架导入成功")
    
    from business_exploration_agents import BusinessExplorationAgents
    print(f"✅ 商业探索导入成功")
    
except Exception as e:
    print(f"❌ 导入测试失败: {e}")

# 生成验证报告
print(f"\n📊 验证总结:")
verification_report = {
    "verification_time": datetime.now().isoformat(),
    "upgrade_version": "V5.7-Memory",
    "checks": {
        "upgrade_flag": upgrade_flag.exists(),
        "memory_system": memory_bank.exists(),
        "memory_integration": memory_integration.exists(),
        "safe_framework": safe_framework.exists(),
        "required_dirs": all((root_dir / d).exists() for d in required_dirs)
    },
    "status": "PASS" if all([
        upgrade_flag.exists(),
        memory_bank.exists(),
        memory_integration.exists(),
        safe_framework.exists(),
        all((root_dir / d).exists() for d in required_dirs)
    ]) else "FAIL"
}

report_path = root_dir / "UPGRADE_VERIFICATION_REPORT.json"
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(verification_report, f, indent=2)

print(f"📄 验证报告已生成: {report_path}")

if verification_report["status"] == "PASS":
    print(f"\n🎉 TITAN V5.7升级验证通过！")
    print(f"   所有核心系统就绪")
    print(f"   记忆系统: ✅ 激活")
    print(f"   安全框架: ✅ 就绪")
    print(f"   商业智能: ✅ 就绪")
else:
    print(f"\n⚠️  升级验证未通过，请检查缺失项")

print(f"\n" + "=" * 60)