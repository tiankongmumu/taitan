"""
ShipMicro Agent Skills Framework — 模块化技能系统
为 AI Agent 提供可插拔、可组合的技能模块。
每个技能是一个独立的"专家模块"，Agent 可以按需加载和调用。

架构:
  AgentSkillRegistry (技能注册中心)
    ├── CodeGenSkill       — 代码生成专家
    ├── UIDesignSkill      — UI/UX 设计专家
    ├── SEOSkill           — SEO 优化专家
    ├── DebuggingSkill     — 调试修复专家
    ├── ResearchSkill      — 市场调研专家
    └── GameDevSkill       — 游戏开发专家（预留）
"""
import os
import sys
import json
from abc import ABC, abstractmethod
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from logger import get_logger
from core_generators.llm_client import LLMClient

log = get_logger("agent_skills")


# ═══════════════════════════════════════════════════
# 基础技能接口
# ═══════════════════════════════════════════════════

class BaseSkill(ABC):
    """所有技能的抽象基类"""

    def __init__(self):
        self.name = "base_skill"
        self.description = "Base skill interface"
        self.version = "1.0"
        self.llm = LLMClient()
        self.call_count = 0
        self.success_count = 0

    @abstractmethod
    def execute(self, context: dict) -> dict:
        """执行技能，接收上下文，返回结果"""
        pass

    def get_system_prompt(self) -> str:
        """返回该技能专属的 system prompt"""
        return ""

    def get_stats(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "calls": self.call_count,
            "successes": self.success_count,
            "success_rate": f"{self.success_count / max(self.call_count, 1) * 100:.0f}%",
        }

    def _call_llm(self, prompt: str) -> str:
        """统一的 LLM 调用封装"""
        self.call_count += 1
        result = self.llm.generate(prompt)
        if result:
            self.success_count += 1
        return result or ""


# ═══════════════════════════════════════════════════
# 具体技能实现
# ═══════════════════════════════════════════════════

class CodeGenSkill(BaseSkill):
    """代码生成专家 — 擅长生成高质量的 React/Next.js 组件"""

    def __init__(self):
        super().__init__()
        self.name = "code_gen"
        self.description = "Generate high-quality React/Next.js components"

    def get_system_prompt(self) -> str:
        return """You are an expert React/Next.js developer specializing in creating
production-ready, single-file components. You excel at:
- Clean, readable TypeScript code
- TailwindCSS for elegant UIs
- Proper React hooks and state management
- Accessibility and responsive design
Always keep code under 200 lines. Use "use client" when needed."""

    def execute(self, context: dict) -> dict:
        spec = context.get("app_spec", {})
        extra = context.get("extra_instructions", "")
        prompt = f"""{self.get_system_prompt()}

Generate a complete page.tsx for:
{json.dumps(spec, indent=2)}

{extra}

Requirements:
1. Export default function component
2. TailwindCSS styling
3. Under 200 lines
4. Wrap in ```tsx block
"""
        code = self._call_llm(prompt)
        extracted = self.llm.extract_code_block(code)
        return {"code": extracted or "", "raw": code, "success": bool(extracted)}


class UIDesignSkill(BaseSkill):
    """UI/UX 设计专家 — 生成精美的界面设计指导"""

    def __init__(self):
        super().__init__()
        self.name = "ui_design"
        self.description = "Generate beautiful UI/UX design guidance"

    def get_system_prompt(self) -> str:
        return """You are a senior UI/UX designer who creates stunning, modern web interfaces.
You specialize in:
- Dark mode design with glassmorphism effects
- Micro-animations and hover effects
- Color theory and typography
- Mobile-first responsive layouts
- Accessibility (WCAG 2.1 AA)"""

    def execute(self, context: dict) -> dict:
        tool_name = context.get("tool_name", "Web Tool")
        tool_desc = context.get("tool_description", "")
        prompt = f"""{self.get_system_prompt()}

Design a UI specification for: {tool_name}
Description: {tool_desc}

Provide:
1. Color palette (hex codes for primary, secondary, accent, background, text)
2. Typography (font families, sizes)
3. Key UI components and layout structure
4. 3 micro-animations to add polish
5. A TailwindCSS className string for the main container

Be concise. Max 200 words.
"""
        result = self._call_llm(prompt)
        return {"design_spec": result, "success": bool(result)}


