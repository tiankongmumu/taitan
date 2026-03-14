"""
TITAN Engine — 4-AI Roundtable Session 6
核心议题: 变现引擎 — 怎么赚到第一块钱？
串行辩论: DeepSeek → Doubao(带DS结论) → Qwen(带DS+Doubao结论)
依赖S5结论作为上下文
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
OUTPUT_JSON = os.path.join(BASE_DIR, "titan_roundtable_s6.json")
OUTPUT_MD = os.path.join(BASE_DIR, "titan_roundtable_s6_monetization.md")
S5_JSON = os.path.join(BASE_DIR, "titan_roundtable_s5.json")

SYSTEM = "You are a revenue engineer and monetization expert for SaaS products. 你必须用中文回答。不要空洞建议，要给出具体的API名称、费用、代码实现步骤。"


def load_s5_summary():
    """加载S5圆桌结论作为上下文"""
    try:
        with open(S5_JSON, "r", encoding="utf-8") as f:
            s5 = json.load(f)
        parts = []
        for r in s5.get("results", []):
            if r.get("ok"):
                parts.append(f"【{r['model']}】: {r['response'][:600]}")
        return "\n".join(parts) if parts else "S5尚未运行"
    except Exception:
        return "S5数据加载失败"


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
    print("TITAN ROUNDTABLE S6: 变现引擎设计")
    print("=" * 60)

    s5_summary = load_s5_summary()

    CONTEXT = f"""【S4结论】商业智能引擎方向已确认(可行性7/10)。
【S5架构摘要】
{s5_summary}

## S6圆桌 — 变现引擎: 怎么赚到第一块钱？"""

    # ── DeepSeek: 变现架构师 ──
    prompt_ds = f"""{CONTEXT}

你是变现架构师。基于S5确定的架构，设计具体的赚钱路径:

1. **30天$100挑战** — 最快赚到$100的操作步骤(每天做什么，具体到小时级)
   - 不允许说"注册XX"，必须说清楚：注册什么平台、审核周期、佣金比例

2. **3大变现通道的代码实现** (每个给出Python函数签名 + 核心逻辑):
   a) **CPS联盟推广**: 用哪个联盟？接口怎么调？佣金流怎么走？
   b) **内容SEO变现**: 自动生成什么内容？发布到哪里？怎么挂广告？
   c) **数据API服务**: 卖什么数据？定价多少？API怎么设计？

3. **单位经济模型**: 每个通道
   - 成本(API费用/服务器) per 1000次
   - 收入 per 1000次
   - 毛利率

4. **必须接入的第三方平台**(名称+API文档链接+免费额度)

总计不超过1500字。要有数字、有代码、有ROI。"""

    ds_result = {"model": "DeepSeek", "response": "", "ok": False}
    if DEEPSEEK_API_KEY:
        ds_result = call("DeepSeek", DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, "deepseek-chat", prompt_ds, 120)
    ds_text = ds_result.get("response", "")

    # ── Doubao: 一线实操专家 ──
    prompt_doubao = f"""{CONTEXT}

DeepSeek(变现架构师)的方案:
---
{ds_text}
---

你是Doubao，一线实操专家。审视DeepSeek的变现方案:

1. **现实检验**: DeepSeek说的30天$100计划靠谱吗？哪些步骤会卡住？
2. **中国市场适配**: 哪些联盟/平台在中国更好用？(淘宝客、京东联盟、拼多多CPS...)
3. **流量获取成本**: 做SEO内容实际需要多长时间见效？有没有更快的冷启动方式？
4. **隐藏坑**: 联盟结算周期、税务问题、平台封号风险
5. **你见过的真实案例**: 类似产品的真实变现数据(MAU→收入对照)

总计不超过1200字。给真实数据，不要理论分析。"""

    doubao_result = {"model": "Doubao", "response": "", "ok": False}
    if DOUBAO_API_KEY:
        doubao_result = call("Doubao", DOUBAO_BASE_URL, DOUBAO_API_KEY, DOUBAO_ENDPOINT, prompt_doubao, 180)
    doubao_text = doubao_result.get("response", "")

    # ── Qwen: 最终变现决策 ──
    prompt_qwen = f"""{CONTEXT}

DeepSeek方案:
---
{ds_text[:1200]}
---

Doubao评审:
---
{doubao_text[:1200]}
---

你是Qwen，CEO做最终决策。综合两人意见:

1. **最终变现战略**: 选定哪个通道作为Day 1优先？理由？
2. **MVP变现版本**: 最小可变现版本需要哪些代码文件？列出文件名+功能
3. **KPI设定**: 第1周/第2周/第4周各追踪什么指标？具体数字目标
4. **预算**: 启动成本(API费用+域名+服务器)，控制在多少以内？
5. **止损线**: 什么情况下该放弃这个通道、切换下一个？

总计不超过1200字。明确决策，不要"都可以试试"。"""

    qwen_result = {"model": "Qwen", "response": "", "ok": False}
    if QWEN_API_KEY:
        qwen_result = call("Qwen", QWEN_BASE_URL, QWEN_API_KEY, "qwen-max", prompt_qwen, 180)

    results = [ds_result, doubao_result, qwen_result]

    # ── 保存 ──
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"time": datetime.now().isoformat(), "session": 6, "topic": "monetization_engine", "results": results}, f, indent=2, ensure_ascii=False)

    md = f"""# TITAN 圆桌 S6: 变现引擎设计
> 时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> 模式: 串行辩论 (DeepSeek → Doubao → Qwen)

---

## DeepSeek (变现架构师)
{ds_text if ds_text else '❌ 未返回'}

---

## Doubao (一线实操专家)
{doubao_text if doubao_text else '❌ 未返回'}

---

## Qwen (CEO 最终决策)
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
