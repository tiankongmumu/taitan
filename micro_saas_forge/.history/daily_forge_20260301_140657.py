import os
import sys
import json
import time
import random
import asyncio
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, Set, ClassVar, Union, Callable, AsyncGenerator
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
import re
import hashlib
from enum import Enum
from pathlib import Path
import traceback
from collections import defaultdict, Counter, deque
import uuid
from pydantic import BaseModel, Field, validator, ValidationError, create_model, ConfigDict
import aiohttp
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, retry_if_result, RetryCallState
import numpy as np
from scipy import stats, spatial
import pickle
import gzip
from functools import lru_cache, wraps, partial
from contextlib import asynccontextmanager, AsyncExitStack
import signal
from hashlib import md5, sha3_256
import orjson
import msgpack
from dataclasses_json import dataclass_json
import backoff
from typing import Literal, Annotated
import inspect
import zstandard as zstd
from sentence_transformers import SentenceTransformer
import faiss
from asyncio import Semaphore, Queue, Event, Lock
import heapq
from statistics import mean, median, stdev
import warnings
warnings.filterwarnings('ignore')

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
    BURST = "burst"

class GenerationStrategy(str, Enum):
    DIVERGENT = "divergent"
    CONVERGENT = "convergent"
    EVOLUTIONARY = "evolutionary"
    COMBINATORIAL = "combinatorial"

@dataclass_json
@dataclass
class IdeaMetrics:
    utility: float = field(default=0.0)
    uniqueness: float = field(default=0.0)
    seo: float = field(default=0.0)
    feasibility: float = field(default=0.0)
    virality: float = field(default=0.0)
    technical_debt: float = field(default=0.0)
    innovation_score: float = field(default=0.0)
    market_fit: float = field(default=0.0)
    developer_experience: float = field(default=0.0)
    
    @property
    def composite_score(self) -> float:
        weights = np.array([0.18, 0.15, 0.10, 0.15, 0.12, -0.10, 0.12, 0.08, 0.10])
        scores = np.array([
            self.utility, self.uniqueness, self.seo,
            self.feasibility, self.virality, self.technical_debt,
            self.innovation_score, self.market_fit, self.developer_experience
        ])
        scores_normalized = (scores - np.min(scores)) / (np.max(scores) - np.min(scores) + 1e-10)
        weighted = np.dot(weights, scores_normalized)
        return float(weighted * 100)
    
    def to_vector(self) -> np.ndarray:
        return np.array([
            self.utility, self.uniqueness, self.seo,
            self.feasibility, self.virality, self.technical_debt,
            self.innovation_score, self.market_fit, self.developer_experience
        ], dtype=np.float32)

class IdeaSchema(BaseModel):
    model_config = ConfigDict(extra='forbid', validate_assignment=True)
    
    name: str = Field(..., min_length=3, max_length=120, description="Unique project name")
    description: str = Field(..., min_length=15, max_length=500, description="Detailed description")
    category: str = Field(..., description="Primary category")
    subcategory: Optional[str] = Field(None, description="Optional subcategory")
    tech_stack: List[str] = Field(default_factory=list, max_items=12, description="Technology stack")
    target_audience: List[str] = Field(default_factory=lambda: ["developers"], description="Target users")
    complexity: Literal["simple", "moderate", "complex", "advanced"] = "moderate"
    generation_strategy: GenerationStrategy = GenerationStrategy.DIVERGENT
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: Set[str] = Field(default_factory=set)
    
    @validator('name')
    def clean_name(cls, v):
        v = re.sub(r'[^\w\s\-\.\:]', '', v)
        v = ' '.join(word.capitalize() for word in v.split())
        return v.strip()
    
    @validator('description')
    def clean_description(cls, v):
        v = v.strip()
        if v and v[-1] not in '.!?':
            v += '.'
        return v
    
    @validator('tech_stack')
    def validate_tech_stack(cls, v):
        seen = set()
        unique_list = []
        for tech in v:
            if tech not in seen:
                seen.add(tech)
                unique_list.append(tech)
        return unique_list[:12]
    
    @validator('tags')
    def validate_tags(cls, v):
        return {tag.lower().strip() for tag in v if tag.strip()}

