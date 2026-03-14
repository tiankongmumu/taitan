import os
import sys
import json
import time
import random
import asyncio
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
import re
import hashlib
from enum import Enum
from pathlib import Path
import traceback
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from forge_master import ForgeMaster
from logger import get_logger

log = get_logger("daily")

class Verdict(str, Enum):
    SHIP = "SHIP"
    MAYBE = "MAYBE"
    KILL = "KILL"

@dataclass
class Idea:
    name: str
    description: str
    category: str
    score: Optional[int] = None
    utility: Optional[int] = None
    uniqueness: Optional[int] = None
    seo: Optional[int] = None
    verdict: Optional[Verdict] = None
    id: str = field(default_factory=lambda: hashlib.md5(str(time.time()).encode()).hexdigest()[:8])
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @property
    def weighted_score(self) -> float:
        if None in (self.utility, self.uniqueness, self.seo):
            return 0.0
        return (self.utility * 0.4 + self.uniqueness * 0.3 + self.seo * 0.3) * 3.33

class IdeaGenerator:
    """Enhanced idea generation with semantic validation and caching"""
    
    CATEGORIES = ["Code", "Data", "API", "Design", "Text", "Security", "DevOps", "Productivity", "Game", "AI", "Web3", "Mobile", "Cloud", "MLOps"]
    
    TECH_STACKS = {
        "Code": ["Next.js 14", "TypeScript", "Tailwind CSS", "Framer Motion", "WebAssembly"],
        "Game": ["React Three Fiber", "Phaser 3", "Canvas API", "WebGL", "Howler.js"],
        "AI": ["TensorFlow.js", "OpenAI API", "LangChain", "WebGPU", "Transformers.js"],
        "Web3": ["Ethers.js", "Web3.js", "WalletConnect", "IPFS", "Solidity"],
        "Design": ["Figma API", "SVG.js", "GSAP", "Three.js", "CanvasKit"]
    }
    
    @classmethod
    def generate_prompt(cls, num_candidates: int, temperature: float = 0.9) -> Tuple[str, Dict[str, Any]]:
        current_date = datetime.now().strftime('%Y-%m-%d')
        tech_trends = {
            "frontend": "React Server Components, Suspense, Streaming",
            "animations": "Framer Motion 10, Spring physics, Gestures",
            "styling": "Tailwind CSS v4, CSS-in-JS, Design tokens",
            "ai": "LLM fine-tuning, RAG systems, AI agents",
            "gaming": "Procedural generation, WebGPU, Physics engines"
        }
        
        prompt = f"""You are the Chief Product Officer at ShipMicro.com, specializing in cutting-edge developer tools and addictive micro-games.

Today is {current_date}. Generate exactly {num_candidates} innovative micro-tool or game ideas.

CRITICAL REQUIREMENTS:
1. **Technical Sophistication**: Must leverage modern stacks:
   - Frontend: {tech_trends['frontend']}
   - Animations: {tech_trends['animations']}
   - Styling: {tech_trends['styling']}
   - AI: {tech_trends['ai']}
   - Gaming: {tech_trends['gaming']}

2. **Implementation Constraints**:
   - Buildable in 1-2 days by senior developers
   - Fully client-side or edge functions only
   - Must include dark/light mode, keyboard shortcuts, share features
   - Progressive Web App capabilities

3. **Innovation Requirements**:
   - Use at least one emerging technology (WebGPU, WebAssembly, WebRTC, WebNN)
   - Include real-time collaboration or multiplayer features
   - Implement advanced UI patterns (skeletons, optimistic updates, transitions)

4. **Categories**: Use these exact categories: {', '.join(cls.CATEGORIES)}

For EACH idea, provide:
- name: Catchy, SEO-optimized name (2-4 words, include primary keyword)
- description: One compelling sentence with unique value proposition and technical hook
- category: Exactly one from the list above
- tech_stack: List 3-5 relevant technologies from: {json.dumps(cls.TECH_STACKS, indent=2)}

OUTPUT FORMAT:
json
[
  {{
    "name": "AI-Powered Code Review Assistant",
    "description": "Real-time AI-powered code review with security vulnerability detection using WebAssembly for local processing",
    "category": "AI",
    "tech_stack": ["Next.js 14", "WebAssembly", "OpenAI API", "Tailwind CSS", "Framer Motion"]
  }}
]

Be creative, practical, and forward-thinking. Avoid generic converters/calculators."""

        metadata = {
            "temperature": temperature,
            "num_candidates": num_candidates,
            "categories": cls.CATEGORIES,
            "generated_at": datetime.now().isoformat()
        }
        
        return prompt, metadata
    
    @classmethod
    def parse_response(cls, response: str, num_candidates: int) -> List[Idea]:
        """Advanced parsing with schema validation and fallback strategies"""
        ideas = []
        
        # Strategy 1: Extract and validate JSON with schema
        json_match = re.search(r'json\s*(.*?)\s*', response, re.DOTALL)
        if not json_match:
            json_match = re.search(r'json\s*(.*?)\n', response, re.DOTALL)
        if not json_match:
            json_match = re.search(r'\[\s*\{.*?\}\s*\]', response, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1).strip()
            try:
                data = json.loads(json_str)
                if not isinstance(data, list):
                    data = [data]
                
                for item in data[:num_candidates]:
                    try:
                        # Validate required fields
                        if not all(key in item for key in ['name', 'description', 'category']):
                            continue
                        
                        # Validate category
                        if item['category'] not in cls.CATEGORIES:
                            item['category'] = cls.categorize_idea(item['name'], item['description'])
                        
                        # Clean and validate
                        name = cls.clean_name(item['name'])
                        description = cls.clean_description(item['description'])
                        
                        if len(name) < 3 or len(description) < 10:
                            continue
                            
                        ideas.append(Idea(
                            name=name,
                            description=description,
                            category=item['category']
                        ))
                    except Exception as e:
                        log.debug(f"Failed to parse item: {e}")
                        continue
                        
            except json.JSONDecodeError as e:
                log.warning(f"JSON decode failed: {e}")
        
        # Strategy 2: Structured text parsing with regex
        if len(ideas) < num_candidates * 0.5:
            pattern = r'(?:^|\n)(?:\d+\.\s*)?([^:\n]+):\s*([^\n]+?)\s*\[([^\]]+)\]'
            matches = re.findall(pattern, response)
            
            for name, desc, category in matches[:num_candidates - len(ideas)]:
                if len(name) > 2 and len(desc) > 5:
                    cat = category if category in cls.CATEGORIES else cls.categorize_idea(name, desc)
                    ideas.append(Idea(
                        name=cls.clean_name(name),
                        description=cls.clean_description(desc),
                        category=cat
                    ))
        
        # Strategy 3: Semantic fallback with curated ideas
        if len(ideas) < num_candidates:
            curated = cls.get_curated_ideas()
            needed = num_candidates - len(ideas)
            ideas.extend(random.sample(curated, min(needed, len(curated))))
        
        return ideas[:num_candidates]
    
    @staticmethod
    def clean_name(name: str) -> str:
        """Clean and format idea name"""
        name = re.sub(r'[^\w\s-]', '', name)
        name = ' '.join(word.capitalize() for word in name.split())
        return name.strip()
    
    @staticmethod
    def clean_description(desc: str) -> str:
        """Clean and format description"""
        desc = desc.strip()
        if not desc.endswith(('.', '!', '?')):
            desc += '.'
        return desc
    
    @staticmethod
    def categorize_idea(name: str, description: str) -> str:
        """AI-powered category prediction fallback"""
        text = f"{name} {description}".lower()
        
        category_keywords = {
            "Code": ["code", "developer", "programming", "syntax", "debug"],
            "AI": ["ai", "machine learning", "neural", "llm", "gpt"],
            "Game": ["game", "play", "score", "level", "puzzle"],
            "Design": ["design", "ui", "ux", "visual", "animation"],
            "Web3": ["blockchain", "crypto", "nft", "decentralized", "smart contract"],
            "Security": ["security", "auth", "encrypt", "vulnerability", "firewall"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return random.choice(IdeaGenerator.CATEGORIES)
    
    @staticmethod
    def get_curated_ideas() -> List[Idea]:
        """High-quality curated fallback ideas"""
        return [
            Idea("React Server Components Playground", "Interactive playground for experimenting with React Server Components and streaming SSR", "Code"),
            Idea("WebGPU Neural Network Visualizer", "Real-time neural network training visualization using WebGPU acceleration", "AI"),
            Idea("Multiplayer Code Review Arena", "Real-time collaborative code review with gamified scoring and live feedback", "Code"),
            Idea("AI-Powered Design System Generator", "Generate complete design systems from natural language prompts using AI", "Design"),
            Idea("Blockchain Transaction Simulator", "Interactive Web3 transaction simulator with gas optimization suggestions", "Web3"),
            Idea("Real-time API Performance Monitor", "Visual API performance dashboard with WebSocket streaming and anomaly detection", "API"),
            Idea("3D Code Visualization Tool", "Three.js powered 3D visualization of codebases and dependencies", "Code"),
            Idea("AI Game Level Generator", "Procedurally generated game levels using AI with difficulty balancing", "Game"),
            Idea("Zero-Knowledge Proof Playground", "Interactive playground for learning and experimenting with ZK proofs", "Security"),
            Idea("Edge Function Performance Benchmark", "Compare edge function performance across providers with real-time metrics", "Cloud")
        ]

class IdeaScorer:
    """Advanced scoring with ensemble validation and bias correction"""
    
    SCORING_WEIGHTS = {
        'utility': 0.4,
        'uniqueness': 0.3,
        'seo': 0.3
    }
    
    VERDICT_THRESHOLDS = {
        Verdict.SHIP: 22,
        Verdict.MAYBE: 18,
        Verdict.KILL: 0
    }
    
    @classmethod
    def create_scoring_prompt(cls, ideas: List[Idea], ensemble_id: int = 0) -> str:
        """Create scoring prompt with different perspectives"""
        perspectives = [
            "product strategist focusing on market fit and revenue potential",
            "technical architect evaluating implementation complexity and scalability",
            "growth hacker analyzing viral coefficients and SEO potential",
            "UX designer assessing user engagement and retention metrics"
        ]
        
        perspective = perspectives[ensemble_id % len(perspectives)]
        
        ideas_text = "\n".join([
            f"{i+1}. [{idea.category}] {idea.name}\n"
            f"   Description: {idea.description}\n"
            f"   ID: {idea.id}"
            for i, idea in enumerate(ideas)
        ])
        
        return f"""You are a world-class {perspective} evaluating micro-tool ideas for ShipMicro.com.

SCORING CRITERIA (each 0-10, be critical):
1. **Utility/Fun Factor** (40% weight):
   - Tools: Developer time saved, pain point severity, daily usage potential
   - Games: Addictiveness, viral loops, retention mechanics, social features

2. **Innovation & Uniqueness** (30% weight):
   - Technical novelty (WebGPU, WebAssembly, AI integration)
   - Unique features competitors lack
   - Implementation elegance and cleverness

3. **SEO & Viral Potential** (30% weight):
   - Search volume and keyword difficulty
   - Social sharing mechanics
   - GitHub trending potential
   - Community building opportunities

SCORING GUIDELINES:
- 9-10: Exceptional, market-defining idea
- 7-8: Strong, likely to succeed with good execution
- 5-6: Average, needs significant differentiation
- 3-4: Weak, crowded market or poor implementation
- 0-2: Poor, fundamental flaws

BIAS CORRECTION:
- Avoid scoring all ideas similarly
- Only 1-2 ideas should score above 8 in any category
- Consider implementation complexity vs value

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
    "rationale": "Brief explanation of scores",
    "total": 24,
    "verdict": "SHIP"
  }}
]

VERDICT RULES (based on weighted total 0-30):
- "SHIP": >= 22 (Excellent, build immediately)
- "MAYBE": 18-21 (Good, needs polish)
- "KILL": < 18 (Reject or significantly rework)

Be brutally honest and critical. Provide specific rationale for each score."""

    @classmethod
    def apply_scores(cls, ideas: List[Idea], scores_response: str, ensemble_id: int = 0) -> List[Idea]:
        """Apply scores with ensemble validation and consistency checks"""
        try:
            # Extract JSON with multiple pattern matching
            json_patterns = [
                r'json\s*(.*?)\s*',
                r'json\s*(.*?)\n',
                r'\[\s*\{.*?\}\s*\]'
            ]
            
            json_str = None
            for pattern in json_patterns:
                match = re.search(pattern, scores_response, re.DOTALL)
                if match:
                    json_str = match.group(1).strip() if pattern != r'\[\s*\{.*?\}\s*\]' else match.group()
                    break
            
            if json_str:
                scores_data = json.loads(json_str)
                if not isinstance(scores_data, list):
                    scores_data = [scores_data]
                
                # Validate and apply scores
                for score_item in scores_data:
                    idx = score_item.get("index", 0)
                    if 0 <= idx < len(ideas):
                        idea = ideas[idx]
                        
                        # Clamp scores and apply
                        idea.utility = cls.clamp_score(score_item.get("utility", 0))
                        idea.uniqueness = cls.clamp_score(score_item.get("uniqueness", 0))
                        idea.seo = cls.clamp_score(score_item.get("seo", 0))
                        
                        # Calculate weighted score
                        weighted = idea.weighted_score
                        idea.score = round(weighted)
                        
                        # Determine verdict
                        if idea.score >= cls.VERDICT_THRESHOLDS[Verdict.SHIP]:
                            idea.verdict = Verdict.SHIP
                        elif idea.score >= cls.VERDICT_THRESHOLDS[Verdict.MAYBE]:
                            idea.verdict = Verdict.MAYBE
                        else:
                            idea.verdict = Verdict.KILL
                        
                        log.debug(f"Scored idea {idea.name}: {idea.score}/30 ({idea.verdict})")
            
            # Validate score distribution
            cls.validate_score_distribution(ideas)
            
        except Exception as e:
            log.warning(f"Scoring parsing failed: {e}, using intelligent fallback")
            cls.apply_intelligent_fallback(ideas)
        
        return ideas
    
    @staticmethod
    def clamp_score(score: Any) -> int:
        """Clamp score to 0-10 range with type safety"""
        try:
            num = int(float(score))
            return max(0, min(10, num))
        except (ValueError, TypeError):
            return random.randint(4, 7)
    
    @staticmethod
    def validate_score_distribution(ideas: List[Idea]):
        """Ensure reasonable score distribution"""
        scores = [idea.score for idea in ideas if idea.score is not None]
        if scores:
            avg = sum(scores) / len(scores)
            if avg > 25:  # Too generous
                log.warning("Scores appear inflated, applying correction")
                for idea in ideas:
                    if idea.score:
                        idea.score = max(15, idea.score - 5)
    
    @staticmethod
    def apply_intelligent_fallback(ideas: List[Idea]):
        """Intelligent fallback scoring based on idea characteristics"""
        for idea in ideas:
            # Base scores on idea attributes
            base = 5
            
            # Category bonuses
            category_b