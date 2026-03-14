import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from logger import get_logger

log = get_logger("codemint_mounter")

def convert_to_nextjs(html_path, js_path, output_path):
    if not os.path.exists(html_path) or not os.path.exists(js_path):
        log.error(f"Missing files for {html_path}")
        return
        
    with open(html_path, "r", encoding="utf-8") as f:
        html_code = f.read()
    with open(js_path, "r", encoding="utf-8") as f:
        js_code = f.read()
        
    prompt = f"""You are an expert Next.js and React developer.
I have a vanilla HTML/JS application that I want to convert into a single-file Next.js React component for a Next.js 14+ App Router project.

HTML:
```html
{html_code}
```

JS:
```javascript
{js_code}
```

Please combine the logic into a single React functional component `export default function ToolPage() {{ ... }}`.
Requirements:
1. Use `"use client";` at the very top.
2. Use React hooks (`useState`, `useEffect`, `useRef`) instead of direct DOM manipulation (`document.getElementById`).
3. Retain the exact same Tailwind CSS styling. Convert `class=` to `className=`.
4. The component should look and function precisely like the original vanilla app.
5. Provide ONLY the final TypeScript/React code wrapped in a ```tsx code block. No extra text or explanations. Do not omit any logic.
6. Make sure to export it as the default export.
"""
    log.info(f"Generating Next.js code for {output_path}...")
    llm = LLMClient()
    response = llm.generate(prompt)
    code = llm.extract_code_block(response)
    
    if code:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(code)
        log.info(f"✅ Successfully wrote to {output_path}")
    else:
        log.error("❌ Failed to extract code from LLM response.")

if __name__ == "__main__":
    # Mount idphoto
    convert_to_nextjs(
        r"d:\Project\1\codemint_tools\codemint_idphoto\frontend\index.html",
        r"d:\Project\1\codemint_tools\codemint_idphoto\frontend\app.js",
        r"d:\Project\1\micro_saas_forge\shipmicro_site\src\app\tools\idphoto\page.tsx"
    )
    
    # Mount hs-tariff
    convert_to_nextjs(
        r"d:\Project\1\codemint_tools\codemint_hs_tariff\frontend\index.html",
        r"d:\Project\1\codemint_tools\codemint_hs_tariff\frontend\app.js",
        r"d:\Project\1\micro_saas_forge\shipmicro_site\src\app\tools\hs-tariff\page.tsx"
    )
