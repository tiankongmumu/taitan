"""
Micro-SaaS Forge — 配置兼容层
所有配置统一由 titan_config.py 管理，本文件仅做向后兼容的 re-export。

⚠️  新代码请直接 `from titan_config import ...`
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

# ── 从 titan_config 统一导入所有常量 ──
from titan_config import (
    # LLM API Keys
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DOUBAO_API_KEY,
    DOUBAO_ENDPOINT,
    DOUBAO_BASE_URL,
    QWEN_API_KEY,
    QWEN_BASE_URL,
    GEMINI_API_KEY,
    GEMINI_BASE_URL,
    # Deployment
    VERCEL_TOKEN,
    # Monetization
    GUMROAD_PRODUCT_ID,
    # LLM Generation Settings
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    LLM_MAX_RETRIES,
    SELF_HEAL_MAX_ATTEMPTS,
    # Paths (str versions for backward compat)
    FORGE_DIR,
    FORGE_ROOT,
    TEMPLATES_DIR,
    GENERATED_APPS_DIR,
    SEO_ASSETS_DIR,
    LOGS_DIR,
    HISTORY_FILE,
    # env helper
    env,
)

# ── 仅存在于旧 config.py 中的常量 ── 
# 这些在 titan_config.py 中没有，需要保留
AFDIAN_TOKEN = env("AFDIAN_TOKEN", "XMhN86swHACRSY9KcEtTp3JraxDgjf5P")
AFDIAN_USER_ID = env("AFDIAN_USER_ID", "tiankongmumu")
