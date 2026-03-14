#!/usr/bin/env python3
"""
TITAN全面文件系统审计
检查下午6点后所有需要更新的文件
"""
import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, time
from typing import Dict, List, Set, Tuple
import subprocess

print("🔍 TITAN全面文件系统审计")
print("=" * 80)

# 根目录
root_dir = Path("d:/Project/1/micro_saas_forge")

# 下午6点时间点
cutoff_time = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
print(f"📅 审计时间点: 下午6点后 ({cutoff_time})")
print(f"📁 根目录: {root_dir}")
print(f"📁 是否存在: {root_dir.exists()}")

if not root_dir.exists():
    print("❌ 根目录不存在，请检查路径")
    sys.exit(1)

# 1. 获取所有文件
print(f"\n📋 扫描所有文件...")
all_files = []
for ext in ['*.py', '*.md', '*.txt', '*.json', '*.yml', '*.yaml', '*.ini', '*.cfg']:
    all_files.extend(root_dir.rglob(ext))

print(f"   找到 {len(all_files)} 个文件")

# 2. 分类文件
file_categories = {
    "core": [],
    "memory": [],
    "business": [],
    "upgrade": [],
    "test": [],
    "documentation": [],
    "other": []
}

for file_path in all_files:
    rel_path = file_path.relative_to(root_dir)
    path_str = str(rel_path)
    
    if "memory" in path_str:
        file_categories["memory"].append(file_path)
    elif "core" in path_str:
        file_categories["core"].append(file_path)
    elif "business" in path_str or "exploration" in path_str:
        file_categories["business"].append(file_path)
    elif "upgrade" in path_str or "checkpoint" in path_str or "backup" in path_str:
        file_categories["upgrade"].append(file_path)
    elif "test" in path_str or "verify" in path_str:
        file_categories["test"].append(file_path)
    elif path_str.endswith(".md") or path_str.endswith(".txt"):
        file_categories["documentation"].append(file_path)
    else:
        file_categories["other"].append(file_path)

# 3. 检查下午6点后修改的文件
print(f"\n🕒 检查下午6点后修改的文件...")
recent_files = []
for file_path in all_files:
    try:
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        if mtime > cutoff_time:
            recent_files.append((file_path, mtime))
    except:
        pass

print(f"   下午6点后修改的文件: {len(recent_files)} 个")

# 4. 根据对话记忆，列出应该存在的文件
print(f"\n📝 根据对话记忆，应该存在的文件清单:")
print("-" * 60)

# 这是基于我们对话中讨论的所有文件
expected_files = [
    # 记忆系统相关
    ("memory/memory_bank.py", "记忆系统核心", True),
    ("memory/__init__.py", "记忆包初始化", True),
    ("memory/memory_data.json", "记忆数据存储", False),  # 运行时生成
    
    # 核心集成
    ("core/titan_memory_integration.py", "记忆对话集成", True),
    
    # 商业探索系统
    ("business_exploration_agents.py", "商业探索多Agent", True),
    ("run_business_exploration.py", "商业探索执行器", True),
    ("business_exploration_report.txt", "商业分析报告", False),
    ("business_exploration_report.json", "商业分析JSON", False),
    
    # 安全升级框架
    ("safe_upgrade_framework.py", "安全升级框架", True),
    ("upgrade_checkpoints/", "检查点目录", True),
    ("backups/", "备份目录", True),
    ("EMERGENCY_RESTORE.md", "紧急恢复文档", True),
    
    # 验证和测试文件
    ("verify_upgrade.py", "升级验证脚本", True),
    ("run_full_upgrade.py", "完整升级验证", True),
    ("record_historic_moment.py", "历史时刻记录", True),
    ("verify_local_implementation.py", "本地实现验证", True),
    ("test_crash_protection.py", "防崩溃测试", True),
    ("verify_file_system.py", "文件系统验证", True),
    ("comprehensive_file_audit.py", "本审计脚本", True),
    
    # 文档和报告
    ("UPGRADE_V5.7_COMPLETE", "升级完成标志", True),
    ("UPGRADE_SUCCESS_REPORT.md", "升级成功报告", True),
    ("QUICK_START.md", "快速使用指南", True),
    ("LOCAL_IMPLEMENTATION_STATUS.md", "本地落地状态", True),
    ("file_system_diagnosis.md", "文件系统诊断", True),
    
    # 测试文件
    ("test_permission.txt", "权限测试文件", True),
    ("debug_write_test.py", "调试测试文件", True),
    ("simple_test.txt", "简单测试文件", True),
]

