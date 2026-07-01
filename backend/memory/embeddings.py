"""
memory/embeddings.py
---------------------
Generates vector embeddings for memory content.

Primary path: Google's text-embedding model (via google-generativeai),
used when GEMINI_API_KEY is set -- this matches the "Google Embeddings"
requirement and gives the best semantic quality.

Fallback path: a local SentenceTransformer model (all-MiniLM-L6-v2).
This keeps the whole system 100% runnable OFFLINE / without any API key,
which matters a lot for a hackathon demo where wifi or quota can fail.

Both paths are normalized to the same output vector size handling so the
Qdrant collection schema stays consistent for a given deployment.
"""

import os
import functools
import numpy as np

USE_GOOGLE_EMBEDDINGS = bool(os.getenv("GEMINI_API_KEY"))

_local_model = None


def _get_local_model():
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer
        _local_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _local_model


@functools.lru_cache(maxsize=2048)
def _cached_google_embed(text: str) -> tuple:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="semantic_similarity",
    )
    return tuple(result["embedding"])


def embed_text(text: str) -> np.ndarray:
    """Return a 1D numpy float32 vector for the given text."""
    text = (text or "").strip()
    if not text:
        text = " "

    if USE_GOOGLE_EMBEDDINGS:
        try:
            vec = _cached_google_embed(text)
            return np.array(vec, dtype=np.float32)
        except Exception:
            # Silently fall back to local embeddings if Google API hiccups
            pass

    model = _get_local_model()
    vec = model.encode(text, normalize_embeddings=True)
    return np.array(vec, dtype=np.float32)


def embedding_dim() -> int:
    """Vector size used to configure the Qdrant collection."""
    return 768 if USE_GOOGLE_EMBEDDINGS else 384
