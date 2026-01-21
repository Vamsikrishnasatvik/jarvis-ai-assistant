import numpy as np
from sentence_transformers import SentenceTransformer
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from .config import settings

class VectorStore:
    """Vector database for storing and retrieving knowledge"""
    
    def __init__(self):
        """Initialize vector store with embedding model"""
        print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # For production: Initialize Pinecone
        # Uncomment when you have Pinecone credentials
        # import pinecone
        # pinecone.init(
        #     api_key=settings.PINECONE_API_KEY,
        #     environment=settings.PINECONE_ENVIRONMENT
        # )
        # self.index = pinecone.Index(settings.PINECONE_INDEX_NAME)
        
        # For development: In-memory storage
        self.memory_store: List[Dict] = []
        print("Vector store initialized (in-memory mode)")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        embedding = self.embedder.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def add_knowledge(self, text: str, metadata: Optional[Dict] = None) -> str:
        """
        Add knowledge entry to vector store
        
        Args:
            text: Knowledge text to store
            metadata: Additional metadata
            
        Returns:
            entry_id: Unique identifier for the entry
        """
        # Generate unique ID
        entry_id = str(uuid.uuid4())
        
        # Generate embedding
        embedding = self.generate_embedding(text)
        
        # Create entry
        entry = {
            "id": entry_id,
            "text": text,
            "embedding": embedding,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in memory (for development)
        self.memory_store.append(entry)
        
        # For production: Store in Pinecone
        # self.index.upsert([
        #     (entry_id, embedding, {"text": text, **(metadata or {})})
        # ])
        
        print(f"Added knowledge entry: {entry_id}")
        return entry_id
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        a = np.array(vec1)
        b = np.array(vec2)
        
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(dot_product / (norm_a * norm_b))
    
    def search(self, query: str, top_k: int = 3, threshold: float = 0.3) -> List[Dict]:
        """
        Search for relevant knowledge entries
        
        Args:
            query: Search query
            top_k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of matching entries with scores
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        
        # For development: Search in memory
        results = []
        for entry in self.memory_store:
            similarity = self.cosine_similarity(query_embedding, entry["embedding"])
            
            if similarity >= threshold:
                results.append({
                    "id": entry["id"],
                    "text": entry["text"],
                    "score": similarity,
                    "metadata": entry["metadata"],
                    "timestamp": entry["timestamp"]
                })
        
        # Sort by score (descending) and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        top_results = results[:top_k]
        
        print(f"Search query: '{query}' - Found {len(top_results)} results")
        return top_results
        
        # For production: Use Pinecone
        # query_results = self.index.query(
        #     query_embedding,
        #     top_k=top_k,
        #     include_metadata=True
        # )
        # 
        # return [
        #     {
        #         "text": match["metadata"]["text"],
        #         "score": match["score"],
        #         "metadata": match["metadata"]
        #     }
        #     for match in query_results["matches"]
        #     if match["score"] >= threshold
        # ]
    
    def list_all(self) -> List[Dict]:
        """List all knowledge entries (without embeddings)"""
        return [
            {
                "id": entry["id"],
                "text": entry["text"],
                "metadata": entry["metadata"],
                "timestamp": entry["timestamp"]
            }
            for entry in self.memory_store
        ]
    
    def delete(self, entry_id: str) -> bool:
        """
        Delete a knowledge entry
        
        Args:
            entry_id: ID of entry to delete
            
        Returns:
            success: True if deleted, False if not found
        """
        # For development: Delete from memory
        initial_count = len(self.memory_store)
        self.memory_store = [e for e in self.memory_store if e["id"] != entry_id]
        deleted = len(self.memory_store) < initial_count
        
        # For production: Delete from Pinecone
        # self.index.delete([entry_id])
        
        if deleted:
            print(f"Deleted knowledge entry: {entry_id}")
        else:
            print(f"Entry not found: {entry_id}")
        
        return deleted
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        return {
            "total_entries": len(self.memory_store),
            "embedding_dimension": len(self.memory_store[0]["embedding"]) if self.memory_store else 0,
            "model": settings.EMBEDDING_MODEL
        }

# Global instance
vector_store = VectorStore()