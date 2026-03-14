"""
TITAN Engine — 4-AI Roundtable Session 7
核心议题: DemandRadar 2.0 — 从"发现需求"升级到"发现赚钱机会"
串行辩论: DeepSeek → Doubao(带DS结论) → Qwen(带DS+Doubao结论)
依赖S5+S6结论作为上下文
"""
import os, sys, json, time, requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL,
    DOUBAO_API_KEY, DOUBAO_BASE_URL, DOUBAO_ENDPOINT,
    QWEN_API_KEY, QWEN_BASE_URL,
)

BASE_DIR = os.path.dirname(__file__)
OUTPUT_JSON = os.path.join(BASE_DIR, "titan_roundtable_s7.json")
OUTPUT_MD = os.path.join(BASE_DIR, "titan_roundtable_s7_demand_radar.md")

SYSTEM = "You are a data engineer and growth hacker specializing in demand discovery systems. 你必须用中文回答。给出具体的API、代码、评分公式。"


def load_prev_summary(*paths):
    parts = []
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for r in data.get("results", []):
                if r.get("ok"):
                    parts.append(f"【{r['model']}·S{data.get('session', '?')}】: {r['response'][:400]}")
        except:
            pass
    return "\n".join(parts) if parts else "前序数据加载失败"


def call(name, url, key, model, prompt, timeout=180):
    print(f">> {name}...")
    h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    d = {"model": model, "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": prompt}
    ], "max_tokens": 3000, "temperature": 0.3}
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
            if i < 2: time.sleep(5)
    return {"model": name, "response": "", "ok": False}


def main():
    print("=" * 60)
    print("TITAN ROUNDTABLE S7: DemandRadar 2.0")
    print("=" * 60)

    prev = load_prev_summary(
        os.path.join(BASE_DIR, "titan_roundtable_s5.json"),
        os.path.join(BASE_DIR, "titan_roundtable_s6.json"),
    )

    CURRENT_RADAR = """当前 demand_radar.py (v1.0) 能力:
- 3个数据源: HackerNews API, LLM趋势预测, 内置关键词库
- 评分模型: opportunity_score = monthly_volume × demand_score / max(competition_level, 1)
- 输出: 排序后的机会列表 [{keyword, source, monthly_volume, opportunity_score}]
- 局限: 无真实搜索量数据(靠LLM估算)、无竞品定价数据、无验证环节"""

    CONTEXT = f"""【S5-S6结论摘要】
{prev}

{CURRENT_RADAR}

## S7圆桌 — DemandRadar 2.0: 从"发现需求"到"发现赚钱机会\""""

    # ── DeepSeek: 数据工程师 ──
    prompt_ds = f"""{CONTEXT}

你是数据工程师。升级 DemandRadar:

1. **新增数据源** (每个必须给出: API endpoint + 免费额度 + 解析方法)
   - Google Trends替代方案
   - Reddit/ProductHunt热帖抓取
   - 竞品定价监控
   - 其他你认为关键的信号源

2. **评分模型v2.0** — 新的机会评分公式
   - 给出完整的数学公式
   - 哪些因子? 权重如何分配?
   - 如何量化"能赚钱"而非只是"有需求"?

3. **验证管道** — 发现一个机会后如何快速验证它值得投入
   - Landing page测试?
   - 关键词竞争分析?
   - 预付费测试?

4. **代码骨架** — 新 demand_radar_v2.py 的类+方法签名

总计不超过1500字。"""

    ds_result = {"model": "DeepSeek", "response": "", "ok": False}
    if DEEPSEEK_API_KEY:
        ds_result = call("DeepSeek", DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, "deepseek-chat", prompt_ds, 120)
    ds_text = ds_result.get("response", "")

    # ── Doubao: 增长黑客 ──
    prompt_doubao = f"""{CONTEXT}

DeepSeek方案:
---
{ds_text}
---

你是Doubao，增长黑客。审视DemandRadar 2.0方案:

1. **数据源可靠性打分**: DeepSeek提的每个数据源，实际可用性(1-10)?
2. **中国市场特有信号源**: 微信指数、百度指数、1688热搜、淘宝生意参谋替代...
3. **反作弊**: 如何识别假趋势/刷量数据?
4. **信号衰减**: 一个"热点"从出现到失去价值通常多久? 如何设计时效性权重?
5. **成本控制**: 运行一次完整扫描的API费用目标应该控制在多少?

总计不超过1200字。"""

    doubao_result = {"model": "Doubao", "response": "", "ok": False}
    if DOUBAO_API_KEY:
        doubao_result = call("Doubao", DOUBAO_BASE_URL, DOUBAO_API_KEY, DOUBAO_ENDPOINT, prompt_doubao, 180)
    doubao_text = doubao_result.get("response", "")

    # ── Qwen: 最终设计 ──
    prompt_qwen = f"""{CONTEXT}

DeepSeek:
---
{ds_text[:1200]}
---

Doubao:
---
{doubao_text[:1200]}
---

你是Qwen，做最终设计决策:

1. **DemandRadar 2.0 最终数据源列表** (最多5个，必须都是免费/极低成本可用的)
2. **最终评分公式** (一个具体的数学公式，含权重)
3. **验证流程**: 机会发现 → 验证 → 执行，各步骤耗时多少?
4. **文件结构**: 重构后的代码文件清单
5. **第一版只做什么**: MVP版DemandRadar 2.0只接1-2个数据源，选哪个?

总计不超过1200字。明确选择，不要列清单。"""

    qwen_result = {"model": "Qwen", "response": "", "ok": False}
    if QWEN_API_KEY:
        qwen_result = call("Qwen", QWEN_BASE_URL, QWEN_API_KEY, "qwen-max", prompt_qwen, 180)

    results = [ds_result, doubao_result, qwen_result]

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"time": datetime.now().isoformat(), "session": 7, "topic": "demand_radar_v2", "results": results}, f, indent=2, ensure_ascii=False)

    md = f"""# TITAN 圆桌 S7: DemandRadar 2.0
> 时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> 模式: 串行辩论 (DeepSeek → Doubao → Qwen)

---

## DeepSeek (数据工程师)
{ds_text if ds_text else '❌ 未返回'}

---

## Doubao (增长黑客)
{doubao_text if doubao_text else '❌ 未返回'}

---

## Qwen (最终设计决策)
{qwen_result.get('response', '') if qwen_result.get('ok') else '❌ 未返回'}
"""
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md)

    for x in results:
        if x.get("ok"):
            print(f"\n{'='*50}\n{x['model']} ({x.get('chars', 0)} chars, {x.get('time', 0)}s)\n{'='*50}\n{x['response']}\n")
        else:
            print(f"\nFAILED: {x['model']}")

    ok_count = sum(1 for x in results if x.get("ok"))
    print(f"\n✅ {ok_count}/3 AI returned | Saved: {OUTPUT_JSON} + {OUTPUT_MD}")


if __name__ == "__main__":
    main()
