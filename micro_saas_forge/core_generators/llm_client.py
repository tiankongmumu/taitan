"""
Micro-SaaS Forge — LLM 客户端 (v5.0 — Pi-Mono Enhanced)
支持：多模型降级（Gemini → DeepSeek → Doubao → Qwen）、指数退避重试、代码块提取。
v4.0: 接入Gemini作为首选编码引擎
v5.0: 学习pi-mono(badlogic/pi-mono) — provider registry + 成本追踪 + 模型能力标注
学习来源: pi-mono (unified LLM API) + Shannon (web security) + Canner/WrenAI
"""
import requests
import json
import re
import time
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL,
    DOUBAO_API_KEY, DOUBAO_BASE_URL, DOUBAO_ENDPOINT,
    QWEN_API_KEY, QWEN_BASE_URL,
    GEMINI_API_KEY, GEMINI_BASE_URL,
    LLM_MAX_TOKENS, LLM_TEMPERATURE, LLM_MAX_RETRIES,
)
from titan_config import (
    GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL,
    MISTRAL_API_KEY, MISTRAL_BASE_URL, MISTRAL_MODEL,
    CEREBRAS_API_KEY, CEREBRAS_BASE_URL, CEREBRAS_MODEL,
    GITHUB_MODELS_TOKEN, GITHUB_MODELS_URL, GITHUB_MODELS_MODEL,
)
from logger import get_logger

log = get_logger("llm")

# ─── 模型配置表（优先级从高到低）───
# DeepSeek 作为首选引擎 — 稳定可靠, Gemini 移至末位(配额耗尽)
MODELS = []
if os.getenv("OPENAI_API_KEY"):
    MODELS.append({
        "name": "OpenAI",
        "url": "https://api.openai.com/v1/chat/completions",
        "key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-4o",
    })
if DEEPSEEK_API_KEY:
    MODELS.append({
        "name": "DeepSeek",
        "url": DEEPSEEK_BASE_URL,
        "key": DEEPSEEK_API_KEY,
        "model": "deepseek-chat",
    })
if DOUBAO_API_KEY:
    MODELS.append({
        "name": "Doubao",
        "url": DOUBAO_BASE_URL,
        "key": DOUBAO_API_KEY,
        "model": DOUBAO_ENDPOINT,
    })
if QWEN_API_KEY:
    MODELS.append({
        "name": "Qwen",
        "url": QWEN_BASE_URL,
        "key": QWEN_API_KEY,
        "model": "qwen-max",
    })
if GEMINI_API_KEY:
    MODELS.append({
        "name": "Gemini",
        "url": GEMINI_BASE_URL,
        "key": GEMINI_API_KEY,
        "model": "gemini-2.5-flash",
        "max_tokens": 16384,
        "strengths": ["coding", "reasoning", "long_output"],
        "cost": {"input": 0.15, "output": 0.60},
    })
# Free LLM Providers (zero-cost fallback)
if GROQ_API_KEY:
    MODELS.append({
        "name": "Groq",
        "url": GROQ_BASE_URL,
        "key": GROQ_API_KEY,
        "model": GROQ_MODEL,
        "cost": {"input": 0, "output": 0},
    })
if MISTRAL_API_KEY:
    MODELS.append({
        "name": "Mistral",
        "url": MISTRAL_BASE_URL,
        "key": MISTRAL_API_KEY,
        "model": MISTRAL_MODEL,
        "cost": {"input": 0, "output": 0},
    })
if CEREBRAS_API_KEY:
    MODELS.append({
        "name": "Cerebras",
        "url": CEREBRAS_BASE_URL,
        "key": CEREBRAS_API_KEY,
        "model": CEREBRAS_MODEL,
        "cost": {"input": 0, "output": 0},
    })
if GITHUB_MODELS_TOKEN:
    MODELS.append({
        "name": "GitHub Models",
        "url": GITHUB_MODELS_URL,
        "key": GITHUB_MODELS_TOKEN,
        "model": GITHUB_MODELS_MODEL,
        "cost": {"input": 0, "output": 0},
    })

