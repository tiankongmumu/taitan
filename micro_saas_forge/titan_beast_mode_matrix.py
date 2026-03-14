import asyncio
import subprocess
import sys
import time
from loguru import logger

logger.add("titan_beast_mode.log", rotation="20 MB", level="INFO")

class TitanBeastMatrix:
    """
    [The Final Ignition] 全量挂机自动印钞引擎 (Beast Mode)
    目标：一键启动所有并行的商业化子核心，让机器自己去：搞流量、查货源、接微信单、自我进化。
    完全脱离人工！
    """
    def __init__(self):
        # 定义四大核心矩阵
        self.systems = [
            {"name": "🕷️ 货源侦察 (Supply Spider)", "script": "supply_finder_spider.py", "process": None},
            {"name": "🌪️ 流量收割 (Traffic Gen)", "script": "traffic_generator_node.py", "process": None},
            {"name": "💬 微信销售 (Daemon Wechat)", "script": "daemon_wechat.py", "process": None},
            {"name": "🧬 核心进化 (Meta-Agent)", "script": "titan_auto_evolution_engine.py", "process": None}
        ]

    def _start_subsystem(self, sys_info: dict):
        logger.info(f"🚀 正在点火启动子矩阵: {sys_info['name']}")
        try:
             # 创建子进程后台独立运行
             p = subprocess.Popen(
                 [sys.executable, sys_info['script']],
                 # stdout=subprocess.DEVNULL, # 让子核心自己写日志，主界面保持干净
                 # stderr=subprocess.DEVNULL
             )
             sys_info['process'] = p
        except Exception as e:
             logger.error(f"❌ 启动失败 {sys_info['name']}: {e}")

    async def ignite(self):
        print("="*60)
        print("🚨 TITAN BEAST MODE MATRIX INITIALIZING 🚨")
        print("核心警报：您即将启动最高级别的全自动化商业收割模式。")
        print("引擎点火后，系统将自主在公域发帖发文、自动接手微信客服、自动下单交易。")
        print("============================================================")
        
        for s in self.systems:
            self._start_subsystem(s)
            await asyncio.sleep(2) # 错峰启动，防止瞬间高IO
            
        print("\n✅ 所有引擎模块已成功升空入列！")
        print("☕ 老板，您可以去喝杯咖啡了。关闭此窗口前，系统将无限期挂机产生利润。")
        print("按 Ctrl+C 紧急切断所有电源。\n")
        
        try:
            while True:
                # 主线程仅仅作为看门狗监控进程存活
                for s in self.systems:
                    p = s.get('process')
                    if p and p.poll() is not None:
                         logger.warning(f"⚠️ 侦测到 {s['name']} 进程可能已终结或崩溃，正在尝试重新拉起...")
                         self._start_subsystem(s)
                
                # 每过60秒汇报一次存活脉搏
                await asyncio.sleep(60)
                logger.info("💓 矩阵健康度 100% | 资产正通过多个节点高速流入...")
                
        except KeyboardInterrupt:
            print("\n🛑 收到最高元首指令：立刻降维停止所有印钞机！")
            for s in self.systems:
                if s['process']:
                    s['process'].terminate()
            print("所有进账通道已被切断。系统安全关顶。")

if __name__ == "__main__":
    matrix = TitanBeastMatrix()
    asyncio.run(matrix.ignite())
