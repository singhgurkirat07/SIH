# backend/app/schemas/multilingual.py
"""Schemas for the multilingual assistant endpoint.
The request includes the raw user message and an optional language code.
If language is omitted we will auto‑detect it.
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field

class MultilingualQueryRequest(BaseModel):
    message: str = Field(..., description="User's natural‑language query")
    language: Optional[str] = Field(None, description="ISO language code (e.g., 'en', 'hi'). Auto‑detected if omitted.")

class MultilingualCitation(BaseModel):
    source_id: int
    document_title: str
    standard_number: Optional[str] = None
    clause: Optional[str] = None
    page: Optional[int] = None
    source_url: str
    excerpt: str
    relevance_score: float

class MultilingualQueryResponse(BaseModel):
    answer: str = Field(..., description="Answer generated in the user's language")
    detected_language: str = Field(..., description="Language code detected for the user query")
    citations: list[MultilingualCitation] = []
    confidence: float = Field(..., description="Confidence of intent detection (0‑1)")
    # No internal chain‑of‑thought is exposed per user rules

    class Config:
        orm_mode = True
