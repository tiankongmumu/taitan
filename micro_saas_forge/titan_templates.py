"""
TITAN Template System v1.0
学习自成功构建案例 (LapSync Stopwatch)
为LLM提供参考代码片段，提高首次编译成功率
"""

# ─── 成功的 page.tsx 结构模板 ───
PAGE_TEMPLATE = '''
"use client";

import {{ useState, useEffect, useRef, useCallback }} from "react";

/* ───────── types ───────── */
interface ItemType {{
  id: number;
  // TODO: add fields
}}

/* ───────── helpers ───────── */
function formatValue(val: number): string {{
  return val.toString();
}}

/* ═══════════════════════════════════════════
   {app_name} — {app_description}
   ═══════════════════════════════════════════ */
export default function Home() {{
  // ── state ──
  const [items, setItems] = useState<ItemType[]>([]);
  const [isActive, setIsActive] = useState(false);

  // ── handlers ──
  const handleAction = useCallback(() => {{
    // TODO: core logic
  }}, []);

  // ── keyboard shortcuts ──
  useEffect(() => {{
    const onKey = (e: KeyboardEvent) => {{
      if (e.code === "Space") {{ e.preventDefault(); handleAction(); }}
    }};
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }}, [handleAction]);

  return (
    <main className="min-h-screen bg-[#0a0a0a] text-white flex flex-col items-center justify-center p-4">
      {{/* Header */}}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
          {{/* App Title */}}
        </h1>
        <p className="text-gray-400 mt-2">{{/* Description */}}</p>
      </div>

      {{/* Main Content Area */}}
      <div className="w-full max-w-2xl bg-white/[0.03] backdrop-blur-xl rounded-2xl border border-white/10 p-8">
        {{/* Core UI */}}
      </div>

      {{/* Action Buttons */}}
      <div className="flex gap-4 mt-6">
        <button
          onClick={{handleAction}}
          className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-xl font-bold hover:shadow-[0_0_20px_rgba(6,182,212,0.4)] transition-all"
        >
          Start
        </button>
      </div>

      {{/* Footer */}}
      <footer className="mt-12 text-gray-600 text-sm">
        Built with ❤️
      </footer>
    </main>
  );
}}
'''

# ─── layout.tsx 模板 ───
LAYOUT_TEMPLATE = '''
import type {{ Metadata }} from "next";
import {{ Geist, Geist_Mono }} from "next/font/google";
import "./globals.css";

const geistSans = Geist({{
  variable: "--font-geist-sans",
  subsets: ["latin"],
}});

const geistMono = Geist_Mono({{
  variable: "--font-geist-mono",
  subsets: ["latin"],
}});

export const metadata: Metadata = {{
  title: "{app_name} — {seo_title}",
  description: "{seo_description}",
}};

export default function RootLayout({{
  children,
}}: Readonly<{{
  children: React.ReactNode;
}}>) {{
  return (
    <html lang="en">
      <body className={{`${{geistSans.variable}} ${{geistMono.variable}} antialiased`}}>
        {{children}}
      </body>
    </html>
  );
}}
'''

# ─── 常见构建错误和修复 ───
KNOWN_FIXES = {
    "missing_use_client": {
        "error_pattern": "useState is not defined",
        "fix": 'Add "use client"; at the very first line of page.tsx',
    },
    "api_route_as_page": {
        "error_pattern": "Cannot use export",
        "fix": "API route should be in app/api/ folder, not in page.tsx",
    },
    "missing_type_import": {
        "error_pattern": "Cannot find name",
        "fix": "Add proper TypeScript type imports at the top",
    },
    "tailwind_syntax": {
        "error_pattern": "bg-[",
        "fix": "Use proper Tailwind class syntax: bg-[#0a0a0a]",
    },
}


def get_page_reference(app_name: str = "", app_desc: str = "") -> str:
    """生成参考代码片段注入到LLM prompt"""
    template = PAGE_TEMPLATE.replace("{app_name}", app_name).replace("{app_description}", app_desc)
    return f"""
=== REFERENCE TEMPLATE (proven to compile successfully) ===
Use this structure as your starting point. The following template has been tested and compiles without errors:

{template}

=== CRITICAL RULES (from successful builds) ===
1. FIRST LINE must be: "use client";
2. Import hooks: {{ useState, useEffect, useRef, useCallback }}
3. Define TypeScript interfaces BEFORE the component
4. Use `export default function Home()` (NOT arrow function)
5. Tailwind classes: bg-[#0a0a0a], text-white, rounded-2xl
6. Keyboard events need cleanup: return () => window.removeEventListener(...)
"""


def get_known_fixes() -> str:
    """获取常见错误修复提示"""
    fixes = "\n=== KNOWN BUILD ERRORS TO AVOID ===\n"
    for name, info in KNOWN_FIXES.items():
        fixes += f"- {name}: {info['fix']}\n"
    return fixes
