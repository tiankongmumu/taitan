import os
import sys
import json
import time
import random
import asyncio
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, Set, ClassVar, Union, Callable, AsyncGenerator, Iterator
from dataclasses import dataclass, asdict, field, replace
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor, Future
import re
import hashlib
from enum import Enum, auto
from pathlib import Path
import traceback
from collections import defaultdict, Counter, deque, OrderedDict
import uuid
from pydantic import BaseModel, Field, validator, ValidationError, create_model, ConfigDict, field_validator
import aiohttp
from aiohttp import ClientSession, ClientTimeout, TCPConnector, ClientResponseError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, retry_if_result, RetryCallState, before_sleep_log
import numpy as np
from numpy.typing import NDArray
from scipy import stats, spatial
import pickle
import gzip
from functools import lru_cache, wraps, partial, cached_property
from contextlib import asynccontextmanager, AsyncExitStack, contextmanager
import signal
from hashlib import md5, sha3_256, blake2b
import orjson
import msgpack
from dataclasses_json import dataclass_json, config
import backoff
from typing import Literal, Annotated, get_args, get_origin
import inspect
import zstandard as zstd
from sentence_transformers import SentenceTransformer
import faiss
from faiss import IndexFlatIP, IndexIDMap, IndexHNSWFlat, MetricType
from asyncio import Semaphore, Queue, Event, Lock, BoundedSemaphore, TaskGroup, CancelledError
import heapq
from statistics import mean, median, stdev, quantiles
import warnings
from itertools import chain, islice, combinations
from math import log2, exp
import gc
from weakref import WeakValueDictionary

warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from forge_master import ForgeMaster
from logger import get_logger

log = get_logger("daily")

class Verdict(str, Enum):
    SHIP = auto()
    MAYBE = auto()
    KILL = auto()

class PerformanceProfile(str, Enum):
    LOW_LATENCY = auto()
    HIGH_THROUGHPUT = auto()
    BALANCED = auto()
    BURST = auto()
    OPTIMIZED = auto()

class GenerationStrategy(str, Enum):
    DIVERGENT = auto()
    CONVERGENT = auto()
    EVOLUTIONARY = auto()
    COMBINATORIAL = auto()
    HYBRID = auto()

@dataclass_json
@dataclass(frozen=True, slots=True)
class IdeaMetrics:
    utility: float = field(default=0.0, metadata=config(ge=0.0, le=1.0))
    uniqueness: float = field(default=0.0, metadata=config(ge=0.0, le=1.0))
    seo: float = field(default=0.0, metadata=config(ge=0.0, le=1.0))
    feasibility: float = field(default=0.0, metadata=config(ge=0.0, le=1.0))
    virality: float = field(default=0.0, metadata=config(ge=0.0, le=1.0))
    technical_debt: float = field(default=0.0, metadata=config(ge=0.0, le=1.0))
    innovation_score: float = field(default=0.0, metadata=config(ge=0.0, le=1.0))
    market_fit: float = field(default=0.0, metadata=config(ge=0.0, le=1.0))
    developer_experience: float = field(default=0.0, metadata=config(ge=0.0, le=1.0))
    performance_score: float = field(default=0.0, metadata=config(ge=0.0, le=1.0))
    accessibility: float = field(default=0.0, metadata=config(ge=0.0, le=1.0))
    
    @cached_property
    def composite_score(self) -> float:
        weights = np.array([0.15, 0.12, 0.08, 0.12, 0.10, -0.12, 0.10, 0.08, 0.07, 0.06, 0.04])
        scores = np.array([
            self.utility, self.uniqueness, self.seo,
            self.feasibility, self.virality, self.technical_debt,
            self.innovation_score, self.market_fit, self.developer_experience,
            self.performance_score, self.accessibility
        ], dtype=np.float32)
        scores_normalized = (scores - np.min(scores)) / (np.max(scores) - np.min(scores) + 1e-10)
        weighted = np.dot(weights, scores_normalized)
        return float(np.clip(weighted * 100, 0.0, 100.0))
    
    def to_vector(self) -> NDArray[np.float32]:
        return np.array([
            self.utility, self.uniqueness, self.seo,
            self.feasibility, self.virality, self.technical_debt,
            self.innovation_score, self.market_fit, self.developer_experience,
            self.performance_score, self.accessibility
        ], dtype=np.float32)
    
    def __add__(self, other: 'IdeaMetrics') -> 'IdeaMetrics':
        fields = {f.name: getattr(self, f.name) + getattr(other, f.name) for f in self.__dataclass_fields__.values()}
        return IdeaMetrics(**fields)
    
    def __truediv__(self, scalar: float) -> 'IdeaMetrics':
        fields = {f.name: getattr(self, f.name) / scalar for f in self.__dataclass_fields__.values()}
        return IdeaMetrics(**fields)

