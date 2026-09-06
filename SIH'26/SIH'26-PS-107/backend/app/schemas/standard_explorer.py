# backend/app/schemas/standard_explorer.py
"""Pydantic schemas for the Standards Explorer and Clause endpoints.
These models expose the data needed by the frontend without leaking internal
SQLAlchemy objects.
"""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field

class ClauseInfo(BaseModel):
    id: int = Field(..., description="Clause primary key")
    clause_number: str = Field(..., description="Clause identifier, e.g., 3.2.1")
    title: Optional[str] = Field(None, description="Optional clause title")
    text: str = Field(..., description="Full clause text")
    source_document: Optional[str] = Field(None, description="Title of the source document")
    page_number: Optional[int] = Field(None, description="Page number in source document")
    source_url: Optional[str] = Field(None, description="URL where the source can be accessed")

class StandardDetail(BaseModel):
    id: int = Field(...)
    number: str = Field(..., description="Standard number, e.g., IS 1234-2020")
    title: str = Field(...)
    revision: Optional[str] = Field(None)
    status: Optional[str] = Field(None, description="Current status e.g., Draft, Active")
    description: Optional[str] = Field(None)
    clauses: List[ClauseInfo] = Field(default_factory=list)
    related_standards: List[str] = Field(default_factory=list, description="Numbers of related standards")
    related_schemes: List[str] = Field(default_factory=list, description="Names of certification schemes")
    testing_information: Optional[str] = Field(None, description="Summary of required tests or labs")
    sources: List[str] = Field(default_factory=list, description="List of source document titles/URLs")

class StandardSearchResult(BaseModel):
    id: int = Field(...)
    number: str = Field(...)
    title: str = Field(...)
    relevance_score: float = Field(..., description="Score from semantic/keyword matching (0‑1)")

class ClauseDetail(BaseModel):
    id: int = Field(...)
    standard_id: int = Field(...)
    clause_number: str = Field(...)
    title: Optional[str] = Field(None)
    text: str = Field(...)
    source_document: Optional[str] = Field(None)
    page_number: Optional[int] = Field(None)
    surrounding_context: Optional[str] = Field(None, description="Excerpt of surrounding text (e.g., +/- 2 sentences)")
    source_url: Optional[str] = Field(None)

class EvidenceChainItem(BaseModel):
    question: str
    retrieved_source: str = Field(..., description="Document title or URL used as evidence")
    clause_number: Optional[str] = None
    answer_fragment: str = Field(..., description="Exact excerpt that supported the answer")

class EvidenceChainResponse(BaseModel):
    answer_id: int = Field(..., description="Internal identifier for the answer (if stored)")
    chain: List[EvidenceChainItem]

