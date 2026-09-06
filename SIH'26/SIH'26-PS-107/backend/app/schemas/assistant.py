# backend/app/schemas/assistant.py
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    """Payload sent by the frontend when the user asks a question."""
    message: str = Field(..., description="User's natural‑language query")
    conversation_id: Optional[str] = Field(None, description="Optional conversation identifier for multi‑turn dialogues")
    language: str = Field("en", description="ISO language code, default English")

class Citation(BaseModel):
    """Structured citation that the frontend will display as a source reference."""
    source_id: int = Field(..., description="Primary key of the Source record")
    document_title: str = Field(..., description="Title of the original document")
    standard_number: Optional[str] = Field(None, description="BIS standard number, if applicable")
    clause: Optional[str] = Field(None, description="Clause/section identifier within the standard")
    page: Optional[int] = Field(None, description="Page number inside the original document")
    source_url: str = Field(..., description="URL where the source can be accessed")
    excerpt: str = Field(..., description="Short excerpt (max ~200 chars) that supports the answer")
    relevance_score: float = Field(..., description="Similarity score (0‑1) after reranking")

class QueryResponse(BaseModel):
    """Response returned by the assistant endpoint.
    All factual statements must be backed by entries in ``citations``.
    """
    answer: str = Field(..., description="Generated answer – must be grounded in citations")
    intent: str = Field(..., description="Detected intent type (see Intent enum)")
    confidence: float = Field(..., description="Confidence of intent detection (0‑1)")
    citations: List[Citation] = Field(default_factory=list, description="Evidence supporting the answer")
    retrieved_sources: List[int] = Field(default_factory=list, description="IDs of Document/Source objects that contributed evidence")
    clarification_required: bool = Field(False, description="True when the system needs more info before answering")
    suggested_questions: Optional[List[str]] = Field(None, description="Optional follow‑up suggestions for the user")

    class Config:
        orm_mode = True
