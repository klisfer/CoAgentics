"""
Timing utility for performance debugging and monitoring.
"""

import time
import logging
from typing import Dict, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class TimingTracker:
    """Track execution times for different operations."""
    
    def __init__(self):
        self.timings: Dict[str, float] = {}
        self.start_times: Dict[str, float] = {}
        self.total_start_time: Optional[float] = None
    
    def start_total_timer(self):
        """Start the total request timer."""
        self.total_start_time = time.time()
        logger.info("Starting total request timer")
    
    def start_timer(self, operation_name: str):
        """Start timing an operation."""
        start_time = time.time()
        self.start_times[operation_name] = start_time
        logger.info(f"Started timer for: {operation_name}")
        return start_time
    
    def end_timer(self, operation_name: str) -> float:
        """End timing an operation and return the duration."""
        if operation_name not in self.start_times:
            logger.warning(f"No start time found for operation: {operation_name}")
            return 0.0
        
        end_time = time.time()
        duration = end_time - self.start_times[operation_name]
        self.timings[operation_name] = duration
        
        logger.info(f"{operation_name}: {duration:.3f}s")
        
        # Clean up
        del self.start_times[operation_name]
        
        return duration
    
    def get_total_time(self) -> float:
        """Get total request time."""
        if self.total_start_time is None:
            return 0.0
        return time.time() - self.total_start_time
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all timings."""
        total_time = self.get_total_time()
        
        summary = {
            "total_time": round(total_time, 3),
            "operations": {k: round(v, 3) for k, v in self.timings.items()},
            "unaccounted_time": round(total_time - sum(self.timings.values()), 3)
        }
        
        logger.info(f"Timing Summary: {summary}")
        return summary
    
    @contextmanager
    def time_operation(self, operation_name: str):
        """Context manager for timing operations."""
        self.start_timer(operation_name)
        try:
            yield
        finally:
            self.end_timer(operation_name)

# Global timing tracker for the current request
_current_tracker: Optional[TimingTracker] = None

def get_current_tracker() -> TimingTracker:
    """Get the current timing tracker."""
    global _current_tracker
    if _current_tracker is None:
        _current_tracker = TimingTracker()
    return _current_tracker

def reset_tracker():
    """Reset the global timing tracker."""
    global _current_tracker
    _current_tracker = TimingTracker()

def start_request_timing():
    """Start timing a new request."""
    reset_tracker()
    tracker = get_current_tracker()
    tracker.start_total_timer()
    return tracker

@contextmanager
def time_operation(operation_name: str):
    """Context manager for timing operations using the global tracker."""
    tracker = get_current_tracker()
    with tracker.time_operation(operation_name):
        yield

def log_timing_summary() -> Dict[str, Any]:
    """Log and return timing summary."""
    tracker = get_current_tracker()
    return tracker.get_summary() 