import os
import sys
import json
import time
import random
import asyncio
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, Set, ClassVar, Union, Callable, AsyncGenerator, Iterator, Literal, Annotated, get_args, get_origin
from dataclasses import dataclass, asdict, field, replace
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor, Future
import re
import hashlib
from enum import Enum, auto
from pathlib import Path
import traceback
from collections import defaultdict, Counter, deque, OrderedDict
import uuid
from pydantic import BaseModel, Field, validator, ValidationError, create_model, ConfigDict, field_validator, model_validator
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
import inspect
import zstandard as zstd
from sentence_transformers import SentenceTransformer
import faiss
from faiss import IndexFlatIP, IndexIDMap, IndexHNSWFlat, MetricType
from asyncio import Semaphore, Queue, Event, Lock, BoundedSemaphore, TaskGroup, CancelledError
import heapq
from statistics import mean, median, stdev, quantiles
import warnings
from itertools import chain, islice, combinations, product
from math import log2, exp, sqrt
import gc
from weakref import WeakValueDictionary, WeakSet
from abc import ABC, abstractmethod
import dataclasses

warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from forge_master import ForgeMaster
from logger import get_logger

log = get_logger("meta_architect")

class Verdict(str, Enum):
    SHIP = "ship"
    MAYBE = "maybe"
    KILL = "kill"

class PerformanceProfile(str, Enum):
    LOW_LATENCY = "low_latency"
    HIGH_THROUGHPUT = "high_throughput"
    BALANCED = "balanced"
    BURST = "burst"
    OPTIMIZED = "optimized"

class GenerationStrategy(str, Enum):
    DIVERGENT = "divergent"
    CONVERGENT = "convergent"
    EVOLUTIONARY = "evolutionary"
    COMBINATORIAL = "combinatorial"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"
    PARALLEL = "parallel"

@dataclass_json
@dataclass(frozen=True, slots=True, kw_only=True)
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
    security: float = field(default=0.0, metadata=config(ge=0.0, le=1.0))
    scalability: float = field(default=0.0, metadata=config(ge=0.0, le=1.0))
    
    @cached_property
    def composite_score(self) -> float:
        weights = np.array([0.12, 0.10, 0.07, 0.11, 0.09, -0.10, 0.09, 0.08, 0.07, 0.06, 0.04, 0.05, 0.06], dtype=np.float32)
        scores = np.array([
            self.utility, self.uniqueness, self.seo,
            self.feasibility, self.virality, self.technical_debt,
            self.innovation_score, self.market_fit, self.developer_experience,
            self.performance_score, self.accessibility, self.security, self.scalability
        ], dtype=np.float32)
        scores_normalized = (scores - np.min(scores)) / (np.max(scores) - np.min(scores) + 1e-10)
        weighted = np.dot(weights, scores_normalized)
        return float(np.clip(weighted * 100, 0.0, 100.0))
    
    def to_vector(self) -> NDArray[np.float32]:
        return np.array([
            self.utility, self.uniqueness, self.seo,
            self.feasibility, self.virality, self.technical_debt,
            self.innovation_score, self.market_fit, self.developer_experience,
            self.performance_score, self.accessibility, self.security, self.scalability
        ], dtype=np.float32)
    
    def __add__(self, other: 'IdeaMetrics') -> 'IdeaMetrics':
        fields = {f.name: getattr(self, f.name) + getattr(other, f.name) for f in dataclasses.fields(self)}
        return IdeaMetrics(**fields)
    
    def __truediv__(self, scalar: float) -> 'IdeaMetrics':
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        fields = {f.name: getattr(self, f.name) / scalar for f in dataclasses.fields(self)}
        return IdeaMetrics(**fields)
    
    @classmethod
    def random(cls, seed: Optional[int] = None) -> 'IdeaMetrics':
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        fields = {}
        for f in dataclasses.fields(cls):
            if f.name == 'technical_debt':
                fields[f.name] = random.uniform(0.0, 0.4)
            else:
                fields[f.name] = random.uniform(0.3, 0.95)
        return cls(**fields)

