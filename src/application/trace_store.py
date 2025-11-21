"""TraceStore for managing trace entries"""
from collections import deque
from threading import Lock
from typing import List, Optional, Dict
from datetime import datetime
from src.models.trace_entry import TraceEntry, TraceDirection, TraceStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TraceStore:
    """Store for trace entries with rolling buffer"""
    
    def __init__(self, max_entries: int = 10000):
        """Initialize trace store
        
        Args:
            max_entries: Maximum number of entries to keep (default 10000)
        """
        self.max_entries = max_entries
        self.entries: deque = deque(maxlen=max_entries)
        self.lock = Lock()
    
    def add_entry(self, entry: TraceEntry):
        """Add a trace entry"""
        with self.lock:
            self.entries.append(entry)
            if len(self.entries) >= self.max_entries:
                logger.debug(f"Trace store reached max entries ({self.max_entries}), oldest entries will be removed")
    
    def get_entries(
        self,
        session_id: Optional[str] = None,
        connection_name: Optional[str] = None,
        direction: Optional[TraceDirection] = None,
        slave_id: Optional[int] = None,
        function_code: Optional[int] = None,
        status: Optional[TraceStatus] = None,
        errors_only: bool = False,
        limit: Optional[int] = None
    ) -> List[TraceEntry]:
        """Get filtered trace entries
        
        Args:
            session_id: Filter by session ID
            connection_name: Filter by connection name
            direction: Filter by direction (TX/RX)
            slave_id: Filter by slave ID
            function_code: Filter by function code
            status: Filter by status
            errors_only: Only return entries with errors
            limit: Maximum number of entries to return
        
        Returns:
            List of matching trace entries
        """
        with self.lock:
            result = list(self.entries)
        
        # Apply filters
        if session_id:
            result = [e for e in result if e.session_id == session_id]
        if connection_name:
            result = [e for e in result if e.connection_name == connection_name]
        if direction:
            result = [e for e in result if e.direction == direction]
        if slave_id is not None:
            result = [e for e in result if e.slave_id == slave_id]
        if function_code is not None:
            result = [e for e in result if e.function_code == function_code]
        if status:
            result = [e for e in result if e.status == status]
        if errors_only:
            result = [e for e in result if e.status != TraceStatus.OK]
        
        # Apply limit
        if limit:
            result = result[-limit:]  # Get most recent entries
        
        return result
    
    def get_all_entries(self) -> List[TraceEntry]:
        """Get all trace entries"""
        with self.lock:
            return list(self.entries)
    
    def clear(self):
        """Clear all trace entries"""
        with self.lock:
            self.entries.clear()
        logger.info("Trace store cleared")
    
    def get_statistics(self) -> Dict:
        """Get aggregated statistics"""
        with self.lock:
            entries = list(self.entries)
        
        if not entries:
            return {
                "total_entries": 0,
                "tx_count": 0,
                "rx_count": 0,
                "ok_count": 0,
                "error_count": 0,
                "timeout_count": 0,
                "crc_error_count": 0,
                "exception_count": 0,
                "avg_response_time_ms": 0.0,
                "timeouts_per_slave": {},
                "crc_errors_per_connection": {},
                "exceptions_per_slave": {}
            }
        
        stats = {
            "total_entries": len(entries),
            "tx_count": sum(1 for e in entries if e.direction == TraceDirection.TX),
            "rx_count": sum(1 for e in entries if e.direction == TraceDirection.RX),
            "ok_count": sum(1 for e in entries if e.status == TraceStatus.OK),
            "error_count": sum(1 for e in entries if e.status != TraceStatus.OK),
            "timeout_count": sum(1 for e in entries if e.status == TraceStatus.TIMEOUT),
            "crc_error_count": sum(1 for e in entries if e.status == TraceStatus.CRC_ERROR),
            "exception_count": sum(1 for e in entries if e.status == TraceStatus.EXCEPTION),
            "avg_response_time_ms": 0.0,
            "timeouts_per_slave": {},
            "crc_errors_per_connection": {},
            "exceptions_per_slave": {}
        }
        
        # Calculate average response time
        response_times = [e.response_time_ms for e in entries if e.response_time_ms is not None]
        if response_times:
            stats["avg_response_time_ms"] = sum(response_times) / len(response_times)
        
        # Timeouts per slave
        for entry in entries:
            if entry.status == TraceStatus.TIMEOUT and entry.slave_id is not None:
                stats["timeouts_per_slave"][entry.slave_id] = stats["timeouts_per_slave"].get(entry.slave_id, 0) + 1
        
        # CRC errors per connection
        for entry in entries:
            if entry.status == TraceStatus.CRC_ERROR and entry.connection_name:
                stats["crc_errors_per_connection"][entry.connection_name] = stats["crc_errors_per_connection"].get(entry.connection_name, 0) + 1
        
        # Exceptions per slave
        for entry in entries:
            if entry.status == TraceStatus.EXCEPTION and entry.slave_id is not None:
                stats["exceptions_per_slave"][entry.slave_id] = stats["exceptions_per_slave"].get(entry.slave_id, 0) + 1
        
        return stats
    
    def get_recent_entries(self, count: int = 100) -> List[TraceEntry]:
        """Get most recent entries"""
        with self.lock:
            return list(self.entries)[-count:]

