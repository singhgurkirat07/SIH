import os
import io
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.engine.normalizer import MaterialNormalizer
from app.models import Material

SQLALCHEMY_DATABASE_URL = "sqlite:///./data/test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
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
def setup_and_teardown():
    # Setup
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown
    Base.metadata.drop_all(bind=engine)

def test_normalization_and_attribute_extraction():
        normalizer = MaterialNormalizer()
        
        # Test Bolt 1
        res1 = normalizer.normalize_description("HEX BOLT M16 X 50 SS304")
        assert res1['normalized'] == "Hexagonal BOLT M16 X 50 Stainless Steel 304"
        assert res1['attributes'].get('material') == "Stainless Steel"
        assert res1['attributes'].get('thread_size') == "M16"
        assert res1['attributes'].get('length') == "50 mm"
        assert res1['attributes'].get('material_type') == "Hex Bolt"
        assert res1['attributes'].get('category') == "Fastener"
    
        # Test Bolt 2
        res2 = normalizer.normalize_description("Hexagonal Bolt M16x50mm Stainless Steel 304")
        assert res2['normalized'] == "Hexagonal Bolt M16 X 50 mm Stainless Steel 304"
        assert res2['attributes'].get('thread_size') == "M16"
        assert res2['attributes'].get('length') == "50 mm"
        assert res2['attributes'].get('material') == "Stainless Steel"
    
        # Test Missing Attributes
        res3 = normalizer.normalize_description("HEX BOLT SS304")
        assert res3['attributes'].get('thread_size') is None
        assert res3['attributes'].get('length') is None
        
        # Test Pipe
        res4 = normalizer.normalize_description("Pipe Seamless 4 inch SCH40 ASTM A106 GR B")
        assert res4['attributes'].get('size') == "4 inch"
        assert res4['attributes'].get('schedule') == "SCH40"
        assert res4['attributes'].get('standard') == "ASTM A106"
        
        # Test Bearing
        res5 = normalizer.normalize_description("Deep Groove Ball Bearing 6205ZZ")
        assert res5['attributes'].get('bearing_number') == "6205"
    
def test_csv_upload_validation():
        # 1. Missing columns
        csv_missing_col = "cpse,description\nCPCL,Test"
        response = client.post(
            "/api/materials/upload",
            files={"file": ("test.csv", io.BytesIO(csv_missing_col.encode("utf-8-sig")), "text/csv")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "Missing required columns" in data["message"]
    
        # 2. Missing fields and valid row
        csv_data = (
            "cpse,material_code,description\n"
            "CPCL,,HEX BOLT M16 X 50 SS304\n"
            "CPCL,CPCL-1001,HEX BOLT M16 X 50 SS304\n"
        )
        response = client.post(
            "/api/materials/upload",
            files={"file": ("test.csv", io.BytesIO(csv_data.encode("utf-8-sig")), "text/csv")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["successful_records"] == 1
        assert data["failed_records"] == 1
        assert "Missing required field" in data["errors"][0]["error"]
    
        # 3. Duplicate material code
        csv_dup = (
            "cpse,material_code,description\n"
            "CPCL,CPCL-1001,ANOTHER BOLT\n"
        )
        response = client.post(
            "/api/materials/upload",
            files={"file": ("test.csv", io.BytesIO(csv_dup.encode("utf-8-sig")), "text/csv")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["failed_records"] == 1
        assert "Duplicate material code" in data["errors"][0]["error"]

def test_data_model_persists_original_and_extracted():
    csv_data = (
        "cpse,material_code,description\n"
        "ONGC,ONGC-100,HEX BOLT M16 X 50 SS304\n"
    )
    client.post(
        "/api/materials/upload",
        files={"file": ("test.csv", io.BytesIO(csv_data.encode("utf-8-sig")), "text/csv")}
    )
    
    # Verify in DB
    db = TestingSessionLocal()
    mat = db.query(Material).filter_by(material_code="ONGC-100").first()
    assert mat is not None
    assert mat.original_description == "HEX BOLT M16 X 50 SS304"
    assert mat.extracted_attributes is not None
    
    attrs = json.loads(mat.extracted_attributes)
    assert attrs["thread_size"] == "M16"
    assert attrs["length"] == "50 mm"
    db.close()
