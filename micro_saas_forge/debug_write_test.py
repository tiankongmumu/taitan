#!/usr/bin/env python3
"""
紧急诊断：文件写入测试
"""
import os
import sys
from pathlib import Path
import traceback

print("🔧 紧急诊断开始...")
print("=" * 60)

# 1. 检查当前工作目录
cwd = os.getcwd()
print(f"1. 当前工作目录: {cwd}")

# 2. 检查目标目录
target_dir = "d:/Project/1/micro_saas_forge"
print(f"2. 目标目录: {target_dir}")
print(f"   目录存在: {os.path.exists(target_dir)}")

# 3. 尝试创建简单文件
test_file = os.path.join(target_dir, "debug_test.txt")
print(f"3. 测试文件: {test_file}")

try:
    # 尝试写入
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(f"TITAN调试测试\n时间: {os.times()}\nPID: {os.getpid()}")
    
    print(f"   ✅ 文件写入成功")
    
    # 验证读取
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"   ✅ 文件读取成功: {content[:50]}...")
    
    # 删除测试文件
    os.remove(test_file)
    print(f"   ✅ 文件删除成功")
    
except Exception as e:
    print(f"   ❌ 写入失败: {e}")
    print(f"   错误详情:")
    traceback.print_exc()

# 4. 检查目录权限
print(f"\n4. 目录权限检查:")
try:
    # 列出目标目录内容
    if os.path.exists(target_dir):
        items = os.listdir(target_dir)
        print(f"   目录内容 ({len(items)} 项):")
        for item in items[:10]:  # 只显示前10个
            print(f"     - {item}")
        if len(items) > 10:
            print(f"     ... 还有 {len(items)-10} 项")
    else:
        print(f"   ❌ 目录不存在")
        
except Exception as e:
    print(f"   ❌ 列出目录失败: {e}")

# 5. 检查Python环境
print(f"\n5. Python环境:")
print(f"   Python版本: {sys.version}")
print(f"   可执行文件: {sys.executable}")
print(f"   路径: {sys.path[:3]}...")

# 6. 检查之前创建的测试文件
previous_test = os.path.join(target_dir, "test_permission.txt")
print(f"\n6. 之前测试文件: {previous_test}")
print(f"   文件存在: {os.path.exists(previous_test)}")

print("\n🔧 诊断完成")