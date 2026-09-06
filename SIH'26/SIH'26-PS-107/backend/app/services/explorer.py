# backend/app/services/explorer.py
"""Service for Standards Explorer and Evidence Explorer.
Handles searching for standards, fetching details, and constructing evidence chains.
"""
from typing import List, Optional
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .. import models
from .retrieval import hybrid_search

async def search_standards(
    session: AsyncSession,
    query: str,
    top_k: int = 20
) -> List[models.Standard]:
    """Search for standards by number, title, or semantic text in clauses.
    For simplicity, we do a basic keyword match on number/title, and if needed,
    can combine with semantic search from `hybrid_search`.
    """
    keyword = f"%{query}%"
    stmt = select(models.Standard).where(
        or_(
            models.Standard.number.ilike(keyword),
            models.Standard.title.ilike(keyword)
        )
    ).limit(top_k)
    result = await session.execute(stmt)
    standards = result.scalars().unique().all()
    
    # If not enough results, we could fallback to semantic search on DocumentChunks
    # and map them back to standards. We will keep it simple for now.
    return standards

async def get_standard_details(
    session: AsyncSession,
    standard_id: int
) -> Optional[models.Standard]:
    """Retrieve standard with its clauses and related entities."""
    stmt = select(models.Standard).options(
        selectinload(models.Standard.clauses),
        selectinload(models.Standard.schemes),
        selectinload(models.Standard.requirements)
    ).where(models.Standard.id == standard_id)
    
    result = await session.execute(stmt)
    return result.scalars().first()

async def get_clause_details(
    session: AsyncSession,
    clause_id: int
) -> Optional[models.StandardClause]:
    """Retrieve clause with its standard and linked document chunks (for context/source)."""
    stmt = select(models.StandardClause).options(
        selectinload(models.StandardClause.standard),
        selectinload(models.StandardClause.chunks).selectinload(models.DocumentChunk.document).selectinload(models.Document.source)
    ).where(models.StandardClause.id == clause_id)
    
    result = await session.execute(stmt)
    return result.scalars().first()

async def get_evidence_chain_mock(answer_id: int) -> dict:
    """Mock implementation for retrieving an evidence chain for an answer.
    In a real system, the assistant endpoint would log or persist the reasoning
    chain (query -> chunks -> citations -> answer). We construct a dummy chain here
    to satisfy the API requirement.
    """
    return {
        "answer_id": answer_id,
        "chain": [
            {
                "question": "What is the requirement for stainless steel bottles?",
                "retrieved_source": "IS 1234:2020 PDF",
                "clause_number": "3.2.1",
                "answer_fragment": "All stainless steel bottles shall conform to IS 1234-2020."
            }
        ]
    }
