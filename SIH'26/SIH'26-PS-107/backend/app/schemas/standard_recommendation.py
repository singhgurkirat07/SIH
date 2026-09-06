# backend/app/schemas/standard_recommendation.py
"""Pydantic models for the Find My Standard recommendation endpoint.
These models are separate from the generic assistant schemas.
"""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field

class StandardRecommendRequest(BaseModel):
    product: str = Field(..., description="Product name or description")
    category: Optional[str] = Field(None, description="Product category, if known")
    material: Optional[str] = Field(None, description="Material or composition")
    intended_use: Optional[str] = Field(None, description="Intended usage/application")
    technical_attributes: List[str] = Field(default_factory=list, description="Other technical/product attributes")

class StandardRecommendation(BaseModel):
    standard_number: str = Field(..., description="Standard identifier, e.g., IS 1234-2020")
    title: str = Field(..., description="Standard title")
    relevance_score: float = Field(..., description="Relevance score (0‑1)")
    matching_attributes: List[str] = Field(default_factory=list, description="Attributes that matched")
    missing_information: List[str] = Field(default_factory=list, description="Attributes that were not found")
    evidence: List[str] = Field(default_factory=list, description="Excerpt(s) from clauses supporting the recommendation")
    possible_certification_scheme: Optional[str] = Field(None, description="Recommended certification scheme, if any")
    confidence_category: str = Field(..., description="One of: High, Medium, Low, Needs confirmation")

class StandardRecommendResponse(BaseModel):
    product: str = Field(...)
    recommendations: List[StandardRecommendation]

    class Config:
        orm_mode = True
