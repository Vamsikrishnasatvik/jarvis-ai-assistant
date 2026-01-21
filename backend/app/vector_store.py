# app/vector_store.py

import uuid
from datetime import datetime
from typing import List, Dict, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from .config import settings


class VectorStore:
    """Vector database for storing and retrieving knowledge"""

    def __init__(self):
        print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.embedder = SentenceTransformer(settings.EMBEDDING_MODEL)

        self.use_pinecone = bool(settings.PINECONE_API_KEY)

        if self.use_pinecone:
            self._init_pinecone()
        else:
            self.memory_store: List[Dict] = []
            print("Vector store initialized (in-memory mode)")

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def _init_pinecone(self):
        from pinecone import Pinecone

        print("Initializing Pinecone vector store...")
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = pc.Index(settings.PINECONE_INDEX_NAME)

        print(
            f"Pinecone index connected: {settings.PINECONE_INDEX_NAME}"
        )

    # ------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------

    def generate_embedding(self, text: str) -> List[float]:
        embedding = self.embedder.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    # ------------------------------------------------------------------
    # Add
    # ------------------------------------------------------------------

    def add_knowledge(self, text: str, metadata: Optional[Dict] = None) -> str:
        entry_id = str(uuid.uuid4())
        embedding = self.generate_embedding(text)

        record = {
            "id": entry_id,
            "text": text,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        if self.use_pinecone:
            self.index.upsert(
                vectors=[
                    (
                        entry_id,
                        embedding,
                        {
                            "text": text,
                            **record["metadata"],
                            "timestamp": record["timestamp"],
                        },
                    )
                ]
            )
        else:
            record["embedding"] = embedding
            self.memory_store.append(record)

        print(f"Added knowledge entry: {entry_id}")
        return entry_id

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 3,
        threshold: float = 0.3,
    ) -> List[Dict]:
        query_embedding = self.generate_embedding(query)

        if self.use_pinecone:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
            )

            matches = []
            for match in results.matches:
                if match.score >= threshold:
                    matches.append(
                        {
                            "id": match.id,
                            "text": match.metadata.get("text", ""),
                            "score": match.score,
                            "metadata": match.metadata,
                            "timestamp": match.metadata.get("timestamp"),
                        }
                    )

            return matches

        # ---------------- In-memory fallback ----------------

        scored = []
        for entry in self.memory_store:
            score = self._cosine_similarity(
                query_embedding, entry["embedding"]
            )
            if score >= threshold:
                scored.append(
                    {
                        "id": entry["id"],
                        "text": entry["text"],
                        "score": score,
                        "metadata": entry["metadata"],
                        "timestamp": entry["timestamp"],
                    }
                )

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, entry_id: str) -> bool:
        if self.use_pinecone:
            self.index.delete(ids=[entry_id])
            print(f"Deleted Pinecone entry: {entry_id}")
            return True

        initial = len(self.memory_store)
        self.memory_store = [
            e for e in self.memory_store if e["id"] != entry_id
        ]
        deleted = len(self.memory_store) < initial

        if deleted:
            print(f"Deleted in-memory entry: {entry_id}")
        return deleted

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------

    def list_all(self) -> List[Dict]:
        if self.use_pinecone:
            # Pinecone does not support listing all vectors safely
            # This endpoint should be disabled or paginated in prod
            return []

        return [
            {
                "id": e["id"],
                "text": e["text"],
                "metadata": e["metadata"],
                "timestamp": e["timestamp"],
            }
            for e in self.memory_store
        ]

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def get_stats(self) -> Dict:
        if self.use_pinecone:
            stats = self.index.describe_index_stats()
            return {
                "backend": "pinecone",
                "dimension": stats.dimension,
                "total_vectors": stats.total_vector_count,
                "model": settings.EMBEDDING_MODEL,
            }

        return {
            "backend": "memory",
            "total_entries": len(self.memory_store),
            "dimension": (
                len(self.memory_store[0]["embedding"])
                if self.memory_store
                else 0
            ),
            "model": settings.EMBEDDING_MODEL,
        }

    # ------------------------------------------------------------------
    # Utils
    # ------------------------------------------------------------------

    def _cosine_similarity(
        self, a: List[float], b: List[float]
    ) -> float:
        a = np.array(a)
        b = np.array(b)
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        return float(np.dot(a, b) / denom) if denom else 0.0


# ----------------------------------------------------------------------
# Global instance (loaded once)
# ----------------------------------------------------------------------

vector_store = VectorStore()
