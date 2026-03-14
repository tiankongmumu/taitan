#!/usr/bin/env python3
"""
TITAN肌肉层心跳监控
每5秒打印当前心跳计数
"""

import time

class MuscleHeartbeat:
    def __init__(self):
        # 初始心跳计数
        self.heartbeat_count = 1
        print("💓 TITAN肌肉层心跳监控启动")
        print(f"   初始心跳: #{self.heartbeat_count}")
        print(f"   监控间隔: 5秒")
        print("-" * 40)
    
    def start_monitoring(self):
        """启动心跳监控循环"""
        try:
            while True:
                # 打印当前心跳
                print(f"[{time.strftime('%H:%M:%S')}] TITAN心跳 #{self.heartbeat_count}")
                
                # 心跳递增
                self.heartbeat_count += 1
                
                # 等待5秒
                time.sleep(5)
                
        except KeyboardInterrupt:
            print(f"\n🛑 心跳监控停止")
            print(f"最终心跳计数: #{self.heartbeat_count-1}")

# 主程序
if __name__ == "__main__":
    monitor = MuscleHeartbeat()
    monitor.start_monitoring()