class SEOSkill(BaseSkill):
    """SEO 优化专家 — 生成优化的标题、描述和关键词"""

    def __init__(self):
        super().__init__()
        self.name = "seo"
        self.description = "Generate optimized SEO metadata and content"

    def get_system_prompt(self) -> str:
        return """You are an SEO expert who optimizes web pages for maximum search visibility.
You specialize in:
- Keyword research and long-tail keywords
- Meta title and description optimization
- Content structure for featured snippets
- Technical SEO best practices"""

    def execute(self, context: dict) -> dict:
        tool_name = context.get("tool_name", "")
        tool_desc = context.get("tool_description", "")
        prompt = f"""{self.get_system_prompt()}

Create SEO metadata for: {tool_name}
Description: {tool_desc}

Return JSON:
{{
  "title": "< 60 chars, include primary keyword",
  "description": "< 155 chars, compelling with CTA",
  "keywords": ["keyword1", "keyword2", ...],
  "h1": "main heading",
  "slug_suggestion": "url-friendly-slug"
}}

Wrap JSON in ```json block.
"""
        result = self._call_llm(prompt)
        try:
            json_str = self.llm.extract_code_block(result)
            seo_data = json.loads(json_str) if json_str else {}
        except (json.JSONDecodeError, TypeError):
            seo_data = {}
        return {"seo_data": seo_data, "raw": result, "success": bool(seo_data)}


class DebuggingSkill(BaseSkill):
    """调试修复专家 — 分析错误并生成修复方案"""

    def __init__(self):
        super().__init__()
        self.name = "debugging"
        self.description = "Analyze errors and generate fix strategies"

    def get_system_prompt(self) -> str:
        return """You are a debugging expert who excels at diagnosing and fixing build errors.
You specialize in:
- Next.js / React build errors
- TypeScript type errors
- Hydration mismatches
- Module resolution issues
You always provide complete, drop-in replacement code."""

    def execute(self, context: dict) -> dict:
        error = context.get("error_output", "")
        code = context.get("current_code", "")
        memory_hints = context.get("memory_hints", "")
        skill_hints = context.get("skill_hints", "")

        prompt = f"""{self.get_system_prompt()}

Fix this build error:

Code:
```tsx
{code[:3000]}
```

Error:
```
{error[:1500]}
```
{memory_hints}
{skill_hints}

Return the COMPLETE fixed file in a ```tsx block.
Keep under 200 lines.
"""
        result = self._call_llm(prompt)
        fixed = self.llm.extract_code_block(result)
        return {"fixed_code": fixed or "", "raw": result, "success": bool(fixed)}


class ResearchSkill(BaseSkill):
    """市场调研专家 — 分析市场趋势，评估产品可行性"""

    def __init__(self):
        super().__init__()
        self.name = "research"
        self.description = "Analyze market trends and evaluate product viability"

    def get_system_prompt(self) -> str:
        return """You are a market research analyst who evaluates product ideas.
You specialize in:
- Developer tools market analysis
- Competitive landscape assessment
- SEO keyword opportunity analysis
- User pain point identification"""

    def execute(self, context: dict) -> dict:
        idea = context.get("idea", "")
        prompt = f"""{self.get_system_prompt()}

Evaluate this product idea: {idea}

Score (1-10) on:
1. Market demand
2. Competition level (10=low competition)
3. SEO opportunity
4. Technical feasibility
5. Monetization potential

Return JSON:
{{
  "scores": {{"demand": N, "competition": N, "seo": N, "feasibility": N, "monetization": N}},
  "overall": N,
  "verdict": "BUILD/SKIP/CONSIDER",
  "one_liner": "1-sentence summary"
}}
Wrap in ```json block.
"""
        result = self._call_llm(prompt)
        try:
            json_str = self.llm.extract_code_block(result)
            data = json.loads(json_str) if json_str else {}
        except (json.JSONDecodeError, TypeError):
            data = {}
        return {"analysis": data, "raw": result, "success": bool(data)}


