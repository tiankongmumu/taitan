"""
TITAN Engine — 4-AI Roundtable Session 5
核心议题: 商业智能引擎架构蓝图
串行辩论: DeepSeek → Doubao(带DS结论) → Qwen(带DS+Doubao结论)
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
OUTPUT_JSON = os.path.join(BASE_DIR, "titan_roundtable_s5.json")
OUTPUT_MD = os.path.join(BASE_DIR, "titan_roundtable_s5_architecture.md")

# ──── S4 结论摘要（作为背景上下文）────
S4_CONTEXT = """【前4轮圆桌结论摘要】
- 架构评分: 3-5/10, 产品评分: 2/10
- 3-AI全票通过: 放弃产品生成，转型商业智能引擎(方向A)
- 路径1(生成高质量产品→广告变现): 可行性2.3/10 ❌
- 路径2(商业智能引擎): 可行性7.0/10 ✅
- 共识: AI应用于需求挖掘、商业漏斗优化、行为分析，而非代码生成
- 现有引擎: demand_radar.py(3源需求扫描), competitor_scanner.py(LLM竞品分析),
  browser_qa.py(7维质量测试), titan_brain.py(7步自治循环)
- 技术栈: Python + Next.js + Vercel, LLM降级链(DeepSeek→Doubao→Qwen)
- 当前收入: $0/月
"""

SYSTEM = "You are a principal systems architect and brutal business strategist. 你必须用中文回答。不要空洞建议，要给出具体的模块名、函数签名、数据流。"


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


# ──── Prompts ────

PROMPT_DS = f"""{S4_CONTEXT}

## S5圆桌 — 商业智能引擎架构蓝图

你是首席架构师。基于S4的共识，设计TITAN Engine v5.0的完整架构。

### 必须回答:

1. **核心模块清单** (7-10个模块)
   - 每个模块: 模块名(英文) + 职责 + 输入/输出 + 关键函数签名
   - 例: `opportunity_scorer.py` → 输入: 原始信号list → 输出: 评分后的机会list

2. **数据流图**
   - 从"发现机会"到"产生收入"的完整pipeline
   - 用ASCII画出模块之间的调用关系

3. **现有模块改造方案**
   - demand_radar.py: 保留/重写/删除? 改什么?
   - competitor_scanner.py: 保留/重写/删除?
   - browser_qa.py: 保留/重写/删除?
   - titan_brain.py: 保留/重写/删除?
   - forge_master.py / app_builder.py: 这些"代码生成"模块怎么处理?

4. **技术选型**
   - 数据库: SQLite够用? 还是需要PostgreSQL?
   - 调度: cron还是APScheduler? 
   - 存储: 文件系统还是需要对象存储?
   - 前端仪表盘: 需不需要? 用什么框架?

5. **MVP范围** — 第一个能跑起来的最小版本包含哪些模块?

每个小节200字以内。总计不超过1500字。具体、可执行、有代码级细节。"""


def make_prompt_doubao(ds_response):
    return f"""{S4_CONTEXT}

## S5圆桌 — 商业智能引擎架构蓝图

DeepSeek(首席架构师)的方案:
---
{ds_response}
---

你是Doubao，商业实战专家。审视DeepSeek的架构方案，回答:

1. **架构评分**(1-10): DeepSeek方案的优缺点
2. **补充/修正**: 他漏了什么关键模块? 哪些设计过度工程化?
3. **数据源实操**: 具体能接入哪些免费/低成本数据API? (不要空说"接入Twitter"，说清楚用什么API、费用多少、限流多少)
4. **变现模块细节**: 从架构角度，变现通道(CPS/SEO/API)各需要什么技术组件?
5. **Solo Dev风险**: 一个人能维护这套架构吗? 哪些模块最容易成为瓶颈?

总计不超过1200字。极度务实，不要画饼。"""


def make_prompt_qwen(ds_response, doubao_response):
    return f"""{S4_CONTEXT}

## S5圆桌 — 商业智能引擎架构蓝图

DeepSeek(首席架构师)的方案:
---
{ds_response[:1500]}
---

Doubao(商业实战专家)的评审:
---
{doubao_response[:1500]}
---

你是Qwen，技术CTO + 最终裁决者。看了两人的讨论:

1. **最终架构决定**: 综合DS和Doubao，给出你认为最优的模块清单(每个一行)
2. **优先级排序**: 哪个模块先做、哪个后做？用P0/P1/P2标注
3. **技术栈最终选型**: 数据库/调度/存储/前端的最终决定(一个选项，不要"都可以")
4. **砍掉什么**: 哪些是过度设计、Solo Dev根本不需要的?
5. **第一周交付物**: 从0开始，第一周应该交付什么才能证明方向A可行?

总计不超过1200字。给出明确答案，不要模棱两可。"""


def main():
    print("=" * 60)
    print("TITAN ROUNDTABLE S5: 商业智能引擎架构蓝图")
    print("=" * 60)

    results = []

    # ── 第1轮: DeepSeek (架构师) ──
    ds_result = {"model": "DeepSeek", "response": "", "ok": False}
    if DEEPSEEK_API_KEY:
        ds_result = call("DeepSeek", DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, "deepseek-chat", PROMPT_DS, 120)
    results.append(ds_result)
    ds_text = ds_result.get("response", "")

    # ── 第2轮: Doubao (商业专家，带DS结论) ──
    doubao_result = {"model": "Doubao", "response": "", "ok": False}
    if DOUBAO_API_KEY:
        doubao_result = call("Doubao", DOUBAO_BASE_URL, DOUBAO_API_KEY, DOUBAO_ENDPOINT,
                             make_prompt_doubao(ds_text), 180)
    results.append(doubao_result)
    doubao_text = doubao_result.get("response", "")

    # ── 第3轮: Qwen (CTO裁决，带DS+Doubao结论) ──
    qwen_result = {"model": "Qwen", "response": "", "ok": False}
    if QWEN_API_KEY:
        qwen_result = call("Qwen", QWEN_BASE_URL, QWEN_API_KEY, "qwen-max",
                           make_prompt_qwen(ds_text, doubao_text), 180)
    results.append(qwen_result)

    # ── 保存JSON ──
    data = {"time": datetime.now().isoformat(), "session": 5, "topic": "architecture_blueprint", "results": results}
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # ── 生成MD报告 ──
    md = f"""# TITAN 圆桌 S5: 商业智能引擎架构蓝图
> 时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> 模式: 串行辩论 (DeepSeek → Doubao → Qwen)

---

## DeepSeek (首席架构师)
{ds_text if ds_text else '❌ 未返回'}

---

## Doubao (商业实战专家)
{doubao_text if doubao_text else '❌ 未返回'}

---

## Qwen (CTO 最终裁决)
{qwen_result.get('response', '') if qwen_result.get('ok') else '❌ 未返回'}
"""
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md)

    # ── 打印结果 ──
    for x in results:
        if x.get("ok"):
            print(f"\n{'='*50}\n{x['model']} ({x.get('chars', 0)} chars, {x.get('time', 0)}s)\n{'='*50}\n{x['response']}\n")
        else:
            print(f"\nFAILED: {x['model']}")

    ok_count = sum(1 for x in results if x.get("ok"))
    print(f"\n✅ {ok_count}/3 AI returned | Saved: {OUTPUT_JSON} + {OUTPUT_MD}")


if __name__ == "__main__":
    main()
