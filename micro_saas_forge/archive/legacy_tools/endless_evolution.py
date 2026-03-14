import time
import os

print("=" * 50)
print("🌀 TITAN ENGINE: ENDLESS EVOLUTION LOOP INITIATED 🌀")
print("=" * 50)

count = 1
while True:
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] --- Starting Evolution Cycle {count} ---")
    os.system("python titan_evolution.py")
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] --- Cycle {count} Finished. Cooldown for 60 seconds... ---")
    time.sleep(60)
    count += 1
