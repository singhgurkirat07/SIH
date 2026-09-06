# backend/app/services/embedding.py
"""Embedding service – loads a sentence‑transformers model and provides
vectorisation of raw text.
We keep the implementation deliberately lightweight; the model can be swapped
via the ``EMBEDDING_MODEL`` env variable.
"""
import os
from typing import List

from sentence_transformers import SentenceTransformer
import numpy as np

_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
_model = SentenceTransformer(_MODEL_NAME)

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Return a list of embedding vectors for the given texts.
    The result is a list of plain Python ``float`` lists – suitable for JSON
    storage or direct similarity computation.
    """
    embeddings = _model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    # Ensure they are plain lists (not numpy arrays) for JSON‑serialisation.
    return embeddings.tolist()

def embed_query(query: str) -> List[float]:
    """Embed a single query string and return a plain list vector."""
    return embed_texts([query])[0]
