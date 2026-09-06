# backend/app/schemas/graph.py
"""Pydantic schemas for the graph‑oriented APIs used in Phase 4.
Only expose the fields needed by the frontend – internal IDs are kept for
reference but can be omitted from the public response if desired.
"""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field

class StandardInfo(BaseModel):
    id: int = Field(..., description="Primary key of the Standard")
    number: str = Field(..., description="Standard identifier, e.g. IS 1234‑2020")
    title: str = Field(..., description="Human readable title")
    revision: Optional[str] = Field(None, description="Revision identifier if any")

class RequirementInfo(BaseModel):
    id: int = Field(...)
    description: str = Field(...)

class TestInfo(BaseModel):
    id: int = Field(...)
    name: str = Field(...)
    description: Optional[str] = None

class LaboratoryInfo(BaseModel):
    id: int = Field(...)
    name: str = Field(...)
    location: Optional[str] = None

class StandardRecommendation(BaseModel):
    standard: StandardInfo
    match_score: float = Field(..., description="Similarity / relevance score (0‑1)")
    matched_attributes: List[str] = Field(default_factory=list, description="Attributes that matched the product description")
    missing_attributes: List[str] = Field(default_factory=list, description="Attributes that were not found but could be relevant")
    supporting_evidence: List[str] = Field(default_factory=list, description="Excerpts from clauses/documents that support the recommendation")
    related_scheme: Optional[str] = Field(None, description="Name of a certification scheme linked to the standard")
    next_action: Optional[str] = Field(None, description="Suggested next step for the user")

class RecommendationResponse(BaseModel):
    product_id: int
    recommendations: List[StandardRecommendation]
    confidence_overall: float = Field(..., description="Overall confidence of the recommendation pipeline")

    class Config:
        orm_mode = True
