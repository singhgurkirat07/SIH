# backend/app/models.py
"""SQLAlchemy ORM models for BIS Assist.
Includes core tables from Phase 2, graph‑oriented entities from Phase 4, and the new
CertificationJourney model for Phase 6.
Only verified/seeded data should be inserted – no synthetic relationships.
"""
import datetime
import json
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    ForeignKey,
    Table,
    Boolean,
    JSON,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# ------------------------------------------------------------
# Phase 2 core models (simplified – actual columns may be larger)
# ------------------------------------------------------------
class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    authority = Column(String, nullable=True)
    documents = relationship("Document", back_populates="source")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    doc_type = Column(String, nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    source = relationship("Source", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    text = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    embedding = Column(Text, nullable=True)  # JSON list of floats
    source_type = Column(String, nullable=False, default="demo") # official, demo
    verification_status = Column(String, nullable=False, default="demo") # verified, demo, unavailable
    document = relationship("Document", back_populates="chunks")
    clause_id = Column(Integer, ForeignKey("standard_clauses.id"), nullable=True)
    clause = relationship("StandardClause", back_populates="chunks")

class Standard(Base):
    __tablename__ = "standards"
    id = Column(Integer, primary_key=True)
    number = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    revision = Column(String, nullable=True)
    clauses = relationship("StandardClause", back_populates="standard")
    schemes = relationship("CertificationScheme", secondary="standard_scheme_association", back_populates="standards")
    products = relationship("Product", secondary="product_standard_association", back_populates="standards")

class StandardClause(Base):
    __tablename__ = "standard_clauses"
    id = Column(Integer, primary_key=True)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    clause_number = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    standard = relationship("Standard", back_populates="clauses")
    chunks = relationship("DocumentChunk", back_populates="clause")
    related_standards = relationship("Standard", secondary="clause_related_standard", back_populates="related_clauses")

# Association for related standards (clause level)
clause_related_standard = Table(
    "clause_related_standard",
    Base.metadata,
    Column("clause_id", Integer, ForeignKey("standard_clauses.id"), primary_key=True),
    Column("standard_id", Integer, ForeignKey("standards.id"), primary_key=True),
)

# ------------------------------------------------------------
# Graph‑oriented entities for Phase 4
# ------------------------------------------------------------
class ProductCategory(Base):
    __tablename__ = "product_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("product_categories.id"), nullable=True)
    category = relationship("ProductCategory", back_populates="products")
    standards = relationship("Standard", secondary="product_standard_association", back_populates="products")
    schemes = relationship("CertificationScheme", secondary="product_scheme_association", back_populates="products")

product_standard_association = Table(
    "product_standard_association",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("standard_id", Integer, ForeignKey("standards.id"), primary_key=True),
)

class CertificationScheme(Base):
    __tablename__ = "certification_schemes"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    standards = relationship("Standard", secondary="standard_scheme_association", back_populates="schemes")
    products = relationship("Product", secondary="product_scheme_association", back_populates="schemes")

standard_scheme_association = Table(
    "standard_scheme_association",
    Base.metadata,
    Column("standard_id", Integer, ForeignKey("standards.id"), primary_key=True),
    Column("scheme_id", Integer, ForeignKey("certification_schemes.id"), primary_key=True),
)

product_scheme_association = Table(
    "product_scheme_association",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("scheme_id", Integer, ForeignKey("certification_schemes.id"), primary_key=True),
)

class Requirement(Base):
    __tablename__ = "requirements"
    id = Column(Integer, primary_key=True)
    description = Column(Text, nullable=False)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    standard = relationship("Standard", backref="requirements")
    tests = relationship("Test", secondary="requirement_test_association", back_populates="requirements")

requirement_test_association = Table(
    "requirement_test_association",
    Base.metadata,
    Column("requirement_id", Integer, ForeignKey("requirements.id"), primary_key=True),
    Column("test_id", Integer, ForeignKey("tests.id"), primary_key=True),
)

class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    requirements = relationship("Requirement", secondary="requirement_test_association", back_populates="tests")
    laboratories = relationship("Laboratory", secondary="test_lab_association", back_populates="tests")

class Laboratory(Base):
    __tablename__ = "laboratories"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    tests = relationship("Test", secondary="test_lab_association", back_populates="laboratories")

test_lab_association = Table(
    "test_lab_association",
    Base.metadata,
    Column("test_id", Integer, ForeignKey("tests.id"), primary_key=True),
    Column("lab_id", Integer, ForeignKey("laboratories.id"), primary_key=True),
)

# ------------------------------------------------------------
# Phase 6 – Certification Journey model
# ------------------------------------------------------------
class EvidenceState(str):
    VERIFIED = "VERIFIED"
    INFERRED = "INFERRED"
    NOT_VERIFIED = "NOT_VERIFIED"

class CertificationJourney(Base):
    __tablename__ = "certification_journeys"
    id = Column(Integer, primary_key=True)
    product_name = Column(String, nullable=False)
    product_description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    # Store the step data as JSON for flexibility
    steps = Column(JSON, nullable=False, default=list)  # List[dict] with step info
    # Optional summary fields for final display
    summary = Column(JSON, nullable=True)

# ------------------------------------------------------------
# Helper mixin for timestamps (optional)
# ------------------------------------------------------------
class TimestampMixin:
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
