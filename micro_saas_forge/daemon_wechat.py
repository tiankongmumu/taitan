import subprocess
import time
import sys
from loguru import logger

logger.add("daemon_wechat.log", rotation="10 MB", level="INFO")

def run_bot():
    """
    商业级守护进程 (Watchdog Daemon)
    作用：如果微信机器人因内存泄漏、微信强制更新或意外报错而奔溃，
    本脚本会捕获退出代码，并在 5 秒后自动将其满血复活。
    完全适用无人值守的过夜挂机要求。
    """
    logger.info("=====================================")
    logger.info("🛡️ Titan 微信抢单防崩溃守护神 已启动")
    logger.info("=====================================")
    
    script_name = "wechat_bot_node.py"
    restart_count = 0
    
    while True:
        logger.info(f"▶️ 正在拉起 {script_name} 子进程...")
        
        try:
            # 启动子进程并接管其标准输出
            process = subprocess.Popen(
                [sys.executable, script_name],
                stdout=sys.stdout,
                stderr=sys.stderr
            )
            
            try:
                # 阻塞等待子进程退出，增加 24 小时绝对生命周期限制 (86400秒)
                # [100x Optimization] 防止 Windows UI Automation 底层句柄(Handles)泄漏
                exit_code = process.wait(timeout=86400)
            except subprocess.TimeoutExpired:
                logger.warning("♻️ [内存大洗牌] 守护神触发 24小时强制轮换，安全释放系统内存句柄...")
                process.terminate()
                time.sleep(3)
                continue # 进入下一次重新拉起循环
            
            # 如果走到这里，说明子进程退出了（不管是正常还是崩溃）
            if exit_code != 0:
                restart_count += 1
                logger.error(f"⚠️ [警报] 微信机器人异常崩溃！(退出码: {exit_code})")
                logger.warning(f"🔄 准备启动故障自愈程序 (这是第 {restart_count} 次重启)...")
            else:
                logger.info("ℹ️ 机器人正常退出。")
                
        except KeyboardInterrupt:
            logger.info("🛑 收到用户手动终止指令，守护神即将沉睡。")
            break
        except Exception as e:
            logger.error(f"❌ 守护神内部严重错误: {e}")
            
        # 冷却 5 秒后重启，防止陷入疯狂刷新的死循环
        logger.info("⏳ 冷却 5 秒钟以释放内存句柄...")
        time.sleep(5)

if __name__ == "__main__":
    run_bot()