@dataclass_json
@dataclass
class Idea:
    name: str
    description: str
    category: str
    subcategory: Optional[str] = None
    tech_stack: List[str] = field(default_factory=list)
    target_audience: List[str] = field(default_factory=lambda: ["developers"])
    complexity: str = "moderate"
    generation_strategy: GenerationStrategy = GenerationStrategy.DIVERGENT
    metrics: IdeaMetrics = field(default_factory=IdeaMetrics)
    verdict: Optional[Verdict] = None
    id: str = field(default_factory=lambda: sha3_256(f"{time.time_ns()}{random.random()}{os.urandom(16)}".encode()).hexdigest()[:14])
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    embeddings: Optional[np.ndarray] = None
    signature: str = field(default_factory=lambda: "")
    tags: Set[str] = field(default_factory=set)
    parent_id: Optional[str] = None
    generation_depth: int = 0
    version: int = 1
    
    def __post_init__(self):
        if not self.signature:
            self.signature = self._compute_signature()
        if not self.tags:
            self.tags = self._extract_tags()
    
    def _compute_signature(self) -> str:
        content = f"{self.name.lower()}{self.description.lower()}{self.category}{''.join(sorted(self.tech_stack))}"
        return sha3_256(content.encode()).hexdigest()
    
    def _extract_tags(self) -> Set[str]:
        tags = set()
        tags.update(re.findall(r'#(\w+)', self.description))
        tags.update([tech.lower().replace('.', '').replace('-', '') for tech in self.tech_stack[:3]])
        tags.add(self.complexity)
        tags.add(self.category.lower())
        return tags
    
    @property
    def weighted_score(self) -> float:
        return self.metrics.composite_score
    
    @property
    def priority(self) -> float:
        base = self.weighted_score
        multipliers = {
            "simple": 1.3,
            "moderate": 1.0,
            "complex": 0.85,
            "advanced": 0.7
        }
        strategy_multipliers = {
            GenerationStrategy.DIVERGENT: 1.2,
            GenerationStrategy.CONVERGENT: 1.0,
            GenerationStrategy.EVOLUTIONARY: 1.15,
            GenerationStrategy.COMBINATORIAL: 1.1
        }
        return base * multipliers.get(self.complexity, 1.0) * strategy_multipliers.get(self.generation_strategy, 1.0)
    
    @property
    def novelty_index(self) -> float:
        if self.embeddings is None:
            return 0.0
        return float(np.linalg.norm(self.embeddings))
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['weighted_score'] = self.weighted_score
        data['priority'] = self.priority
        data['novelty_index'] = self.novelty_index
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
            tags=schema.tags
        )
    
    def mutate(self, mutation_rate: float = 0.3) -> 'Idea':
        mutations = random.sample(['name', 'description', 'tech_stack', 'complexity', 'category'], 
                                 k=random.randint(1, 3))
        mutated = Idea(
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
            metadata=self.metadata.copy()
        )
        
        for mutation in mutations:
            if mutation == 'name' and random.random() < mutation_rate:
                mutated.name = f"{mutated.name} {random.choice(['Pro', 'AI', 'Next', 'Edge', 'Cloud', 'Studio', 'Labs'])}"
            elif mutation == 'description' and random.random() < mutation_rate:
                mutated.description = f"{mutated.description} Enhanced with {random.choice(['AI', 'real-time', 'blockchain', 'AR', 'quantum'])} capabilities."
            elif mutation == 'tech_stack' and random.random() < mutation_rate:
                if mutated.tech_stack and random.random() < 0.5:
                    mutated.tech_stack.pop(random.randrange(len(mutated.tech_stack)))
                mutated.tech_stack.append(random.choice([
                    "Next.js 15", "TypeScript 5.5", "Tailwind CSS v4", "Framer Motion 11",
                    "React Three Fiber", "WebGPU", "TensorFlow.js", "WebAssembly"
                ]))
            elif mutation == 'complexity' and random.random() < mutation_rate:
                mutated.complexity = random.choice(["simple", "moderate", "complex", "advanced"])
            elif mutation == 'category' and random.random() < mutation_rate:
                mutated.category = random.choice(IdeaGenerator.CATEGORIES)
        
        return mutated

