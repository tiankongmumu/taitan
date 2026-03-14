"""
TITAN Engine — 4-AI Roundtable Session 3
Building on Sessions 1+2, deeper dive on architecture and execution priority.
Shorter prompt to ensure all models respond.
"""
import os, sys, json, time, requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL,
    DOUBAO_API_KEY, DOUBAO_BASE_URL, DOUBAO_ENDPOINT,
    QWEN_API_KEY, QWEN_BASE_URL,
)

OUTPUT = os.path.join(os.path.dirname(__file__), "titan_roundtable_s3.json")

PROMPT = """这是TITAN Engine圆桌会议第3轮。前两轮结论：
- 评分3-5/10，架构方向对但执行全建立在虚假数据上
- 5大问题：零变现、假数据、低质量、无分析、零流量
- DeepSeek建议：AdSense + Stripe定价 + pytrends + SerpAPI + Umami + shadcn-ui

本轮深入讨论3个具体问题：

## Q1: TITAN引擎的核心定位应该是什么？
选项A: 批量生成100+低质量工具，靠长尾SEO获取流量（数量打法）
选项B: 精做10个顶级工具，每个都能与市场上最好的竞争（质量打法）
选项C: 做一个垂直SaaS平台（如"开发者工具集"），整合所有工具（平台打法）
选一个并解释为什么，要给出具体的数据支撑。

## Q2: 如果只有30天时间，从现在的$0到第一个$100收入，最快路径是什么？
要求极度具体：第几天做什么，用什么工具，预期产出。

## Q3: TITAN引擎真正需要的AI能力是什么？
当前所有AI都用来"生成代码"——这可能是错误的方向。
AI应该用在哪些环节才能真正产生商业价值？

中文回答，每个问题不超过300字。总共不超过1000字。"""


def call(name, url, key, model, timeout=180):
    print(f"\n>> {name}...")
    h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    d = {"model": model, "messages": [
        {"role": "system", "content": "You are a $1M/year indie developer. Be concise, max 1000 chars per question."},
        {"role": "user", "content": PROMPT}
    ], "max_tokens": 2000, "temperature": 0.3}
    for i in range(3):
        try:
            t = time.time()
            r = requests.post(url, headers=h, json=d, timeout=timeout)
            r.raise_for_status()
            c = r.json()["choices"][0]["message"]["content"]
            e = round(time.time() - t, 1)
            print(f"   OK: {len(c)} chars, {e}s")
            return {"model": name, "response": c, "chars": len(c), "time": e, "ok": True}
        except Exception as ex:
            print(f"   RETRY {i+1}: {ex}")
            if i < 2: time.sleep(3)
    return {"model": name, "response": "", "ok": False}


def main():
    print("=" * 50)
    print("TITAN ROUNDTABLE S3: Deep Strategy")
    print("=" * 50)
    r = []
    if DEEPSEEK_API_KEY: r.append(call("DeepSeek", DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, "deepseek-chat", 90))
    if DOUBAO_API_KEY: r.append(call("Doubao", DOUBAO_BASE_URL, DOUBAO_API_KEY, DOUBAO_ENDPOINT, 180))
    if QWEN_API_KEY: r.append(call("Qwen", QWEN_BASE_URL, QWEN_API_KEY, "qwen-max", 180))

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump({"time": datetime.now().isoformat(), "session": 3, "results": r}, f, indent=2, ensure_ascii=False)

    for x in r:
        if x.get("ok"):
            print(f"\n{'='*40}\n{x['model']} ({x['chars']} chars)\n{'='*40}\n{x['response']}\n")
        else:
            print(f"\nFAILED: {x['model']}")
    print(f"\nSaved: {OUTPUT}")


if __name__ == "__main__":
    main()
