import os
import sys
import json
import time
import random
import asyncio
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from forge_master import ForgeMaster
from logger import get_logger

log = get_logger("daily")

@dataclass
class Idea:
    name: str
    description: str
    category: str
    score: Optional[int] = None
    utility: Optional[int] = None
    uniqueness: Optional[int] = None
    seo: Optional[int] = None
    verdict: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class IdeaGenerator:
    """Enhanced idea generation with better prompts and validation"""
    
    CATEGORIES = ["Code", "Data", "API", "Design", "Text", "Security", "DevOps", "Productivity", "Game", "AI", "Web3", "Mobile"]
    
    @staticmethod
    def generate_prompt(num_candidates: int) -> str:
        current_date = datetime.now().strftime('%Y-%m-%d')
        return f"""You are the Chief Product Officer at ShipMicro.com, specializing in cutting-edge developer tools and addictive micro-games.

Today is {current_date}. Generate exactly {num_candidates} innovative micro-tool or game ideas.

CRITICAL REQUIREMENTS:
1. **For Tools**: Must solve REAL developer pain points with elegant, client-side solutions
2. **For Games**: Must be highly addictive HTML5/React games with viral potential (think: Wordle clones, physics puzzles, idle RPGs)
3. **Technical Feasibility**: Must be implementable in 1-2 days by a senior developer
4. **Modern Stack**: Consider Next.js 14, Tailwind CSS, Framer Motion, React hooks, WebAssembly, WebGL
5. **Categories**: Use these exact categories: {', '.join(IdeaGenerator.CATEGORIES)}

For EACH idea, provide:
- name: Catchy, SEO-friendly name (2-4 words)
- description: One compelling sentence highlighting unique value
- category: Exactly one from the list above

OUTPUT FORMAT:
json
[
  {{
    "name": "AI Code Review Assistant",
    "description": "Real-time AI-powered code review with security vulnerability detection",
    "category": "AI"
  }}
]


Be creative, practical, and forward-thinking. Avoid generic converters/calculators."""

    @staticmethod
    def parse_response(response: str, num_candidates: int) -> List[Idea]:
        """Robust parsing with multiple fallback strategies"""
        ideas = []
        
        # Strategy 1: Extract JSON from code blocks
        json_patterns = [
            r'json\n(.*?)\n',
            r'\n(.*?)\n',
            r'\[.*\]'
        ]
        
        json_str = None
        for pattern in json_patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                json_str = match.group(1) if pattern != r'\[.*\]' else match.group()
                break
        
        if json_str:
            try:
                data = json.loads(json_str)
                for item in data[:num_candidates]:
                    if all(key in item for key in ['name', 'description', 'category']):
                        ideas.append(Idea(
                            name=item['name'].strip(),
                            description=item['description'].strip(),
                            category=item['category'].strip()
                        ))
            except json.JSONDecodeError:
                log.warning("Failed to parse JSON, falling back to regex extraction")
        
        # Strategy 2: Fallback to regex extraction
        if not ideas:
            lines = response.strip().split('\n')
            for line in lines:
                if ':' in line and len(line) < 200:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        ideas.append(Idea(
                            name=parts[0].strip(),
                            description=parts[1].strip(),
                            category=random.choice(IdeaGenerator.CATEGORIES)
                        ))
        
        # Strategy 3: Ultimate fallback
        if not ideas:
            fallback_ideas = [
                Idea("React Component Playground", "Interactive playground for building and testing React components with live preview", "Code"),
                Idea("Web3 Transaction Simulator", "Visualize and simulate blockchain transactions before execution", "Web3"),
                Idea("AI-Powered SVG Animator", "Generate stunning SVG animations using natural language prompts", "Design"),
                Idea("Real-time API Load Tester", "Visual load testing with real-time metrics and WebSocket support", "API"),
                Idea("Neural Network Playground", "Interactive neural network builder with TensorFlow.js visualization", "AI"),
                Idea("CSS Grid Generator Pro", "Advanced CSS Grid generator with responsive breakpoints and animation", "Design"),
                Idea("JWT Security Auditor", "Comprehensive JWT analysis with security vulnerability detection", "Security"),
                Idea("WebAssembly Benchmark Suite", "Compare WebAssembly performance across different compilers", "Code"),
                Idea("3D Physics Sandbox", "Interactive 3D physics simulation using Three.js and Cannon.js", "Game"),
                Idea("Real-time Data Pipeline Visualizer", "Visualize streaming data pipelines with Apache Kafka simulation", "Data")
            ]
            ideas = random.sample(fallback_ideas, min(num_candidates, len(fallback_ideas)))
        
        return ideas[:num_candidates]

