#!/usr/bin/env python3
"""
测试文件写入权限
"""
import os
from pathlib import Path

print("🔧 测试文件写入权限...")

# 测试当前工作目录
cwd = os.getcwd()
print(f"当前工作目录: {cwd}")

# 测试根目录
root_dir = "d:/Project/1/micro_saas_forge"
print(f"目标根目录: {root_dir}")

# 检查目录是否存在
if os.path.exists(root_dir):
    print("✅ 根目录存在")
    
    # 尝试创建测试文件
    test_file = os.path.join(root_dir, "test_permission.txt")
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("TITAN文件写入测试 - " + str(os.getpid()))
        print(f"✅ 文件创建成功: {test_file}")
        
        # 读取验证
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ 文件读取成功: {content}")
        
        # 删除测试文件
        os.remove(test_file)
        print("✅ 文件删除成功")
        
    except PermissionError as e:
        print(f"❌ 权限错误: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")
else:
    print(f"❌ 根目录不存在: {root_dir}")
    
    # 尝试创建目录
    try:
        os.makedirs(root_dir, exist_ok=True)
        print(f"✅ 已创建目录: {root_dir}")
    except Exception as e:
        print(f"❌ 无法创建目录: {e}")

print("🔧 测试完成")