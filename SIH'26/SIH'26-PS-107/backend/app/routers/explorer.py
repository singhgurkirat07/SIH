# backend/app/routers/explorer.py
"""Router for Standards Explorer and Evidence Explorer APIs."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from ..schemas.standard_explorer import (
    StandardSearchResult,
    StandardDetail,
    ClauseDetail,
    EvidenceChainResponse,
    ClauseInfo
)
from ..services.explorer import (
    search_standards,
    get_standard_details,
    get_clause_details,
    get_evidence_chain_mock
)
# Note: In a real implementation we would import get_db dependency. 
# We'll mock it here if database.py is not present.
try:
    from ..database import get_db
except ImportError:
    # Dummy dependency for standalone execution
    async def get_db():
        yield None

router = APIRouter(prefix="/api/explorer", tags=["Explorer"])
logger = logging.getLogger(__name__)

@router.get("/standards", response_model=List[StandardSearchResult])
async def search_standards_api(
    query: str,
    top_k: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Search for standards."""
    standards = await search_standards(db, query, top_k)
    results = []
    for s in standards:
        results.append(StandardSearchResult(
            id=s.id,
            number=s.number,
            title=s.title,
            relevance_score=1.0  # Dummy score for keyword match
        ))
    return results

@router.get("/standards/{standard_id}", response_model=StandardDetail)
async def get_standard_api(
    standard_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get full details of a standard."""
    std = await get_standard_details(db, standard_id)
    if not std:
        raise HTTPException(status_code=404, detail="Standard not found")
        
    clauses = []
    for c in std.clauses:
        clauses.append(ClauseInfo(
            id=c.id,
            clause_number=c.clause_number,
            text=c.text,
            # Mocking source/page for now
            source_document="BIS Document",
            page_number=1,
            source_url="https://bis.gov.in/demo"
        ))
        
    schemes = [sch.name for sch in std.schemes]
    
    return StandardDetail(
        id=std.id,
        number=std.number,
        title=std.title,
        revision=std.revision,
        status="Active",
        description="Standard description",
        clauses=clauses,
        related_standards=[],
        related_schemes=schemes,
        testing_information="Testing required per Clause 4.",
        sources=["https://bis.gov.in/demo"]
    )

@router.get("/clauses/{clause_id}", response_model=ClauseDetail)
async def get_clause_api(
    clause_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed clause view with surrounding context."""
    clause = await get_clause_details(db, clause_id)
    if not clause:
        raise HTTPException(status_code=404, detail="Clause not found")
        
    doc_title = None
    doc_url = None
    page_num = None
    if clause.chunks and len(clause.chunks) > 0:
        chunk = clause.chunks[0]
        page_num = chunk.page_number
        if chunk.document:
            doc_title = chunk.document.title
            if chunk.document.source:
                doc_url = chunk.document.source.url

    return ClauseDetail(
        id=clause.id,
        standard_id=clause.standard_id,
        clause_number=clause.clause_number,
        title=None,
        text=clause.text,
        source_document=doc_title or "Unknown Document",
        page_number=page_num,
        surrounding_context="... " + clause.text[:50] + " ...",
        source_url=doc_url
    )

@router.get("/evidence/{answer_id}", response_model=EvidenceChainResponse)
async def get_evidence_api(
    answer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get the evidence chain for a specific assistant answer."""
    # In a real scenario we'd fetch from DB.
    chain = await get_evidence_chain_mock(answer_id)
    return chain
