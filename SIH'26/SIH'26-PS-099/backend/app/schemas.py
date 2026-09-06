from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field

# Material Schemas
class NormalizedAttributeBase(BaseModel):
    attribute_name: str
    attribute_value: str
    confidence: float

class NormalizedAttributeResponse(NormalizedAttributeBase):
    id: int
    material_id: int
    model_config = ConfigDict(from_attributes=True)

class MaterialBase(BaseModel):
    cpse: str
    material_code: str
    description: str
    original_description: Optional[str] = None
    normalized_description: Optional[str] = None
    category: Optional[str] = None
    material_type: Optional[str] = None
    unit: Optional[str] = None
    specification: Optional[str] = None
    extracted_attributes: Optional[str] = None
    manufacturer: Optional[str] = None
    historical_quantity: Optional[float] = None
    historical_cost: Optional[float] = None

class MaterialCreate(MaterialBase):
    pass

class MaterialResponse(MaterialBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class MaterialDetail(MaterialResponse):
    attributes: List[NormalizedAttributeResponse] = []
    model_config = ConfigDict(from_attributes=True)

# Match Result Schemas
class MatchResultBase(BaseModel):
    match_type: str
    confidence_score: float
    semantic_similarity: float
    attribute_similarity: float
    technical_similarity: float
    text_similarity: float
    category_similarity: float
    explanation: Optional[str] = None
    status: str = 'pending'
    common_national_code: Optional[str] = None

class MatchResultResponse(MatchResultBase):
    id: int
    material_a_id: int
    material_b_id: int
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class MatchResultDetail(MatchResultResponse):
    material_a: MaterialResponse
    material_b: MaterialResponse
    model_config = ConfigDict(from_attributes=True)

# NMC Schemas
class NMCMappingBase(BaseModel):
    cpse: str
    original_code: str
    status: str = 'proposed'

class NMCMappingResponse(NMCMappingBase):
    id: int
    nmc_id: int
    material_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class NMCBase(BaseModel):
    nmc_code: str
    category: str
    description: str
    normalized_attributes: Optional[str] = None

class NMCResponse(NMCBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class NMCDetail(NMCResponse):
    mappings: List[NMCMappingResponse] = []
    model_config = ConfigDict(from_attributes=True)

# Audit Log Schemas
class AuditLogResponse(BaseModel):
    id: int
    timestamp: datetime
    user: str
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    details: Optional[str] = None
    material_ids: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# Dashboard Schemas
class DashboardResponse(BaseModel):
    total_materials: int
    total_matches: int
    pending_reviews: int
    approved_matches: int
    rejected_matches: int
    total_nmc_generated: int
    average_confidence: float

# Review Action Schema
class ReviewAction(BaseModel):
    action: str = Field(..., description="approve or reject")
    reason: Optional[str] = None

# Bulk Upload Response
class BulkUploadResponse(BaseModel):
    message: str
    total_records: int
    successful_records: int
    failed_records: int
    errors: Optional[List[Dict[str, Any]]] = None

# Golden Test Metrics
class GoldenTestMetrics(BaseModel):
    precision: float
    recall: float
    f1: float
    accuracy: float
    total_pairs: int
    correct_predictions: int

# Search Result
class SearchResult(BaseModel):
    materials: List[MaterialDetail]
    total_count: int
    page: int
    size: int
