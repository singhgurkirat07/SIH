# backend/app/schemas/lab_discovery.py
"""Schemas for Testing Laboratory discovery (Phase 9)."""
from typing import List, Optional
from pydantic import BaseModel, Field

class LabCapability(BaseModel):
    test_name: str
    related_standard: Optional[str] = None
    verification_source: str = Field(..., description="Source document where this capability is verified")

class LabResult(BaseModel):
    id: int
    name: str = Field(..., description="Laboratory name")
    location: Optional[str] = Field(None, description="Location of the laboratory")
    capabilities: List[LabCapability] = Field(default_factory=list, description="Relevant testing capabilities")
    accreditation: Optional[str] = Field(None, description="Recognition/accreditation info if available")
    source: str = Field(..., description="Primary source reference for this lab")
    relevance_explanation: str = Field(..., description="Explanation of why this lab is relevant to the query")

class LabSearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="General search query")
    product_category: Optional[str] = None
    test_type: Optional[str] = None
    location: Optional[str] = None
    standard_number: Optional[str] = None

class LabSearchResponse(BaseModel):
    results: List[LabResult]
