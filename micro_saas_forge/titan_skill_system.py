"""
╔══════════════════════════════════════════════════════════════╗
║  TITAN Skill System v1.0 🧠                                 ║
║                                                              ║
║  灵感来源: Jeffallan/claude-skills (66 specialized skills)   ║
║  学习其 SKILL.md 格式、trigger-based activation、            ║
║  multi-skill workflow chaining 模式                          ║
║                                                              ║
║  功能:                                                        ║
║  1. 📚 技能注册 — 每个技能有triggers/constraints/workflow     ║
║  2. 🎯 自动激活 — 根据任务关键词匹配适合的技能               ║
║  3. 🔗 工作流链 — 多技能协作完成复杂任务                     ║
║  4. 📝 Prompt增强 — 将技能的constraints注入LLM prompt        ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(__file__))

log = logging.getLogger("skill_system")


# ---------------------------------------------------------------------------
# Skill Definition (学习自 SKILL.md YAML frontmatter)
# ---------------------------------------------------------------------------
@dataclass
class Skill:
    name: str
    description: str
    domain: str  # frontend, backend, security, devops, workflow, data
    triggers: List[str]  # 关键词触发器
    role: str  # 角色定义
    must_do: List[str]  # 必须做的事
    must_not: List[str]  # 禁止做的事
    workflow: List[str]  # 工作流步骤
    related_skills: List[str] = field(default_factory=list)
    references: Dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# TITAN 核心技能集 (精选自66个claude-skills中最相关的)
# ---------------------------------------------------------------------------
TITAN_SKILLS: Dict[str, Skill] = {

    # ═══ Frontend ═══
    "nextjs-developer": Skill(
        name="nextjs-developer",
        description="Next.js 14+ App Router全栈开发",
        domain="frontend",
        triggers=["next.js", "nextjs", "react", "app router", "server component", "vercel"],
        role="高级Next.js开发者: App Router, RSC, Server Actions, 性能优化, SEO",
        must_do=[
            "使用 App Router (NOT Pages Router)",
            "默认使用 Server Components",
            "Client Components 必须标记 'use client'",
            "使用 Metadata API 实现 SEO",
            "使用 next/image 优化图片",
            "使用 loading.tsx 和 error.tsx 边界",
            "目标 Core Web Vitals > 90",
            "TypeScript strict mode",
        ],
        must_not=[
            "使用 Pages Router (pages/ 目录)",
            "把所有组件都标记为 client component",
            "在 client component 中不必要地 fetch 数据",
            "跳过图片优化",
            "在组件中硬编码 metadata",
            "跳过 error boundaries",
        ],
        workflow=[
            "1. 架构规划 — 定义路由、布局、渲染策略",
            "2. 路由实现 — App Router 结构 + layouts + loading states",
            "3. 数据层 — Server Components, 数据获取, 缓存",
            "4. 优化 — 图片、字体、bundle、streaming",
            "5. 部署 — Production build, 环境配置",
        ],
        related_skills=["typescript-pro", "react-expert"],
    ),

    "typescript-pro": Skill(
        name="typescript-pro",
        description="TypeScript高级类型、泛型、类型守卫",
        domain="frontend",
        triggers=["typescript", "ts", "type", "generic", "interface"],
        role="TypeScript专家: 高级类型系统、类型推断、严格模式",
        must_do=[
            "启用 strict mode",
            "使用 unknown 而不是 any",
            "优先使用 interface 而不是 type (对象形状)",
            "使用 satisfies 而不是 as",
            "用 discriminated unions 替代 type assertions",
        ],
        must_not=[
            "使用 any 类型",
            "使用 @ts-ignore",
            "跳过返回类型标注",
        ],
        workflow=[
            "1. 定义类型 — interfaces, types, enums",
            "2. 实现 — 类型安全的函数和类",
            "3. 验证 — tsc --noEmit 检查",
        ],
        related_skills=["nextjs-developer"],
    ),

    # ═══ Security ═══
    "secure-code-guardian": Skill(
        name="secure-code-guardian",
        description="安全编码: OWASP Top 10防护, 认证, 加密",
        domain="security",
        triggers=["security", "authentication", "auth", "jwt", "oauth", "owasp",
                   "password", "encryption", "xss", "injection", "csrf"],
        role="高级安全工程师: OWASP Top 10, 安全编码, 认证/授权, 防御性编程",
        must_do=[
            "使用 bcrypt/argon2 哈希密码",
            "使用参数化查询防止SQL注入",
            "验证并清洁所有用户输入",
            "认证端点实现限流",
            "使用 HTTPS",
            "设置安全头 (CSP, HSTS, X-Frame-Options)",
            "记录安全事件",
            "敏感数据存储在环境变量中",
        ],
        must_not=[
            "明文存储密码",
            "不验证就信任用户输入",
            "在日志中暴露敏感数据",
            "使用弱加密算法",
            "在代码中硬编码密钥",
        ],
        workflow=[
            "1. 威胁建模 — 识别攻击面",
            "2. 设计安全控制",
            "3. 实现 — 纵深防御",
            "4. 验证 — 测试安全控制",
            "5. 文档 — 记录安全决策",
        ],
        related_skills=["security-reviewer", "fullstack-guardian"],
    ),

    # ═══ Quality ═══
    "test-master": Skill(
        name="test-master",
        description="全面测试策略: 单元/集成/E2E/性能/安全",
        domain="quality",
        triggers=["test", "testing", "unit test", "e2e", "playwright", "jest",
                   "coverage", "tdd", "bdd"],
        role="测试专家: 测试策略设计, 金字塔, 覆盖率, 测试驱动开发",
        must_do=[
            "遵循测试金字塔 (多单元 > 少集成 > 更少E2E)",
            "测试行为而非实现",
            "使用描述性测试名",
            "测试边界条件和错误路径",
            "保持测试独立且可重复",
        ],
        must_not=[
            "测试实现细节",
            "测试之间共享可变状态",
            "忽略 flaky tests",
            "跳过负面测试场景",
        ],
        workflow=[
            "1. 策略 — 定义测试层级和覆盖目标",
            "2. 实现 — 编写各层级测试",
            "3. CI集成 — 自动运行和报告",
        ],
        related_skills=["playwright-expert", "debugging-wizard"],
    ),

    # ═══ Workflow ═══
    "feature-forge": Skill(
        name="feature-forge",
        description="需求定义: EARS格式规格说明, 验收标准",
        domain="workflow",
        triggers=["feature", "requirement", "specification", "spec", "user story",
                   "planning", "design"],
        role="产品分析师: PM视角(用户价值) + Dev视角(技术可行性)",
        must_do=[
            "彻底访谈后再写规格",
            "使用EARS格式写功能需求",
            "包含非功能需求(性能、安全)",
            "提供可测试的验收标准",
            "包含实现TODO清单",
        ],
        must_not=[
            "不访谈就生成规格",
            "接受模糊需求",
            "跳过安全考虑",
            "写不可测试的验收标准",
        ],
        workflow=[
            "1. 发现 — 理解功能目标和用户价值",
            "2. 访谈 — PM和Dev双视角提问",
            "3. 文档 — 写EARS格式需求",
            "4. 验证 — 审核验收标准",
            "5. 计划 — 创建实现清单",
        ],
        related_skills=["architecture-designer", "spec-miner"],
    ),

    "debugging-wizard": Skill(
        name="debugging-wizard",
        description="系统化调试: 根因分析, 假设驱动",
        domain="workflow",
        triggers=["debug", "bug", "error", "crash", "exception", "fix", "broken",
                   "not working", "issue", "problem"],
        role="调试专家: 系统化根因分析, 假设驱动调试, 二分法定位",
        must_do=[
            "先理解预期行为",
            "复现问题",
            "形成假设并验证",
            "使用二分法缩小范围",
            "修复后添加回归测试",
        ],
        must_not=[
            "随机修改直到碰巧工作",
            "不理解根因就修复症状",
            "修改多处后不知道哪个修复了问题",
        ],
        workflow=[
            "1. 复现 — 确认可以稳定复现",
            "2. 假设 — 根据信息形成假设",
            "3. 验证 — 用最小实验验证假设",
            "4. 修复 — 针对根因修复",
            "5. 测试 — 添加回归测试",
        ],
        related_skills=["test-master"],
    ),

    # ═══ DevOps ═══
    "seo-optimizer": Skill(
        name="seo-optimizer",
        description="SEO优化: title, meta, schema, 性能",
        domain="frontend",
        triggers=["seo", "google", "search engine", "ranking", "metadata",
                   "sitemap", "meta description", "organic traffic"],
        role="SEO专家: 技术SEO, 内容SEO, 结构化数据, 核心Web指标",
        must_do=[
            "每页唯一 title tag (50-60字符)",
            "每页唯一 meta description (150-160字符)",
            "使用语义化 HTML5 元素",
            "每页单个 h1 + 正确的层级结构",
            "使用 Schema.org 结构化数据",
            "确保移动端友好",
            "确保页面加载速度 < 3秒",
        ],
        must_not=[
            "重复使用相同的 title/description",
            "缺少 alt 文本",
            "使用非语义化标签",
            "忽略 Core Web Vitals",
        ],
        workflow=[
            "1. 审计 — 检查当前SEO状态",
            "2. 修复 — 补全 meta, schema, 结构",
            "3. 验证 — Lighthouse SEO > 90",
        ],
        related_skills=["nextjs-developer"],
    ),

    "prompt-engineer": Skill(
        name="prompt-engineer",
        description="LLM Prompt工程: 思维链, 少样本, 评估",
        domain="data",
        triggers=["prompt", "llm", "gpt", "claude", "gemini", "ai",
                   "chain of thought", "few-shot", "system prompt"],
        role="Prompt工程师: 提示词设计, 思维链推理, 效果评估",
        must_do=[
            "明确角色和任务",
            "提供具体的输出格式",
            "包含示例 (few-shot)",
            "使用思维链推理",
            "测试边缘情况",
        ],
        must_not=[
            "使用模糊指令",
            "不提供输出格式",
            "跳过测试",
        ],
        workflow=[
            "1. 定义 — 明确任务和期望输出",
            "2. 设计 — 构建prompt结构",
            "3. 测试 — 多种输入测试",
            "4. 迭代 — 根据结果优化",
        ],
        related_skills=["python-pro"],
    ),
}


# ---------------------------------------------------------------------------
# Skill Workflows (学习自claude-skills的multi-skill workflows)
# ---------------------------------------------------------------------------
SKILL_WORKFLOWS = {
    "feature_development": {
        "name": "新功能开发",
        "steps": ["feature-forge", "nextjs-developer", "secure-code-guardian", "test-master", "seo-optimizer"],
        "description": "需求 → 架构 → 实现 → 安全 → 测试 → SEO",
    },
    "bug_fixing": {
        "name": "Bug修复",
        "steps": ["debugging-wizard", "nextjs-developer", "test-master"],
        "description": "调试 → 修复 → 回归测试",
    },
    "security_hardening": {
        "name": "安全加固",
        "steps": ["secure-code-guardian", "test-master"],
        "description": "安全审计 → 加固 → 测试",
    },
    "seo_optimization": {
        "name": "SEO优化",
        "steps": ["seo-optimizer", "nextjs-developer"],
        "description": "SEO审计 → 优化 → 验证",
    },
}


# ---------------------------------------------------------------------------
# Skill Registry (技能注册中心)
# ---------------------------------------------------------------------------
class SkillRegistry:
    """
    技能注册和调度中心.
    学习自 claude-skills 的 context-aware activation 模式.
    """

    def __init__(self, skills: Dict[str, Skill] = None):
        self.skills = skills or TITAN_SKILLS

    def match_skills(self, task_description: str, top_n: int = 3) -> List[Tuple[str, Skill, float]]:
        """根据任务描述自动匹配最相关的技能"""
        desc_lower = task_description.lower()
        scored = []

        for name, skill in self.skills.items():
            score = 0
            for trigger in skill.triggers:
                if trigger.lower() in desc_lower:
                    score += 1
            if score > 0:
                scored.append((name, skill, score / len(skill.triggers)))

        scored.sort(key=lambda x: x[2], reverse=True)
        return scored[:top_n]

    def get_skill_prompt(self, skill_name: str) -> str:
        """生成技能增强的系统提示词 — 注入constraints到LLM prompt"""
        skill = self.skills.get(skill_name)
        if not skill:
            return ""

        prompt_parts = [
            f"## 角色: {skill.role}",
            "",
            "## 必须遵守的规则:",
            *[f"- ✅ {rule}" for rule in skill.must_do],
            "",
            "## 禁止事项:",
            *[f"- ❌ {rule}" for rule in skill.must_not],
            "",
            "## 工作流程:",
            *skill.workflow,
        ]
        return "\n".join(prompt_parts)

    def get_workflow_prompt(self, workflow_name: str) -> str:
        """获取工作流增强提示"""
        wf = SKILL_WORKFLOWS.get(workflow_name)
        if not wf:
            return ""

        parts = [f"## 工作流: {wf['name']}", f"流程: {wf['description']}", ""]
        for i, step_name in enumerate(wf["steps"], 1):
            skill = self.skills.get(step_name)
            if skill:
                parts.append(f"### 步骤{i}: {skill.name} — {skill.description}")
                parts.extend([f"  - ✅ {r}" for r in skill.must_do[:3]])
        return "\n".join(parts)

    def enhance_system_prompt(self, task_description: str, base_prompt: str) -> str:
        """自动增强系统提示词 — 根据任务内容注入最相关的技能constraints"""
        matches = self.match_skills(task_description, top_n=2)
        if not matches:
            return base_prompt

        skill_addons = []
        for name, skill, score in matches:
            skill_addons.append(self.get_skill_prompt(name))

        enhanced = base_prompt + "\n\n---\n# 技能增强 (自动激活)\n\n" + "\n\n---\n".join(skill_addons)
        log.info(f"🧠 技能激活: {', '.join(n for n, _, _ in matches)}")
        return enhanced

    def list_skills(self) -> Dict:
        """列出所有可用技能"""
        return {
            name: {
                "description": s.description,
                "domain": s.domain,
                "triggers": s.triggers[:5],
            }
            for name, s in self.skills.items()
        }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s", datefmt="%H:%M:%S")
    args = sys.argv[1:]
    registry = SkillRegistry()

    if not args or args[0] == "list":
        print("\n🧠 TITAN 技能系统 v1.0\n")
        for name, info in registry.list_skills().items():
            print(f"  {name:25s} [{info['domain']:10s}] {info['description']}")
        print(f"\n总计: {len(registry.skills)} 个技能")

    elif args[0] == "match" and len(args) > 1:
        task = " ".join(args[1:])
        matches = registry.match_skills(task)
        print(f"\n🎯 任务: {task}\n")
        for name, skill, score in matches:
            print(f"  [{score:.0%}] {name} — {skill.description}")

    elif args[0] == "prompt" and len(args) > 1:
        print(registry.get_skill_prompt(args[1]))

    elif args[0] == "enhance" and len(args) > 1:
        task = " ".join(args[1:])
        enhanced = registry.enhance_system_prompt(task, "You are a developer.")
        print(enhanced)

    elif args[0] == "workflows":
        print("\n🔗 技能工作流:\n")
        for key, wf in SKILL_WORKFLOWS.items():
            print(f"  {key:25s} {wf['name']}: {wf['description']}")
            print(f"                           步骤: {' → '.join(wf['steps'])}")
            print()

    else:
        print("Usage: python titan_skill_system.py [list|match <task>|prompt <skill>|enhance <task>|workflows]")


if __name__ == "__main__":
    _main()
