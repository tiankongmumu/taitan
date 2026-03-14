import time
import re
import pyautogui
import pyperclip
import random
from loguru import logger as log

# Setup logging
log.add("logs/xianyu_sales_bot.log", rotation="5 MB", level="INFO")

class XianyuSalesBot:
    def __init__(self):
        self.reply_interval = 2 # Check more frequently for RPA
        log.info("🚀 Xianyu Auto Sales Bot Initialized (PyAutoGUI Mode)")
        
        # We assume the user has left the PC Xianyu chat window open and active on the screen.
        # For a more robust approach, we would use image recognition to find the chat box.
        # self.chat_box_img = "assets/chat_box.png"
        
    def get_delivery_link_xhs(self) -> str:
        """Returns the delivery link for Product 1 (XHS Publisher)."""
        return "地址: https://pan.baidu.com/s/1xyz_mock_link_xhs 提取: 8888"

    def get_delivery_link_extractor(self) -> str:
        """Returns the delivery link for Product 2 (Video Extractor)."""
        return "地址: https://pan.baidu.com/s/1xyz_mock_link_video 提取: 6666"

    def process_message(self, text: str) -> str:
        """Determine what to reply based on the buyer's message."""
        text = text.upper().strip()
        
        clean_text = text.replace("-", "").replace(" ", "")
        
        # Scenario 1: Buyer mentions payment, order number, or directly asks for the tutorial/code
        if any(keyword in text for keyword in ["已拍", "付款", "单号", "发货", "链接", "教程", "发我"]):
            # Check which product they bought based on context (if they mentioned it) or default to asking
            if "水印" in text or "提取" in text or "视频" in text:
                link = self.get_delivery_link_extractor()
                product_name = "《全网短视频无水印提取器源码》"
            else:
                link = self.get_delivery_link_xhs()
                product_name = "《小红书全自动AI助手源码》"
                
            reply = (
                f"收到啦老板！感谢支持。这是您的{product_name}及配套实操讲解：\n"
                f"【{link}】\n"
                f"解压密码：TITAN2026\n"
                f"遇到问题先看配套视频哦，本商品为知识付费/软件源码，拍下后自动发货，感谢您的理解与支持~"
            )
            return reply

        # Scenario 2: Generic pre-sales question
        if any(keyword in text for keyword in ["怎么用", "好用吗", "能防封吗", "在吗", "小白", "报错", "怎么卖", "有货吗"]):
            reply = (
                "在的老板！咱们店里的核心爆款都有货：\n"
                "1. 【小红书AI自动发帖机】（适合副业引流刚需）\n"
                "2. 【抖快无水印视频提取器】（适合二创影视解说搬运工）\n"
                "全都是【源码级测试脚本】，仅供个人学习研究自动化使用，小白双击即可用。\n"
                "可以直接拍对应链接，24小时系统通过自动回复秒发源码压缩包（永久有效）！拍完发一句【已拍】即可发货。"
            )
            return reply
            
        return None

    def _read_latest_message(self) -> str:
        """Use PyAutoGUI to copy the latest message from the active Xianyu window."""
        log.info("Reading latest message explicitly from active window...")
        
        # Clear clipboard first
        pyperclip.copy("")
        
        # Ctrl+A to select all, Ctrl+C to copy
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.5)
        # Click somewhere off-text to deselect if necessary
        pyautogui.click() 
        
        text = pyperclip.paste()
        return text

    def _send_reply(self, reply: str):
        """Use PyAutoGUI to send the constructed reply."""
        delay = random.uniform(3.0, 8.0)
        log.info(f"⏳ Waiting {delay:.1f}s to simulate human typing...")
        time.sleep(delay)
        
        log.info(f"📤 Auto-replying:\n{reply}\n")
        
        # Copy reply to clipboard
        pyperclip.copy(reply)
        
        # Paste and Send
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        pyautogui.press('enter')

    def _tick(self):
        """Single polling tick."""
        text = self._read_latest_message()
        if text:
            reply = self.process_message(text)
            if reply:
                self._send_reply(reply)
        else:
            log.debug("No text found in clipboard or active window.")
        
    def start_polling(self):
        """Start the infinite polling loop."""
        log.info("Bot is now actively monitoring idle fish messages via PyAutoGUI. Press Ctrl+C to stop.")
        try:
            while True:
                self._tick()
                time.sleep(self.reply_interval)
        except KeyboardInterrupt:
            log.info("🛑 Bot stopped by user.")

if __name__ == "__main__":
    bot = XianyuSalesBot()
    # To prevent it from going crazy when testing, we just run once
    # bot._tick()
