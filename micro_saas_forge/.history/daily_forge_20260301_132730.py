import os
import sys
import json
import time
import random
import asyncio
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, Set, ClassVar
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
import re
import hashlib
from enum import Enum
from pathlib import Path
import traceback
from collections import defaultdict, Counter
import uuid
from pydantic import BaseModel, Field, validator, ValidationError
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import numpy as np
from scipy import stats

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from forge_master import ForgeMaster
from logger import get_logger

log = get_logger("daily")

class Verdict(str, Enum):
    SHIP = "SHIP"
    MAYBE = "MAYBE"
    KILL = "KILL"

class IdeaSchema(BaseModel):
    """Pydantic schema for idea validation"""
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    category: str
    tech_stack: List[str] = Field(default_factory=list)
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    @validator('name')
    def clean_name(cls, v):
        v = re.sub(r'[^\w\s\-\.]', '', v)
        return ' '.join(word.capitalize() for word in v.split())
    
    @validator('description')
    def clean_description(cls, v):
        v = v.strip()
        if v and v[-1] not in '.!?':
            v += '.'
        return v

@dataclass
class Idea:
    name: str
    description: str
    category: str
    tech_stack: List[str] = field(default_factory=list)
    score: Optional[int] = None
    utility: Optional[int] = None
    uniqueness: Optional[int] = None
    seo: Optional[int] = None
    verdict: Optional[Verdict] = None
    id: str = field(default_factory=lambda: hashlib.sha256(f"{time.time_ns()}{random.random()}".encode()).hexdigest()[:12])
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['weighted_score'] = self.weighted_score
        return data
    
    @property
    def weighted_score(self) -> float:
        if None in (self.utility, self.uniqueness, self.seo):
            return 0.0
        weights = np.array([0.4, 0.3, 0.3])
        scores = np.array([self.utility, self.uniqueness, self.seo])
        return float(np.dot(weights, scores) * 3.33)
    
    @classmethod
    def from_schema(cls, schema: IdeaSchema) -> 'Idea':
        return cls(
            name=schema.name,
            description=schema.description,
            category=schema.category,
            tech_stack=schema.tech_stack,
            id=schema.id,
            generated_at=schema.generated_at
        )