class GameDevSkill(BaseSkill):
    """游戏开发专家 — 生成 HTML5 Canvas 小游戏（为 Arcade 预留）"""

    def __init__(self):
        super().__init__()
        self.name = "game_dev"
        self.description = "Generate HTML5 Canvas mini-games"

    def get_system_prompt(self) -> str:
        return """You are an HTML5 game developer specializing in browser mini-games.
You use pure Canvas API (no frameworks).
You excel at: game loops, collision detection, keyboard/touch input,
score tracking, particle effects, and responsive canvas sizing."""

    def execute(self, context: dict) -> dict:
        game_type = context.get("game_type", "2048")
        prompt = f"""{self.get_system_prompt()}

Create a complete, single-file HTML5 game: {game_type}

Requirements:
1. Pure HTML + CSS + JavaScript in one file
2. Use Canvas API for rendering
3. Responsive (works on mobile and desktop)
4. Score tracking with localStorage high score
5. Clean, polished visual design
6. Under 300 lines

Wrap in ```html block.
"""
        result = self._call_llm(prompt)
        code = self.llm.extract_code_block(result)
        return {"game_code": code or "", "raw": result, "success": bool(code)}


# ═══════════════════════════════════════════════════
# 技能注册中心
# ═══════════════════════════════════════════════════

class AgentSkillRegistry:
    """技能注册中心 — 管理所有可用技能"""

    def __init__(self):
        self._skills: dict[str, BaseSkill] = {}
        self._register_defaults()

    def _register_defaults(self):
        """注册所有默认技能"""
        defaults = [
            CodeGenSkill(),
            UIDesignSkill(),
            SEOSkill(),
            DebuggingSkill(),
            ResearchSkill(),
            GameDevSkill(),
        ]
        for skill in defaults:
            self.register(skill)

    def register(self, skill: BaseSkill):
        """注册一个新技能"""
        self._skills[skill.name] = skill
        log.info(f"🔧 技能已注册: {skill.name} v{skill.version}")

    def get(self, name: str) -> BaseSkill | None:
        """获取一个技能"""
        return self._skills.get(name)

    def execute(self, skill_name: str, context: dict) -> dict:
        """执行一个技能"""
        skill = self.get(skill_name)
        if not skill:
            log.error(f"技能不存在: {skill_name}")
            return {"error": f"Skill '{skill_name}' not found", "success": False}

        log.info(f"🎯 执行技能: {skill.name} — {skill.description}")
        try:
            result = skill.execute(context)
            log.info(f"  {'✅' if result.get('success') else '❌'} 技能 {skill.name} 执行{'成功' if result.get('success') else '失败'}")
            return result
        except Exception as e:
            log.error(f"  ❌ 技能 {skill.name} 异常: {e}")
            return {"error": str(e), "success": False}

    def compose(self, skill_names: list[str], context: dict) -> list[dict]:
        """组合执行多个技能（串行），每个技能的输出注入到下一个技能的上下文"""
        results = []
        ctx = dict(context)
        for name in skill_names:
            result = self.execute(name, ctx)
            results.append({"skill": name, **result})
            # 将结果注入到下一个技能的上下文
            ctx.update(result)
        return results

    def list_skills(self) -> list[dict]:
        """列出所有可用技能"""
        return [
            {"name": s.name, "description": s.description, "version": s.version}
            for s in self._skills.values()
        ]

    def get_all_stats(self) -> list[dict]:
        """获取所有技能的调用统计"""
        return [s.get_stats() for s in self._skills.values()]


# 全局单例
_registry = None

def get_registry() -> AgentSkillRegistry:
    """获取全局技能注册中心单例"""
    global _registry
    if _registry is None:
        _registry = AgentSkillRegistry()
    return _registry


# ═══════════════════════════════════════════════════
# 自测
# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    print("🔧 Agent Skills Framework 自测\n")

    registry = get_registry()

    # 列出所有技能
    print("📋 可用技能:")
    for s in registry.list_skills():
        print(f"  🔧 {s['name']} v{s['version']} — {s['description']}")

    # 测试技能组合 (不实际调 LLM，只测试框架)
    print(f"\n📊 技能统计:")
    for stat in registry.get_all_stats():
        print(f"  {stat['name']}: {stat['calls']} calls, {stat['success_rate']} success")

    # 测试无效技能
    result = registry.execute("nonexistent", {})
    assert result.get("success") == False
    print(f"\n  无效技能测试: ✅ (正确返回错误)")

    print("\n✅ Agent Skills Framework 自测通过")
