"""
TITAN Engine v3.0: Skill Extractor (领悟工坊)
负责利用大模型阅读 github_raw_data 里的开源代码，提炼并总结为通用的 Skill Prompt，
存入 memory_bank 的 architectural_patterns.json 中备用。
"""
import os
import json
import time
from config import FORGE_ROOT
from logger import get_logger
from core_generators.llm_client import LLMClient
import memory_bank as mem

log = get_logger("extractor")

RAW_DATA_DIR = os.path.join(FORGE_ROOT, "github_raw_data")

class SkillExtractor:
    def __init__(self):
        self.llm = LLMClient()
        # 记录已经提取过的项目，避免重复提炼
        self.processed_repos_file = os.path.join(RAW_DATA_DIR, "processed_repos.json")
        self.processed = self._load_processed()

    def _load_processed(self) -> set:
        if os.path.exists(self.processed_repos_file):
            try:
                with open(self.processed_repos_file, "r", encoding="utf-8") as f:
                    return set(json.load(f))
            except Exception:
                pass
        return set()

    def _save_processed(self):
        with open(self.processed_repos_file, "w", encoding="utf-8") as f:
            json.dump(list(self.processed), f, ensure_ascii=False)

    def extract_from_repo(self, repo_dir_name: str):
        if repo_dir_name in self.processed:
            log.info(f"⏭️ {repo_dir_name} 已处理过，跳过...")
            return

        repo_path = os.path.join(RAW_DATA_DIR, repo_dir_name)
        if not os.path.isdir(repo_path):
            return

        log.info(f"🧠 正在深度阅读开源项目: {repo_dir_name}")
        
        # 加载 meta 数据
        meta_path = os.path.join(repo_path, "meta.json")
        repo_name = repo_dir_name
        domain = "agent"
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                repo_name = meta.get("full_name", repo_dir_name)
                domain = meta.get("domain", "agent")
                
        # 收集该项目的所有代码
        code_snippets = []
        target_files = []
        for file in os.listdir(repo_path):
            if file == "meta.json" or file == "processed_repos.json":
                continue
            fpath = os.path.join(repo_path, file)
            if os.path.isfile(fpath):
                target_files.append(file)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        code_snippets.append(f"--- FILE: {file} ---\n{f.read()[:3000]}\n")
                except Exception:
                    pass

        if not code_snippets:
            log.warning(f"  ⚠️ {repo_dir_name} 没有可供阅读的代码。")
            return

        combined_code = "\n".join(code_snippets)
        if len(combined_code) > 12000:
            combined_code = combined_code[:12000] # 防止超限

        domain_instructions = {
            "agent": "Agent state-machine loops or DAG workflows.\n- Effective system architectures for LLM apps.\n- Tool use schemas or prompt engineering tricks.",
            "frontend": "Advanced UI component patterns.\n- Render optimizations and state management architectures.\n- Component decoupling techniques.",
            "backend": "High-concurrency API designs.\n- ORM setups, connection pooling, and routing efficiency.\n- Domain-Driven Design (DDD) or microservice patterns.",
            "game-engine": "Entity Component Systems (ECS) or game loop designs.\n- Memory pooling and render pipeline optimizations.\n- Event bus and performance-critical structuring."
        }
        
        instruction_text = domain_instructions.get(domain, domain_instructions["agent"])

        extract_prompt = f"""You are the Chief Architect of the TITAN AI Generation Engine.
Your task is to review the following open-source project files and extract up to 2 strictly actionable 'Design Patterns' or 'Skills' that our AI code generator can use in the future.

Repository: {repo_name} (Domain: {domain})
Files read: {', '.join(target_files)}

CODE SNIPPETS:
{combined_code}

Instructions:
Identify any advanced engineering patterns in this domain, for example:
- {instruction_text}

Respond ONLY with a valid JSON array of objects. Do not include markdown code block wrappers like ```json.
If nothing valuable can be extracted, return [].
Format for each object in the array:
{{
  "category": "Frontend" | "Backend" | "GameEngine" | "Agent" | "Pipeline" | "General",
  "description": "What this pattern does and why it is superior (max 50 words).",
  "prompt_fragment": "The exact instructional prompt snippet (max 100 words) we can inject into our generator context when building similar apps in the future. Must be an actionable constraint/rule."
}}
"""
        log.info("  🤖 正在请教大模型提炼架构模式...")
        try:
            result_str = self.llm.generate(extract_prompt, is_json=True)
            patterns = json.loads(result_str)
            
            if not isinstance(patterns, list):
                if isinstance(patterns, dict) and "category" in patterns:
                    patterns = [patterns] # 有时它只返回一个对象
                else:
                    patterns = []

            if not patterns:
                log.info("  ⚠️ 大模型未发现值得提取的硬核模式。")
            else:
                for p in patterns:
                    mem.remember_pattern(
                        category=p.get("category", "General"),
                        source_repo=repo_name,
                        description=p.get("description", "Extracted pattern"),
                        prompt_fragment=p.get("prompt_fragment", "")
                    )
                log.info(f"  ✅ 成功提炼 {len(patterns)} 条高级技能！")

            self.processed.add(repo_dir_name)
            self._save_processed()
            
        except Exception as e:
            log.error(f"  ❌ 提取失败: {e}")

    def run_all(self):
        if not os.path.exists(RAW_DATA_DIR):
            log.error("没有找到 github_raw_data 目录，请先运行 github_scholar.py")
            return
            
        dirs = [d for d in os.listdir(RAW_DATA_DIR) if os.path.isdir(os.path.join(RAW_DATA_DIR, d))]
        if not dirs:
            log.info("暂无数据可提炼。")
            return
            
        for d in dirs:
            try:
                self.extract_from_repo(d)
                time.sleep(1)
            except Exception as e:
                log.error(f"  ❌ 跳过 {d} 因为发生活动级错误: {e}")
                time.sleep(5)
            
        log.info("=" * 60)
        log.info("🎓 领悟工坊 (Skill Extractor) 处理完毕！")
        log.info("=" * 60)

if __name__ == "__main__":
    extractor = SkillExtractor()
    extractor.run_all()