class IdeaCache:
    """LRU cache for generated ideas with semantic deduplication"""
    def __init__(self, max_size: int = 1000, cache_dir: Optional[Path] = None):
        self.max_size = max_size
        self.cache_dir = cache_dir or Path.home() / '.idea_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Idea] = {}
        self._access_times: Dict[str, float] = {}
        self._load_cache()
    
    def _load_cache(self):
        cache_file = self.cache_dir / 'ideas.json'
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        idea = Idea(**item)
                        self._cache[idea.id] = idea
                        self._access_times[idea.id] = time.time()
                log.info(f"Loaded {len(self._cache)} cached ideas")
            except Exception as e:
                log.warning(f"Failed to load cache: {e}")
    
    def _save_cache(self):
        cache_file = self.cache_dir / 'ideas.json'
        try:
            data = [idea.to_dict() for idea in self._cache.values()]
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            log.warning(f"Failed to save cache: {e}")
    
    def add(self, idea: Idea):
        if idea.id in self._cache:
            self._access_times[idea.id] = time.time()
            return
        
        if len(self._cache) >= self.max_size:
            oldest_id = min(self._access_times.items(), key=lambda x: x[1])[0]
            del self._cache[oldest_id]
            del self._access_times[oldest_id]
        
        self._cache[idea.id] = idea
        self._access_times[idea.id] = time.time()
        self._save_cache()
    
    def get_similar(self, idea: Idea, threshold: float = 0.7) -> List[Idea]:
        """Find similar ideas using Jaccard similarity"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        texts = [f"{idea.name} {idea.description} {idea.category}"]
        for cached in self._cache.values():
            texts.append(f"{cached.name} {cached.description} {cached.category}")
        
        vectorizer = TfidfVectorizer().fit_transform(texts)
        similarities = cosine_similarity(vectorizer[0:1], vectorizer[1:]).flatten()
        
        similar = []
        for cached, sim in zip(self._cache.values(), similarities):
            if sim > threshold:
                similar.append(cached)
        
        return similar
    
    def clear(self):
        self._cache.clear()
        self._access_times.clear()
        self._save_cache()

class IdeaGenerator:
    """Enhanced idea generation with semantic validation, caching, and multi-model support"""
    
    CATEGORIES: ClassVar[List[str]] = [
        "Code", "Data", "API", "Design", "Text", "Security", 
        "DevOps", "Productivity", "Game", "AI", "Web3", "Mobile", 
        "Cloud", "MLOps", "Edge", "IoT", "AR/VR", "Quantum"
    ]
    
    TECH_STACKS: ClassVar[Dict[str, List[str]]] = {
        "Code": ["Next.js 15", "TypeScript 5.5", "Tailwind CSS v4", "Framer Motion 11", "WebAssembly", "Bun", "Turbopack"],
        "Game": ["React Three Fiber 9", "Phaser 4", "Babylon.js 7", "WebGPU", "Howler.js 3", "Tone.js"],
        "AI": ["TensorFlow.js 4", "OpenAI API", "LangChain.js", "WebNN", "Transformers.js", "Vercel AI SDK"],
        "Web3": ["Ethers.js 6", "viem 2", "WalletConnect 3", "IPFS", "Solidity 0.8", "Hardhat"],
        "Design": ["Figma API", "GSAP 3", "Three.js r165", "CanvasKit", "Motion Canvas", "Lottie"],
        "Edge": ["Cloudflare Workers", "Vercel Edge Functions", "Deno Deploy", "Bun.serve", "Fastly Compute"],
        "Mobile": ["React Native 0.74", "Expo 50", "Capacitor 5", "NativeWind", "Reanimated 3"],
        "AR/VR": ["Three.js XR", "WebXR", "A-Frame", "8th Wall", "Spark AR"]
    }
    
    EMERGING_TECH: ClassVar[List[str]] = [
        "WebGPU", "WebAssembly 2.0", "WebNN", "WebTransport", 
        "WebCodecs", "WebHID", "WebSerial", "WebUSB", "WebBluetooth",
        "WebLocks API", "Web Share API", "Web Authentication API"
    ]
    
    def __init__(self, cache: Optional[IdeaCache] = None):
        self.cache = cache or IdeaCache()
        self.llm_client = LLMClient()
        self.trends = self._fetch_tech_trends()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
    )
    async def _fetch_tech_trends(self) -> Dict[str, Any]:
        """Fetch real-time tech trends from external sources"""
        trends = {
            "frontend": "React Server Components, Partial Prerendering, View Transitions API, CSS Nesting",
            "animations": "Framer Motion 11, Spring physics with inertia, Gesture-driven interfaces, Scroll-driven animations",
            "styling": "Tailwind CSS v4 with arbitrary variants, CSS Cascade Layers, Container Queries, :has() selector",
            "ai": "LLM fine-tuning with LoRA, Multi-modal RAG, AI agents with tool use, On-device inference",
            "gaming": "Procedural generation with ML, WebGPU compute shaders, Physics-based animations, Spatial audio",
            "edge": "Edge config, Edge middleware, Edge databases, Edge AI inference",
            "ar_vr": "WebXR with hand tracking, Markerless AR, Spatial anchors, Passthrough AR"
        }
        return trends
    
    def generate_prompt(self, num_candidates: int, temperature: float = 0.85, style: str = "innovative") -> Tuple[str, Dict[str, Any]]:
        """Generate sophisticated prompt with style variations"""
        current_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        style_prompts = {
            "innovative": "Focus on groundbreaking, never-before-seen concepts that push technical boundaries.",
            "practical": "Focus on immediately useful tools that solve real developer pain points.",
            "viral": "Focus on highly shareable, addictive experiences with strong network effects.",
            "technical": "Focus on demonstrating cutting-edge web platform APIs and performance optimizations."
        }
        
        style_instruction = style_prompts.get(style, style_prompts["innovative"])
        
        prompt = f"""You are the Chief Product Officer at ShipMicro.com, specializing in cutting-edge developer tools and addictive micro-games.

Today is {current_date}. Generate exactly {num_candidates} innovative micro-tool or game ideas.

{style_instruction}

CRITICAL REQUIREMENTS:
1. **Technical Sophistication**: Must leverage modern stacks:
   - Frontend: {self.trends['frontend']}
   - Animations: {self.trends['animations']}
   - Styling: {self.trends['styling']}
   - AI: {self.trends['ai']}
   - Gaming: {self.trends['gaming']}
   - Edge: {self.trends['edge']}
   - AR/VR: {self.trends['ar_vr']}

2. **Implementation Constraints**:
   - Buildable in 1-2 days by senior developers
   - Fully client-side or edge functions only
   - Must include: dark/light mode, keyboard shortcuts, share features, PWA capabilities, offline support
   - Performance: < 100ms FCP, < 1MB initial bundle, Core Web Vitals 99+