class LLMClient:
    """统一的大模型调用客户端，支持降级重试。
    v3.5: 梯度超时 + Token 用量追踪 + 响应验证器。
    """
    # 梯度超时：首选模型快速失败，降级模型给更多时间
    TIMEOUT_TIERS = [60, 90, 120]
    MIN_RESPONSE_LENGTH = 50  # 响应验证器：最低有效响应长度
    USAGE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory", "llm_usage.json")

    def generate(
        self,
        prompt: str = None,
        system_prompt: str = "You are an expert Next.js and TypeScript developer.",
        messages: list = None,
        is_json: bool = False,
    ) -> str:
        if not MODELS:
            log.error("没有可用的 LLM API Key！请检查 .env 配置。")
            return ""

        # Prepare messages if not provided
        if messages is None:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]

        for idx, model_cfg in enumerate(MODELS):
            timeout = self.TIMEOUT_TIERS[min(idx, len(self.TIMEOUT_TIERS) - 1)]
            result = self._call_with_retry(model_cfg, messages, is_json, timeout=timeout)
            if result and len(result) >= self.MIN_RESPONSE_LENGTH:
                return result
            if result and len(result) < self.MIN_RESPONSE_LENGTH:
                log.warning(f"{model_cfg['name']} 响应过短 ({len(result)} chars < {self.MIN_RESPONSE_LENGTH})，视为无效，尝试降级...")
            else:
                log.warning(f"{model_cfg['name']} 全部重试失败，尝试下一个模型...")

        log.error("所有模型均已耗尽！返回空结果。")
        return ""

    def _call_with_retry(
        self, cfg: dict, messages: list, is_json: bool, timeout: int = 120
    ) -> str:
        headers = {
            "Authorization": f"Bearer {cfg['key']}",
            "Content-Type": "application/json",
        }
        data = {
            "model": cfg["model"],
            "messages": messages,
            "max_tokens": cfg.get("max_tokens", LLM_MAX_TOKENS),
            "temperature": LLM_TEMPERATURE,
        }
        if is_json:
            data["response_format"] = {"type": "json_object"}

        for attempt in range(1, LLM_MAX_RETRIES + 1):
            try:
                log.info(f"[{cfg['name']}] 请求中 (尝试 {attempt}/{LLM_MAX_RETRIES}, timeout={timeout}s)...")
                res = requests.post(
                    cfg["url"], headers=headers, json=data, timeout=timeout
                )
                res.raise_for_status()
                resp_json = res.json()
                content = resp_json["choices"][0]["message"]["content"]
                log.info(f"[{cfg['name']}] 成功返回 {len(content)} 字符")
                
                # 📊 Token 用量追踪 (v3.5)
                self._track_usage(cfg["name"], resp_json.get("usage", {}), cfg)
                
                return content
            except requests.exceptions.Timeout:
                log.warning(f"[{cfg['name']}] 超时 (尝试 {attempt}, timeout={timeout}s)")
            except requests.exceptions.HTTPError as e:
                status = e.response.status_code if e.response is not None else "?"
                body = ""
                if e.response is not None:
                    try:
                        body = e.response.text[:200]
                    except Exception:
                        body = "(无法读取响应体)"
                log.warning(f"[{cfg['name']}] HTTP {status} (尝试 {attempt}): {body}")
                if status == 429:  # Rate limit
                    wait = 2 ** attempt * 5
                    log.info(f"  限流，等待 {wait}s...")
                    time.sleep(wait)
                    continue
            except Exception as e:
                log.warning(f"[{cfg['name']}] 异常: {e} (尝试 {attempt})")

            # 指数退避
            if attempt < LLM_MAX_RETRIES:
                wait = 2 ** attempt
                log.info(f"  退避等待 {wait}s...")
                time.sleep(wait)

        return ""

    def _track_usage(self, model_name: str, usage: dict, model_cfg: dict = None):
        """📊 Token 用量 + 成本追踪 (v5.0, 学习自pi-mono的cost tracking)"""
        if not usage:
            return
        try:
            # 计算本次调用成本 (pi-mono pattern: $/1M tokens)
            cost_cfg = (model_cfg or {}).get("cost", {"input": 0, "output": 0})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            cost = (input_tokens * cost_cfg.get("input", 0) + output_tokens * cost_cfg.get("output", 0)) / 1_000_000

            os.makedirs(os.path.dirname(self.USAGE_FILE), exist_ok=True)
            records = []
            if os.path.exists(self.USAGE_FILE):
                with open(self.USAGE_FILE, "r", encoding="utf-8") as f:
                    records = json.load(f)
            records.append({
                "ts": datetime.now().isoformat(),
                "model": model_name,
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": usage.get("total_tokens", 0),
                "cost_usd": round(cost, 6),
            })
            records = records[-500:]
            with open(self.USAGE_FILE, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)

            # 累计成本日志
            total_cost = sum(r.get("cost_usd", 0) for r in records)
            log.info(f"  💰 本次: ${cost:.6f} | 累计: ${total_cost:.4f}")
        except Exception:
            pass

    @staticmethod
    def extract_code_block(text: str) -> str:
        """从 Markdown 代码块中提取代码，忽略对话文本。"""
        if not text:
            return ""
        
        # 匹配 ```语言 \n 代码 \n```
        import re
        match = re.search(r"```[a-zA-Z]*\n(.*?)(?:\n```|$)", text, re.DOTALL)
        if match:
            return match.group(1).strip()
            
        # Fallback 匹配
        if "```" in text:
            parts = text.split("```")
            if len(parts) >= 3:
                # [0] 是前言, [1] 是代码块带语言, [2] 是结尾
                code_raw = parts[1].strip()
                if "\n" in code_raw:
                    return code_raw.split("\n", 1)[1].strip()
                return code_raw
                
        return text.strip()