class IdeaSchema(BaseModel):
    model_config = ConfigDict(extra='forbid', validate_assignment=True, frozen=True)
    
    name: str = Field(..., min_length=3, max_length=120, description="Unique project name")
    description: str = Field(..., min_length=15, max_length=500, description="Detailed description")
    category: str = Field(..., description="Primary category")
    subcategory: Optional[str] = Field(None, description="Optional subcategory")
    tech_stack: List[str] = Field(default_factory=list, max_items=15, description="Technology stack")
    target_audience: List[str] = Field(default_factory=lambda: ["developers"], description="Target users")
    complexity: Literal["simple", "moderate", "complex", "advanced", "expert"] = "moderate"
    generation_strategy: GenerationStrategy = GenerationStrategy.HYBRID
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: Set[str] = Field(default_factory=set)
    architecture: Literal["monolith", "microservices", "serverless", "edge", "hybrid"] = "monolith"
    
    @field_validator('name')
    @classmethod
    def clean_name(cls, v: str) -> str:
        v = re.sub(r'[^\w\s\-\.\:]', '', v)
        v = ' '.join(word.capitalize() for word in v.split())
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def clean_description(cls, v: str) -> str:
        v = v.strip()
        if v and v[-1] not in '.!?':
            v += '.'
        return v
    
    @field_validator('tech_stack')
    @classmethod
    def validate_tech_stack(cls, v: List[str]) -> List[str]:
        seen = set()
        unique_list = []
        for tech in v:
            normalized = tech.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_list.append(tech)
        return unique_list[:15]
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Set[str]) -> Set[str]:
        return {tag.lower().strip() for tag in v if tag.strip()}

