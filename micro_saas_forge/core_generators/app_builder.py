"""
Micro-SaaS Forge — 应用生成器 (v3.0 — Skill-Enhanced)
支持：LLM 代码生成、Gumroad 注入、node_modules 排除、自愈编译引擎。
v3.0: 接入 titan_skill_system (学自 claude-skills) — 自动注入 MUST DO/MUST NOT 规则
"""
import os
import shutil
import json
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEMPLATES_DIR, GENERATED_APPS_DIR, GUMROAD_PRODUCT_ID, SELF_HEAL_MAX_ATTEMPTS
from logger import get_logger
from core_generators.llm_client import LLMClient
import memory_bank as mem
import skill_learner as skills
from titan_skill_system import SkillRegistry
from titan_templates import get_page_reference, get_known_fixes

log = get_logger("builder")

# 复制模板时需要排除的目录
COPY_IGNORE = shutil.ignore_patterns("node_modules", ".next", ".git", "__pycache__")


class AppBuilder:
    def __init__(self):
        self.base_template_dir = TEMPLATES_DIR
        self.output_dir = GENERATED_APPS_DIR
        self.llm = LLMClient()
        self.skill_registry = SkillRegistry()  # v3.0: 技能系统 (学自 claude-skills)

    # ──────────── Step 1: Idea → Spec ────────────
    def transform_idea(self, raw_idea: str) -> dict:
        """将原始点子转换为标准化的工程规格。"""
        log.info("将点子转换为工程规格...")
        prompt = f"""
Convert this raw idea into a strict JSON spec for a Next.js Micro-SaaS app.
Raw Idea: {raw_idea}

The JSON MUST have exactly these keys:
- "name": Application Name (e.g. "Auto Interface Tool")
- "slug": URL slug (e.g. "auto-interface-tool")
- "pain_point": Short description of what problem it solves
- "core_features": Array of 3-4 feature strings
- "tech_stack": ["Next.js", "TailwindCSS"]
- "gumroad_product_id": "{GUMROAD_PRODUCT_ID}"
"""
        result = self.llm.generate(prompt, is_json=True)
        try:
            spec = json.loads(result)
            # 确保 gumroad_product_id 始终使用配置值
            spec["gumroad_product_id"] = GUMROAD_PRODUCT_ID
            return spec
        except Exception as e:
            log.error(f"JSON 解析失败: {e}")
            return {
                "name": "Fallback Tool",
                "slug": "fallback-tool",
                "pain_point": raw_idea,
                "core_features": ["Core Feature 1", "Core Feature 2"],
                "tech_stack": ["Next.js", "TailwindCSS"],
                "gumroad_product_id": GUMROAD_PRODUCT_ID,
            }

    # ──────────── Step 2: Spec → Code ────────────
    def generate_and_inject(self, app_spec: dict) -> str:
        """生成代码、注入支付组件、执行自愈编译。"""
        os.makedirs(self.output_dir, exist_ok=True)
        app_path = os.path.join(self.output_dir, app_spec["slug"])

        # 1. 复制模板（排除 node_modules）
        if os.path.exists(self.base_template_dir):
            if os.path.exists(app_path):
                shutil.rmtree(app_path, ignore_errors=True)
            shutil.copytree(self.base_template_dir, app_path, ignore=COPY_IGNORE, dirs_exist_ok=True)
            log.info(f"模板复制完成（已排除 node_modules）")
        else:
            log.warning(f"模板目录不存在: {self.base_template_dir}，创建空结构")
            os.makedirs(os.path.join(app_path, "src", "app"), exist_ok=True)

        # 2. LLM 生成 page.tsx
        log.info("生成 page.tsx...")
        
        # 💰 获取匹配的联盟营销组件
        from titan_affiliate_injector import TitanAffiliateInjector
        try:
            injector = TitanAffiliateInjector()
            affiliate_jsx = injector.get_affiliate_widget(app_spec.get("name", ""), app_spec.get("pain_point", ""))
        except Exception as e:
            log.warning(f"  ⚠️ 联盟营销组件获取失败: {e}")
            affiliate_jsx = "{/* Ads disabled fallback */}"
            
        shipmicro_badge = '<a href="https://shipmicro.com" target="_blank" style="position:fixed;bottom:16px;right:16px;padding:6px 12px;background:#111;color:#888;border-radius:20px;font-size:12px;text-decoration:none;border:1px solid #333;z-index:999">🚢 ShipMicro</a>'

        # 🧠 Memory Recall: 查找类似的成功模板
        memory_context = ""
        similar_templates = mem.recall_template(app_spec.get("idea", "") + " " + app_spec.get("name", ""))
        if similar_templates:
            memory_context = "\n\n## Reference Code from Similar Successful Tools:\n"
            for t in similar_templates[:2]:
                memory_context += f"\n### {t.get('app_slug', 'tool')} (score: {t.get('quality_score', '?')}):\n```tsx\n{t['code_snippet'][:400]}\n```\n"
            log.info(f"🧠 注入 {len(similar_templates)} 个成功模板记忆到 prompt")

        # 🎯 Category-Specific Skill Injection (OpenClaw pattern)
        category = app_spec.get("category", "Code")
        category_skill = self._get_category_skill(category)
        
        # 🧠 Failure Memory: recall past failures for this category
        failure_context = ""
        try:
            failures = mem.recall_failures(category)
            if failures:
                failure_context = "\n\n## ⚠️ AVOID THESE KNOWN FAILURE PATTERNS:\n"
                for f in failures[:2]:
                    failure_context += f"- {f.get('reason', 'Unknown failure')}\n"
                log.info(f"🧠 注入 {len(failures)} 个失败记忆警告")
        except Exception:
            pass  # memory_bank may not have recall_failures yet

        # 🎓 Scholar Pattern Injection v3.5: 多域智能注入 (lobehub Prompt 分层 + Dify 循环节点)
        scholar_context = ""
        try:
            # 根据 category 智能匹配注入域
            domain_map = {
                "Game": "GameEngine", "Tap": "GameEngine", "Dodge": "GameEngine",
                "Memory": "GameEngine", "Classic": "GameEngine", "Arcade": "GameEngine",
                "Code": "Pipeline", "Data": "Pipeline", "API": "Backend",
                "DevOps": "Backend", "Security": "Backend",
                "Design": "Frontend", "AI": "Agent", "Productivity": "Frontend",
            }
            primary_domain = domain_map.get(category, "General")
            
            # 跨域融合: 主域 1 + 辅助域 1
            patterns = mem.recall_pattern(primary_domain, top_k=1)
            aux_patterns = mem.recall_pattern("Pipeline", top_k=1) if primary_domain != "Pipeline" else mem.recall_pattern("Agent", top_k=1)
            all_patterns = (patterns or []) + (aux_patterns or [])
            
            if all_patterns:
                scholar_context = "\n\n=== 👑 ADVANCED ARCHITECTURAL PATTERNS (Learned from GitHub Top 100) ===\n"
                for p in all_patterns:
                    scholar_context += f"Pattern [{p.get('category', '?')}] from {p.get('source_repo', 'Unknown')}:\n"
                    scholar_context += f"RULE: {p.get('prompt_fragment', '')}\n\n"
                log.info(f"🎓 注入 {len(all_patterns)} 个跨域高级模式 (主域: {primary_domain})")
        except Exception as e:
            log.warning(f"  ⚠️ 学术模式加载失败: {e}")

        # === v5.0 Prompt 分层架构 (lobehub-inspired + claude-skills enhanced) ===
        identity_layer = """You are TITAN ENGINE v5.0 — an AI code architect with 66 specialized skills and 127 design patterns from the world's top open-source projects."""
        
        context_layer = f"""App Spec:
{json.dumps(app_spec, indent=2)}
{memory_context}
{failure_context}

{get_page_reference(app_spec.get('name', ''), app_spec.get('pain_point', ''))}
{get_known_fixes()}"""

        # 🧠 v3.0: 技能系统自动激活 (学自 claude-skills 的 context-aware activation)
        app_desc = f"{app_spec.get('name', '')} {app_spec.get('pain_point', '')} Next.js React TypeScript"
        skill_matches = self.skill_registry.match_skills(app_desc, top_n=2)
        skill_constraints = ""
        if skill_matches:
            activated_names = [n for n, _, _ in skill_matches]
            log.info(f"🧠 技能自动激活: {', '.join(activated_names)}")
            for name, skill, score in skill_matches:
                skill_constraints += self.skill_registry.get_skill_prompt(name) + "\n\n"

        skill_layer = f"""
=== CATEGORY-SPECIFIC SKILL ===
{category_skill}
{scholar_context}

=== ACTIVATED EXPERT SKILLS (auto-matched) ===
{skill_constraints}"""

        constraint_layer = f"""=== AESTHETICS ===
1. DARK MODE: Use `bg-[#0a0a0a]`, `text-white`.
2. GLASSMORPHISM: `backdrop-blur-xl`, `bg-white/5`, `border border-white/10`, `rounded-2xl`.
3. MICRO-ANIMATIONS: hover glows, scale, transitions.

=== LAYOUT & COMPONENTS ===
4. STRUCTURE: `export default function Home() {{ ... }}`.
5. VISUAL HIERARCHY: title (text-3xl font-bold) → description (text-gray-400) → content → footer.
6. INPUT DESIGN: `bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder:text-gray-600 focus:ring-2 focus:ring-cyan-500/40`.
7. BUTTON DESIGN: `bg-gradient-to-r from-cyan-500 to-blue-500 hover:shadow-[0_0_20px_rgba(6,182,212,0.4)] text-white font-bold py-3 px-6 rounded-xl`.
8. RESULT DISPLAY: `bg-white/[0.03] rounded-xl p-6 border border-white/10 font-mono text-sm`.
9. RESPONSIVE: `max-w-2xl mx-auto px-4`.

=== FUNCTIONALITY ===
10. FUNCTIONAL COMPLETENESS: The tool MUST actually work end-to-end.
11. ERROR HANDLING: Graceful handling, inline error messages with `text-red-400 text-sm mt-2`.
12. NO PAYWALLS: This is a FREE tool.

=== MONETIZATION (CRITICAL DO NOT SKIP) ===
Insert this EXACT JSX block near the bottom of your UI, just above the main container's closing tag. Do not modify its structure.
{affiliate_jsx}

=== TECHNICAL ===
13. Add "use client"; at the top if using React hooks.
14. Do NOT import external libraries. Use inline SVGs or emoji.
15. KEEP UNDER 450 LINES but ensure core logic is fully functional.
16. Add this JSX at the bottom:
   <div dangerouslySetInnerHTML={{{{ __html: `{shipmicro_badge}` }}}} />
17. Wrap your entire code in a ```tsx block."""

        page_prompt = f"""{identity_layer}

Write a complete, single-file Next.js React component (page.tsx).

{context_layer}

{skill_layer}

{constraint_layer}
"""
        page_code = self.llm.extract_code_block(self.llm.generate(page_prompt))
        if not page_code:
            log.error("page.tsx 生成失败")
            return ""
        
        # 🛡️ v5.1: Truncation Detection — 检测 LLM 截断并尝试修复
        page_code = self._detect_and_repair_truncation(page_code, app_spec)
        
        self._write_file(app_path, "src/app/page.tsx", page_code)

        # 3. LLM 生成 API route
        log.info("生成 API route...")
        api_prompt = f"""
Write a Next.js App Router API route (app/api/generate/route.ts) for:
{json.dumps(app_spec, indent=2)}

Requirements:
1. Export an `async function POST(req: Request)`.
2. Return a mocked JSON response simulating the core functionality.
3. Wrap your code in a ```ts block.
"""
        api_code = self.llm.extract_code_block(self.llm.generate(api_prompt))
        if not api_code:
            log.warning("API route 生成失败，使用兜底")
            api_code = (
                "import { NextResponse } from 'next/server';\n"
                "export async function POST() { return NextResponse.json({ success: true }); }"
            )
        api_dir = os.path.join(app_path, "src", "app", "api", "generate")
        os.makedirs(api_dir, exist_ok=True)
        self._write_file(app_path, "src/app/api/generate/route.ts", api_code)

        # 4. 注入 SEO 元数据到 layout.tsx
        self._inject_seo_metadata(app_path, app_spec)

        # 5. 自愈编译引擎
        build_success = self._self_heal_build(app_path)
        if build_success:
            # 🧠 Memory Store: 存储成功编译的模板
            try:
                final_page = os.path.join(app_path, "src", "app", "page.tsx")
                if os.path.exists(final_page):
                    with open(final_page, "r", encoding="utf-8") as f:
                        final_code = f.read()
                    mem.remember_success(
                        app_desc=app_spec.get("idea", "") + " " + app_spec.get("name", ""),
                        page_code=final_code,
                        app_slug=app_spec.get("slug", ""),
                    )
            except Exception as e:
                log.warning(f"记忆存储失败: {e}")
        else:
            log.warning("自愈编译最终失败，但代码已生成，可手动修复")

        return app_path

    # ──────────── 自愈编译引擎 ────────────
    def _self_heal_build(self, app_path: str) -> bool:
        """尝试编译，失败则让 LLM 修复，最多循环 N 次。"""
        # 首先安装依赖
        if not os.path.exists(os.path.join(app_path, "node_modules")):
            log.info("安装 npm 依赖...")
            try:
                subprocess.run(
                    ["npm", "install"], cwd=app_path,
                    capture_output=True, text=True, check=True, timeout=120, shell=True
                )
            except Exception as e:
                log.warning(f"npm install 失败: {e}，跳过编译验证")
                return False

        for attempt in range(1, SELF_HEAL_MAX_ATTEMPTS + 1):
            log.info(f"🔨 编译验证 (尝试 {attempt}/{SELF_HEAL_MAX_ATTEMPTS})...")
            try:
                result = subprocess.run(
                    ["npm", "run", "build"], cwd=app_path,
                    capture_output=True, text=True, timeout=180, shell=True
                )
                if result.returncode == 0:
                    log.info("✅ 编译成功！代码质量验证通过")
                    return True

                # 编译失败，提取错误
                error_output = result.stderr[-2000:] if result.stderr else result.stdout[-2000:]
                log.warning(f"编译失败 (尝试 {attempt}): {error_output[:200]}...")

                if attempt >= SELF_HEAL_MAX_ATTEMPTS:
                    break

                # 让 LLM 修复（注入 Memory Bank 历史修复经验）
                log.info("🩹 启动自愈引擎...")
                page_path = os.path.join(app_path, "src", "app", "page.tsx")
                with open(page_path, "r", encoding="utf-8") as f:
                    current_code = f.read()

                # 🧠 Memory Recall: 查找类似错误的历史修复经验
                past_fixes = mem.recall_fix(error_output)
                memory_hint = ""
                if past_fixes:
                    memory_hint = "\n\n## Past fixes for similar errors (from Memory Bank):\n"
                    for pf in past_fixes:
                        memory_hint += f"\nError was: {pf['error_snippet'][:150]}\nFix applied:\n```tsx\n{pf['fixed_code_snippet'][:300]}\n```\n"
                    log.info(f"🧠 注入 {len(past_fixes)} 条历史修复经验到自愈 prompt")

                # 🧬 Auto-Learn: 检测技能缺口并自动学习
                skill_hint = ""
                try:
                    learned = skills.auto_learn_from_error(error_output, app_slug=os.path.basename(app_path))
                    if learned:
                        skill_hint = skills.get_relevant_skills("", error_output=error_output)
                except Exception as e:
                    log.warning(f"自动学习引擎异常: {e}")

                fix_prompt = f"""
The following Next.js page.tsx has a build error. Fix it.

Current code:
```tsx
{current_code}
```

Build error:
```
{error_output}
```
{memory_hint}
{skill_hint}
Requirements:
1. Return the COMPLETE fixed file, not just the changed parts.
2. KEEP UNDER 300 LINES. Maintain the dark mode, glassmorphism, and animations.
3. Wrap your code in a ```tsx block.
"""
                fixed_code = self.llm.extract_code_block(self.llm.generate(fix_prompt))
                if fixed_code:
                    # 🧠 Memory Store: 记住这次修复经验
                    mem.remember_fix(
                        error_output=error_output,
                        old_code=current_code[:300],
                        fixed_code=fixed_code[:500],
                        app_slug=os.path.basename(app_path)
                    )
                    self._write_file(app_path, "src/app/page.tsx", fixed_code)
                    log.info("自愈补丁已应用（已存入记忆库），重新编译...")
                else:
                    log.error("自愈引擎未能生成修复代码")
                    break

            except subprocess.TimeoutExpired:
                log.warning(f"编译超时 (尝试 {attempt})")
                break
            except Exception as e:
                log.error(f"编译异常: {e}")
                break

        return False

    # ──────────── SEO 元数据注入 ────────────
    def _inject_seo_metadata(self, app_path: str, app_spec: dict):
        """在 layout.tsx 中注入 title 和 meta description。"""
        layout_path = os.path.join(app_path, "src", "app", "layout.tsx")
        if not os.path.exists(layout_path):
            return

        try:
            with open(layout_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 替换默认的 metadata
            if "Create Next App" in content:
                content = content.replace(
                    'title: "Create Next App"',
                    f'title: "{app_spec["name"]} - {app_spec["pain_point"]}"',
                )
                content = content.replace(
                    'description: "Generated by create next app"',
                    f'description: "The easiest way to solve {app_spec["pain_point"]}. Try {app_spec["name"]} now."',
                )
                with open(layout_path, "w", encoding="utf-8") as f:
                    f.write(content)
                log.info("SEO 元数据已注入 layout.tsx")
        except Exception as e:
            log.warning(f"SEO 元数据注入失败: {e}")

    # ──────────── Category Skill Fragments (TITAN v2.0) ────────────
    GAME_CATEGORIES = {"Game", "Tap", "Dodge", "Memory", "Pattern", "Math", "Typing", "Reaction", "Classic", "Arcade"}
    CODE_CATEGORIES = {"Code", "Data", "API", "DevOps", "Security", "Web3"}
    DESIGN_CATEGORIES = {"Design", "AI", "Productivity"}

    def _get_category_skill(self, category: str) -> str:
        """Return category-specific prompt fragment (OpenClaw-inspired Skill Injection)."""
        if category in self.GAME_CATEGORIES:
            return """GAME-SPECIFIC REQUIREMENTS:
- Use HTML5 Canvas via useRef + useEffect for rendering. Set canvas size with `width={400} height={400}`.
- Implement a proper game loop using requestAnimationFrame.
- Add a SCORE display (top-right, fixed, `text-2xl font-bold text-cyan-400`).
- Add START/RESTART button that resets game state.
- Use keyboard listeners (onKeyDown) or touch events for mobile.
- Add simple sound feedback using Web Audio API oscillator on key events.
- Game MUST be playable immediately — no loading screens or setup."""

        if category in self.CODE_CATEGORIES:
            return """DEV TOOL-SPECIFIC REQUIREMENTS:
- Follow INPUT → PROCESS → OUTPUT pattern:
  * LEFT/TOP: textarea or input for user data
  * RIGHT/BOTTOM: formatted output/result
- Add a "Copy to Clipboard" button on the output with `navigator.clipboard.writeText()`.
- For code-related tools, use `font-mono` and syntax-style coloring.
- Add a "Clear" button to reset both input and output.
- Show processing status with a subtle spinner or "Processing..." text.
- Handle large inputs gracefully (truncate display if > 10000 chars)."""

        if category in self.DESIGN_CATEGORIES:
            return """DESIGN/VISUAL TOOL-SPECIFIC REQUIREMENTS:
- Use Canvas API (via useRef) for any drawing/visual manipulation.
- Add color picker input: `<input type="color" />` styled to match dark theme.
- Include EXPORT functionality (download as PNG via `canvas.toDataURL()`).
- Add UNDO capability using a state history array.
- For AI tools, show a "thinking" animation while processing.
- Make the canvas/workspace take at least 60% of viewport height."""

        return """GENERAL TOOL REQUIREMENTS:
- Implement the core functionality completely — no placeholders.
- Add a clear call-to-action that explains what the tool does.
- Show example input/output to guide the user."""

    # ──────────── v5.1: Truncation Detection & Repair ────────────
    def _detect_and_repair_truncation(self, code: str, app_spec: dict) -> str:
        """Detect if LLM output was truncated and attempt auto-repair."""
        if not code or len(code) < 50:
            return code
        
        # Heuristic 1: Unbalanced curly braces
        open_braces = code.count('{') - code.count('}')
        # Heuristic 2: Missing export default closure
        has_export = 'export default function' in code
        lines = code.strip().split('\n')
        last_line = lines[-1].strip() if lines else ''
        ends_with_closure = last_line in ('}', '};', ');', '</main>', 'export default')
        # Heuristic 3: Unterminated JSX (opening tag without closing)
        unterminated_jsx = last_line.startswith('<') and not last_line.endswith('>')
        
        is_truncated = (open_braces > 2) or (has_export and not ends_with_closure) or unterminated_jsx
        
        if not is_truncated:
            return code
        
        log.warning(f"🚨 截断检测: 未闭合大括号={open_braces}, 缺少闭合={not ends_with_closure}, JSX未终止={unterminated_jsx}")
        log.info("🩹 尝试 LLM 自动修复截断...")
        
        # Take last 60 lines as context for repair
        tail = '\n'.join(lines[-60:])
        repair_prompt = f"""The following TSX code was truncated mid-generation. Complete ONLY the remaining closing code.
Do NOT rewrite the entire component. Just provide the missing closing JSX tags, braces, and the final `}}` to properly close the `export default function`.

The app is: {app_spec.get('name', 'Unknown')} — {app_spec.get('pain_point', '')}

TRUNCATED TAIL (last 60 lines):
```tsx
{tail}
```

Rules:
1. Output ONLY the missing completion code (closing tags, braces).
2. Wrap in a ```tsx block.
3. Keep it minimal — just close what's open."""
        
        try:
            repair_code = self.llm.extract_code_block(self.llm.generate(repair_prompt))
            if repair_code and len(repair_code) > 5:
                repaired = code.rstrip() + '\n' + repair_code
                # Verify repair improved brace balance
                new_balance = repaired.count('{') - repaired.count('}')
                if abs(new_balance) < abs(open_braces):
                    log.info(f"✅ 截断修复成功: 大括号差 {open_braces} → {new_balance}")
                    return repaired
                else:
                    log.warning(f"⚠️ LLM修复未改善平衡 ({new_balance})，尝试机械修复")
        except Exception as e:
            log.warning(f"LLM修复失败: {e}")
        
        # Fallback: mechanical closure
        closure = ""
        for _ in range(max(0, open_braces)):
            closure += "\n}"
        if closure:
            log.info(f"🔧 机械修复: 添加 {open_braces} 个闭合大括号")
            return code.rstrip() + closure + "\n"
        
        return code

    def _get_shipmicro_badge(self) -> str:
        return '<a href="https://shipmicro.com" target="_blank" style="position:fixed;bottom:16px;right:16px;">🚢 ShipMicro</a>'

    def _write_file(self, base: str, rel_path: str, content: str):
        full = os.path.join(base, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        log.debug(f"写入: {rel_path} ({len(content)} 字符)")

    def generate_fallback_page(self, app_spec: dict) -> str:
        """降级模式：生成静态 HTML 落地页。"""
        fallback_dir = os.path.join(self.output_dir, f"{app_spec['slug']}_fallback")
        os.makedirs(fallback_dir, exist_ok=True)
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{app_spec['name']} - Coming Soon</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; color: white; }}
        .card {{ background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius: 20px; padding: 3rem; max-width: 500px; text-align: center; }}
        h1 {{ font-size: 2rem; margin-bottom: 1rem; }}
        p {{ opacity: 0.9; margin-bottom: 1.5rem; }}
        input {{ padding: 12px 20px; border: none; border-radius: 10px; width: 100%; margin-bottom: 1rem; font-size: 1rem; }}
        button {{ padding: 12px 30px; background: white; color: #764ba2; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; font-size: 1rem; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>{app_spec['name']}</h1>
        <p>{app_spec['pain_point']}</p>
        <p>We're launching soon. Join the waitlist!</p>
        <input type="email" placeholder="Enter your email" required />
        <button type="submit">Join Waitlist</button>
    </div>
</body>
</html>"""
        path = os.path.join(fallback_dir, "index.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        return path
