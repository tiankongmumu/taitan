"""
TITAN Engine — 4-AI Roundtable Session 8
核心议题: 12周落地路线图 — 每周干什么？量化验收标准
串行辩论: DeepSeek → Doubao(带DS结论) → Qwen(带DS+Doubao结论)
综合S5-S7全部结论
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
OUTPUT_JSON = os.path.join(BASE_DIR, "titan_roundtable_s8.json")
OUTPUT_MD = os.path.join(BASE_DIR, "titan_roundtable_s8_roadmap.md")

SYSTEM = "You are a startup CTO who has built and shipped 3 SaaS products from zero to $10K MRR. 你必须用中文回答。给出可执行的周级任务，附量化指标。"


def load_prev_summary(*paths):
    parts = []
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for r in data.get("results", []):
                if r.get("ok"):
                    # 取Qwen的最终裁决优先，其次取最长的
                    parts.append(f"【{r['model']}·S{data.get('session', '?')}】: {r['response'][:350]}")
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
    print("TITAN ROUNDTABLE S8: 12周落地路线图")
    print("=" * 60)

    prev = load_prev_summary(
        os.path.join(BASE_DIR, "titan_roundtable_s5.json"),
        os.path.join(BASE_DIR, "titan_roundtable_s6.json"),
        os.path.join(BASE_DIR, "titan_roundtable_s7.json"),
    )

    CONTEXT = f"""【S5-S7完整结论摘要】
{prev}

## S8圆桌 — 12周落地路线图

背景: Solo developer, 每天可投入4-6小时, 有Python/JS技能, 有3个LLM API, 已有shipmicro.com域名+Vercel部署, 当前收入$0。
目标: 12周后实现$500+/月的持续收入。"""

    # ── DeepSeek: 项目经理 ──
    prompt_ds = f"""{CONTEXT}

你是项目经理。制定12周路线图:

1. **Phase 1 (Week 1-4): 基础搭建**
   - 每周交付物(具体的文件名/功能)
   - 每周验收标准(量化指标)
   - 每周预计工时

2. **Phase 2 (Week 5-8): 变现启动**
   - 第一笔收入应该在哪周产生？
   - 收入来源是什么？
   - 流量从哪里来？

3. **Phase 3 (Week 9-12): 规模化**
   - 如何从$10/月增长到$500/月？
   - 关键增长杠杆是什么？
   - 自动化什么？手动优化什么？

4. **风险登记表**: Top 5风险 + 缓解方案

5. **每周仪表盘**: 跟踪什么KPI？(列出5个具体指标名+目标值)

总计不超过1500字。用表格呈现路线图。"""

    ds_result = {"model": "DeepSeek", "response": "", "ok": False}
    if DEEPSEEK_API_KEY:
        ds_result = call("DeepSeek", DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, "deepseek-chat", prompt_ds, 120)
    ds_text = ds_result.get("response", "")

    # ── Doubao: 创业导师 ──
    prompt_doubao = f"""{CONTEXT}

DeepSeek的路线图:
---
{ds_text}
---

你是Doubao，连续创业者/导师。审视路线图:

1. **进度风险**: 哪些周的任务量不现实？(Solo dev每天4-6h)
2. **收入预期校准**: DeepSeek的收入预期靠谱吗？给出你的真实估计
3. **最可能失败的环节**: 12周计划中最容易烂尾的是什么？为什么？
4. **快速胜利**: 有没有Week 1-2就能见到收入(哪怕$1)的快捷方式？
5. **中国市场时间线**: 在中国市场做这个，哪些步骤会更快/更慢？

总计不超过1200字。"""

    doubao_result = {"model": "Doubao", "response": "", "ok": False}
    if DOUBAO_API_KEY:
        doubao_result = call("Doubao", DOUBAO_BASE_URL, DOUBAO_API_KEY, DOUBAO_ENDPOINT, prompt_doubao, 180)
    doubao_text = doubao_result.get("response", "")

    # ── Qwen: 最终路线图 ──
    prompt_qwen = f"""{CONTEXT}

DeepSeek路线图:
---
{ds_text[:1200]}
---

Doubao评审:
---
{doubao_text[:1200]}
---

你是Qwen，做最终路线图决策:

1. **最终12周计划** — 用表格(周/交付物/验收指标/预计工时)
2. **第一周DAY BY DAY**: Week 1每天做什么(Mon-Sun)？
3. **止损决策点**: 哪一周如果没达到什么指标就该pivot？
4. **必须外包/买的**: 哪些环节不值得自己做？花钱买什么更划算？
5. **成功概率**: 你给这个12周计划打多少分(1-10)？为什么？

总计不超过1500字。用markdown表格呈现。"""

    qwen_result = {"model": "Qwen", "response": "", "ok": False}
    if QWEN_API_KEY:
        qwen_result = call("Qwen", QWEN_BASE_URL, QWEN_API_KEY, "qwen-max", prompt_qwen, 180)

    results = [ds_result, doubao_result, qwen_result]

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"time": datetime.now().isoformat(), "session": 8, "topic": "12_week_roadmap", "results": results}, f, indent=2, ensure_ascii=False)

    md = f"""# TITAN 圆桌 S8: 12周落地路线图
> 时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> 模式: 串行辩论 (DeepSeek → Doubao → Qwen)

---

## DeepSeek (项目经理)
{ds_text if ds_text else '❌ 未返回'}

---

## Doubao (创业导师)
{doubao_text if doubao_text else '❌ 未返回'}

---

## Qwen (最终路线图)
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