class IdeaScorer:
    """Advanced scoring with weighted criteria and consistency checks"""
    
    SCORING_WEIGHTS = {
        'utility': 0.4,
        'uniqueness': 0.3,
        'seo': 0.3
    }
    
    @staticmethod
    def create_scoring_prompt(ideas: List[Idea]) -> str:
        ideas_text = "\n".join([
            f"{i+1}. [{idea.category}] {idea.name}: {idea.description}"
            for i, idea in enumerate(ideas)
        ])
        
        return f"""You are a world-class product strategist evaluating micro-tool ideas for ShipMicro.com.

SCORING CRITERIA (each 0-10):
1. **Utility/Fun Factor** (40% weight):
   - Tools: How much time does this save developers? How painful is the problem it solves?
   - Games: How addictive/viral is this? Retention potential?

2. **Innovation & Uniqueness** (30% weight):
   - How novel is this approach? Does it use modern tech (AI, Web3, WebAssembly)?
   - Is there a unique twist that competitors lack?

3. **SEO & Viral Potential** (30% weight):
   - Search volume for related terms? Social sharing potential?
   - Could this trend on GitHub/Twitter/Product Hunt?

SCORING GUIDELINES:
- 9-10: Exceptional, market-leading idea
- 7-8: Strong, likely successful
- 5-6: Average, needs improvement
- 3-4: Weak, many alternatives exist
- 0-2: Poor, don't build

IDEAS TO SCORE:
{ideas_text}

OUTPUT FORMAT:
json
[
  {{
    "index": 0,
    "utility": 8,
    "uniqueness": 7,
    "seo": 9,
    "total": 24,
    "verdict": "SHIP"
  }}
]


VERDICT RULES:
- "SHIP": total >= 22 (Excellent)
- "MAYBE": 18-21 (Good, needs polish)
- "KILL": < 18 (Reject)

Be brutally honest. Only 1-2 ideas should get "SHIP" verdict."""

    @staticmethod
    def apply_scores(ideas: List[Idea], scores_response: str) -> List[Idea]:
        """Apply scores with validation and normalization"""
        try:
            # Extract JSON
            json_match = re.search(r'json\n(.*?)\n', scores_response, re.DOTALL)
            if not json_match:
                json_match = re.search(r'\[.*\]', scores_response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1) if '' in scores_response else json_match.group()
                scores_data = json.loads(json_str)
                
                for score_item in scores_data:
                    idx = score_item.get("index", 0)
                    if 0 <= idx < len(ideas):
                        ideas[idx].utility = min(max(score_item.get("utility", 0), 0), 10)
                        ideas[idx].uniqueness = min(max(score_item.get("uniqueness", 0), 0), 10)
                        ideas[idx].seo = min(max(score_item.get("seo", 0), 0), 10)
                        
                        # Calculate weighted total
                        total = (
                            ideas[idx].utility * IdeaScorer.SCORING_WEIGHTS['utility'] +
                            ideas[idx].uniqueness * IdeaScorer.SCORING_WEIGHTS['uniqueness'] +
                            ideas[idx].seo * IdeaScorer.SCORING_WEIGHTS['seo']
                        ) * 3.33  # Scale to 0-30
                        
                        ideas[idx].score = round(total)
                        
                        # Determine verdict
                        if ideas[idx].score >= 22:
                            ideas[idx].verdict = "SHIP"
                        elif ideas[idx].score >= 18:
                            ideas[idx].verdict = "MAYBE"
                        else:
                            ideas[idx].verdict = "KILL"
        except Exception as e:
            log.warning(f"Scoring parsing failed: {e}, using fallback")
            for idea in ideas:
                idea.utility = random.randint(5, 9)
                idea.uniqueness = random.randint(4, 8)
                idea.seo = random.randint(5, 9)
                idea.score = idea.utility + idea.uniqueness + idea.seo
                idea.verdict = "SHIP" if idea.score >= 22 else ("MAYBE" if idea.score >= 18 else "KILL")
        
        return ideas

