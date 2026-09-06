import pytest
from app.engine.nmc_generator import NMCGenerator
from app.engine.normalizer import MaterialNormalizer

@pytest.fixture
def normalizer():
    return MaterialNormalizer()

@pytest.fixture
def nmc_gen():
    return NMCGenerator()

def test_nmc_determinism(normalizer, nmc_gen):
    # Two different descriptions of the same material
    desc1 = "HEX BOLT M16 X 50 MM SS304"
    desc2 = "Bolt Hex M16x50 Stainless Steel 304"
    
    m1 = normalizer.normalize_description(desc1)
    m2 = normalizer.normalize_description(desc2)
    
    code1 = nmc_gen.generate_code(m1['attributes'])
    code2 = nmc_gen.generate_code(m2['attributes'])
    
    # Both must generate the exact same NMC
    assert code1 == code2
    assert code1 == "NMC-BLT-SS304-M16-050"

def test_nmc_differentiation(normalizer, nmc_gen):
    # Two different materials
    desc1 = "HEX BOLT M16 X 50 SS304"
    desc2 = "HEX BOLT M16 X 60 SS304"
    
    m1 = normalizer.normalize_description(desc1)
    m2 = normalizer.normalize_description(desc2)
    
    code1 = nmc_gen.generate_code(m1['attributes'])
    code2 = nmc_gen.generate_code(m2['attributes'])
    
    # Must generate different NMCs
    assert code1 != code2
    assert code1 == "NMC-BLT-SS304-M16-050"
    assert code2 == "NMC-BLT-SS304-M16-060"

def test_nmc_pipes_and_valves(normalizer, nmc_gen):
    desc_pipe = "Pipe Seamless 4 inch SCH40 CS"
    desc_valve = "Gate Valve 2 inch 150# CS Flanged"
    
    m_pipe = normalizer.normalize_description(desc_pipe)
    m_valve = normalizer.normalize_description(desc_valve)
    
    code_pipe = nmc_gen.generate_code(m_pipe['attributes'])
    code_valve = nmc_gen.generate_code(m_valve['attributes'])
    
    assert code_pipe == "NMC-PIP-CARBONSTEEL-004-SCH40"
    assert code_valve == "NMC-VLV-CARBONSTEEL-002-150"

def test_nmc_missing_attributes(normalizer, nmc_gen):
    desc = "BOLT HEX SS304"  # Missing size and length
    m = normalizer.normalize_description(desc)
    code = nmc_gen.generate_code(m['attributes'])
    
    assert code == "NMC-BLT-SS304-XXX-XXX"
