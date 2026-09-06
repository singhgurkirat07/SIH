import pytest
from app.engine.matcher import MaterialMatcher
from app.engine.normalizer import MaterialNormalizer

@pytest.fixture
def normalizer():
    return MaterialNormalizer()

@pytest.fixture
def matcher():
    return MaterialMatcher()

def test_identical_materials(normalizer, matcher):
    desc1 = "HEX BOLT M16 X 50 SS304"
    desc2 = "Hexagonal Bolt M16x50mm Stainless Steel 304"
    m1 = normalizer.normalize_description(desc1)
    m2 = normalizer.normalize_description(desc2)
    
    result = matcher.match_materials(m1, m2)
    assert result['match_type'] in ['IDENTICAL', 'DUPLICATE']
    assert result['confidence_score'] >= 85

def test_genuinely_different_materials(normalizer, matcher):
    desc1 = "HEX BOLT M16 X 50 SS304"
    desc2 = "Gate Valve 2 inch 150# CS Flanged"
    m1 = normalizer.normalize_description(desc1)
    m2 = normalizer.normalize_description(desc2)
    
    result = matcher.match_materials(m1, m2)
    assert result['match_type'] == 'DIFFERENT'
    assert result['confidence_score'] < 60

def test_clashing_technical_attributes(normalizer, matcher):
    desc1 = "HEX BOLT M16 X 50 SS304"
    desc2 = "HEX BOLT M16 X 60 SS304"
    m1 = normalizer.normalize_description(desc1)
    m2 = normalizer.normalize_description(desc2)
    
    result = matcher.match_materials(m1, m2)
    # The attributes should clash (50mm vs 60mm)
    assert result['match_type'] == 'DIFFERENT'
    assert result['confidence_score'] <= 55
    
    # Check explanations
    assert any("Different length: 50 mm vs 60 mm" in d for d in result['differences'])

def test_near_duplicate(normalizer, matcher):
    desc1 = "Electric Motor 15KW 3PH 1440RPM"
    desc2 = "MOTOR SQUIRREL CAGE 15KW 3PHASE 1440 RPM"
    m1 = normalizer.normalize_description(desc1)
    m2 = normalizer.normalize_description(desc2)
    
    result = matcher.match_materials(m1, m2)
    assert result['match_type'] in ['FUNCTIONALLY_EQUIVALENT', 'NEAR_DUPLICATE', 'DUPLICATE', 'IDENTICAL']
    assert result['confidence_score'] > 60

def test_unit_variations(normalizer, matcher):
    desc1 = "Pipe Seamless 4 inch SCH40"
    desc2 = "PIPE SMLS 4IN SCH40"
    m1 = normalizer.normalize_description(desc1)
    m2 = normalizer.normalize_description(desc2)
    
    result = matcher.match_materials(m1, m2)
    assert result['match_type'] in ['IDENTICAL', 'DUPLICATE']