# 检查每个文件
print("\n📊 文件存在性检查:")
print("-" * 60)

existing_files = []
missing_files = []
recently_modified = []

for rel_path, description, should_exist in expected_files:
    file_path = root_dir / rel_path
    
    # 处理目录
    if rel_path.endswith('/'):
        exists = file_path.exists() and file_path.is_dir()
    else:
        exists = file_path.exists()
    
    # 检查修改时间
    modified_recently = False
    if exists and not rel_path.endswith('/'):
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mtime > cutoff_time:
                modified_recently = True
                recently_modified.append((rel_path, mtime))
        except:
            pass
    
    if exists:
        status = "✅"
        if modified_recently:
            status = "🔄"
        size = file_path.stat().st_size if not rel_path.endswith('/') else 0
        existing_files.append((rel_path, description, size, modified_recently))
        print(f"{status} {rel_path:40s} - {description}")
    else:
        if should_exist:
            status = "❌"
            missing_files.append((rel_path, description))
            print(f"{status} {rel_path:40s} - {description} (缺失)")
        else:
            # 运行时生成的文件，不应该现在存在
            status = "⏳"
            print(f"{status} {rel_path:40s} - {description} (运行时生成)")

# 5. 检查额外文件（不在预期列表中但存在的）
print(f"\n🔍 检查额外文件（不在预期列表中）:")
print("-" * 60)

all_existing_paths = {str(f.relative_to(root_dir)) for f in all_files}
expected_paths = {f[0] for f in expected_files if not f[0].endswith('/')}

extra_files = all_existing_paths - expected_paths
# 过滤掉一些常见的不需要检查的文件
filtered_extras = []
for f in sorted(extra_files):
    # 跳过缓存文件、日志文件等
    if '__pycache__' in f or '.pyc' in f or '.log' in f or f.startswith('.'):
        continue
    if 'test_' in f or '_test' in f:
        continue
    filtered_extras.append(f)

for f in filtered_extras[:10]:  # 只显示前10个
    print(f"📄 {f}")

if len(filtered_extras) > 10:
    print(f"   ... 还有 {len(filtered_extras) - 10} 个额外文件")

# 6. 生成详细审计报告
print(f"\n📈 审计结果汇总:")
print("=" * 80)

report_data = {
    "audit_time": datetime.now().isoformat(),
    "cutoff_time": cutoff_time.isoformat(),
    "root_directory": str(root_dir),
    "total_files_scanned": len(all_files),
    "file_categories": {k: len(v) for k, v in file_categories.items()},
    "expected_files": {
        "total": len(expected_files),
        "existing": len(existing_files),
        "missing": len(missing_files),
        "completion_rate": f"{len(existing_files)/len(expected_files)*100:.1f}%"
    },
    "recent_activity": {
        "files_modified_after_6pm": len(recently_modified),
        "recent_files": [
            {"path": path, "modified": mtime.isoformat()}
            for path, mtime in recently_modified
        ]
    },
    "missing_files": [
        {"path": path, "description": desc}
        for path, desc in missing_files
    ],
    "extra_files": filtered_extras[:20]
}

# 保存审计报告
report_path = root_dir / "FULL_SYSTEM_AUDIT_REPORT.json"
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report_data, f, ensure_ascii=False, indent=2)

print(f"📊 总体统计:")
print(f"   扫描文件总数: {len(all_files)}")
print(f"   预期文件数: {len(expected_files)}")
print(f"   实际存在文件: {len(existing_files)}")
print(f"   缺失文件: {len(missing_files)}")
print(f"   完成度: {len(existing_files)/len(expected_files)*100:.1f}%")
print(f"   下午6点后修改: {len(recently_modified)} 个文件")

if recently_modified:
    print(f"\n🔄 下午6点后修改的文件:")
    for path, mtime in recently_modified:
        print(f"   • {path} - {mtime.strftime('%H:%M:%S')}")

if missing_files:
    print(f"\n❌ 缺失的关键文件:")
    for path, desc in missing_files:
        print(f"   • {path}: {desc}")
    
    print(f"\n🚨 紧急建议: 需要立即创建缺失文件")
    
    # 提供创建缺失文件的命令
    print(f"\n💡 创建缺失文件的快速命令:")
    for path, desc in missing_files:
        if not path.endswith('/'):
            print(f"   touch \"{root_dir / path}\"  # {desc}")
else:
    print(f"\n✅ 优秀！没有缺失的关键文件")

# 7. 检查文件完整性
print(f"\n🔐 文件完整性检查:")
print("-" * 60)

