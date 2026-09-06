# backend/app/schemas/conversation.py
"""Schemas for multi-turn conversation and context management (Phase 10)."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class EntityState(BaseModel):
    product: Optional[str] = None
    material: Optional[str] = None
    use: Optional[str] = None
    capacity: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    technical_attributes: List[str] = Field(default_factory=list)
    selected_standard: Optional[str] = None

class Message(BaseModel):
    role: str = Field(..., description="user or assistant")
    content: str

class ConversationContext(BaseModel):
    conversation_id: str
    entities: EntityState = Field(default_factory=EntityState)
    history: List[Message] = Field(default_factory=list)

class ConversationalRequest(BaseModel):
    conversation_id: str
    message: str
    language: str = "en"

class ConversationalResponse(BaseModel):
    answer: str
    entities: EntityState
    clarification_requested: bool = False
    citations: List[Dict[str, Any]] = Field(default_factory=list)
