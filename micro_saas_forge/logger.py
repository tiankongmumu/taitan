"""
Micro-SaaS Forge — 统一日志系统
同时输出到终端（彩色）和 logs/ 目录（持久化文件）。
"""
import logging
import os
from datetime import datetime
from config import LOGS_DIR


def get_logger(name: str = "forge") -> logging.Logger:
    """获取带文件和终端 handler 的 logger 实例。"""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # 避免重复添加 handler

    logger.setLevel(logging.DEBUG)

    # ── 终端输出 ──
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        "%(asctime)s │ %(levelname)-7s │ %(message)s",
        datefmt="%H:%M:%S"
    ))
    logger.addHandler(console)

    # ── 文件输出 ──
    os.makedirs(LOGS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_handler = logging.FileHandler(
        os.path.join(LOGS_DIR, f"forge_{timestamp}.log"),
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s"
    ))
    logger.addHandler(file_handler)

    return logger
