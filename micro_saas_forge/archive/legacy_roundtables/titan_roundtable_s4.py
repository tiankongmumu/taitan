"""
TITAN Engine — 4-AI Roundtable Session 4
Core question: Can TITAN make quality products? Or should it pivot entirely?
"""
import os, sys, json, time, requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL,
    DOUBAO_API_KEY, DOUBAO_BASE_URL, DOUBAO_ENDPOINT,
    QWEN_API_KEY, QWEN_BASE_URL,
)

OUTPUT = os.path.join(os.path.dirname(__file__), "titan_roundtable_s4.json")

PROMPT = """TITAN圆桌会议第4轮。前3轮结论：
- 架构3-5分，产品2分
- 3AI共识：当前10个产品（5工具+5游戏）是低端垃圾，无商业价值
- AI不应用于代码生成，应用于商业漏斗优化

本轮核心辩题：

## 辩题A: TITAN引擎是否具备生成"高质量产品"的能力？

请诚实回答：
- LLM（DeepSeek/Doubao/Qwen）能生成什么级别的Web产品？
- "高质量产品"的定义是什么？需要哪些能力？（设计、交互、性能、商业逻辑）
- 当前LLM生成的HTML工具 vs 市面专业工具（如regex101、jwt.io），差距有多大？
- 差距是否可以通过提升prompt、加模板、多轮修复来弥补？

## 辩题B: 两条路选哪条？

路径1: 先让泰坦引擎学会生成高质量产品 → 再接广告变现
路径2: 放弃产品生成 → 改造泰坦为"商业智能引擎"（发现赚钱机会，用其他方式变现：如CPS推广、内容变现、API转售）

对比两条路的：
- 可行性（1-10分）
- 时间成本
- 预期收入
- 技术风险

## 辩题C: 还有没有第三条路？

如果路径1和路径2都不好，提出你认为最好的方案。

中文。每个辩题300字以内。总计不超过1000字。极度诚实。"""


def call(name, url, key, model, timeout=180):
    print(f">> {name}...")
    h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    d = {"model": model, "messages": [
        {"role": "system", "content": "You are a brutally honest tech investor evaluating a startup. No sugarcoating."},
        {"role": "user", "content": PROMPT}
    ], "max_tokens": 2000, "temperature": 0.4}
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
    print("TITAN ROUNDTABLE S4: Quality vs Pivot")
    print("=" * 50)
    r = []
    if DEEPSEEK_API_KEY: r.append(call("DeepSeek", DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, "deepseek-chat", 90))
    if DOUBAO_API_KEY: r.append(call("Doubao", DOUBAO_BASE_URL, DOUBAO_API_KEY, DOUBAO_ENDPOINT, 180))
    if QWEN_API_KEY: r.append(call("Qwen", QWEN_BASE_URL, QWEN_API_KEY, "qwen-max", 180))

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump({"time": datetime.now().isoformat(), "session": 4, "results": r}, f, indent=2, ensure_ascii=False)

    for x in r:
        if x.get("ok"):
            print(f"\n{'='*40}\n{x['model']}\n{'='*40}\n{x['response']}\n")
        else:
            print(f"\nFAILED: {x['model']}")
    print(f"\nSaved: {OUTPUT}")

if __name__ == "__main__":
    main()
