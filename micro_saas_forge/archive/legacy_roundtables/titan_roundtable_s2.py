"""
TITAN Engine — 4-AI Roundtable Session 2
Topic: What exactly must be built to transform TITAN from a tech demo into a commercial engine?
"""
import os
import sys
import json
import time
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL,
    DOUBAO_API_KEY, DOUBAO_BASE_URL, DOUBAO_ENDPOINT,
    QWEN_API_KEY, QWEN_BASE_URL,
)

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "titan_roundtable_commercial.json")

PROMPT = """你是一个年营收超过100万美元的独立开发者 + 商业顾问。

以下是 TITAN Engine v4.0 的现状（一个自动生成 Web 工具/游戏并部署到 shipmicro.com 的 Python 引擎）：

## 当前状态
- 产品: shipmicro.com — 5个开发者工具 + 5个小游戏
- 技术栈: Next.js + Vercel + Python + 3个LLM (DeepSeek/Doubao/Qwen)
- 收入: $0/月
- 流量: 接近 0
- 分析: 仅 localStorage（假数据）
- 变现: 无 AdSense、无付费、无邮件列表
- 需求发现: 硬编码关键词 + LLM 幻觉
- 竞品分析: 完全依赖 LLM（无真实数据）

## 上一轮圆桌结论
4个AI一致认为：(1) 零变现 (2) 假数据 (3) 低质量 (4) 无分析 (5) 零流量
评分：3-5/10

## 本轮议题：具体怎么做？

请给出**极度具体**的升级方案，必须包含：

### 1. 变现系统设计
- 具体用什么广告网络？API 怎么接入？代码怎么写？
- 付费模式怎么设计？定价多少？
- 邮件收集用什么服务？怎么集成？

### 2. 真实数据接入
- 用什么 API 获取真实搜索量？免费方案还是付费方案？
- 竞品分析用什么工具？SerpAPI？Ahrefs？怎么接入？
- 流量分析用 GA4 还是 Umami？具体怎么集成到 Next.js？

### 3. 产品质量跃升
- LLM 生成代码质量怎么从 6 分提到 8 分？
- 需要什么样的模板系统？
- UI 组件库怎么选？

### 4. 流量获取引擎
- SEO 具体怎么做？需要写什么内容？
- 社交分发怎么做？哪些平台？
- 要不要做 Programmatic SEO？怎么做？

### 5. 完整技术路线图
- 第1周做什么？（精确到每天）
- 第2-4周做什么？
- 第2-3个月做什么？
- 6个月目标是什么？

请用中文回答。要**极度具体**——我要的是可直接执行的代码级方案，不是泛泛的建议。
给出具体的 API 端点、npm 包名、Python 库名、配置代码片段。"""


def call_model(name, url, api_key, model, prompt, timeout=120):
    print(f"\n{'='*50}")
    print(f"Calling {name}...")
    print(f"{'='*50}")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a successful indie developer who has built multiple $10K+/month products. Give extremely specific, actionable advice with code snippets."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 4000,
        "temperature": 0.3,
    }
    for attempt in range(3):
        try:
            start = time.time()
            res = requests.post(url, headers=headers, json=data, timeout=timeout)
            res.raise_for_status()
            content = res.json()["choices"][0]["message"]["content"]
            elapsed = round(time.time() - start, 1)
            print(f"OK {name}: {len(content)} chars in {elapsed}s")
            return {"model": name, "response": content, "chars": len(content), "time_seconds": elapsed, "success": True}
        except Exception as e:
            print(f"WARN {name} attempt {attempt+1}: {e}")
            if attempt < 2: time.sleep(2 ** (attempt + 1))
    return {"model": name, "response": "", "success": False}


def main():
    print("\n" + "=" * 60)
    print("TITAN ENGINE — 4-AI ROUNDTABLE SESSION 2: COMMERCIAL PATH")
    print("=" * 60)
    results = []
    if DEEPSEEK_API_KEY:
        results.append(call_model("DeepSeek", DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, "deepseek-chat", PROMPT, 90))
    if DOUBAO_API_KEY:
        results.append(call_model("Doubao", DOUBAO_BASE_URL, DOUBAO_API_KEY, DOUBAO_ENDPOINT, PROMPT, 120))
    if QWEN_API_KEY:
        results.append(call_model("Qwen", QWEN_BASE_URL, QWEN_API_KEY, "qwen-max", PROMPT, 120))

    output = {"time": datetime.now().isoformat(), "topic": "Commercial Engine Upgrade Path", "results": results}
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    for r in results:
        if r.get("success"):
            print(f"\n{'='*50}\n{r['model']} ({r['chars']} chars)\n{'='*50}")
            print(r["response"][:500])
            print(f"... [{max(0, r['chars']-500)} more]")

    print(f"\nFull saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
