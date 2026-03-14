import os
import sys
import json
import time
import random
import asyncio
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, Set, ClassVar, Union
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
import re
import hashlib
from enum import Enum
from pathlib import Path
import traceback
from collections import defaultdict, Counter, deque
import uuid
from pydantic import BaseModel, Field, validator, ValidationError, create_model
import aiohttp
from aiohttp import ClientSession, ClientTimeout
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, retry_if_result
import numpy as np
from scipy import stats
import pickle
import gzip
from functools import lru_cache, wraps
from contextlib import asynccontextmanager
import signal
from hashlib import md5
import orjson
import msgpack
from dataclasses_json import dataclass_json
import backoff
from typing import Literal
import inspect

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from forge_master import ForgeMaster
from logger import get_logger

log = get_logger("daily")

class Verdict(str, Enum):
    SHIP = "SHIP"
    MAYBE = "MAYBE"
    KILL = "KILL"

class PerformanceProfile(str, Enum):
    LOW_LATENCY = "low_latency"
    HIGH_THROUGHPUT = "high_throughput"
    BALANCED = "balanced"

@dataclass_json
@dataclass
class IdeaMetrics:
    utility: int = field(default=0)
    uniqueness: int = field(default=0)
    seo: int = field(default=0)
    feasibility: int = field(default=0)
    virality: int = field(default=0)
    technical_debt: int = field(default=0)
    
    @property
    def composite_score(self) -> float:
        weights = np.array([0.25, 0.2, 0.15, 0.2, 0.1, 0.1])
        scores = np.array([self.utility, self.uniqueness, self.seo, 
                          self.feasibility, self.virality, -self.technical_debt])
        normalized = (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)
        return float(np.dot(weights, normalized) * 100)

class IdeaSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=120)
    description: str = Field(..., min_length=15, max_length=280)
    category: str
    tech_stack: List[str] = Field(default_factory=list)
    target_audience: List[str] = Field(default_factory=lambda: ["developers"])
    complexity: Literal["simple", "moderate", "complex"] = "moderate"
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
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
    
    @validator('tech_stack')
    def validate_tech_stack(cls, v):
        return list(dict.fromkeys(v))[:8]

