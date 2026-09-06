# backend/app/services/retrieval.py
"""Hybrid retrieval service for BIS knowledge.
Implements:
* Vector similarity using sentence‑transformers embeddings stored in the DB (JSON list).
* Simple keyword matching (substring search) as a fallback.
* Optional metadata filtering (standard number, source ID, etc.).
The service is deliberately lightweight – it loads all chunks into memory for the demo.
In production you would replace this with a proper ANN index (e.g., pgvector
or an external vector store) and full‑text search.
"""
import logging
from typing import List, Tuple, Dict, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .embedding import embed_query
from .. import models

logger = logging.getLogger(__name__)

async def _load_chunks(session: AsyncSession) -> List[models.DocumentChunk]:
    """Load all chunks – demo implementation.
    Real‑world code should page or query a vector index.
    """
    result = await session.execute(select(models.DocumentChunk))
    return result.scalars().unique().all()

def _cosine_sim(a: List[float], b: List[float]) -> float:
    # Assume vectors are already L2‑normalized.
    return sum(x * y for x, y in zip(a, b))

async def hybrid_search(
    session: AsyncSession,
    query: str,
    top_k: int = 5,
    metadata_filter: Dict[str, Any] | None = None,
) -> List[Tuple[models.DocumentChunk, float]]:
    """Return top‑k chunks with a combined relevance score.

    Parameters
    ----------
    session: AsyncSession – DB session.
    query: str – user query.
    top_k: int – number of chunks to return.
    metadata_filter: optional dict with keys like ``standard_number`` or ``source_id``.
    """
    # 1️⃣ Embed the query
    query_vec = embed_query(query)

    # 2️⃣ Load chunks (demo)
    chunks = await _load_chunks(session)

    # 3️⃣ Compute vector similarity for each chunk that has an embedding
    vec_scores: List[Tuple[models.DocumentChunk, float]] = []
    for chunk in chunks:
        if not chunk.embedding:
            continue
        try:
            # Chunk embedding stored as JSON list → Python list
            chunk_vec = chunk.embedding  # type: ignore[arg-type]
            if isinstance(chunk_vec, str):
                chunk_vec = json.loads(chunk_vec)
            score = _cosine_sim(query_vec, chunk_vec)
            vec_scores.append((chunk, score))
        except Exception as exc:  # pragma: no cover – defensive
            logger.warning("Failed to score chunk %s: %s", chunk.id, exc)

    # 4️⃣ Keyword match (binary) – presence of the query substring in the chunk text
    combined: List[Tuple[models.DocumentChunk, float]] = []
    for chunk, vec_score in vec_scores:
        kw_match = 1.0 if query.lower() in (chunk.text or "").lower() else 0.0
        # Weighted combination – vector component has higher weight
        combined_score = 0.7 * vec_score + 0.3 * kw_match
        combined.append((chunk, combined_score))

    # 5️⃣ Apply metadata filter (simple post‑filter for demo)
    if metadata_filter:
        filtered = []
        for chunk, score in combined:
            keep = True
            # Example filters – expand as needed
            if "standard_number" in metadata_filter:
                # Chunk may be linked to a clause → clause → standard
                if not (chunk.clause and chunk.clause.standard and chunk.clause.standard.number == metadata_filter["standard_number"]):
                    keep = False
            if "source_id" in metadata_filter and chunk.document.source_id != metadata_filter["source_id"]:
                keep = False
            if keep:
                filtered.append((chunk, score))
        combined = filtered

    # 6️⃣ Sort and return top‑k
    combined.sort(key=lambda x: x[1], reverse=True)
    return combined[:top_k]
