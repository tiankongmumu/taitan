import os
import sys
import json
import time
import random
import asyncio
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, Set, ClassVar, Union, Callable, AsyncGenerator, Iterator, Literal, Annotated, get_args, get_origin, TypeAlias
from dataclasses import dataclass, asdict, field, replace
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor, Future, Executor
import re
import hashlib
from enum import Enum, auto
from pathlib import Path
import traceback
from collections import defaultdict, Counter, deque, OrderedDict
import uuid
from pydantic import BaseModel, Field, validator, ValidationError, create_model, ConfigDict, field_validator, model_validator, field_serializer
import aiohttp
from aiohttp import ClientSession, ClientTimeout, TCPConnector, ClientResponseError, ClientError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, retry_if_result, RetryCallState, before_sleep_log, wait_random_exponential
import numpy as np
from numpy.typing import NDArray
from scipy import stats, spatial
import pickle
import gzip
from functools import lru_cache, wraps, partial, cached_property, total_ordering
from contextlib import asynccontextmanager, AsyncExitStack, contextmanager, aclosing
import signal
from hashlib import md5, sha3_256, blake2b, sha256
import orjson
import msgpack
from dataclasses_json import dataclass_json, config
import backoff
import inspect
import zstandard as zstd
from sentence_transformers import SentenceTransformer
import faiss
from faiss import IndexFlatIP, IndexIDMap, IndexHNSWFlat, MetricType, IndexIVFFlat, IndexScalarQuantizer
from asyncio import Semaphore, Queue, Event, Lock, BoundedSemaphore, TaskGroup, CancelledError, TimeoutError as AsyncTimeoutError
import heapq
from statistics import mean, median, stdev, quantiles, fmean
import warnings
from itertools import chain, islice, combinations, product, batched
from math import log2, exp, sqrt, log10, erf
import gc
from weakref import WeakValueDictionary, WeakSet, ref
from abc import ABC, abstractmethod, abstractproperty
import dataclasses
from types import MappingProxyType
from decimal import Decimal, ROUND_HALF_UP
import secrets
from concurrent.futures import FIRST_COMPLETED, ALL_COMPLETED, wait as futures_wait

warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning)

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from forge_master import ForgeMaster
from logger import get_logger

log = get_logger("meta_architect_enhanced")

class Verdict(str, Enum):
    SHIP = "ship"
    MAYBE = "maybe"
    KILL = "kill"
    REFACTOR = "refactor"
    INCUBATE = "incubate"

class PerformanceProfile(str, Enum):
    LOW_LATENCY = "low_latency"
    HIGH_THROUGHPUT = "high_throughput"
    BALANCED = "balanced"
    BURST = "burst"
    OPTIMIZED = "optimized"
    EDGE_OPTIMIZED = "edge_optimized"
    REAL_TIME = "real_time"

class GenerationStrategy(str, Enum):
    DIVERGENT = "divergent"
    CONVERGENT = "convergent"
    EVOLUTIONARY = "evolutionary"
    COMBINATORIAL = "combinatorial"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"
    PARALLEL = "parallel"
    RECURSIVE = "recursive"
    TRANSFORMATIVE = "transformative"
    METAMORPHIC = "metamorphic"

class StylingFramework(str, Enum):
    TAILWIND = "tailwind"
    CSS_MODULES = "css_modules"
    STYLED_COMPONENTS = "styled_components"
    VANILLA_EXTRACT = "vanilla_extract"
    PANDA_CSS = "panda_css"
    STITCHES = "stitches"
    ZERO_RUNTIME = "zero_runtime"
    UNOCSS = "unocss"

class AnimationLibrary(str, Enum):
    FRAMER_MOTION = "framer_motion"
    AUTO_ANIMATE = "auto_animate"
    GSAP = "gsap"
    REACT_SPRING = "react_spring"
    NONE = "none"
    MOTION_ONE = "motion_one"
    LENIS = "lenis"
    THREE_JS = "three_js"

class StateManagement(str, Enum):
    REACT_CONTEXT = "react_context"
    ZUSTAND = "zustand"
    JOTAI = "jotai"
    VALTIO = "valtio"
    REDUX_TOOLKIT = "redux_toolkit"
    MOBX = "mobx"
    RECOIL = "recoil"
    XSTATE = "xstate"
    EFFECTOR = "effector"

class DataFetching(str, Enum):
    SWR = "swr"
    REACT_QUERY = "react_query"
    APOLLO = "apollo"
    URQL = "urql"
    RTK_QUERY = "rtk_query"
    GRAPHQL_REQUEST = "graphql_request"
    FETCH = "fetch"
    AXIOS = "axios"