class IdeaSchema(BaseModel):
    model_config = ConfigDict(extra='forbid', validate_assignment=True, frozen=True, str_strip_whitespace=True)
    
    name: str = Field(..., min_length=3, max_length=120, description="Unique project name")
    description: str = Field(..., min_length=15, max_length=800, description="Detailed description")
    category: str = Field(..., description="Primary category")
    subcategory: Optional[str] = Field(None, description="Optional subcategory")
    tech_stack: List[str] = Field(default_factory=list, max_items=20, description="Technology stack")
    target_audience: List[str] = Field(default_factory=lambda: ["developers"], description="Target users")
    complexity: Literal["simple", "moderate", "complex", "advanced", "expert"] = "moderate"
    generation_strategy: GenerationStrategy = GenerationStrategy.ADAPTIVE
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:16])
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: Set[str] = Field(default_factory=set)
    architecture: Literal["monolith", "microservices", "serverless", "edge", "hybrid", "jamstack", "isomorphic"] = "hybrid"
    performance_profile: PerformanceProfile = PerformanceProfile.OPTIMIZED
    nextjs_version: Literal["14", "15"] = "15"
    uses_app_router: bool = True
    uses_react_server_components: bool = True
    uses_partial_prerendering: bool = False
    styling_framework: Literal["tailwind", "css_modules", "styled_components", "vanilla_extract", "panda_css"] = "tailwind"
    animation_library: Literal["framer_motion", "auto_animate", "gsap", "react_spring", "none"] = "framer_motion"
    state_management: List[str] = Field(default_factory=lambda: ["react_context"], description="State management solutions")
    data_fetching: List[str] = Field(default_factory=lambda: ["swr", "react_query"], description="Data fetching strategies")
    
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
        return unique_list[:20]
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Set[str]) -> Set[str]:
        return {tag.lower().strip().replace(' ', '_') for tag in v if tag.strip()}
    
    @field_validator('state_management', 'data_fetching')
    @classmethod
    def deduplicate_lists(cls, v: List[str]) -> List[str]:
        seen = set()
        return [x for x in v if not (x in seen or seen.add(x))]
    
    @model_validator(mode='after')
    def validate_tech_consistency(self) -> 'IdeaSchema':
        if self.nextjs_version == "15" and not self.uses_app_router:
            raise ValueError("Next.js 15 requires App Router")
        if self.uses_partial_prerendering and not self.uses_react_server_components:
            raise ValueError("Partial Prerendering requires React Server Components")
        return self

