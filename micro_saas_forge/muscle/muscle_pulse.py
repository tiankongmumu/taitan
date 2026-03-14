#!/usr/bin/env python3
"""
TITAN肌肉层脉冲
每5秒输出PULSE信号
"""

import time

def main():
    print("💪 TITAN肌肉层脉冲激活")
    print("📡 信号频率: 每5秒")
    print("-" * 30)
    
    pulse_count = 0
    try:
        while True:
            pulse_count += 1
            print(f"[{time.strftime('%H:%M:%S')}] PULSE #{pulse_count}")
            time.sleep(5)
    except KeyboardInterrupt:
        print(f"\n🛑 脉冲停止 - 总脉冲数: {pulse_count}")

if __name__ == "__main__":
    main()