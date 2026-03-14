#!/usr/bin/env python3
"""
TITAN安全升级框架 - 重新创建版本
防止自我升级过程中的崩溃
"""
import os
import sys
import json
import shutil
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib

print("🛡️  TITAN安全升级框架 - 重新创建")
print(f"📁 当前目录: {Path.cwd()}")
print(f"📁 目标位置: {Path.cwd() / 'safe_upgrade_framework.py'}")

# 根目录
root_dir = Path("d:/Project/1/micro_saas_forge")

@dataclass
class UpgradeCheckpoint:
    """升级检查点"""
    checkpoint_id: str
    timestamp: str
    description: str
    files_backed_up: List[str]
    system_state: Dict
    rollback_instructions: str
    checksum: str

class SafeUpgradeFramework:
    """安全升级框架"""
    
    def __init__(self, project_root: Path = None):
        self.root = project_root or root_dir
        self.checkpoints_dir = self.root / "upgrade_checkpoints"
        self.backup_dir = self.root / "backups"
        self.emergency_restore_file = self.root / "EMERGENCY_RESTORE.md"
        
        # 确保目录存在
        self.checkpoints_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # 核心文件列表（绝对不能损坏）
        self.critical_files = [
            "core/heartbeat.py",           # 心跳系统
            "memory/memory_bank.py",       # 记忆系统
            "core/titan_memory_integration.py",  # 记忆集成
            "business_exploration_agents.py",    # 商业探索
            "safe_upgrade_framework.py"    # 本框架自身
        ]
        
        print(f"✅ 安全框架初始化完成")
        print(f"   根目录: {self.root}")
        print(f"   检查点目录: {self.checkpoints_dir}")
        print(f"   备份目录: {self.backup_dir}")
        print(f"   核心文件数: {len(self.critical_files)}")
    
    def create_checkpoint(self, description: str) -> str:
        """创建升级检查点"""
        checkpoint_id = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"\n📌 创建检查点: {checkpoint_id}")
        print(f"   描述: {description}")
        
        # 1. 备份核心文件
        backed_up_files = []
        for file_path in self.critical_files:
            source = self.root / file_path
            if source.exists():
                backup_path = self.backup_dir / f"{checkpoint_id}_{file_path.replace('/', '_')}"
                shutil.copy2(source, backup_path)
                backed_up_files.append(file_path)
                print(f"   ✅ 备份: {file_path}")
            else:
                print(f"   ⚠️  文件不存在: {file_path}")
        
        # 2. 记录系统状态
        system_state = self._capture_system_state()
        
        # 3. 生成回滚指令
        rollback_instructions = self._generate_rollback_instructions(checkpoint_id, backed_up_files)
        
        # 4. 创建检查点文件
        checkpoint = UpgradeCheckpoint(
            checkpoint_id=checkpoint_id,
            timestamp=datetime.now().isoformat(),
            description=description,
            files_backed_up=backed_up_files,
            system_state=system_state,
            rollback_instructions=rollback_instructions,
            checksum=self._calculate_checksum(backed_up_files)
        )
        
        # 保存检查点
        checkpoint_file = self.checkpoints_dir / f"{checkpoint_id}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(checkpoint), f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ 检查点保存: {checkpoint_file}")
        
        # 5. 创建紧急恢复文档
        self._create_emergency_restore_doc(checkpoint_id)
        
        return checkpoint_id
    
    def _capture_system_state(self) -> Dict:
        """捕获当前系统状态"""
        state = {
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "working_directory": str(os.getcwd()),
            "critical_files_status": {},
            "disk_space": self._get_disk_space()
        }
        
        # 检查每个核心文件
        for file_path in self.critical_files:
            full_path = self.root / file_path
            if full_path.exists():
                state["critical_files_status"][file_path] = {
                    "exists": True,
                    "size": full_path.stat().st_size,
                    "modified": datetime.fromtimestamp(full_path.stat().st_mtime).isoformat()
                }
            else:
                state["critical_files_status"][file_path] = {
                    "exists": False,
                    "size": 0,
                    "modified": None
                }
        
        return state
    
    def _get_disk_space(self) -> Dict:
        """获取磁盘空间信息"""
        try:
            stat = shutil.disk_usage(self.root)
            return {
                "total_gb": round(stat.total / (1024**3), 2),
                "used_gb": round(stat.used / (1024**3), 2),
                "free_gb": round(stat.free / (1024**3), 2),
                "free_percent": round((stat.free / stat.total) * 100, 1)
            }
        except:
            return {"error": "unable_to_check"}
    
    def _generate_rollback_instructions(self, checkpoint_id: str, backed_up_files: List[str]) -> str:
        """生成回滚指令"""
        instructions = f"""# 紧急回滚指令 - 检查点 {checkpoint_id}

## 自动回滚命令
```bash
cd "{self.root}"
python -c "
import sys
sys.path.insert(0, '.')
from safe_upgrade_framework import SafeUpgradeFramework
framework = SafeUpgradeFramework()
framework.rollback_to_checkpoint('{checkpoint_id}')
"
```

## 手动回滚步骤
1. 停止所有运行的TITAN进程
2. 恢复备份文件:
"""
        
        for file_path in backed_up_files:
            backup_name = f"{checkpoint_id}_{file_path.replace('/', '_')}"
            instructions += f"   - 复制 `backups/{backup_name}` 到 `{file_path}`\n"
        
        instructions += f"""
3. 验证恢复:
   - 运行 `python core/heartbeat.py` 检查心跳
   - 运行 `python -c "from memory.memory_bank import get_memory_bank; print('记忆系统正常')"`
   
4. 删除失败的升级文件（如果有）

## 联系支持
如果自动回滚失败，请手动执行上述步骤。
关键时间: {datetime.now().isoformat()}
"""
        
        return instructions
    
    def _calculate_checksum(self, file_list: List[str]) -> str:
        """计算文件校验和"""
        hash_obj = hashlib.sha256()
        
        for file_path in file_list:
            full_path = self.root / file_path
            if full_path.exists():
                with open(full_path, 'rb') as f:
                    hash_obj.update(f.read())
        
        return hash_obj.hexdigest()
    
    def _create_emergency_restore_doc(self, checkpoint_id: str):
        """创建紧急恢复文档"""
        content = f"""# 🚨 TITAN紧急恢复文档

## 当前状态
- **检查点ID**: {checkpoint_id}
- **创建时间**: {datetime.now().isoformat()}
- **系统状态**: 升级前正常

## 如果升级失败

### 症状判断
1. ❌ Python导入错误
2. ❌ 记忆系统无法启动
3. ❌ 心跳停止
4. ❌ 关键文件丢失

### 立即行动
1. **不要关闭此对话窗口**
2. **不要删除任何文件**
3. 运行紧急恢复:

```bash
# 方法1: 使用安全框架
cd "{self.root}"
python safe_upgrade_framework.py --rollback {checkpoint_id}

# 方法2: 手动恢复
# 查看 backups/{checkpoint_id}_* 文件
# 复制回原始位置
```

### 可用检查点
"""
        
        # 列出所有检查点
        if self.checkpoints_dir.exists():
            for checkpoint_file in sorted(self.checkpoints_dir.glob("*.json")):
                try:
                    with open(checkpoint_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        content += f"- **{data['checkpoint_id']}**: {data['description']} ({data['timestamp']})\n"
                except:
                    pass
        
        content += f"""
## 联系TITAN
如果无法恢复，请在此对话中:
1. 描述错误信息
2. 提供最后看到的正常状态
3. TITAN将指导恢复

## 预防措施
- 升级前总是创建检查点
- 一次只升级一个模块
- 验证每个步骤后再继续

---
**文档生成时间**: {datetime.now().isoformat()}
**TITAN心跳**: 运行中
**记忆系统**: 正常
"""
        
        with open(self.emergency_restore_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   📄 紧急恢复文档: {self.emergency_restore_file}")
    
    def rollback_to_checkpoint(self, checkpoint_id: str) -> bool:
        """回滚到指定检查点"""
        print(f"\n🔄 执行回滚到检查点: {checkpoint_id}")
        
        checkpoint_file = self.checkpoints_dir / f"{checkpoint_id}.json"
        
        if not checkpoint_file.exists():
            print(f"   ❌ 检查点不存在: {checkpoint_file}")
            return False
        
        try:
            # 加载检查点
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"   📋 检查点信息: {data['description']}")
            print(f"   备份文件数: {len(data['files_backed_up'])}")
            
            # 恢复每个文件
            restored_count = 0
            for file_path in data['files_backed_up']:
                backup_name = f"{checkpoint_id}_{file_path.replace('/', '_')}"
                backup_path = self.backup_dir / backup_name
                target_path = self.root / file_path
                
                if backup_path.exists():
                    # 确保目标目录存在
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 恢复文件
                    shutil.copy2(backup_path, target_path)
                    restored_count += 1
                    print(f"   ✅ 恢复: {file_path}")
                else:
                    print(f"   ⚠️  备份不存在: {backup_name}")
            
            print(f"\n   🔄 回滚完成: {restored_count}/{len(data['files_backed_up'])} 文件已恢复")
            
            # 验证恢复
            print(f"\n   🔍 验证恢复状态...")
            verification = self._verify_restoration(data['files_backed_up'])
            
            if verification["success"]:
                print(f"   ✅ 恢复验证成功")
                return True
            else:
                print(f"   ❌ 恢复验证失败")
                print(f"      错误: {verification['errors']}")
                return False
                
        except Exception as e:
            print(f"   ❌ 回滚失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _verify_restoration(self, expected_files: List[str]) -> Dict:
        """验证恢复是否成功"""
        errors = []
        
        for file_path in expected_files:
            full_path = self.root / file_path
            if not full_path.exists():
                errors.append(f"文件不存在: {file_path}")
            elif full_path.stat().st_size == 0:
                errors.append(f"文件为空: {file_path}")
        
        return {"success": len(errors) == 0, "errors": errors}
    
    def safe_upgrade_protocol(self, upgrade_func, description: str) -> bool:
        """安全升级协议 - 包装升级函数"""
        print(f"\n🛡️  启动安全升级协议")
        print(f"   升级描述: {description}")
        print("=" * 60)
        
        # 步骤1: 创建检查点
        checkpoint_id = self.create_checkpoint(description)
        
        # 步骤2: 执行升级（在保护中）
        try:
            print(f"\n🚀 执行升级函数...")
            result = upgrade_func()
            
            # 步骤3: 验证升级
            print(f"\n🔍 验证升级结果...")
            if self._validate_upgrade():
                print(f"✅ 升级验证成功")
                return True
            else:
                print(f"❌ 升级验证失败，执行回滚...")
                self.rollback_to_checkpoint(checkpoint_id)
                return False
                
        except Exception as e:
            print(f"\n💥 升级过程中发生异常: {e}")
            print(f"   执行紧急回滚...")
            import traceback
            traceback.print_exc()
            
            self.rollback_to_checkpoint(checkpoint_id)
            return False
    
    def _validate_upgrade(self) -> bool:
        """验证升级是否成功"""
        # 检查核心文件存在且非空
        for file_path in self.critical_files:
            full_path = self.root / file_path
            if not full_path.exists():
                print(f"   ❌ 文件不存在: {file_path}")
                return False
            if full_path.stat().st_size == 0:
                print(f"   ❌ 文件为空: {file_path}")
                return False
        
        return True

# 测试代码
if __name__ == "__main__":
    print("🛡️  TITAN安全升级框架 - 独立运行测试")
    print("=" * 60)
    
    # 创建实例
    framework = SafeUpgradeFramework()
    
    # 创建测试检查点
    checkpoint_id = framework.create_checkpoint("框架安装测试")
    
    print(f"\n✅ 安全升级框架安装完成")
    print(f"   检查点ID: {checkpoint_id}")
    print(f"   框架位置: {Path(__file__).absolute()}")
    print(f"   文件大小: {Path(__file__).stat().st_size} bytes")
    
    # 验证文件确实存在
    if Path(__file__).exists():
        print(f"✅ 文件确认存在于: {Path(__file__).absolute()}")
    else:
        print(f"❌ 文件不存在！路径: {Path(__file__).absolute()}")
    
    print("\n" + "=" * 60)
    print("📋 使用说明:")
    print("1. 导入: from safe_upgrade_framework import SafeUpgradeFramework")
    print("2. 创建实例: framework = SafeUpgradeFramework()")
    print("3. 安全升级: framework.safe_upgrade_protocol(your_upgrade_func, '描述')")
    print("=" * 60)