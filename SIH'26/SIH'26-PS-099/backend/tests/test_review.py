import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Material, MatchResult, NMCMapping, CommonNationalCode, ReviewerFeedback, AuditLog

engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Create test materials
    m1 = Material(cpse="A", material_code="1", description="M1")
    m2 = Material(cpse="B", material_code="2", description="M2")
    db.add(m1)
    db.add(m2)
    db.commit()

    # Create common national code
    nmc = CommonNationalCode(nmc_code="NMC-TEST-123", category="Fastener")
    db.add(nmc)
    db.commit()

    # Create proposed mappings
    db.add(NMCMapping(nmc_id=nmc.id, material_id=m1.id, status="proposed", cpse="A"))
    db.add(NMCMapping(nmc_id=nmc.id, material_id=m2.id, status="proposed", cpse="B"))
    
    # Create pending match
    match = MatchResult(
        material_a_id=m1.id, material_b_id=m2.id, status="pending",
        match_type="DUPLICATE", confidence_score=85.0,
        semantic_similarity=0.8, attribute_similarity=0.9, technical_similarity=0.9,
        text_similarity=0.8, category_similarity=1.0,
        common_national_code="NMC-TEST-123"
    )
    db.add(match)
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

def test_approve_match():
    # 1. Approve match
    db = TestingSessionLocal()
    match = db.query(MatchResult).first()
    
    response = client.post(f"/api/matches/{match.id}/approve", json={"reviewer": "test_user"})
    assert response.status_code == 200
    
    # 2. Check Match Status
    db.refresh(match)
    assert match.status == "approved"
    assert match.reviewed_by == "test_user"

    # 3. Check NMCMapping Status
    mappings = db.query(NMCMapping).all()
    for m in mappings:
        assert m.status == "approved"

    # 4. Check Audit Log
    logs = db.query(AuditLog).filter_by(action="match_approved").all()
    assert len(logs) == 1
    assert logs[0].user == "test_user"

    # 5. Check Feedback Data
    feedbacks = db.query(ReviewerFeedback).all()
    assert len(feedbacks) == 1
    assert feedbacks[0].decision == "approved"
    assert feedbacks[0].semantic_similarity == 0.8

def test_reject_match():
    db = TestingSessionLocal()
    match = db.query(MatchResult).first()
    
    response = client.post(f"/api/matches/{match.id}/reject", json={"reviewer": "test_user"})
    assert response.status_code == 200
    
    db.refresh(match)
    assert match.status == "rejected"

    mappings = db.query(NMCMapping).all()
    for m in mappings:
        assert m.status == "rejected"

    logs = db.query(AuditLog).filter_by(action="match_rejected").all()
    assert len(logs) == 1

    feedbacks = db.query(ReviewerFeedback).all()
    assert len(feedbacks) == 1
    assert feedbacks[0].decision == "rejected"

def test_reranker_training_insufficient_data():
    response = client.post("/api/reranker/train")
    assert response.status_code == 200
    assert response.json()["result"]["status"] == "error"
    assert "Insufficient data" in response.json()["result"]["message"]

def test_reranker_training_sufficient_data():
    db = TestingSessionLocal()
    # Add 20 dummy feedback records
    for i in range(25):
        db.add(ReviewerFeedback(
            match_id=1, decision="approved" if i % 2 == 0 else "rejected",
            semantic_similarity=0.9 if i % 2 == 0 else 0.4,
            attribute_similarity=0.9 if i % 2 == 0 else 0.4,
            technical_similarity=0.9, text_similarity=0.9, category_similarity=1.0,
            predicted_match_type="DUPLICATE"
        ))
    db.commit()

    response = client.post("/api/reranker/train")
    assert response.status_code == 200
    assert response.json()["result"]["status"] == "success"
    assert "accuracy" in response.json()["result"]

    status_response = client.get("/api/reranker/status")
    assert status_response.json()["trained"] is True