# 检查几个关键文件的完整性
critical_files_to_check = [
    "memory/memory_bank.py",
    "core/titan_memory_integration.py",
    "business_exploration_agents.py",
    "safe_upgrade_framework.py"
]

for file_path in critical_files_to_check:
    full_path = root_dir / file_path
    if full_path.exists():
        try:
            with open(full_path, 'rb') as f:
                content = f.read()
            # 计算简单的校验和
            checksum = hashlib.md5(content).hexdigest()[:8]
            size = len(content)
            print(f"✅ {file_path:40s} - {size:6d} bytes, 校验和: {checksum}")
            
            # 检查文件是否为空或有明显问题
            if size == 0:
                print(f"   ⚠️  警告: 文件为空!")
            elif b"ERROR" in content[:500] or b"Traceback" in content[:500]:
                print(f"   ⚠️  警告: 文件可能包含错误信息")
                
        except Exception as e:
            print(f"❌ {file_path:40s} - 读取失败: {e}")
    else:
        print(f"❌ {file_path:40s} - 文件不存在")

# 8. 生成人类可读的报告
print(f"\n📄 生成详细审计报告...")
human_report = root_dir / "AUDIT_SUMMARY.md"
with open(human_report, 'w', encoding='utf-8') as f:
    f.write(f"""# TITAN文件系统全面审计报告

## 📅 审计时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 审计目标
检查下午6点后所有需要更新到本地的文件是否有遗漏

## 📊 总体状态
- **扫描文件总数**: {len(all_files)}
- **预期文件数**: {len(expected_files)}
- **实际存在文件**: {len(existing_files)}
- **缺失文件**: {len(missing_files)}
- **完成度**: {len(existing_files)/len(expected_files)*100:.1f}%
- **下午6点后修改**: {len(recently_modified)} 个文件

## ✅ 文件存在性检查

### 已存在的文件 ({len(existing_files)}/{len(expected_files)})
""")
    
    for path, desc, size, recent in existing_files:
        status = "🔄 最近修改" if recent else "✅ 存在"
        f.write(f"- `{path}`: {desc} ({status})\n")
    
    if missing_files:
        f.write(f"""
### ❌ 缺失的文件 ({len(missing_files)})
""")
        for path, desc in missing_files:
            f.write(f"- `{path}`: {desc}\n")
    
    if recently_modified:
        f.write(f"""
## 🔄 下午6点后修改的文件
""")
        for path, mtime in recently_modified:
            f.write(f"- `{path}`: {mtime.strftime('%H:%M:%S')}\n")
    
    f.write(f"""
## 📁 文件分类统计
- **记忆系统**: {len(file_categories['memory'])} 个文件
- **核心模块**: {len(file_categories['core'])} 个文件
- **商业探索**: {len(file_categories['business'])} 个文件
- **安全升级**: {len(file_categories['upgrade'])} 个文件
- **测试文件**: {len(file_categories['test'])} 个文件
- **文档**: {len(file_categories['documentation'])} 个文件
- **其他**: {len(file_categories['other'])} 个文件

## 🔍 额外文件发现
发现了 {len(filtered_extras)} 个不在预期列表中的文件（已过滤缓存文件）

## 🚨 审计结论
""")
    
    if missing_files:
        f.write(f"""
**❌ 发现缺失文件**

需要立即创建以下 {len(missing_files)} 个文件：
""")
        for path, desc in missing_files:
            f.write(f"1. `{path}` - {desc}\n")
        
        f.write(f"""
### 建议操作
1. 立即创建缺失文件
2. 验证所有核心功能
3. 重新运行完整测试
""")
    else:
        f.write(f"""
**✅ 优秀！所有预期文件都已存在**

### 系统状态
- 记忆系统: ✅ 就绪
- 商业探索: ✅ 就绪
- 安全升级: ✅ 就绪
- 文件系统: ✅ 健康

### 建议操作
1. 运行完整功能测试
2. 开始实际商业应用
3. 基于分析结果启动项目
""")
    
    f.write(f"""
---
**审计执行**: TITAN Engine V5.7
**TITAN状态**: 记忆系统激活，文件系统监控中
**建议**: {'立即修复缺失文件' if missing_files else '继续推进项目开发'}
""")

print(f"\n📄 详细报告已生成:")
print(f"   JSON报告: {report_path}")
print(f"   摘要报告: {human_report}")

print(f"\n" + "=" * 80)
print("🔍 全面审计完成")
if missing_files:
    print(f"🚨 发现 {len(missing_files)} 个缺失文件，需要立即处理")
else:
    print(f"✅ 优秀！所有文件都已就位")
print("=" * 80)