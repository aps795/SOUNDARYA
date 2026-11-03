"""Local Semantic Document Store and Retrieval-Augmented Generation (RAG) Engine."""

from __future__ import annotations
import os
import re
import math
import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from app.core.config import config

logger = logging.getLogger("Soundarya.Memory.RAG")


@dataclass
class DocumentChunk:
    doc_id: str
    filename: str
    chunk_index: int
    content: str
    vector: Dict[str, float]


class LocalVectorStore:
    """Zero-dependency, local TF-IDF cosine-similarity vector store for personal document search."""

    def __init__(self, storage_dir: Optional[Path] = None) -> None:
        self.storage_dir = storage_dir or config.vector_store_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "vector_index.json"
        self.chunks: List[DocumentChunk] = []
        self._load_index()

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r"\b[a-zA-Z0-9_\-\u0900-\u097F]{2,}\b", text.lower())
        stopwords = {
            "the", "and", "is", "in", "to", "of", "a", "an", "for", "on", "with",
            "hai", "ka", "ki", "ke", "ko", "se", "mein", "aur", "ye", "woh"
        }
        return [w for w in words if w not in stopwords]

    def _compute_vector(self, text: str) -> Dict[str, float]:
        tokens = self._tokenize(text)
        if not tokens:
            return {}
        counts: Dict[str, int] = {}
        for t in tokens:
            counts[t] = counts.get(t, 0) + 1
        
        # Calculate L2 normalized TF vector
        length = math.sqrt(sum(c * c for c in counts.values()))
        return {k: round(v / length, 4) for k, v in counts.items()}

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        dot_product = sum(vec1[k] * vec2[k] for k in vec1 if k in vec2)
        return dot_product

    def ingest_document(self, file_path: str | Path, chunk_size: int = 500) -> int:
        """Read a document, chunk it into passages, compute vectors, and store."""
        path = Path(file_path)
        if not path.exists():
            return 0

        text = path.read_text(encoding="utf-8", errors="replace")
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        doc_id = path.name

        # Remove previous chunks of this document
        self.chunks = [c for c in self.chunks if c.filename != doc_id]

        new_count = 0
        for idx, para in enumerate(paragraphs):
            if len(para) < 20:
                continue
            vec = self._compute_vector(para)
            chunk = DocumentChunk(
                doc_id=f"{doc_id}_{idx}",
                filename=doc_id,
                chunk_index=idx,
                content=para,
                vector=vec
            )
            self.chunks.append(chunk)
            new_count += 1

        self._save_index()
        logger.info(f"Ingested {new_count} chunks from '{doc_id}'.")
        return new_count

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Find most semantically relevant document passages for query."""
        q_vec = self._compute_vector(query)
        if not q_vec:
            return []

        scored = []
        for c in self.chunks:
            score = self._cosine_similarity(q_vec, c.vector)
            if score > 0.05:
                scored.append((score, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, c in scored[:top_k]:
            results.append({
                "score": round(score, 3),
                "filename": c.filename,
                "content": c.content,
                "chunk_index": c.chunk_index
            })
        return results

    def _save_index(self) -> None:
        data = [asdict(c) for c in self.chunks]
        self.index_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load_index(self) -> None:
        if self.index_file.exists():
            try:
                data = json.loads(self.index_file.read_text(encoding="utf-8"))
                self.chunks = [DocumentChunk(**item) for item in data]
            except Exception as e:
                logger.error(f"Failed to load vector index: {e}")
                self.chunks = []


# Global instance
vector_store = LocalVectorStore()
