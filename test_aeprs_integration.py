# test_aeprs_integration.py
"""
Integration tests for AEPRS with SPECTRA
"""

import pytest
import asyncio
import tempfile
import json
from datetime import datetime
from pathlib import Path

def test_aeprs_framework_initialization():
    """Test AEPRS framework can be initialized"""
    from aeprs.core.framework import AEPRSFramework
    
    framework = AEPRSFramework()
    assert framework is not None
    assert len(framework.patterns) > 0  # Should have default patterns

def test_error_pattern_matching():
    """Test error pattern matching functionality"""
    from aeprs.core.framework import AEPRSFramework, ErrorEvent, ErrorSeverity
    
    framework = AEPRSFramework()
    
    # Create a test error event
    error_event = ErrorEvent(
        timestamp=datetime.now(),
        source="test_script.py",
        message="SyntaxError: invalid syntax",
        severity=ErrorSeverity.HIGH
    )
    
    # Process the event
    result = asyncio.run(framework.process_event(error_event))
    
    assert result is not None
    assert len(result['matched_patterns']) > 0
    assert result['matched_patterns'][0].pattern_type.value == "syntax"

def test_collector_functionality():
    """Test error collector functionality"""
    from aeprs.core.collector import LogFileCollector, ErrorEvent
    
    # Create a temporary log file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        f.write("INFO: Application started\n")
        f.write("ERROR: Database connection failed\n")
        f.write("CRITICAL: System shutdown initiated\n")
        temp_log_path = f.name
    
    try:
        collector = LogFileCollector([temp_log_path])
        events = list(collector.collect())
        
        assert len(events) >= 2  # Should find ERROR and CRITICAL
        assert any("Database connection failed" in event.message for event in events)
        
    finally:
        Path(temp_log_path).unlink()

def test_analyzer_functionality():
    """Test error analyzer functionality"""
    from aeprs.core.analyzer import PatternAnalyzer, ErrorEvent, ErrorSeverity
    
    analyzer = PatternAnalyzer()
    
    # Create test events
    events = [
        ErrorEvent(
            timestamp=datetime.now(),
            source="test1.py",
            message="ModuleNotFoundError: No module named 'requests'",
            severity=ErrorSeverity.MEDIUM
        ),
        ErrorEvent(
            timestamp=datetime.now(),
            source="test2.py", 
            message="ModuleNotFoundError: No module named 'numpy'",
            severity=ErrorSeverity.MEDIUM
        )
    ]
    
    analysis = analyzer.analyze_patterns(events)
    
    assert analysis is not None
    assert 'pattern_frequency' in analysis
    assert 'recommendations' in analysis

def test_auto_debugger_functionality():
    """Test auto-debugger functionality"""
    from aeprs.core.auto_debugger import AutoDebugger, ErrorEvent, ErrorSeverity
    
    debugger = AutoDebugger()
    
    error_event = ErrorEvent(
        timestamp=datetime.now(),
        source="test_script.py",
        message="NameError: name 'undefined_variable' is not defined",
        severity=ErrorSeverity.HIGH
    )
    
    suggestions = debugger.generate_suggestions(error_event)
    
    assert suggestions is not None
    assert len(suggestions) > 0
    assert any("variable" in suggestion.lower() for suggestion in suggestions)

def test_spectra_neural_integration():
    """Test SPECTRA neural framework integration"""
    try:
        from aeprs.spectra.integration import SPECTRAIntegration
        from aeprs.core.framework import AEPRSFramework, ErrorEvent, ErrorSeverity
        
        framework = AEPRSFramework()
        spectra = SPECTRAIntegration(framework)
        
        # Test neural processing
        error_event = ErrorEvent(
            timestamp=datetime.now(),
            source="neural_test.py",
            message="RuntimeError: CUDA out of memory",
            severity=ErrorSeverity.HIGH
        )
        
        neural_result = spectra.process_through_neural_network(error_event)
        
        assert neural_result is not None
        assert 'consciousness_state' in neural_result
        assert 'memory_formation' in neural_result
        
    except ImportError:
        pytest.skip("SPECTRA integration not available")

def test_pattern_export_import():
    """Test pattern export and import functionality"""
    from aeprs.core.framework import AEPRSFramework, ErrorPattern, PatternType, ErrorSeverity
    
    framework = AEPRSFramework()
    
    # Add a custom pattern
    custom_pattern = ErrorPattern(
        id="test_pattern_001",
        pattern_type=PatternType.LOGIC,
        severity=ErrorSeverity.MEDIUM,
        description="Test pattern for export/import",
        regex_pattern=r"TestError: (.+)",
        solutions=["Fix the test error"]
    )
    
    framework.add_pattern(custom_pattern)
    
    # Export patterns
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        export_path = f.name
    
    try:
        framework.export_patterns(export_path)
        
        # Create new framework and import
        new_framework = AEPRSFramework()
        original_count = len(new_framework.patterns)
        
        new_framework.import_patterns(export_path)
        
        assert len(new_framework.patterns) > original_count
        assert "test_pattern_001" in new_framework.patterns
        
    finally:
        Path(export_path).unlink()

def test_real_time_monitoring():
    """Test real-time error monitoring"""
    from aeprs.core.framework import AEPRSFramework
    from aeprs.core.collector import LogFileCollector
    
    framework = AEPRSFramework()
    
    # Create temporary log file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        temp_log_path = f.name
    
    try:
        collector = LogFileCollector([temp_log_path])
        framework.register_collector(collector.collect)
        
        # Write some errors to the log file
        with open(temp_log_path, 'a') as f:
            f.write("ERROR: Test error 1\n")
            f.write("CRITICAL: Test error 2\n")
        
        # Start monitoring briefly
        collector.start()
        import time
        time.sleep(2)  # Let it collect
        collector.stop()
        
        # Check that events were collected
        stats = framework.get_statistics()
        assert stats['total_events'] > 0
        
    finally:
        Path(temp_log_path).unlink()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])