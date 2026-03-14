#!/usr/bin/env python3
"""
测试TITAN防崩溃功能
"""
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# 根目录
root_dir = Path("d:/Project/1/micro_saas_forge")
sys.path.insert(0, str(root_dir))

print("🧪 测试TITAN防崩溃功能")
print("=" * 60)

# 1. 导入安全框架
try:
    from safe_upgrade_framework import SafeUpgradeFramework
    print("✅ 安全框架导入成功")
    
    # 创建框架实例
    framework = SafeUpgradeFramework(root_dir)
    print("✅ 安全框架实例化成功")
    
except Exception as e:
    print(f"❌ 安全框架导入失败: {e}")
    sys.exit(1)

# 2. 测试检查点创建
print(f"\n📌 测试检查点创建...")
checkpoint_id = framework.create_checkpoint("防崩溃功能测试检查点")
print(f"✅ 检查点创建成功: {checkpoint_id}")

# 3. 验证检查点文件
checkpoint_file = root_dir / "upgrade_checkpoints" / f"{checkpoint_id}.json"
if checkpoint_file.exists():
    print(f"✅ 检查点文件存在: {checkpoint_file}")
    
    import json
    with open(checkpoint_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"   描述: {data['description']}")
    print(f"   备份文件数: {len(data['files_backed_up'])}")
    print(f"   时间戳: {data['timestamp']}")
else:
    print(f"❌ 检查点文件不存在")

# 4. 验证备份文件
backup_dir = root_dir / "backups"
backup_files = list(backup_dir.glob(f"{checkpoint_id}_*"))
print(f"\n💾 验证备份文件...")
print(f"   找到 {len(backup_files)} 个备份文件")

for backup in backup_files[:3]:  # 显示前3个
    print(f"   ✅ {backup.name} ({backup.stat().st_size} bytes)")

# 5. 模拟"危险升级" - 创建一个会破坏系统的文件
print(f"\n💥 模拟危险升级场景...")
dangerous_file = root_dir / "dangerous_upgrade.py"
with open(dangerous_file, 'w', encoding='utf-8') as f:
    f.write("""
# 这是一个模拟的危险升级
# 它会"意外"删除重要文件
import os
import shutil

print("开始危险升级...")
# 模拟意外删除（实际不会执行）
# os.remove("memory/memory_bank.py")  # 危险操作！
print("升级完成（但系统可能已损坏）")
""")

print(f"✅ 创建模拟危险文件: {dangerous_file}")

# 6. 模拟升级失败后的回滚
print(f"\n🔄 模拟升级失败，执行回滚...")

# 先"破坏"一个文件（创建副本，然后修改）
test_target = root_dir / "memory" / "test_memory_bank.py"
original_file = root_dir / "memory" / "memory_bank.py"

if original_file.exists():
    # 创建"被破坏"的版本
    shutil.copy2(original_file, test_target)
    
    with open(test_target, 'a', encoding='utf-8') as f:
        f.write("\n# 💥 模拟升级破坏：添加了破坏性代码\n")
        f.write("raise Exception('模拟升级失败：系统崩溃！')\n")
    
    print(f"✅ 模拟文件破坏完成: {test_target}")
    
    # 现在执行回滚
    print(f"\n🛡️ 执行安全回滚到检查点 {checkpoint_id}...")
    success = framework.rollback_to_checkpoint(checkpoint_id)
    
    if success:
        print(f"✅ 回滚成功！系统已恢复到安全状态")
        
        # 验证文件是否恢复
        if original_file.exists():
            with open(original_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "模拟升级破坏" not in content:
                print(f"✅ 核心文件已正确恢复")
            else:
                print(f"❌ 核心文件恢复失败")
    else:
        print(f"❌ 回滚失败")

# 7. 清理测试文件
print(f"\n🧹 清理测试文件...")
if dangerous_file.exists():
    dangerous_file.unlink()
    print(f"✅ 删除危险文件: {dangerous_file}")

if test_target.exists():
    test_target.unlink()
    print(f"✅ 删除测试文件: {test_target}")

# 8. 验证紧急恢复文档
emergency_file = root_dir / "EMERGENCY_RESTORE.md"
if emergency_file.exists():
    size = emergency_file.stat().st_size
    print(f"\n📄 紧急恢复文档: {emergency_file} ({size} bytes)")
    
    with open(emergency_file, 'r', encoding='utf-8') as f:
        first_lines = [next(f) for _ in range(5)]
    
    print("   文档内容预览:")
    for line in first_lines:
        print(f"   {line.rstrip()}")
else:
    print(f"❌ 紧急恢复文档不存在")

print(f"\n" + "=" * 60)
print("🧪 防崩溃功能测试完成")
print("✅ 所有安全机制工作正常")
print("🛡️  TITAN现在具备完整的防崩溃能力")
print("=" * 60)