@dataclass_json
@dataclass(frozen=False, slots=True, kw_only=True)
class Idea:
    name: str
    description: str
    category: str
    subcategory: Optional[str] = None
    tech_stack: List[str] = field(default_factory=list)
    target_audience: List[str] = field(default_factory=lambda: ["developers"])
    complexity: str = "moderate"
    generation_strategy: GenerationStrategy = GenerationStrategy.ADAPTIVE
    metrics: IdeaMetrics = field(default_factory=IdeaMetrics.random)
    verdict: Optional[Verdict] = None
    id: str = field(default_factory=lambda: blake2b(f"{time.time_ns()}{random.random()}{os.urandom(32)}".encode(), digest_size=12).hexdigest())
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    embeddings: Optional[NDArray[np.float32]] = None
    signature: str = field(default_factory=lambda: "")
    tags: Set[str] = field(default_factory=set)
    parent_id: Optional[str] = None
    generation_depth: int = 0
    version: int = 1
    architecture: str = "hybrid"
    last_accessed: float = field(default_factory=time.monotonic)
    performance_profile: PerformanceProfile = PerformanceProfile.OPTIMIZED
    nextjs_version: str = "15"
    uses_app_router: bool = True
    uses_react_server_components: bool = True
    uses_partial_prerendering: bool = False
    styling_framework: str = "tailwind"
    animation_library: str = "framer_motion"
    state_management: List[str] = field(default_factory=lambda: ["react_context"])
    data_fetching: List[str] = field(default_factory=lambda: ["swr", "react_query"])
    mutation_history: List[Dict[str, Any]] = field(default_factory=list)
    similarity_score: float = 0.0
    
    def __post_init__(self):
        object.__setattr__(self, 'last_accessed', time.monotonic())
        if not self.signature:
            object.__setattr__(self, 'signature', self._compute_signature())
        if not self.tags:
            object.__setattr__(self, 'tags', self._extract_tags())
        if not self.metadata.get('created_at'):
            self.metadata['created_at'] = self.generated_at
    
    def _compute_signature(self) -> str:
        content = f"{self.name.lower()}{self.description.lower()}{self.category}{''.join(sorted(self.tech_stack))}{self.architecture}{self.nextjs_version}{self.styling_framework}"
        return sha3_256(content.encode(), usedforsecurity=False).hexdigest()
    
    def _extract_tags(self) -> Set[str]:
        tags = set()
        tags.update(re.findall(r'#(\w+)', self.description))
        tags.update([tech.lower().replace('.', '').replace('-', '_') for tech in self.tech_stack[:5]])
        tags.add(self.complexity)
        tags.add(self.category.lower().replace(' ', '_'))
        tags.add(self.architecture)
        tags.add(f"nextjs_{self.nextjs_version}")
        tags.add(self.styling_framework)
        tags.add(self.animation_library)
        tags.update([aud.lower().replace(' ', '_') for aud in self.target_audience[:3]])
        tags.add(self.performance_profile.value)
        return tags
    
    @cached_property
    def weighted_score(self) -> float:
        return self.metrics.composite_score
    
    @cached_property
    def priority(self) -> float:
        base = self.weighted_score
        multipliers = {
            "simple": 1.5,
            "moderate": 1.0,
            "complex": 0.9,
            "advanced": 0.85,
            "expert": 0.8
        }
        strategy_multipliers = {
            GenerationStrategy.DIVERGENT: 1.3,
            GenerationStrategy.CONVERGENT: 1.0,
            GenerationStrategy.EVOLUTIONARY: 1.25,
            GenerationStrategy.COMBINATORIAL: 1.2,
            GenerationStrategy.HYBRID: 1.35,
            GenerationStrategy.ADAPTIVE: 1.4,
            GenerationStrategy.PARALLEL: 1.3
        }
        arch_multipliers = {
            "monolith": 1.0,
            "microservices": 1.15,
            "serverless": 1.25,
            "edge": 1.3,
            "hybrid": 1.2,
            "jamstack": 1.25,
            "isomorphic": 1.35
        }
        perf_multipliers = {
            PerformanceProfile.LOW_LATENCY: 1.2,
            PerformanceProfile.HIGH_THROUGHPUT: 1.1,
            PerformanceProfile.BALANCED: 1.0,
            PerformanceProfile.BURST: 1.15,
            PerformanceProfile.OPTIMIZED: 1.25
        }
        nextjs_multiplier = 1.1 if self.nextjs_version == "15" else 1.0
        rsc_multiplier = 1.15 if self.uses_react_server_components else 1.0
        ppr_multiplier = 1.2 if self.uses_partial_prerendering else 1.0
        
        return (base * 
                multipliers.get(self.complexity, 1.0) * 
                strategy_multipliers.get(self.generation_strategy, 1.0) * 
                arch_multipliers.get(self.architecture, 1.0) * 
                perf_multipliers.get(self.performance_profile, 1.0) * 
                nextjs_multiplier * 
                rsc_multiplier * 
                ppr_multiplier)
    
    @cached_property
    def novelty_index(self) -> float:
        if self.embeddings is None:
            return 0.0