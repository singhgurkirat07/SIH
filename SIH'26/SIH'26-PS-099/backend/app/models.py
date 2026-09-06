from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint, Text, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    cpse = Column(String, index=True, nullable=False)
    material_code = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    original_description = Column(String, nullable=True)
    normalized_description = Column(String, nullable=True)
    category = Column(String, index=True, nullable=True)
    material_type = Column(String, index=True, nullable=True)
    unit = Column(String, nullable=True)
    specification = Column(String, nullable=True)
    extracted_attributes = Column(Text, nullable=True)
    manufacturer = Column(String, nullable=True)
    historical_quantity = Column(Float, nullable=True)
    historical_cost = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint('cpse', 'material_code', name='uix_cpse_material_code'),)

    attributes = relationship("NormalizedAttribute", back_populates="material", cascade="all, delete-orphan")
    matches_a = relationship("MatchResult", foreign_keys="MatchResult.material_a_id", back_populates="material_a")
    matches_b = relationship("MatchResult", foreign_keys="MatchResult.material_b_id", back_populates="material_b")
    nmc_mappings = relationship("NMCMapping", back_populates="material")


class NormalizedAttribute(Base):
    __tablename__ = "normalized_attributes"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    attribute_name = Column(String, index=True, nullable=False)
    attribute_value = Column(String, index=True, nullable=False)
    confidence = Column(Float, nullable=False)

    material = relationship("Material", back_populates="attributes")


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    material_a_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    material_b_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    match_type = Column(String, index=True, nullable=False)
    confidence_score = Column(Float, nullable=False)
    semantic_similarity = Column(Float, nullable=False)
    attribute_similarity = Column(Float, nullable=False)
    technical_similarity = Column(Float, nullable=False)
    text_similarity = Column(Float, nullable=False)
    category_similarity = Column(Float, nullable=False)
    explanation = Column(Text, nullable=True)
    status = Column(String, index=True, default='pending')
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    common_national_code = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    material_a = relationship("Material", foreign_keys=[material_a_id], back_populates="matches_a")
    material_b = relationship("Material", foreign_keys=[material_b_id], back_populates="matches_b")
    feedbacks = relationship("ReviewerFeedback", back_populates="match", cascade="all, delete-orphan")


class CommonNationalCode(Base):
    __tablename__ = "common_national_codes"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nmc_code = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    normalized_attributes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    mappings = relationship("NMCMapping", back_populates="nmc", cascade="all, delete-orphan")


class NMCMapping(Base):
    __tablename__ = "nmc_mappings"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nmc_id = Column(Integer, ForeignKey("common_national_codes.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    cpse = Column(String, index=True, nullable=False)
    original_code = Column(String, index=True, nullable=False)
    status = Column(String, default='proposed')
    created_at = Column(DateTime, default=datetime.utcnow)

    nmc = relationship("CommonNationalCode", back_populates="mappings")
    material = relationship("Material", back_populates="nmc_mappings")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = Column(String, default='system')
    action = Column(String, index=True, nullable=False)
    entity_type = Column(String, index=True, nullable=False)
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    material_ids = Column(String, nullable=True)


class ReviewerFeedback(Base):
    __tablename__ = "reviewer_feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    match_id = Column(Integer, ForeignKey("match_results.id"), nullable=False)
    decision = Column(String, nullable=False)
    semantic_similarity = Column(Float, nullable=False)
    attribute_similarity = Column(Float, nullable=False)
    technical_similarity = Column(Float, nullable=False)
    text_similarity = Column(Float, nullable=False)
    category_similarity = Column(Float, nullable=False)
    predicted_match_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("MatchResult", back_populates="feedbacks")


class GoldenTestPair(Base):
    __tablename__ = "golden_test_pairs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    material_a_description = Column(String, nullable=False)
    material_b_description = Column(String, nullable=False)
    material_a_cpse = Column(String, nullable=False)
    material_b_cpse = Column(String, nullable=False)
    expected_label = Column(String, nullable=False)
    predicted_label = Column(String, nullable=True)
    predicted_confidence = Column(Float, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    evaluated_at = Column(DateTime, nullable=True)
