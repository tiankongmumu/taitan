import os
import json
import requests

from config import FORGE_ROOT
from core_generators.llm_client import LLMClient
import memory_bank as mem

def run_assessment():
    print("🚀 TITAN v3.0 架构师评估系统启动")
    
    # 1. 提取当前项目
    apps_dir = os.path.join(FORGE_ROOT, "generated_apps")
    if not os.path.exists(apps_dir):
        print("未找到 generated_apps 目录。")
        return
        
    recent_apps = sorted([d for d in os.listdir(apps_dir) if os.path.isdir(os.path.join(apps_dir, d))], reverse=True)[:3]
    print(f"📥 提取近期生成的 {len(recent_apps)} 个项目: {recent_apps}")
    
    app_codes = ""
    for app in recent_apps:
        page_path = os.path.join(apps_dir, app, "src", "app", "page.tsx")
        if os.path.exists(page_path):
            with open(page_path, "r", encoding="utf-8") as f:
                code = f.read()
                app_codes += f"--- APP: {app} ---\n{code[:3000]}\n\n"

    # 2. 提取新学到的高级模式
    patterns = mem._load_patterns()
    pattern_text = ""
    for p in patterns:
        pattern_text += f"- [{p.get('category')}] 源自 {p.get('source_repo')}: {p.get('description')}\n"

    # 3. 构建评估 Prompt
    prompt = f"""你是 TITAN 智能引擎的首席架构师 (CTO)。
我们刚刚通过 GitHub Top 100 开源项目 (如 Dify, RAGFlow, LobeHub) 学习了大量高级能力，具体如下：
{pattern_text}

然而，在应用这些新能力之前，我们昨天/今天用 TITAN v2.0 引擎生成了一些微型 SaaS 应用：
CURRENT GENERATED APPS (前台代码片段):
{app_codes}

任务：
请对我们目前生成的这些项目进行【专业、冷静、甚至可以用批判的眼光】的架构分析报告。
请重点阐述：
1. 【现状诊断】：从顶层架构、可维护性、Agent流、数据处理角度看，这些代码目前有什么明显的幼稚或不足之处？
2. 【降维打击】：结合我们刚刚从 GitHub 学来的神级设计模式（如循环节点、多租户隔离、模块化Prompt分层），如果我们用 TITAN v3.0 重写它们，能具体在哪些地方产生质的飞跃？
3. 【最终结论】：对 TITAN 引擎未来生产力的预期。

以 Markdown 格式输出。语言风格：极其专业，冷静，类似高级首席架构师汇报。
"""

    print("🧠 正在使用 DeepSeek (CTO 模式) 深入评估代码与架构差距...")
    llm = LLMClient()
    report = llm.generate(prompt)

    out_file = os.path.join(os.path.dirname(FORGE_ROOT), "titan_v3_assessment.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"✅ 评估完成！报告已保存至 {out_file}")

if __name__ == "__main__":
    run_assessment()
