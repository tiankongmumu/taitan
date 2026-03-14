import os
import sys
import json
import zipfile
import shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from logger import get_logger

log = get_logger("titan_packager")

class TitanSourcePackager:
    """
    Automatically packages generated applications into ZIP files and 
    generates sales copy (for Xianyu/Gumroad) to sell the source code.
    """
    
    def __init__(self):
        self.llm = LLMClient()
        self.output_dir = os.path.join(os.path.dirname(__file__), "ready_for_sale")
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _create_zip(self, source_dir: str, app_name: str) -> str | None:
        """Create a clean ZIP of the source code, excluding build artifacts"""
        zip_filename = f"{app_name.replace(' ', '_').lower()}_source_code.zip"
        zip_path = os.path.join(self.output_dir, zip_filename)
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    # Exclude node_modules and .next directories
                    dirs[:] = [d for d in dirs if d not in ['node_modules', '.next', '.git']]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Avoid zipping the zip itself if placed inside
                        if not file.endswith('.zip'):
                            arcname = os.path.relpath(file_path, source_dir)
                            zipf.write(file_path, arcname)
            return zip_path
        except Exception as e:
            log.error(f"Failed to ZIP {source_dir}: {e}")
            return None

    def _generate_sales_copy(self, app_name: str, app_description: str) -> dict:
        """Generate high-converting Xianyu/Gumroad sales copy"""
        prompt = f"""You are a top-tier copywriter selling software source code on platforms like Xianyu (闲鱼) or Gumroad.
We are selling the complete, ready-to-deploy source code for an app called '{app_name}'.
Features: {app_description}

Write a highly converting, professional yet accessible sales listing in Chinese.
It MUST include:
1. An eye-catching title (Xianyu style, no banned words, highlight "Source Code", "Next.js", "Ready to deploy").
2. A compelling description stating the value (perfect for graduation projects, commercial use, or learning modern web dev).
3. A breakdown of the tech stack (Next.js, TailwindCSS, Dark Mode UI).
4. A suggested price point (e.g. 50-300 RMB)

Return ONLY valid JSON format:
{{
    "title": "...",
    "body": "...",
    "suggested_price": "99"
}}
"""
        try:
            import re
            result = self.llm.generate(prompt, is_json=True)
            match = re.search(r'\{.*\}', result.strip(), re.DOTALL)
            if match:
                result = match.group(0)
            return json.loads(result)
        except Exception as e:
            log.warning(f"Failed to generate sales copy: {e}")
            return {
                "title": f"【现成源码】{app_name} 完整前端代码 Next.js",
                "body": f"全新手写 {app_name} 工具源码。\n技术栈：Next.js + TailwindCSS。\n完美支持暗黑模式，适合毕设或商业二开。\n拍下自动发网盘链接。",
                "suggested_price": "99"
            }

    def package_for_sale(self, app_name: str, source_dir: str, app_description: str) -> dict:
        """Main method to execute the packaging pipeline"""
        log.info(f"📦 Packaging {app_name} for source code sale...")
        
        # 1. Zip the code
        zip_path = self._create_zip(source_dir, app_name)
        if not zip_path:
            return {"success": False, "error": "Zip creation failed"}
            
        log.info(f"   ✅ Zipped code to {zip_path}")
        
        # 2. Generate copy
        copy_data = self._generate_sales_copy(app_name, app_description)
        log.info(f"   ✅ Generated Xianyu sales copy")
        
        # 3. Save listing info
        listing_info = {
            "app_name": app_name,
            "packaged_at": datetime.now().isoformat(),
            "zip_path": zip_path,
            "sales_copy": copy_data
        }
        
        info_path = os.path.join(self.output_dir, f"{app_name.replace(' ', '_').lower()}_listing.json")
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(listing_info, f, ensure_ascii=False, indent=2)
            
        log.info(f"   ✅ Saved listing package info ready for manual/RPA upload")
        
        return {
            "success": True,
            "zip_path": zip_path,
            "listing_info": info_path,
            "price": copy_data.get("suggested_price", "99")
        }

if __name__ == "__main__":
    # Test script locally
    packager = TitanSourcePackager()
    print(packager._generate_sales_copy("Test App", "A cool test app"))
