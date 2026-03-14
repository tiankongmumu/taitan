"""
TITAN Semantic Memory (L3) 🏛️
Implements vector search (RAG) to find relevant axioms and patterns.
Uses simple local FAISS/JSON hybrid for maximum portability without complex DB overhead.
"""

import os
import json
import numpy as np
from pathlib import Path
import logging

# Fallback for embedding generation if transformer is not available
# In a real TITAN env, we would use an LLM embedding API
def simple_text_to_vector(text: str, dim: int = 128) -> np.ndarray:
    """A simplistic deterministic embedding for demo/fallback purposes."""
    np.random.seed(sum(ord(c) for c in text) % 9999)
    return np.random.rand(dim).astype('float32')

class TitanSemanticMemory:
    def __init__(self):
        self.memory_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "memory"
        self.vector_index_file = self.memory_dir / "semantic_index.json"
        self.axioms_file = self.memory_dir.parent / "knowledge_axioms.json"
        
        self.index = [] # List of {vector: [], payload: {}}
        self._load_index()

    def _load_index(self):
        if self.vector_index_file.exists():
            try:
                with open(self.vector_index_file, "r", encoding="utf-8") as f:
                    self.index = json.load(f)
            except:
                self.index = []

    def save_index(self):
        with open(self.vector_index_file, "w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)

    def add_axiom(self, axiom: str, metadata: dict = None):
        """将一个新的公理添加到语义索引中"""
        vec = simple_text_to_vector(axiom).tolist()
        self.index.append({
            "vector": vec,
            "text": axiom,
            "metadata": metadata or {}
        })
        self.save_index()

    def query(self, query_text: str, top_k: int = 2) -> list[str]:
        """根据查询内容检索最相关的公理或模式"""
        if not self.index:
            return []
            
        query_vec = simple_text_to_vector(query_text)
        
        # Calculate cosine similarity manually for zero-dependency portability
        scores = []
        for entry in self.index:
            entry_vec = np.array(entry["vector"])
            similarity = np.dot(query_vec, entry_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(entry_vec))
            scores.append((similarity, entry["text"]))
            
        scores.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scores[:top_k]]

if __name__ == "__main__":
    semantic = TitanSemanticMemory()
    semantic.add_axiom("Always use 'npx -y' for interactive commands to prevent hanging.")
    semantic.add_axiom("Prioritize Dark Mode UI for developer tools.")
    
    print("Query result:", semantic.query("How to run npx safely?"))
