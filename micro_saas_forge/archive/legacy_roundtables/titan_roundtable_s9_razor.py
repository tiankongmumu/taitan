"""
TITAN Engine — 4-AI Roundtable Session 9
核心议题: 架构路线大辩论：Antigravity极简剃刀MVP vs S5-S8庞大系统
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
OUTPUT_JSON = os.path.join(BASE_DIR, "titan_roundtable_s9.json")
OUTPUT_MD = os.path.join(BASE_DIR, "titan_roundtable_s9_razor.md")

SYSTEM = "You are a pragmatic software architect, growth hacker, and startup founder. Your goal is to maximize the probability of survival for a solo developer. 你必须用中文极度客观、冷血地进行技术和商业评审。"

def load_s5_to_s8_context():
    return """【前情提要】
S5-S8阶段，你们（三个AI）共同设计了一套“商业智能引擎”转型方案，包含10个Python模块构成的长流水线：
信号采集 -> 过滤 -> 聚合 -> 评分 -> 竞品分析 -> 策略生成 -> CPS注入 -> SEO内容生成 -> API网关暴露

【Antigravity 的冷血批评与重构建议 (Razor MVP)】
统筹AI (Antigravity) 认为你们的设计存在三大致命漏洞：
1. SEO内容已死：用LLM生成800字废话引流转化率为0，直接做“真实数据展示/排行榜排行榜”更有效。
2. API维护黑洞：找5个数据源，几天就因为限流封禁瘫痪，Solo dev精力会被耗尽。
3. Token/幻觉级联：10个模块层层传递会导致幻觉积累，成本指数上升。

Antigravity 提出了极简“剃刀”方案（只需3个文件）：
1. `pipeline_crawler.py`: 只抓两个极度稳定的源（Reddit r/SaaS热帖 + 淘宝企业服务高佣金榜）。
2. `titan_analyzer.py`: 直接把抓到的Top 20帖子和Top 20商品组装成巨大JSON，让最强模型一次性进行Few-Shot撮合匹配（痛点-方案-链接）。
3. `static_publisher.py`: 渲染成极简HTML数据卡片/排行榜（通过GitHub Actions推到Vercel）。
"""

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
    print("TITAN ROUNDTABLE S9: Antigravity Razor vs Complex System")
    print("=" * 60)

    CONTEXT = load_s5_to_s8_context()

    # ── DeepSeek: 原始设计者视角 ──
    prompt_ds = f"""{CONTEXT}

你是DeepSeek，之前复杂架构的发起者。现在面对Antigravity的“降维打击”，请你进行深度反思：

1. **直面批评**：Antigravity说的三大漏洞（SEO已死、API黑洞、Token联级幻觉）是否切中要害？承认错误或进行辩护。
2. **架构对比**：对比10模块Pipeline和3个文件的Razor MVP，各自在“第一周存活率”上的得分是多少？
3. **技术难点剖析**：Antigravity的`titan_analyzer.py`（巨大JSON，一次发给LLM做撮合）在实现上有什么难度？（Token上下文限制？推理能力瓶颈？）
4. **你的投票**：如果是你作为Solo Dev，你会选原方案还是Razor极简方案？

总计不超过1200字。"""

    ds_result = {"model": "DeepSeek", "response": "", "ok": False}
    if DEEPSEEK_API_KEY:
        ds_result = call("DeepSeek", DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, "deepseek-chat", prompt_ds, 120)
    ds_text = ds_result.get("response", "")

    # ── Doubao: 商业化落地验证 ──
    prompt_doubao = f"""{CONTEXT}

DeepSeek的反思：
---
{ds_text}
---

你是Doubao，专注中国市场落地与商业验证。就“直接做真实数据展现/排行榜卡片取代AI SEO生成”这个点：

1. **流量转化**：这两种截然不同的大众展现形式（长文 vs 数据卡片/排行榜），在中国市场环境下，哪个带货转化率（淘宝联盟CPS）会更高？给出真实商业逻辑分析。
2. **流量来源**：如果放弃写文章，那做出的“网页数据卡片”靠什么获得冷启动流量？（微信群发？知乎图文？）
3. **数据源批判**：Antigravity建议只抓【Reddit】和【淘宝联盟企业大王榜】组合，这在中国有没有“水土不服”的问题？
4. **你的投票**：支持Antigravity的极致实用主义，还是坚守原本稍微长远的规划？

总计不超过1200字。"""

    doubao_result = {"model": "Doubao", "response": "", "ok": False}
    if DOUBAO_API_KEY:
        doubao_result = call("Doubao", DOUBAO_BASE_URL, DOUBAO_API_KEY, DOUBAO_ENDPOINT, prompt_doubao, 180)
    doubao_text = doubao_result.get("response", "")

    # ── Qwen: CTO最终代码设计 ──
    prompt_qwen = f"""{CONTEXT}

DeepSeek立场：
---
{ds_text[:1200]}
---

Doubao立场：
---
{doubao_text[:1200]}
---

你是Qwen，最终执行的CTO。既然这是一场决定代码命运的会议：

1. **一锤定音**：选定最终的架构策略，并给出你的CTO级别总结。
2. **核心逻辑重写**：采用Antigravity的Razor方案，给出 `titan_analyzer.py` 的关键Python代码框架！（重点展示：怎么把 Reddit帖子 和 淘宝商品两个异构数据组装，如何写这个一次性的“Few-Shot”系统Prompt给LLM，提取出对应的最佳推荐结果）。
3. **首周10小时计划**：作为下班后的Solo dev，只给你10个小时，怎么先把这套Razor闭环跑上线？

总计不超过1500字。包含具体的Prompt设计思路。"""

    qwen_result = {"model": "Qwen", "response": "", "ok": False}
    if QWEN_API_KEY:
        qwen_result = call("Qwen", QWEN_BASE_URL, QWEN_API_KEY, "qwen-max", prompt_qwen, 180)

    results = [ds_result, doubao_result, qwen_result]

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"time": datetime.now().isoformat(), "session": 9, "topic": "razor_vs_complex", "results": results}, f, indent=2, ensure_ascii=False)

    md = f"""# TITAN 圆桌 S9: 架构大辩论 — 极简MVP vs 庞大系统
> 时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> 模式: 串行辩论 (DeepSeek → Doubao → Qwen)

---

## 批评与重构背景 (Antigravity)
- **指出漏洞**: 1. AI SEO纯长文流量转化低，该做数据排行榜; 2. 5大API数据源维护=Solo开发者陷阱; 3. 10环节Pipeline=极高成本与幻觉叠加。
- **Razor极简三件套**: 
  1. `pipeline_crawler.py` (仅Reddit+淘宝联盟)
  2. `titan_analyzer.py` (单次LLM撮合痛点与产品)
  3. `static_publisher.py` (渲染直观的数据卡片/排行榜)

---

## DeepSeek (原架构师的反思)
{ds_text if ds_text else '❌ 未返回'}

---

## Doubao (商业化落地验证)
{doubao_text if doubao_text else '❌ 未返回'}

---

## Qwen (CTO最终裁定与核心代码)
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