class SemanticCache:
    def __init__(self, max_size: int = 5000, cache_dir: Optional[Path] = None, 
                 embedding_dim: int = 384, use_faiss: bool = True):
        self.max_size = max_size
        self.cache_dir = cache_dir or Path.home() / '.idea_semantic_cache_v2'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_dim = embedding_dim
        self.use_faiss = use_faiss
        
        self._cache: Dict[str, Idea] = {}
        self._access_queue: deque = deque()
        self._signature_index: Dict[str, str] = {}
        self._category_index: Dict[str, Set[str]] = defaultdict(set)
        self._tag_index: Dict[str, Set[str]] = defaultdict(set)
        self._embedding_model: Optional[SentenceTransformer] = None
        self._faiss_index: Optional[faiss.Index] = None
        self._id_to_faiss: Dict[str, int] = {}
        self._faiss_to_id: Dict[int, str] = {}
        self._faiss_counter = 0
        self._lock = Lock()
        
        self._load_cache()
        if self.use_faiss and self._cache:
            self._build_faiss_index()
    
    def _load_cache(self):
        cache_file = self.cache_dir / 'ideas.msgpack.zst'
        if cache_file.exists():
            try:
                dctx = zstd.ZstdDecompressor()
                with open(cache_file, 'rb') as f:
                    with dctx.stream_reader(f) as reader:
                        data = msgpack.unpack(reader, raw=False)
                
                for item in data:
                    idea = Idea.from_dict(item)
                    self._add_to_indexes(idea, skip_save=True)
                
                log.info(f"Loaded {len(self._cache)} cached ideas with semantic indexing")
            except Exception as e:
                log.error(f"Failed to load cache: {e}", exc_info=True)
                self._cache.clear()
    
    async def _save_cache_async(self):
        async with self._lock:
            self._save_cache()
    
    def _save_cache(self):
        cache_file = self.cache_dir / 'ideas.msgpack.zst'
        backup_file = self.cache_dir / f'ideas.backup.{int(time.time())}.msgpack.zst'
        
        try:
            if cache_file.exists():
                cache_file.rename(backup_file)
            
            data = [idea.to_dict() for idea in self._cache.values()]
            
            cctx = zstd.ZstdCompressor(level=3)
            with open(cache_file, 'wb') as f:
                with cctx.stream_writer(f) as compressor:
                    msgpack.pack(data, compressor)
            
            for backup in self.cache_dir.glob('ideas.backup.*.msgpack.zst'):
                if backup.stat().st_mtime < time.time() - 86400:
                    backup.unlink()
                    
        except Exception as e:
            log.error(f"Failed to save cache: {e}", exc_info=True)
    
    def _add_to_indexes(self, idea: Idea, skip_save: bool = False):
        if idea.signature in self._signature_index:
            existing_id = self._signature_index[idea.signature]
            if existing_id in self._access_queue:
                self._access_queue.remove(existing_id)
            self._access_queue.append(existing_id)
            return
        
        self._cache[idea.id] = idea
        self._access_queue.append(idea.id)
        self._signature_index[idea.signature] = idea.id
        self._category_index[idea.category].add(idea.id)
        
        for tag in idea.tags:
            self._tag_index[tag].add(idea.id)
        
        if self.use_faiss and idea.embeddings is not None:
            self._add_to_faiss(idea)
        
        if len(self._access_queue) > self.max_size:
            oldest_id = self._access_queue.popleft()
            self._remove_from_indexes(oldest_id)
        
        if not skip_save:
            asyncio.create_task(self._save_cache_async())
    
    def _add_to_faiss(self, idea: Idea):
        if self._faiss_index is None:
            self._faiss_index = faiss.IndexFlatIP(self.embedding_dim)
        
        embedding = idea.embeddings.reshape(1, -1).astype(np.float32)
        self._faiss_index.add(embedding)
        self._id_to_faiss[idea.id] = self._faiss_counter
        self._faiss_to_id[self._faiss_counter] = idea.id
        self._faiss_counter += 1
    
    def _remove_from_indexes(self, idea_id: str):
        if idea_id in self._cache:
            idea = self._cache[idea_id]
            del self._signature_index[idea.signature]
            self._category_index[idea.category].discard(idea_id)
            
            for tag in idea.tags:
                self._tag_index[tag].discard(idea_id)
            
            if self.use_faiss and idea_id in self._id_to_faiss:
                faiss_id = self._id_to_faiss[idea_id]
                del self._id_to_faiss[idea_id]
                del self._faiss_to_id[faiss_id]
            
            del self._cache[idea_id]
    
    def add(self, idea: Idea):
        self._add_to_indexes(idea)
    
    async def add_batch(self, ideas: List[Idea]):
        for idea in ideas:
            self._add_to_indexes(idea, skip_save=True)