@dataclass_json
@dataclass
class Idea:
    name: str
    description: str
    category: str
    tech_stack: List[str] = field(default_factory=list)
    target_audience: List[str] = field(default_factory=lambda: ["developers"])
    complexity: str = "moderate"
    metrics: IdeaMetrics = field(default_factory=IdeaMetrics)
    verdict: Optional[Verdict] = None
    id: str = field(default_factory=lambda: hashlib.sha3_256(f"{time.time_ns()}{random.random()}".encode()).hexdigest()[:10])
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    embeddings: Optional[np.ndarray] = None
    signature: str = field(default_factory=lambda: "")
    
    def __post_init__(self):
        if not self.signature:
            self.signature = self._compute_signature()
    
    def _compute_signature(self) -> str:
        content = f"{self.name.lower()}{self.description.lower()}{self.category}"
        return md5(content.encode()).hexdigest()
    
    @property
    def weighted_score(self) -> float:
        return self.metrics.composite_score
    
    @property
    def priority(self) -> float:
        base = self.weighted_score
        multipliers = {
            "simple": 1.2,
            "moderate": 1.0,
            "complex": 0.8
        }
        return base * multipliers.get(self.complexity, 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['weighted_score'] = self.weighted_score
        data['priority'] = self.priority
        if self.embeddings is not None:
            data['embeddings'] = self.embeddings.tolist()
        return data
    
    @classmethod
    def from_schema(cls, schema: IdeaSchema) -> 'Idea':
        return cls(
            name=schema.name,
            description=schema.description,
            category=schema.category,
            tech_stack=schema.tech_stack,
            target_audience=schema.target_audience,
            complexity=schema.complexity,
            id=schema.id,
            generated_at=schema.generated_at,
            metadata=schema.metadata
        )

class SemanticCache:
    def __init__(self, max_size: int = 2000, cache_dir: Optional[Path] = None, 
                 embedding_dim: int = 384):
        self.max_size = max_size
        self.cache_dir = cache_dir or Path.home() / '.idea_semantic_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_dim = embedding_dim
        self._cache: Dict[str, Idea] = {}
        self._access_queue: deque = deque()
        self._signature_index: Dict[str, str] = {}
        self._category_index: Dict[str, Set[str]] = defaultdict(set)
        self._embeddings: Optional[np.ndarray] = None
        self._load_cache()
    
    def _load_cache(self):
        cache_file = self.cache_dir / 'ideas.msgpack'
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    data = msgpack.unpack(f, raw=False)
                    for item in data:
                        idea = Idea.from_dict(item)
                        self._add_to_indexes(idea)
                log.info(f"Loaded {len(self._cache)} cached ideas with semantic indexing")
            except Exception as e:
                log.warning(f"Failed to load cache: {e}")
                self._cache.clear()
    
    def _save_cache(self):
        cache_file = self.cache_dir / 'ideas.msgpack'
        try:
            data = [idea.to_dict() for idea in self._cache.values()]
            with open(cache_file, 'wb') as f:
                msgpack.pack(data, f)
        except Exception as e:
            log.warning(f"Failed to save cache: {e}")
    
    def _add_to_indexes(self, idea: Idea):
        self._cache[idea.id] = idea
        self._access_queue.append(idea.id)
        self._signature_index[idea.signature] = idea.id
        self._category_index[idea.category].add(idea.id)
        
        if len(self._access_queue) > self.max_size:
            oldest_id = self._access_queue.popleft()
            self._remove_from_indexes(oldest_id)
    
    def _remove_from_indexes(self, idea_id: str):
        if idea_id in self._cache:
            idea = self._cache[idea_id]
            del self._signature_index[idea.signature]
            self._category_index[idea.category].discard(idea_id)
            del self._cache[idea_id]
    
    def add(self, idea: Idea):
        if idea.signature in self._signature_index:
            existing_id = self._signature_index[idea.signature]
            self._access_queue.remove(existing_id)
            self._access_queue.append(existing_id)
            return
        
        self._add_to_indexes(idea)
        self._save_cache()
    
    def get_similar(self, idea: Idea, threshold: float = 0.75, 
                   max_results: int = 10) -> List[Idea]:
        similar = []
        for cached in self._cache.values():
            if cached.category != idea.category:
                continue
            
            name_sim = self._jaccard_similarity(idea.name, cached.name)
            desc_sim = self._jaccard_similarity(idea.description, cached.description)
            tech_sim = len(set(idea.tech_stack) & set(cached.tech_stack)) / max(len(set(idea.tech_stack) | set(cached.tech_stack)), 1)
            
            composite_sim = (name_sim * 0.4 + desc_sim * 0.4 + tech_sim * 0.2)
            if composite_sim > threshold:
                similar.append((composite_sim, cached))
        
        similar.sort(key=lambda x: x[0], reverse=True)
        return [idea for _, idea in similar[:max_results]]
    
    def _jaccard_similarity(self, a: str, b: str) -> float:
        set_a = set(a.lower().split())
        set_b = set(b.lower().split())
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return intersection / union if union > 0 else 0
    
    def get_by_category(self, category: str, limit: int = 20) -> List[Idea]:
        ids = list(self._category_index.get(category, set()))[:limit]
        return [self._cache[idea_id] for idea_id in ids if idea_id in self._cache]
    
    def clear(self):
        self._cache.clear()
        self._access_queue.clear()
        self._signature_index.clear()
        self._category_index.clear()
        self._save_cache()

class AsyncRateLimiter:
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()
    
    async def acquire(self):
        now = time.time()
        while self.calls and self.calls[0] <= now - self.period:
            self.calls.popleft()
        
        if len(self.calls) >= self.max_calls:
            sleep_time = self.calls[0] + self.period - now
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                now = time.time()
        
        self.calls.append(now)

class IdeaGenerator:
    CATEGORIES: ClassVar[List[str]] = [
        "Code", "Data", "API", "Design", "Text", "Security", 
        "DevOps", "Productivity", "Game", "AI", "Web3", "Mobile", 
        "Cloud", "MLOps", "Edge", "IoT", "AR/VR", "Quantum", "Blockchain",
        "SaaS", "Open Source", "Developer Tools", "Low Code", "No Code"
    ]
    
    TECH_STACKS: ClassVar[Dict[str, List[str]]] = {
        "Code": ["Next.js 15", "TypeScript 5.5", "Tailwind CSS v4", "Framer Motion 11", 
                 "WebAssembly", "Bun", "Turbopack", "Vite 5", "SWC", "Rome", "Biome"],
        "Game": ["React Three Fiber 9", "Phaser 4", "Babylon.js 7", "WebGPU", 
                 "Howler.js 3", "Tone.js", "PixiJS 7", "PlayCanvas", "Godot Web"],
        "AI": ["TensorFlow.js 4", "OpenAI API", "LangChain.js", "WebNN", 
               "Transformers.js", "Vercel AI SDK", "Hugging Face.js", "LlamaIndex", "CrewAI"],
        "Web3": ["Ethers.js 6", "viem 2", "WalletConnect 3", "IPFS", 
                 "Solidity 0.8", "Hardhat", "Foundry", "The Graph", "Ceramic"],
        "Design": ["Figma API", "GSAP 3", "Three.js r165", "CanvasKit", 
                   "Motion Canvas", "Lottie", "Spline", "Rive", "Framer"],
        "Edge": ["Cloudflare Workers", "Vercel Edge Functions", "Deno Deploy", 
                 "Bun.serve", "Fastly Compute", "Netlify Edge", "Supabase Edge"],
        "Mobile": ["React Native 0.74", "Expo 50", "Capacitor 5", "NativeWind", 
                   "Reanimated 3", "Tamagui", "Solito", "React Native Skia"],
        "AR/VR": ["Three.js XR", "WebXR", "A-Frame", "8th Wall", 
                  "Spark AR", "Lens Studio", "Amazon Sumerian"],
        "Quantum": ["Qiskit.js", "Cirq", "PennyLane", "Strawberry Fields", "ProjectQ"]
    }
    
    EMERGING_TECH: ClassVar[List[str]] = [
        "WebGPU", "WebAssembly 2.0", "WebNN", "WebTransport", 
        "WebCodecs", "WebHID", "WebSerial", "WebUSB", "WebBluetooth",
        "WebLocks API", "Web Share API", "Web Authentication API",
        "View Transitions API", "CSS Nesting", "Container Queries",
        "Scroll-driven Animations", "Popover API", "Anchor Positioning"
    ]
    
    STYLE_PROMPTS: ClassVar[Dict[str, str]] = {
        "innovative": "Focus on groundbreaking, never-before-seen concepts that push technical boundaries with novel interactions.",
        "practical": "Focus on immediately useful tools that solve real developer pain points with elegant solutions.",
        "viral": "Focus on highly shareable, addictive experiences with strong network effects and social hooks.",
        "technical": "Focus on demonstrating cutting-edge web platform APIs and performance optimizations with benchmarks.",
        "minimal": "Focus on elegant, single-purpose tools with beautiful interfaces and zero configuration.",
        "enterprise": "Focus on scalable, secure solutions with enterprise-grade features and compliance."
    }
    
    def __init__(self, cache: Optional[SemanticCache] = None, 
                 performance_profile: PerformanceProfile = PerformanceProfile.BALANCED):
        self.cache = cache or SemanticCache()
        self.llm_client = LLMClient()
        self.rate_limiter = AsyncRateLimiter(max_calls=30, period=60)
        self.performance_profile = performance_profile
        self.trends = {}
        self._trends_fetched_at = 0
        self._trends_ttl = 3600
        
        self._batch_size = {
            PerformanceProfile.LOW_LATENCY: 2,
            PerformanceProfile.HIGH_THROUGHPUT: 8,
            PerformanceProfile.BALANCED: 5
        }[performance_profile]
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError, ConnectionError))
    )
    async def _fetch_tech_trends(self) -> Dict[str, Any]:
        current_time = time.time()
        if current_time - self._trends_fetched_at < self._trends_ttl and self.trends:
            return self.trends
        
        async with ClientSession(timeout=ClientTimeout(total=10)) as session:
            trends = {
                "frontend": "React Server Components, Partial Prerendering, View Transitions API, CSS Nesting, React Compiler",
                "animations": "Framer Motion 11, Spring physics with inertia, Gesture-driven interfaces, Scroll-driven animations, Motion One",
                "styling": "Tailwind CSS v4 with arbitrary variants, CSS Cascade Layers, Container Queries, :has() selector, CSS Anchor Positioning",
                "ai": "LLM fine-tuning with LoRA, Multi-modal RAG, AI agents with tool use, On-device inference, Mixture of Experts",
                "gaming": "Procedural generation with ML, WebGPU compute shaders, Physics-based animations, Spatial audio, Real-time ray tracing",
                "edge": "Edge config, Edge middleware, Edge databases, Edge AI inference, Edge KV storage",
                "ar_vr": "WebXR with hand tracking, Markerless AR, Spatial anchors, Passthrough AR, Haptic feedback",
                "performance": "Islands architecture, React Server Components, Streaming SSR, Progressive Hydration, Code Splitting"
            }
            
            self.trends = trends
            self._trend