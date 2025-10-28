"""
Simple in-memory conversation memory and optional KBIndex backed by FAISS (or linear search fallback).
"""
from typing import List, Dict, Any, Optional
import numpy as np

try:
    import faiss
    _FAISS_AVAILABLE = True
except Exception:
    _FAISS_AVAILABLE = False

class InMemoryConversationMemory:
    def __init__(self, embedder=None):
        self.embedder = embedder
        self.items: List[Dict[str, Any]] = []

    def add_message(self, item: Dict[str, Any]):
        self.items.append(item)
        if len(self.items) > 200:
            self.items.pop(0)

    def find_relevant(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.items:
            return []
        embeddings = np.array([np.array(it["embedding"]) for it in self.items])
        q = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        E = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8)
        sims = (E @ q).astype(float)
        idx = np.argsort(-sims)[:top_k]
        return [{"score": float(sims[i]), "item": self.items[i]} for i in idx if sims[i] > 0.05]

class KBIndex:
    def __init__(self, items: List[Dict[str, Any]]):
        self.items = items
        self.embeddings = np.array([it["embedding"] for it in items])
        self._use_faiss = _FAISS_AVAILABLE
        if self._use_faiss:
            d = self.embeddings.shape[1]
            self.index = faiss.IndexFlatIP(d)
            self.index.add(self.embeddings.astype('float32'))

    def search_by_embedding(self, query_embedding: Any, top_k: int = 4) -> List[Dict[str, Any]]:
        q = np.array(query_embedding).astype('float32')
        if self._use_faiss:
            D, I = self.index.search(np.expand_dims(q, 0), top_k)
            results = []
            for score, i in zip(D[0], I[0]):
                if i < 0:
                    continue
                results.append({"score": float(score), "item": self.items[int(i)]})
            return results
        else:
            E = self.embeddings
            qn = q / (np.linalg.norm(q) + 1e-8)
            En = E / (np.linalg.norm(E, axis=1, keepdims=True) + 1e-8)
            sims = En @ qn
            idx = np.argsort(-sims)[:top_k]
            return [{"score": float(sims[i]), "item": self.items[i]} for i in idx]
