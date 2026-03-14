"""
╔══════════════════════════════════════════════════╗
║  TITAN Unified Configuration v2.0                ║
║  Single source of truth for all settings         ║
║  v2.0: 合并 config.py 的全部内容，成为唯一配置   ║
╚══════════════════════════════════════════════════╝
"""
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
FORGE_DIR = Path(r"d:\Project\1\micro_saas_forge")
PROJECT_DIR = FORGE_DIR.parent
OPENCLAW_DIR = Path(os.path.expanduser("~")) / ".openclaw"
LOG_DIR = FORGE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 兼容 config.py 的路径常量
FORGE_ROOT = str(FORGE_DIR)
TEMPLATES_DIR = str(FORGE_DIR / "templates" / "nextjs_base")
GENERATED_APPS_DIR = str(FORGE_DIR / "generated_apps")
SEO_ASSETS_DIR = str(FORGE_DIR / "seo_assets")
LOGS_DIR = str(LOG_DIR)
HISTORY_FILE = str(FORGE_DIR / "history.json")

# ---------------------------------------------------------------------------
# .env Loader
# ---------------------------------------------------------------------------
def _load_env():
    env_path = FORGE_DIR / ".env"
    cfg = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip(' "\'')
    return cfg

_ENV = _load_env()

def env(key: str, default: str = "") -> str:
    return os.environ.get(key) or _ENV.get(key) or default

# ---------------------------------------------------------------------------
# LLM Configuration
# ---------------------------------------------------------------------------
DEEPSEEK_API_KEY = env("DEEPSEEK_API_KEY")
DEEPSEEK_URL     = "https://api.deepseek.com/chat/completions"
DEEPSEEK_BASE_URL = DEEPSEEK_URL  # 兼容 config.py
DEEPSEEK_MODEL   = "deepseek-chat"

QWEN_API_KEY     = env("QWEN_API_KEY")
QWEN_URL         = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
QWEN_BASE_URL    = QWEN_URL  # 兼容
QWEN_MODEL       = "qwen-max"

DOUBAO_API_KEY   = env("DOUBAO_API_KEY")
DOUBAO_ENDPOINT  = env("DOUBAO_ENDPOINT", "ep-20260223143416-6xqjh")
DOUBAO_URL       = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
DOUBAO_BASE_URL  = DOUBAO_URL  # 兼容

GEMINI_API_KEY   = env("GEMINI_API_KEY")
GEMINI_BASE_URL  = env("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions")

# Free LLM Providers (from free-llm-api-resources)
GROQ_API_KEY       = env("GROQ_API_KEY")
GROQ_BASE_URL      = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL         = "llama-3.3-70b-versatile"

MISTRAL_API_KEY    = env("MISTRAL_API_KEY")
MISTRAL_BASE_URL   = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL      = "mistral-small-latest"

CEREBRAS_API_KEY   = env("CEREBRAS_API_KEY")
CEREBRAS_BASE_URL  = "https://api.cerebras.ai/v1/chat/completions"
CEREBRAS_MODEL     = "llama3.1-8b"

GITHUB_MODELS_TOKEN = env("GITHUB_MODELS_TOKEN")
GITHUB_MODELS_URL   = "https://models.inference.ai.azure.com/chat/completions"
GITHUB_MODELS_MODEL = "gpt-4o"

LLM_MAX_TOKENS      = int(env("LLM_MAX_TOKENS", "4000"))
LLM_TEMPERATURE     = float(env("LLM_TEMPERATURE", "0.2"))
LLM_MAX_RETRIES     = int(env("LLM_MAX_RETRIES", "3"))
LLM_TIMEOUT_SECONDS = 60
SELF_HEAL_MAX_ATTEMPTS = int(env("SELF_HEAL_MAX_ATTEMPTS", "3"))

# ---------------------------------------------------------------------------
# Deployment & Monetization
# ---------------------------------------------------------------------------
VERCEL_TOKEN       = env("VERCEL_TOKEN")
GUMROAD_PRODUCT_ID = env("GUMROAD_PRODUCT_ID", "dummy_product_id")

# ---------------------------------------------------------------------------
# Brain Configuration
# ---------------------------------------------------------------------------
BRAIN_MAX_HISTORY    = 20
BRAIN_HEALTH_PORT    = 8080
BRAIN_LOG_FILE       = LOG_DIR / "titan_brain.jsonl"

# ---------------------------------------------------------------------------
# WebSocket Configuration
# ---------------------------------------------------------------------------
WS_URL               = env("OPENCLAW_WS_URL", "ws://127.0.0.1:18789")
WS_PING_INTERVAL     = 30
WS_PING_TIMEOUT      = 10
WS_RECONNECT_MIN     = 1
WS_RECONNECT_MAX     = 60
WS_RECONNECT_FACTOR  = 2
WS_MESSAGE_BUFFER    = 100

# ---------------------------------------------------------------------------
# Tool Orchestrator Configuration
# ---------------------------------------------------------------------------
TOOL_QUEUE_MAX_SIZE       = 50
TOOL_EXECUTION_TIMEOUT    = 120
TOOL_RETRY_ATTEMPTS       = 2
TOOL_RETRY_DELAY          = 3

# Circuit Breaker
CB_FAILURE_THRESHOLD      = 3
CB_RECOVERY_TIMEOUT       = 60
CB_HALF_OPEN_MAX_CALLS    = 1

# ---------------------------------------------------------------------------
# Tool Script Paths
# ---------------------------------------------------------------------------
TOOL_SCRIPTS = {
    "news_scraper":  FORGE_DIR / "news_scraper.py",
    "codemint":      FORGE_DIR / "daily_forge.py",
    "publisher_xhs": FORGE_DIR / "xhs_publisher_async.py",
    "publisher_reddit": FORGE_DIR / "reddit_publisher.py",
    "generate_tools": FORGE_DIR / "generate_tools.py",
    "quality_gate":  FORGE_DIR / "quality_gate.py",
    "beast_mode":    PROJECT_DIR / "beast_mode_distribute.py",
    "demand_radar":  FORGE_DIR / "demand_radar.py",
    "web_scanner":   FORGE_DIR / "titan_web_scanner.py",
    "deployer":      FORGE_DIR / "titan_deployer.py",
    "skill_system":  FORGE_DIR / "titan_skill_system.py",
    "nurturer_twitter": FORGE_DIR / "twitter_nurturer.py",
    "github_scholar": FORGE_DIR / "github_scholar.py",
    "skill_extractor": FORGE_DIR / "skill_extractor.py",
}

# ---------------------------------------------------------------------------
# Beast Mode Scheduler
# ---------------------------------------------------------------------------
BEAST_MODE_HOUR   = 7
BEAST_MODE_MINUTE = 0