class QualityForge:
    """Main orchestrator with parallel processing and better error handling"""
    
    def __init__(self):
        self.llm = LLMClient()
        self.executor = ThreadPoolExecutor(max_workers=3)
        
    def generate_candidates(self, num_candidates: int = 10) -> List[Idea]:
        """Generate candidate ideas with retry logic"""
        log.info(f"🧠 Generating {num_candidates} candidate ideas...")
        
        for attempt in range(3):
            try:
                prompt = IdeaGenerator.generate_prompt(num_candidates)
                response = self.llm.generate(prompt)
                ideas = IdeaGenerator.parse_response(response, num_candidates)
                
                if len(ideas) >= num_candidates * 0.7:  # 70% success threshold
                    log.info(f"✅ Generated {len(ideas)} ideas (attempt {attempt + 1})")
                    return ideas
                else:
                    log.warning(f"Attempt {attempt + 1}: Only got {len(ideas)} ideas")
            except Exception as e:
                log.warning(f"Attempt {attempt + 1} failed: {e}")
            
            if attempt < 2:
                time.sleep(1)
        
        # Final fallback
        return IdeaGenerator.parse_response("", num_candidates)
    
    def score_ideas(self, ideas: List[Idea]) -> List[Idea]:
        """Score ideas with parallel processing for large batches"""
        log.info(f"⚖️ AI scoring {len(ideas)} ideas...")
        
        if len(ideas) <= 5:
            # Small batch, single request
            prompt = IdeaScorer.create_scoring_prompt(ideas)
            response = self.llm.generate(prompt)
            return IdeaScorer.apply_scores(ideas, response)
        else:
            # Large batch, split and process in parallel
            batch_size = 5
            batches = [ideas[i:i + batch_size] for i in range(0, len(ideas), batch_size)]
            
            def score_batch(batch: List[Idea]) -> List[Idea]:
                prompt = IdeaScorer.create_scoring_prompt(batch)
                response = self.llm.generate(prompt)
                return IdeaScorer.apply_scores(batch, response)
            
            scored_batches = []
            futures = [self.executor.submit(score_batch, batch) for batch in batches]
            
            for future in as_completed(futures):
                try:
                    scored_batches.extend(future.result())
                except Exception as e:
                    log.error(f"Batch scoring failed: {e}")
                    # Apply default scores to failed batch
                    for idea in batch:
                        idea.utility = random.randint(5, 8)
                        idea.uniqueness = random.randint(4, 7)
                        idea.seo = random.randint(5, 8)
                        idea.score = idea.utility + idea.uniqueness + idea.seo
                        idea.verdict = "SHIP" if idea.score >= 22 else ("MAYBE" if idea.score >= 18 else "KILL")
                    scored_batches.extend(batch)
            
            return scored_batches
    
    def select_top_ideas(self, ideas: List[Idea], top_n: int = 3) -> List[Idea]:
        """Select top ideas with diversity consideration"""
        # Filter and sort
        valid_ideas = [idea for idea in ideas if idea.score is not None]
        valid_ideas.sort(key=lambda x: x.score, reverse=True)
        
        # Log ranking
        log.info("\n📊 IDEA RANKINGS:")
        for i, idea in enumerate(valid_ideas[:10]):  # Show top 10
            emoji = "🚀" if idea.verdict == "SHIP" else ("⚠️" if idea.verdict == "MAYBE" else "❌")
            log.info(f"  {emoji} #{i+1:2d} [{idea.score:2d}/30] {idea.name}")
            log.info(f"       Utility: {idea.utility}/10 | Uniqueness: {idea.uniqueness}/10 | SEO: {idea.seo}/10")
            log.info(f"       Category: {idea.category} | Verdict: {idea.verdict}")
        
        # Select with category diversity
        selected = []
        categories_seen = set()
        
        for idea in valid_ideas:
            if idea.verdict in ("SHIP", "MAYBE"):
                if idea.category not in categories_seen or len(selected) < top_n // 2:
                    selected.append(idea)
                    categories_seen.add(idea.category)
                if len(selected) >= top_n:
                    break
        
        # Fill remaining slots with highest scores
        if len(selected) < top_n:
            for idea in valid_ideas:
                if idea not in selected and idea.verdict in ("SHIP", "MAYBE"):
                    selected.append(idea)
                    if len(selected) >= top_n:
                        break
        
        # Ultimate fallback
        if not selected and valid_ideas:
            selected = valid_ideas[:top_n]
        
        log.info(f"\n✅ Selected {len(selected)} ideas for production:")
        for idea in selected:
            log.info(f"  🏆 {idea.name} (Score: {idea.score}/30, Category: {idea.category})")
        
        return selected
    
    def forge_idea(self, idea: Idea, index: int, total: int) -> Dict[str, Any]:
        """Forge a single idea with enhanced context"""
        log.info(f"\n{'='*50}")
        log.info(f"🔨 [{index}/{total}] Forging: {idea.name}")
        log.info(f"{'='*50}")
        log.info(f"📝 Description: {idea.description}")
        log.info(f"🏷️ Category: {idea.category}")
        log.info(f"📊 Score: {idea.score}/30 (U:{idea.utility}/10, N:{idea.uniqueness}/10, S:{idea.seo}/10)")
        
        try:
            forge = ForgeMaster()
            
            # Enhanced idea context for better generation
            enhanced_context = {
                "name": idea.name,
                "description": idea.description,
                "category": idea.category,
                "score": idea.score,
                "requirements": [
                    "Use Next.js 14 with App Router",
                    "Implement responsive design with Tailwind CSS",
                    "Add subtle animations with Framer Motion",
                    "Use modern React hooks (useState, useEffect, useCallback)",
                    "Ensure excellent TypeScript coverage",
                    "Implement dark/light mode toggle",
                    "Add keyboard shortcuts for power users",
                    "Include share functionality",
                    "Make it fully client-side with no backend"
                ]
            }
            
            success = forge.run_pipeline(json.dumps(enhanced_context))
            
            if success:
                log.info(f"✅ Successfully forged: {idea.name}")
                return {"idea": idea, "success": True}
            else:
                log.warning(f"❌ Failed to forge: {idea.name}")
                return {"idea": idea, "success": False}
                
        except Exception as e:
            log.error(f"💥 Exception during forging: {str(e)}")
            return {"idea": idea, "success": False, "error": str(e)}
    
    def run(self, num_tools: int = 3, dry_run: bool = False) -> List[Dict[str, Any]]:
        """Main execution pipeline"""
        log.info("=" * 60)
        log.info("🚀 SHIPMICRO QUALITY FORGE v3.0")
        log.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log.info(f"🎯 Target: {num_tools} premium tools from curated selection")
        log.info(f"⚡ Mode: {'DRY RUN' if dry_run else 'PRODUCTION'}")
        log.info("=" * 60)