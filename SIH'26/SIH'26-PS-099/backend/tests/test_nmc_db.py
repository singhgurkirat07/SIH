import pytest
from app.database import Base, get_db
from app.models import Material, MatchResult, CommonNationalCode, NMCMapping, NormalizedAttribute
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from fastapi.testclient import TestClient

# Use in-memory SQLite for DB testing
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

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
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_multiple_cpse_mappings():
    # Insert materials for different CPSEs
    db = TestingSessionLocal()
    m1 = Material(cpse="CPCL", material_code="C1", description="HEX BOLT M16 X 50 SS304", original_description="HEX BOLT M16 X 50 SS304")
    m2 = Material(cpse="NTPC", material_code="N2", description="Bolt Hex M16x50 Stainless Steel 304", original_description="Bolt Hex M16x50 Stainless Steel 304")
    db.add(m1)
    db.add(m2)
    db.commit()
    db.refresh(m1)
    db.refresh(m2)

    # Run matching
    response = client.post("/api/match")
    assert response.status_code == 200

    # Verify NMC and Mappings
    nmcs = db.query(CommonNationalCode).all()
    assert len(nmcs) == 1
    nmc = nmcs[0]
    
    mappings = db.query(NMCMapping).filter_by(nmc_id=nmc.id).all()
    assert len(mappings) == 2
    mapped_cpses = {m.cpse for m in mappings}
    assert mapped_cpses == {"CPCL", "NTPC"}

def test_rejected_matches():
    db = TestingSessionLocal()
    m1 = Material(cpse="CPCL", material_code="C1", description="HEX BOLT M16 X 50 SS304", original_description="HEX BOLT M16 X 50 SS304")
    m2 = Material(cpse="BHEL", material_code="B1", description="HEX BOLT M16 X 60 SS304", original_description="HEX BOLT M16 X 60 SS304")
    db.add(m1)
    db.add(m2)
    db.commit()

    # Create a match result manually that is rejected
    mr = MatchResult(
        material_a_id=1, material_b_id=2, match_type='DIFFERENT', 
        confidence_score=40, status='rejected'
    )
    db.add(mr)
    db.commit()

    # The API shouldn't create NMC for rejected/DIFFERENT matches
    response = client.post("/api/match")
    
    nmcs = db.query(CommonNationalCode).all()
    # It might create separate NMCs for each if they are distinct! 
    # But wait, run_matching only creates NMCs for pairs that MATCH.
    assert len(nmcs) == 0

def test_edited_attributes():
    # If attributes are edited, NMC code should reflect it.
    from app.engine.nmc_generator import NMCGenerator
    import json
    
    gen = NMCGenerator()
    attrs = {"category": "Fastener", "grade": "SS304", "thread_size": "M16", "length": "50 mm"}
    code1 = gen.generate_code(attrs)
    
    # Edit attribute
    attrs["length"] = "60 mm"
    code2 = gen.generate_code(attrs)
    
    assert code1 == "NMC-BLT-SS304-M16-050"
    assert code2 == "NMC-BLT-SS304-M16-060"
    assert code1 != code2