@dataclass_json
@dataclass(frozen=True, slots=True, kw_only=True, order=True)
class IdeaMetrics:
    utility: float = field(default=0.0, metadata=config(ge=0.0, le=1.0, decimal_places=3))
    uniqueness: float = field(default=0.0, metadata=config(ge=0.0, le=1.0, decimal_places=3))
    seo: float = field(default=0.0, metadata=config(ge=0.0, le=1.0, decimal_places=3))
    feasibility: float = field(default=0.0, metadata=config(ge=0.0, le=1.0, decimal_places=3))
    virality: float = field(default=0.0, metadata=config(ge=0.0, le=1.0, decimal_places=3))
    technical_debt: float = field(default=0.0, metadata=config(ge=0.0, le=1.0, decimal_places=3))
    innovation_score: float = field(default=0.0, metadata=config(ge=0.0, le=1.0, decimal_places=3))
    market_fit: float = field(default=0.0, metadata=config(ge=0.0, le=1.0, decimal_places=3))
    developer_experience: float = field(default=0.0, metadata=config(ge=0.0, le=1.0, decimal_places=3))
    performance_score: float = field(default=0.0, metadata=config(ge=0.0, le=1.0, decimal_places=3))
    accessibility: float = field(default=0.0, metadata=config(ge=0.0, le=1.0, decimal_places=3))
    security: float = field(default=0.0, metadata=config(ge=0.0, le=1.0, decimal_places=3))
    scalability: float = field(default=0.0, metadata=config(ge=0.0, le=1.0, decimal_places=3))
    maintainability: float = field(default=0.0, metadata=config(ge=0.0, le=1.0, decimal_places=3))
    sustainability: float = field(default=0.0, metadata=config(ge=0.0, le=1.0, decimal_places=3))
    ethical_alignment: float = field(default=0.0, metadata=config(ge=0.0, le=1.0, decimal_places=3))
    
    _WEIGHTS: ClassVar[NDArray[np.float32]] = np.array([
        0.10, 0.09, 0.06, 0.10, 0.08, -0.09, 0.08, 0.07, 0.07, 
        0.06, 0.05, 0.05, 0.06, 0.04, 0.03, 0.03
    ], dtype=np.float32)
    
    _NORMALIZATION_EPSILON: ClassVar[float] = 1e-12
    
    @cached_property
    def composite_score(self) -> float:
        scores = np.array([
            self.utility, self.uniqueness, self.seo,
            self.feasibility, self.virality, self.technical_debt,
            self.innovation_score, self.market_fit, self.developer_experience,
            self.performance_score, self.accessibility, self.security, 
            self.scalability, self.maintainability, self.sustainability,
            self.ethical_alignment
        ], dtype=np.float32)
        
        min_val = np.min(scores)
        max_val = np.max(scores)
        range_val = max_val - min_val
        
        if range_val < self._NORMALIZATION_EPSILON:
            scores_normalized = np.zeros_like(scores)
        else:
            scores_normalized = (scores - min_val) / range_val
        
        weighted = np.dot(self._WEIGHTS, scores_normalized)
        sigmoid_score = 1.0 / (1.0 + np.exp(-weighted * 10))
        return float(np.clip(sigmoid_score * 100, 0.0, 100.0))
    
    def to_vector(self) -> NDArray[np.float32]:
        return np.array([
            self.utility, self.uniqueness, self.seo,
            self.feasibility, self.virality, self.technical_debt,
            self.innovation_score, self.market_fit, self.developer_experience,
            self.performance_score, self.accessibility, self.security, 
            self.scalability, self.maintainability, self.sustainability,
            self.ethical_alignment
        ], dtype=np.float32)
    
    def __add__(self, other: 'IdeaMetrics') -> 'IdeaMetrics':
        if not isinstance(other, IdeaMetrics):
            return NotImplemented
        fields = {f.name: getattr(self, f.name) + getattr(other, f.name) 
                 for f in dataclasses.fields(self)}
        return IdeaMetrics(**fields)
    
    def __sub__(self, other: 'IdeaMetrics') -> 'IdeaMetrics':
        if not isinstance(other, IdeaMetrics):
            return NotImplemented
        fields = {f.name: getattr(self, f.name) - getattr(other, f.name) 
                 for f in dataclasses.fields(self)}
        return IdeaMetrics(**fields)
    
    def __mul__(self, scalar: float) -> 'IdeaMetrics':
        fields = {f.name: getattr(self, f.name) * scalar 
                 for f in dataclasses.fields(self)}
        return IdeaMetrics(**fields)
    
    def __truediv__(self, scalar: float) -> 'IdeaMetrics':
        if abs(scalar) < self._NORMALIZATION_EPSILON:
            raise ZeroDivisionError("Cannot divide by zero")
        fields = {f.name: getattr(self, f.name) / scalar 
                 for f in dataclasses.fields(self)}
        return IdeaMetrics(**fields)
    
    def __lt__(self, other: 'IdeaMetrics') -> bool:
        return self.composite_score < other.composite_score
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IdeaMetrics):
            return NotImplemented
        return all(getattr(self, f.name) == getattr(other, f.name) 
                  for f in dataclasses.fields(self))
    
    @classmethod
    def random(cls, seed: Optional[int] = None, 
               bias: Optional[Dict[str, float]] = None) -> 'IdeaMetrics':
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        fields = {}
        bias = bias or {}
        
        for f in dataclasses.fields(cls):
            if f.name in bias:
                base = bias[f.name]
                jitter = random.uniform(-0.1, 0.1)
                fields[f.name] = np.clip(base + jitter, 0.0, 1.0)
            elif f.name == 'technical_debt':
                fields[f.name] = random.uniform(0.0, 0.3)
            elif f.name in ('security', 'accessibility', 'ethical_alignment'):
                fields[f.name] = random.uniform(0.6, 0.95)
            else:
                fields[f.name] = random.uniform(0.4, 0.95)
        
        return cls(**fields)
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'IdeaMetrics':
        valid_fields = {f.name for f in dataclasses.fields(cls)}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)
    
    def to_dict(self, precision: int = 4) -> Dict[str, float]:
        return {f.name: round(getattr(self, f.name), precision) 
                for f in dataclasses.fields(self)}