@dataclass_json
@dataclass(frozen=False, slots=True)
class Idea:
    name: str
    description: str
    category: str
    subcategory: Optional[str] = None
    tech_stack: List[str] = field(default_factory=list)
    target_audience: List[str] = field(default_factory=lambda: ["developers"])
    complexity: str = "moderate"
    generation_strategy: GenerationStrategy = GenerationStrategy.HYBRID
    metrics: IdeaMetrics = field(default_factory=IdeaMetrics)
    verdict: Optional[Verdict] = None
    id: str = field(default_factory=lambda: blake2b(f"{time.time_ns()}{random.random()}{os.urandom(32)}".encode(), digest_size=10).hexdigest())
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    embeddings: Optional[NDArray[np.float32]] = None
    signature: str = field(default_factory=lambda: "")
    tags: Set[str] = field(default_factory=set)
    parent_id: Optional[str] = None
    generation_depth: int = 0
    version: int = 1
    architecture: str = "monolith"
    last_accessed: float = field(default_factory=time.monotonic)
    
    def __post_init__(self):
        object.__setattr__(self, 'last_accessed', time.monotonic())
        if not self.signature:
            object.__setattr__(self, 'signature', self._compute_signature())
        if not self.tags:
            object.__setattr__(self, 'tags', self._extract_tags())
    
    def _compute_signature(self) -> str:
        content = f"{self.name.lower()}{self.description.lower()}{self.category}{''.join(sorted(self.tech_stack))}{self.architecture}"
        return sha3_256(content.encode()).hexdigest()
    
    def _extract_tags(self) -> Set[str]:
        tags = set()
        tags.update(re.findall(r'#(\w+)', self.description))
        tags.update([tech.lower().replace('.', '').replace('-', '_') for tech in self.tech_stack[:4]])
        tags.add(self.complexity)
        tags.add(self.category.lower())
        tags.add(self.architecture)
        tags.update([aud.lower() for aud in self.target_audience[:2]])
        return tags
    
    @cached_property
    def weighted_score(self) -> float:
        return self.metrics.composite_score
    
    @cached_property
    def priority(self) -> float:
        base = self.weighted_score
        multipliers = {
            "simple": 1.4,
            "moderate": 1.0,
            "complex": 0.9,
            "advanced": 0.8,
            "expert": 0.75
        }
        strategy_multipliers = {
            GenerationStrategy.DIVERGENT: 1.25,
            GenerationStrategy.CONVERGENT: 1.0,
            GenerationStrategy.EVOLUTIONARY: 1.2,
            GenerationStrategy.COMBINATORIAL: 1.15,
            GenerationStrategy.HYBRID: 1.3
        }
        arch_multipliers = {
            "monolith": 1.0,
            "microservices": 1.1,
            "serverless": 1.15,
            "edge": 1.2,
            "hybrid": 1.05
        }
        return base * multipliers.get(self.complexity, 1.0) * strategy_multipliers.get(self.generation_strategy, 1.0) * arch_multipliers.get(self.architecture, 1.0)
    
    @cached_property
    def novelty_index(self) -> float:
        if self.embeddings is None:
            return 0.0
        return float(np.linalg.norm(self.embeddings))
    
    @cached_property
    def entropy_score(self) -> float:
        text = f"{self.name} {self.description}"
        char_freq = Counter(text)
        total = len(text)
        entropy = -sum((freq/total) * log2(freq/total) for freq in char_freq.values() if freq > 0)
        return float(entropy)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['weighted_score'] = self.weighted_score
        data['priority'] = self.priority
        data['novelty_index'] = self.novelty_index
        data['entropy_score'] = self.entropy_score
        if self.embeddings is not None:
            data['embeddings'] = self.embeddings.tolist()
        data['tags'] = list(self.tags)
        return data
    
    @classmethod
    def from_schema(cls, schema: IdeaSchema) -> 'Idea':
        return cls(
            name=schema.name,
            description=schema.description,
            category=schema.category,
            subcategory=schema.subcategory,
            tech_stack=schema.tech_stack,
            target_audience=schema.target_audience,
            complexity=schema.complexity,
            generation_strategy=schema.generation_strategy,
            id=schema.id,
            generated_at=schema.generated_at,
            metadata=schema.metadata,
            tags=schema.tags,
            architecture=schema.architecture
        )
    
    def mutate(self, mutation_rate: float = 0.25, temperature: float = 1.0) -> 'Idea':
        mutation_candidates = ['name', 'description', 'tech_stack', 'complexity', 'category', 'architecture', 'target_audience']
        weights = [0.15, 0.2, 0.25, 0.1, 0.1, 0.1, 0.1]
        adjusted_rate = mutation_rate * temperature
        
        num_mutations = np.random.binomial(len(mutation_candidates), adjusted_rate)
        if num_mutations == 0:
            num_mutations = 1
        
        mutations = random.choices(mutation_candidates, weights=weights, k=num_mutations)
        
        mutated = replace(
            self,
            name=self.name,
            description=self.description,
            category=self.category,
            subcategory=self.subcategory,
            tech_stack=self.tech_stack.copy(),
            target_audience=self.target_audience.copy(),
            complexity=self.complexity,
            generation_strategy=self.generation_strategy,
            metrics=IdeaMetrics(),
            parent_id=self.id,
            generation_depth=self.generation_depth + 1,
            version=self.version + 1,
            tags=self.tags.copy(),
            metadata=self.metadata.copy(),
            architecture=self.architecture,
            embeddings=None,
            signature=""
        )
        
        tech_enhancements = [
            "Next.js 15 (App Router)", "TypeScript 5.5+", "Tailwind CSS v4", "Framer Motion 11",
            "React Three Fiber", "WebGPU", "TensorFlow.js", "WebAssembly", "Rust/WASM",
            "GraphQL (Apollo)", "tRPC", "Prisma", "Drizzle ORM", "Supabase", "Clerk Auth",
            "Resend", "React Email", "Shadcn/ui", "Aceternity UI", "Magic UI"
        ]
        
        architecture_patterns = ["monolith", "microservices", "serverless", "edge", "hybrid"]
        audience_options = ["developers", "enterprise", "startups", "creators", "educators", "consumers"]
        
        for mutation in set(mutations):
            if mutation == 'name' and random.random() < adjusted_rate:
                suffixes = ['Pro', 'AI', 'Next', 'Edge', 'Cloud', 'Studio', 'Labs', 'X', 'OS', 'Hub']
                prefixes = ['Smart', 'Intelligent', 'Quantum', 'Neural', 'Hyper', 'Ultra']
                if random.random() > 0.5:
                    mutated.name = f"{random.choice(prefixes)} {mutated.name}"
                else:
                    mutated.name = f"{mutated.name} {random.choice(suffixes)}"
            elif mutation == 'description' and random.random() < adjusted_rate:
                enhancers = [
                    "Enhanced with AI/ML capabilities for intelligent automation.",
                    "Built with real-time collaboration and WebSocket integration.",
                    "Leverages edge computing for ultra-low latency performance.",
                    "Incorporates blockchain for decentralized verification.",
                    "Uses AR/VR for immersive user experiences.",
                    "Optimized for serverless deployment with auto-scaling.",
                    "Features advanced analytics and data visualization.",
                    "Includes comprehensive accessibility (a11y) compliance."
                ]
                mutated.description = f"{mutated.description} {random.choice(enhancers)}"
            elif mutation == 'tech_stack' and random.random() < adjusted_rate:
                if mutated.tech_stack and random.random() < 0.6:
                    remove_idx = random.randrange(len(mutated.tech_stack))
                    mutated.tech_stack.pop(remove_idx)
                additions = random.sample(tech_enhancements, k=random.randint(1, 3))
                mutated.tech_stack.extend