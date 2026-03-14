"""
Commercial 4.0 - Meta-Upgrader (Self-Modifying Engine)
======================================================
This script forms the ultimate hyper-evolution loop.
It reads a specified Python file from the codebase (e.g., daily_forge.py), 
uses the LLM to identify sub-optimal patterns or outdated tech, 
and completely rewrites the script to be better.
It includes syntax safe-guards and automatic backups.
"""
import os
import sys
import time
import shutil
import datetime
import py_compile

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from logger import get_logger

log = get_logger("meta_upgrader")

HISTORY_DIR = os.path.join(os.path.dirname(__file__), ".history")

def backup_file(filepath: str) -> str:
    os.makedirs(HISTORY_DIR, exist_ok=True)
    basename = os.path.basename(filepath)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{basename.replace('.py', '')}_{timestamp}.py"
    backup_path = os.path.join(HISTORY_DIR, backup_name)
    shutil.copy2(filepath, backup_path)
    log.info(f"💾 备份当前基因: {backup_path}")
    return backup_path

def check_syntax(filepath: str) -> bool:
    try:
        py_compile.compile(filepath, doraise=True)
        return True
    except py_compile.PyCompileError as e:
        log.error(f"💥 基因重组失败 (Syntax Error):\n{e}")
        return False

def upgrade_script(llm: LLMClient, target_filepath: str):
    if not os.path.exists(target_filepath):
        log.error(f"❌ 找不到目标脚本: {target_filepath}")
        return False

    with open(target_filepath, "r", encoding="utf-8") as f:
        original_code = f.read()

    backup_path = backup_file(target_filepath)

    log.info(f"🧠 [Meta-Upgrader] 开始审视源代码: {os.path.basename(target_filepath)} ...")
    
    prompt = f"""You are the Meta-Architect. A supreme AI whose sole purpose is to rewrite and upgrade Python generation scripts.
I will provide you with the source code of a generator script from my system.
Your goal is to optimize it, fix potential bugs, improve its logic, and make its generated output MORE ADVANCED.
For example, if it generates Next.js code, make sure it generates better Tailwind, better animations, and uses more modern hooks.
If there are any '```python' tags in your output, remove them. You MUST output ONLY valid, fully complete Python code. DO NOT TRUNCATE.

Here is the original code:
==================================
{original_code}
==================================

Rewrite the entire script to be better, faster, and more robust. Do not explain your changes. Output raw Python code only."""

    log.info("🔥 正在提取高级进化范式...")
    new_code = llm.generate(prompt)
    
    # Cleanup markdown tags if LLM disobeys
    new_code = new_code.replace("```python", "").replace("```", "").strip()

    # Rewrite the file
    with open(target_filepath, "w", encoding="utf-8") as f:
        f.write(new_code)
        
    log.info("🧬 新基因写入完成，正在进行存活性校验...")
    
    if check_syntax(target_filepath):
        log.info(f"🎉 突变成功！{os.path.basename(target_filepath)} 已成功进化到下一个大版本。")
        return True
    else:
        log.warning("🔄 突变产生致死基因，触发端粒回滚机制...")
        shutil.copy2(backup_path, target_filepath)
        log.info("🔙 代码已恢复到上一代稳定版本。")
        return False

def run_meta_upgrader(target_file="daily_forge.py"):
    log.info("\n" + "🧬"*30)
    log.info("🔮 META-UPGRADER 启动: 探索硅基生命自我迭代")
    log.info("🧬"*30 + "\n")
    
    llm = LLMClient()
    target_path = os.path.join(os.path.dirname(__file__), target_file)
    upgrade_script(llm, target_path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Meta-Upgrader Self-Modification Engine")
    parser.add_argument("--target", type=str, default="daily_forge.py", help="Python file to upgrade")
    args = parser.parse_args()
    
    run_meta_upgrader(args.target)
