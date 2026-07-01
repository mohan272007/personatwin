"""
memory/vector_store.py
------------------------
Thin wrapper around Qdrant for long-term semantic memory.

Two modes, controlled by env var QDRANT_URL:
  - Not set  -> embedded/local Qdrant, persisted to disk at ./qdrant_data
               (zero-setup, perfect for a same-day hackathon demo)
  - Set      -> connects to a real Qdrant server (e.g. the one started by
               docker-compose.yml), for a more "production" deployment.

Every point stored carries the user_id in its payload so semantic search
is always scoped to a single user's digital twin (multi-tenant safe).
"""

import os
import uuid
from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from memory.embeddings import embed_text, embedding_dim

COLLECTION_NAME = "persona_twin_memories"


class VectorStore:
    def __init__(self):
        qdrant_url = os.getenv("QDRANT_URL")
        if qdrant_url:
            self.client = QdrantClient(url=qdrant_url)
        else:
            self.client = QdrantClient(path="./qdrant_data")
        self._ensure_collection()

    def _ensure_collection(self):
        collections = [c.name for c in self.client.get_collections().collections]
        if COLLECTION_NAME not in collections:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=qmodels.VectorParams(
                    size=embedding_dim(),
                    distance=qmodels.Distance.COSINE,
                ),
            )

    def upsert_memory(
        self,
        memory_id: str,
        user_id: str,
        content: str,
        memory_type: str,
        created_at: str,
        importance: float = 0.5,
    ):
        vector = embed_text(content)
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                qmodels.PointStruct(
                    id=memory_id,
                    vector=vector.tolist(),
                    payload={
                        "user_id": user_id,
                        "content": content,
                        "memory_type": memory_type,
                        "created_at": created_at,
                        "importance": importance,
                    },
                )
            ],
        )

    def search(self, user_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        vector = embed_text(query)
        results = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector.tolist(),
            query_filter=qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="user_id", match=qmodels.MatchValue(value=user_id)
                    )
                ]
            ),
            limit=top_k,
        )
        return [
            {
                "id": str(r.id),
                "score": float(r.score),
                "content": r.payload.get("content", ""),
                "memory_type": r.payload.get("memory_type", "conversation"),
                "created_at": r.payload.get("created_at", ""),
            }
            for r in results
        ]

    def delete_user_memories(self, user_id: str):
        self.client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=qmodels.FilterSelector(
                filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="user_id", match=qmodels.MatchValue(value=user_id)
                        )
                    ]
                )
            ),
        )


# Singleton instance used across the app
vector_store = VectorStore()
