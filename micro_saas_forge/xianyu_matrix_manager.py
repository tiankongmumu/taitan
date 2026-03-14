import random
import time
from datetime import datetime, timedelta
from loguru import logger as log

log.add("logs/xianyu_matrix.log", rotation="5 MB", level="INFO")

class MatrixManager:
    def __init__(self):
        # Physical goods camouflage to dilute the virtual goods ratio (3:1)
        self.cover_items = [
            {"title": "考研英语二历年真题及解析，基本全新", "price": 15.0, "type": "physical"},
            {"title": "自用的小米蓝牙耳机，右耳有点杂音", "price": 35.0, "type": "physical"},
            {"title": "公司发的机械键盘，青轴，带侧刻", "price": 50.0, "type": "physical"},
            {"title": "闲置的电脑支架，铝合金的", "price": 20.0, "type": "physical"},
            {"title": "一套尤克里里，买来没弹过基础教程", "price": 40.0, "type": "physical"},
            {"title": "健身卡转让，还剩半年", "price": 300.0, "type": "physical"},
            {"title": "各种闲置小说，打包带走", "price": 25.0, "type": "physical"}
        ]
        
        # Our main virtual products
        self.core_items = [
            {"title": "OpenClaw本地专属配置包提速辅助", "price": 9.9, "type": "virtual"},
            {"title": "AI程序员部署环境加速节点大全", "price": 15.9, "type": "virtual"},
            {"title": "独立开发者必备：本地环境配置文件包", "price": 5.0, "type": "virtual"}
        ]
        
    def generate_publishing_schedule(self, target_date: datetime):
        """
        Generate a daily schedule for posting items.
        Avoids 1:00-6:00 AM (TITAN Engine evolution phase).
        Rotates 3 physical and 1 virtual good per day.
        """
        log.info(f"🗓️ Generating publishing schedule for {target_date.strftime('%Y-%m-%d')}")
        
        # Select items for the day
        todays_items = random.sample(self.cover_items, 3) + random.sample(self.core_items, 1)
        random.shuffle(todays_items) 
        
        # Define 4 safe time slots
        slots = [
            target_date.replace(hour=random.randint(8, 11), minute=random.randint(0, 59)),
            target_date.replace(hour=random.randint(12, 14), minute=random.randint(0, 59)),
            target_date.replace(hour=random.randint(17, 19), minute=random.randint(0, 59)),
            target_date.replace(hour=random.randint(20, 23), minute=random.randint(0, 59))
        ]
        slots.sort()
        
        schedule = []
        for i, item in enumerate(todays_items):
            schedule.append({
                "time": slots[i],
                "item": item
            })
            
        for s in schedule:
            log.info(f"[{s['time'].strftime('%H:%M')}] Publish {s['item']['type'].upper()} ITEM: {s['item']['title']} (￥{s['item']['price']})")
            
        return schedule


if __name__ == "__main__":
    import sys
    manager = MatrixManager()
    
    if "--test" in sys.argv:
        manager.generate_publishing_schedule(datetime.now())
