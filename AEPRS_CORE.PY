"""
AEPRS Core Framework
Adaptive Error Pattern Recognition System main framework
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import threading
from concurrent.futures import ThreadPoolExecutor

class ErrorSeverity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class PatternType(Enum):
    SYNTAX = "syntax"
    RUNTIME = "runtime"
    LOGIC = "logic"
    PERFORMANCE = "performance"
    SECURITY = "security"

@dataclass
class ErrorPattern:
    """Represents an identified error pattern"""
    id: str
    pattern_type: PatternType
    severity: ErrorSeverity
    description: str
    regex_pattern: str
    frequency: int = 0
    last_seen: datetime = field(default_factory=datetime.now)
    solutions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ErrorEvent:
    """Represents a single error event"""
    timestamp: datetime
    source: str
    message: str
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    resolved: bool = False

class AEPRSFramework:
    """Main AEPRS Framework class"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.patterns: Dict[str, ErrorPattern] = {}
        self.events: List[ErrorEvent] = []
        self.collectors: List[Callable] = []
        self.analyzers: List[Callable] = []
        self.auto_debuggers: List[Callable] = []
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._running = False
        self._lock = threading.RLock()
        
        # Initialize components
        self._setup_logging()
        self._load_default_patterns()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = self.config.get('log_level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _load_default_patterns(self):
        """Load default error patterns"""
        default_patterns = [
            ErrorPattern(
                id="py_syntax_001",
                pattern_type=PatternType.SYNTAX,
                severity=ErrorSeverity.HIGH,
                description="Python syntax error",
                regex_pattern=r"SyntaxError: (.+)",
                solutions=["Check syntax near the error location", "Verify proper indentation"]
            ),
            ErrorPattern(
                id="py_import_001",
                pattern_type=PatternType.RUNTIME,
                severity=ErrorSeverity.MEDIUM,
                description="Module import error",
                regex_pattern=r"ModuleNotFoundError: No module named '(.+)'",
                solutions=["Install missing module", "Check module name spelling", "Verify PYTHONPATH"]
            ),
            ErrorPattern(
                id="py_attr_001",
                pattern_type=PatternType.RUNTIME,
                severity=ErrorSeverity.MEDIUM,
                description="Attribute error",
                regex_pattern=r"AttributeError: '(.+)' object has no attribute '(.+)'",
                solutions=["Check attribute name", "Verify object type", "Check documentation"]
            )
        ]
        
        for pattern in default_patterns:
            self.patterns[pattern.id] = pattern
    
    def register_collector(self, collector: Callable):
        """Register an error collector"""
        with self._lock:
            self.collectors.append(collector)
            self.logger.info(f"Registered collector: {collector.__name__}")
    
    def register_analyzer(self, analyzer: Callable):
        """Register an error analyzer"""
        with self._lock:
            self.analyzers.append(analyzer)
            self.logger.info(f"Registered analyzer: {analyzer.__name__}")
    
    def register_auto_debugger(self, debugger: Callable):
        """Register an auto-debugger"""
        with self._lock:
            self.auto_debuggers.append(debugger)
            self.logger.info(f"Registered auto-debugger: {debugger.__name__}")
    
    def add_pattern(self, pattern: ErrorPattern):
        """Add a new error pattern"""
        with self._lock:
            self.patterns[pattern.id] = pattern
            self.logger.info(f"Added pattern: {pattern.id}")
    
    def remove_pattern(self, pattern_id: str):
        """Remove an error pattern"""
        with self._lock:
            if pattern_id in self.patterns:
                del self.patterns[pattern_id]
                self.logger.info(f"Removed pattern: {pattern_id}")
    
    def add_event(self, event: ErrorEvent):
        """Add a new error event"""
        with self._lock:
            self.events.append(event)
            self.logger.debug(f"Added event from {event.source}: {event.message[:100]}...")
    
    async def process_event(self, event: ErrorEvent) -> Dict[str, Any]:
        """Process a single error event"""
        results = {
            'event': event,
            'matched_patterns': [],
            'analysis_results': [],
            'debug_suggestions': []
        }
        
        # Pattern matching
        for pattern in self.patterns.values():
            if self._match_pattern(event, pattern):
                results['matched_patterns'].append(pattern)
                pattern.frequency += 1
                pattern.last_seen = datetime.now()
        
        # Run analyzers
        for analyzer in self.analyzers:
            try:
                analysis = await self._run_async(analyzer, event, results['matched_patterns'])
                if analysis:
                    results['analysis_results'].append(analysis)
            except Exception as e:
                self.logger.error(f"Analyzer {analyzer.__name__} failed: {e}")
        
        # Run auto-debuggers
        for debugger in self.auto_debuggers:
            try:
                suggestions = await self._run_async(debugger, event, results)
                if suggestions:
                    results['debug_suggestions'].extend(suggestions)
            except Exception as e:
                self.logger.error(f"Auto-debugger {debugger.__name__} failed: {e}")
        
        return results
    
    def _match_pattern(self, event: ErrorEvent, pattern: ErrorPattern) -> bool:
        """Check if an event matches a pattern"""
        import re
        try:
            return bool(re.search(pattern.regex_pattern, event.message, re.IGNORECASE))
        except re.error:
            self.logger.warning(f"Invalid regex in pattern {pattern.id}")
            return False
    
    async def _run_async(self, func: Callable, *args) -> Any:
        """Run a function asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args)
    
    async def start(self):
        """Start the AEPRS framework"""
        self._running = True
        self.logger.info("AEPRS Framework started")
        
        # Start collectors
        collector_tasks = []
        for collector in self.collectors:
            task = asyncio.create_task(self._run_collector(collector))
            collector_tasks.append(task)
        
        # Wait for all tasks
        if collector_tasks:
            await asyncio.gather(*collector_tasks, return_exceptions=True)
    
    async def _run_collector(self, collector: Callable):
        """Run a collector continuously"""
        while self._running:
            try:
                events = await self._run_async(collector)
                if events:
                    for event in events:
                        self.add_event(event)
                        await self.process_event(event)
            except Exception as e:
                self.logger.error(f"Collector {collector.__name__} failed: {e}")
            
            await asyncio.sleep(1)  # Prevent tight loop
    
    def stop(self):
        """Stop the AEPRS framework"""
        self._running = False
        self.executor.shutdown(wait=True)
        self.logger.info("AEPRS Framework stopped")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get framework statistics"""
        with self._lock:
            return {
                'total_patterns': len(self.patterns),
                'total_events': len(self.events),
                'active_collectors': len(self.collectors),
                'active_analyzers': len(self.analyzers),
                'active_debuggers': len(self.auto_debuggers),
                'pattern_frequencies': {
                    pid: pattern.frequency 
                    for pid, pattern in self.patterns.items()
                }
            }
    
    def export_patterns(self, filepath: str):
        """Export patterns to JSON file"""
        patterns_data = {}
        for pid, pattern in self.patterns.items():
            patterns_data[pid] = {
                'pattern_type': pattern.pattern_type.value,
                'severity': pattern.severity.value,
                'description': pattern.description,
                'regex_pattern': pattern.regex_pattern,
                'frequency': pattern.frequency,
                'last_seen': pattern.last_seen.isoformat(),
                'solutions': pattern.solutions,
                'metadata': pattern.metadata
            }
        
        with open(filepath, 'w') as f:
            json.dump(patterns_data, f, indent=2)
        
        self.logger.info(f"Exported {len(patterns_data)} patterns to {filepath}")
    
    def import_patterns(self, filepath: str):
        """Import patterns from JSON file"""
        with open(filepath, 'r') as f:
            patterns_data = json.load(f)
        
        imported_count = 0
        for pid, data in patterns_data.items():
            try:
                pattern = ErrorPattern(
                    id=pid,
                    pattern_type=PatternType(data['pattern_type']),
                    severity=ErrorSeverity(data['severity']),
                    description=data['description'],
                    regex_pattern=data['regex_pattern'],
                    frequency=data.get('frequency', 0),
                    last_seen=datetime.fromisoformat(data.get('last_seen', datetime.now().isoformat())),
                    solutions=data.get('solutions', []),
                    metadata=data.get('metadata', {})
                )
                self.add_pattern(pattern)
                imported_count += 1
            except Exception as e:
                self.logger.error(f"Failed to import pattern {pid}: {e}")
        
        self.logger.info(f"Imported {imported_count} patterns from {filepath}")