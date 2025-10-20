"""
AEPRS Error Collector
Collects errors from various sources
"""

import os
import sys
import logging
import traceback
import threading
import time
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime
from pathlib import Path
import re
import subprocess
import psutil

from .framework import ErrorEvent, ErrorSeverity

class ErrorCollector:
    """Base error collector class"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self._running = False
        self._thread = None
    
    def start(self):
        """Start the collector"""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._collect_loop)
            self._thread.daemon = True
            self._thread.start()
            self.logger.info(f"Started collector: {self.name}")
    
    def stop(self):
        """Stop the collector"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        self.logger.info(f"Stopped collector: {self.name}")
    
    def _collect_loop(self):
        """Main collection loop"""
        while self._running:
            try:
                events = list(self.collect())
                if events:
                    self.logger.debug(f"Collected {len(events)} events")
                time.sleep(self.config.get('interval', 5))
            except Exception as e:
                self.logger.error(f"Collection error: {e}")
                time.sleep(1)
    
    def collect(self) -> Generator[ErrorEvent, None, None]:
        """Collect errors - to be implemented by subclasses"""
        raise NotImplementedError

class LogFileCollector(ErrorCollector):
    """Collects errors from log files"""
    
    def __init__(self, log_paths: List[str], config: Optional[Dict[str, Any]] = None):
        super().__init__("LogFileCollector", config)
        self.log_paths = [Path(p) for p in log_paths]
        self.file_positions = {}
        self.error_patterns = [
            r'ERROR\s*:?\s*(.+)',
            r'CRITICAL\s*:?\s*(.+)',
            r'FATAL\s*:?\s*(.+)',
            r'Exception\s*:?\s*(.+)',
            r'Traceback\s*\(most recent call last\)',
        ]
    
    def collect(self) -> Generator[ErrorEvent, None, None]:
        """Collect errors from log files"""
        for log_path in self.log_paths:
            if not log_path.exists():
                continue
            
            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # Seek to last known position
                    last_pos = self.file_positions.get(str(log_path), 0)
                    f.seek(last_pos)
                    
                    lines = f.readlines()
                    if lines:
                        self.file_positions[str(log_path)] = f.tell()
                        
                        for line in lines:
                            event = self._parse_log_line(line.strip(), str(log_path))
                            if event:
                                yield event
            
            except Exception as e:
                self.logger.error(f"Error reading {log_path}: {e}")
    
    def _parse_log_line(self, line: str, source: str) -> Optional[ErrorEvent]:
        """Parse a