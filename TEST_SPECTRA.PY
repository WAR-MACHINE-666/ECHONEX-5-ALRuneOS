# test_spectra.py
"""
Test suite for SPECTRA Neural Framework integration
"""

import pytest
import os
import sys
from pathlib import Path

# Add the parent directory to the path to import SPECTRA modules
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_spectra_file_exists():
    """Test 1: Check that the SPECTRA file exists"""
    spectra_file = Path("SPECTRA")
    assert spectra_file.exists(), "SPECTRA file not found"

def test_excerpt_exists():
    """Test 2: Check that the excerpt '3. **Sma' exists in the SPECTRA file"""
    spectra_file = Path("SPECTRA")
    if not spectra_file.exists():
        pytest.skip("SPECTRA file not found")
    
    with open(spectra_file, encoding="utf-8") as f:
        content = f.read()
    
    assert "3. **Sma" in content, "Excerpt '3. **Sma' not found in SPECTRA file"

def test_excerpt_is_markdown_list():
    """Test 3: Check that the excerpt is part of a Markdown numbered list"""
    spectra_file = Path("SPECTRA")
    if not spectra_file.exists():
        pytest.skip("SPECTRA file not found")
    
    with open(spectra_file, encoding="utf-8") as f:
        lines = f.readlines()
    
    found = False
    for line in lines:
        if line.strip().startswith("3. **Sma"):
            found = True
            break
    
    assert found, "Excerpt '3. **Sma' is not formatted as a Markdown numbered list item"

def test_excerpt_not_truncated():
    """Test 4: Check that the excerpt is followed by additional text (not truncated)"""
    spectra_file = Path("SPECTRA")
    if not spectra_file.exists():
        pytest.skip("SPECTRA file not found")
    
    with open(spectra_file, encoding="utf-8") as f:
        content = f.read()
    
    idx = content.find("3. **Sma")
    assert idx != -1, "Excerpt '3. **Sma' not found"
    
    # Check that at least 10 characters follow the excerpt
    remaining_content = content[idx + len("3. **Sma"):]
    assert len(remaining_content) >= 10, "Excerpt appears to be truncated (less than 10 characters follow)"

def test_spectra_framework_structure():
    """Test 5: Verify SPECTRA framework has expected structure"""
    try:
        from spectra_framework.core.base import BaseModule, NeuralSignal
        from spectra_framework.consciousness.consciousness_module import ConsciousnessModule
        from spectra_framework.memory.memory_systems import MemoryFormationSystem
        
        # Test that classes can be instantiated
        signal = NeuralSignal(
            source_module="test",
            target_module="test",
            signal_type="test",
            data={},
            timestamp=0.0
        )
        
        assert signal.source_module == "test"
        assert signal.target_module == "test"
        assert signal.signal_type == "test"
        
    except ImportError as e:
        pytest.skip(f"SPECTRA framework modules not available: {e}")

def test_spectra_integration_with_aeprs():
    """Test 6: Verify SPECTRA can integrate with AEPRS"""
    try:
        from aeprs.core.framework import AEPRSFramework, ErrorEvent, ErrorSeverity
        from aeprs.spectra.integration import SPECTRAIntegration
        
        # Create AEPRS framework
        aeprs = AEPRSFramework()
        
        # Create SPECTRA integration
        spectra_integration = SPECTRAIntegration(aeprs)
        
        # Test error event processing
        test_event = ErrorEvent(
            timestamp=datetime.now(),
            source="test_source",
            message="Test error message",
            severity=ErrorSeverity.MEDIUM
        )
        
        # Process through SPECTRA
        result = spectra_integration.process_error_through_spectra(test_event)
        
        assert result is not None
        assert 'spectra_analysis' in result
        
    except ImportError as e:
        pytest.skip(f"Integration modules not available: {e}")

def test_odg_integration():
    """Test 7: Verify ODG file integration works"""
    try:
        from aeprs.spectra.integration import ODGSPECTRAIntegrator
        
        # Sample ODG content (simplified)
        sample_odg = '''<?xml version="1.0"?>
        <office:document-content>
            <office:body>
                <office:drawing>
                    <draw:page>
                        <draw:custom-shape>
                            <text:p>Start Process</text:p>
                        </draw:custom-shape>
                    </draw:page>
                </office:drawing>
            </office:body>
        </office:document-content>'''
        
        sample_config = {
            "nodes": [
                {
                    "id": "node1",
                    "name": "Start Process",
                    "type": "green",
                    "value": 120
                }
            ],
            "paths": []
        }
        
        integrator = ODGSPECTRAIntegrator(sample_odg, sample_config)
        structure = integrator.parse_odg_structure()
        
        assert structure is not None
        assert 'nodes' in structure
        
    except ImportError as e:
        pytest.skip(f"ODG integration not available: {e}")

if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])