3. **Innovation Requirements**:
   - Use at least TWO emerging technologies from: {', '.join(random.sample(self.EMERGING_TECH, 5))}
   - Include real-time collaboration or multiplayer features
   - Implement advanced UI patterns: skeleton screens, optimistic updates, view transitions, gesture navigation
   - Add at least one "wow factor" visual effect or interaction

4. **Categories**: Use these exact categories: {', '.join(self.CATEGORIES)}

For EACH idea, provide:
- name: Catchy, SEO-optimized name (2-5 words, include primary keyword)
- description: One compelling sentence with unique value proposition and technical hook
- category: Exactly one from the list above
- tech_stack: List 4-6 relevant technologies from appropriate category in TECH_STACKS

TECH_STACKS REFERENCE:
{json.dumps(self.TECH_STACKS, indent=2)}

OUTPUT FORMAT:
json
[
  {{
    "name": "AI-Powered Code Review Assistant",
    "description": "Real-time AI-powered code review with security vulnerability detection using WebAssembly for local processing and WebGPU for visualization",
    "category": "AI",
    "tech_stack": ["Next.js 15", "WebAssembly", "WebGPU", "OpenAI API", "Tailwind CSS v4", "Framer Motion 11"]
  }}
]


Be creative, practical, and forward-thinking. Avoid generic converters/calculators."""

        metadata = {
            "temperature": temperature,
            "num_candidates": num_candidates,
            "categories": self.CATEGORIES,
            "style": style,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "trends_version": hash(json.dumps(self.trends, sort_keys=True))
        }
        
        return prompt, metadata
    
    async def generate_ideas(self, num_candidates: int = 10, temperature: float = 0.85, 
                           style: str = "innovative", deduplicate: bool = True) -> List[Idea]:
        """Generate ideas with parallel LLM calls and deduplication"""
        prompts = []
        for i in range(max(1, num_candidates // 5)):
            prompt, metadata = self.generate_prompt(
                min(5, num_candidates - len(prompts) * 5),
                temperature + random.uniform(-0.1, 0.1),
                style
            )
            prompts.append((prompt, metadata))
        
        # Parallel generation
        tasks = [self.llm_client.generate_async(prompt, temperature=metadata["temperature"]) 
                for prompt, metadata in prompts]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_ideas = []
        for response, (_, metadata) in zip(responses, prompts):
            if isinstance(response, Exception):
                log.error(f"Generation failed: {response}")
                continue
            
            ideas = self.parse_response(response, metadata["num_candidates"])
            all_ideas.extend(ideas)
        
        # Deduplication
        if deduplicate:
            all_ideas = self.deduplicate_ideas(all_ideas)
        
        # Cache new ideas
        for idea in all_ideas:
            self.cache.add(idea)
        
        return all_ideas[:num_candidates]
    
    def parse_response(self, response: str, num_candidates: int) -> List[Idea]:
        """Advanced parsing with multiple fallback strategies and validation"""
        ideas = []
        
        # Strategy 1: Extract JSON with code block detection
        json_patterns = [
            r'json\s*(.*?)\s*',
            r'\s*(.*?)\s*',
            r'json\s*(.*?)\s*',
            r'\[\s*\{.*?\}\s*\]'
        ]
        
        json_str = None
        for pattern in json_patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                json_str = match.group(1).strip()
                break
        
        if json_str:
            try:
                data = json.loads(json_str)
                if not isinstance(data, list):
                    data = [data]
                
                for item in data[:num_candidates]:
                    try:
                        # Validate with Pydantic
                        schema = IdeaSchema(**item)
                        idea = Idea.from_schema(schema)
                        
                        # Validate tech stack
                        if not idea.tech_stack:
                            idea.tech_stack = self._suggest_tech_stack(idea.category)
                        
                        # Check for emerging tech
                        if not any(tech in idea.description for tech in self.EMERGING_TECH):
                            idea.metadata['needs_tech_boost'] = True
                        
                        ideas.append(idea)
                    except ValidationError as e:
                        log.debug(f"Validation failed: {e}")
                        continue
                    except Exception as e:
                        log.debug(f"Failed to parse item: {e}")
                        continue
            except json.JSONDecodeError as e:
                log.warning(f"JSON decode failed: {e}")
        
        # Strategy 2: Structured text parsing with NLP
        if len(ideas) < num_candidates * 0.7:
            ideas.extend(self._parse_structured_text(response, num_candidates - len(ideas)))
        
        # Strategy 3: Semantic generation from keywords
        if len(ideas) < num_candidates:
            ideas.extend(self._generate_from_keywords(response, num_candidates - len(ideas)))
        
        # Strategy 4: Curated fallback
        if len(ideas) < num_candidates:
            curated = self.get_curated_ideas()
            needed = num_candidates - len(ideas)