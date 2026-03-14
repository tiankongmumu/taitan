"""TITAN Engine Diagnostic — tests API key loading and LLM connectivity"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from titan_config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL,
    GEMINI_API_KEY, GEMINI_BASE_URL,
    DOUBAO_API_KEY, DOUBAO_BASE_URL, DOUBAO_ENDPOINT,
    QWEN_API_KEY, QWEN_BASE_URL,
)

print("="*50)
print("TITAN Engine Diagnostic")
print("="*50)

# 1. Check keys
keys = {
    "DeepSeek": (DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL),
    "Gemini": (GEMINI_API_KEY, GEMINI_BASE_URL),
    "Doubao": (DOUBAO_API_KEY, DOUBAO_BASE_URL),
    "Qwen": (QWEN_API_KEY, QWEN_BASE_URL),
}

print("\n--- API Keys ---")
for name, (key, url) in keys.items():
    has_key = bool(key and len(key) > 5)
    print(f"  {name}: {'OK' if has_key else 'MISSING'} (key={key[:10]}... url={url[:40]})")

# 2. Test each API with simple request
import requests

print("\n--- API Connectivity (10s timeout) ---")
for name, (key, url) in keys.items():
    if not key or len(key) < 5:
        print(f"  {name}: SKIP (no key)")
        continue
    
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    data = {
        "model": "deepseek-chat" if name == "DeepSeek" else 
                 "gemini-2.5-flash" if name == "Gemini" else
                 DOUBAO_ENDPOINT if name == "Doubao" else "qwen-max",
        "messages": [{"role": "user", "content": "say hello"}],
        "max_tokens": 5,
    }
    
    try:
        t = time.time()
        r = requests.post(url, headers=headers, json=data, timeout=10)
        elapsed = time.time() - t
        print(f"  {name}: HTTP {r.status_code} ({elapsed:.1f}s) - {r.text[:100]}")
    except requests.exceptions.Timeout:
        print(f"  {name}: TIMEOUT (>10s)")
    except Exception as e:
        print(f"  {name}: ERROR - {e}")

print("\n--- Done ---")