class IdeaSchema(BaseModel):
    model_config = ConfigDict(
        extra='forbid', 
        validate_assignment=True, 
        frozen=True, 
        str_strip_whitespace=True,
        str_min_length=1,
        use_enum_values=False,
        arbitrary_types_allowed=True,
        ser_json_timedelta='iso8601',
        ser_json_bytes='base64'
    )
    
    name: str = Field(
        ..., 
        min_length=3, 
        max_length=120, 
        description="Unique project name",
        examples=["NextJS AI Dashboard", "Real-time Collaboration Platform"]
    )
    description: str = Field(
        ..., 
        min_length=15, 
        max_length=1200, 
        description="Detailed description with key features",
        examples=["A modern dashboard with AI-powered insights..."]
    )
    category: str = Field(
        ..., 
        description="Primary category",
        min_length=2,
        max_length=50
    )
    subcategory: Optional[str] = Field(
        None, 
        description="Optional subcategory",
        min_length=2,
        max_length=50
    )
    tech_stack: List[str] = Field(
        default_factory=list, 
        max_items=25, 
        min_items=1,
        description="Technology stack with versions"
    )
    target_audience: List[str] = Field(
        default_factory=lambda: ["developers"], 
        min_items=1,
        description="Target users and personas"
    )
    complexity: Literal["simple", "moderate", "complex", "advanced", "expert"] = "moderate"
    generation_strategy: GenerationStrategy = Field(
        default=GenerationStrategy.ADAPTIVE,
        description="Strategy used for generation"
    )
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier"
    )
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Generation timestamp"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    tags: Set[str] = Field(
        default_factory=set,
        max_items=30,
        description="Searchable tags"
    )
    architecture: Literal[
        "monolith", "microservices", "serverless", "edge", 
        "hybrid", "jamstack", "isomorphic", "microfrontend", "event_driven"
    ] = "hybrid"
    performance_profile: PerformanceProfile = PerformanceProfile.OPTIMIZED
    nextjs_version: Literal["14", "15", "canary"] = "15"
    uses_app_router: bool = True
    uses_react_server_components: bool = True
    uses_partial_prerendering: bool = False
    uses_server_actions: bool = True
    uses_view_transitions: bool = False
    styling_framework: StylingFramework = StylingFramework.TAILWIND
    animation_library: AnimationLibrary = AnimationLibrary.FRAMER_MOTION
    state_management: List[StateManagement] = Field(
        default_factory=lambda: [StateManagement.REACT_CONTEXT],
        max_items=3,
        description="State management solutions"
    )
    data_fetching: List[DataFetching] = Field(
        default_factory=lambda: [DataFetching.SWR, DataFetching.REACT_QUERY],
        max_items=3,
        description="Data fetching strategies"
    )
    ui_library: Optional[str] = Field(
        None,
        description="UI component library",
        examples=["shadcn/ui", "MUI", "Chakra UI", "Radix UI", "Headless UI"]
    )
    analytics: List[str] = Field(
        default_factory=list,
        description="Analytics and monitoring tools"
    )
    deployment_target: List[str] = Field(
        default_factory=lambda: ["vercel"],
        description="Deployment platforms"
    )
    
    @field_validator('name')
    @classmethod
    def clean_name(cls, v: str) -> str:
        v = re.sub