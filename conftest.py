# conftest.py
"""
Pytest configuration and fixtures for AEPRS tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def sample_spectra_file(temp_dir):
    """Create a sample SPECTRA file for testing"""
    spectra_content = """
# SPECTRA Neural Framework

## Overview
The SPECTRA Neural Framework is a bio-inspired cognitive architecture.

## Components

1. **Perception Module**
   - Processes sensory input
   - Applies emotional coloration

2. **Memory Formation System**
   - Episodic memory
   - Semantic memory

3. **SPECTRA Core**
   - Decision making
   - Remorse calculation

4. **Additional modules...**
"""
    
    spectra_file = temp_dir / "SPECTRA"
    with open(spectra_file, 'w', encoding='utf-8') as f:
        f.write(spectra_content)
    
    return spectra_file

@pytest.fixture
def sample_log_file(temp_dir):
    """Create a sample log file for testing"""
    log_content = """
2024-01-01 10:00:00 INFO: Application started
2024-01-01 10:01:00 ERROR: Database connection failed
2024-01-01 10:02:00 WARNING: Retrying connection
2024-01-01 10:03:00 CRITICAL: System shutdown initiated
2024-01-01 10:04:00 INFO: Cleanup completed
"""
    
    log_file = temp_dir / "test.log"
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(log_content.strip())
    
    return log_file

@pytest.fixture
def aeprs_framework():
    """Create an AEPRS framework instance for testing"""
    from aeprs.core.framework import AEPRSFramework
    return AEPRSFramework()