"""Diagnostics engine for analyzing trace entries"""
from typing import List, Dict, Optional
from collections import defaultdict
from src.models.trace_entry import TraceEntry, TraceStatus, TraceDirection
from src.application.trace_store import TraceStore
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DiagnosticFinding:
    """A diagnostic finding/issue"""
    
    def __init__(self, severity: str, category: str, message: str, details: Optional[str] = None):
        """Initialize diagnostic finding
        
        Args:
            severity: "Error", "Warning", or "Info"
            category: Category of issue (e.g., "Timeout", "CRC Error", "ID Conflict")
            message: Short message describing the issue
            details: Optional detailed description
        """
        self.severity = severity
        self.category = category
        self.message = message
        self.details = details
    
    def __str__(self):
        return f"[{self.severity}] {self.category}: {self.message}"


class DiagnosticsEngine:
    """Engine for analyzing trace entries and producing diagnostics"""
    
    def __init__(self, trace_store: TraceStore):
        """Initialize diagnostics engine"""
        self.trace_store = trace_store
    
    def analyze(self) -> List[DiagnosticFinding]:
        """Analyze trace entries and return list of findings"""
        findings = []
        
        entries = self.trace_store.get_all_entries()
        if not entries:
            return findings
        
        # Group entries by session and connection
        entries_by_session = defaultdict(list)
        entries_by_connection = defaultdict(list)
        entries_by_slave = defaultdict(list)
        
        for entry in entries:
            if entry.session_id:
                entries_by_session[entry.session_id].append(entry)
            if entry.connection_name:
                entries_by_connection[entry.connection_name].append(entry)
            if entry.slave_id is not None:
                entries_by_slave[entry.slave_id].append(entry)
        
        # Check for timeouts per slave
        findings.extend(self._check_timeouts(entries_by_slave))
        
        # Check for CRC errors per connection
        findings.extend(self._check_crc_errors(entries_by_connection))
        
        # Check for ID conflicts (same slave ID on different connections)
        findings.extend(self._check_id_conflicts(entries_by_slave, entries))
        
        # Check for repeated exceptions
        findings.extend(self._check_repeated_exceptions(entries_by_slave))
        
        # Check for high error rates
        findings.extend(self._check_error_rates(entries_by_session))
        
        # Check for slow response times
        findings.extend(self._check_slow_responses(entries_by_session))
        
        return findings
    
    def _check_timeouts(self, entries_by_slave: Dict[int, List[TraceEntry]]) -> List[DiagnosticFinding]:
        """Check for excessive timeouts per slave"""
        findings = []
        timeout_threshold = 5  # Warn if more than 5 timeouts
        
        for slave_id, entries in entries_by_slave.items():
            timeout_count = sum(1 for e in entries if e.status == TraceStatus.TIMEOUT)
            total_requests = sum(1 for e in entries if e.direction == TraceDirection.TX)
            
            if timeout_count >= timeout_threshold:
                severity = "Error" if timeout_count > timeout_threshold * 2 else "Warning"
                findings.append(DiagnosticFinding(
                    severity=severity,
                    category="Timeout",
                    message=f"Many timeouts on Slave {slave_id} ({timeout_count} timeouts out of {total_requests} requests)",
                    details=f"Check cable, slave ID, baudrate or network connection. {timeout_count} timeout errors recorded."
                ))
        
        return findings
    
    def _check_crc_errors(self, entries_by_connection: Dict[str, List[TraceEntry]]) -> List[DiagnosticFinding]:
        """Check for CRC errors per connection"""
        findings = []
        crc_threshold = 3  # Warn if more than 3 CRC errors
        
        for connection_name, entries in entries_by_connection.items():
            crc_count = sum(1 for e in entries if e.status == TraceStatus.CRC_ERROR)
            
            if crc_count >= crc_threshold:
                severity = "Error" if crc_count > crc_threshold * 2 else "Warning"
                findings.append(DiagnosticFinding(
                    severity=severity,
                    category="CRC Error",
                    message=f"Multiple CRC errors on {connection_name} ({crc_count} errors)",
                    details=f"Check cable quality, electrical noise or baudrate settings. {crc_count} CRC errors recorded."
                ))
        
        return findings
    
    def _check_id_conflicts(self, entries_by_slave: Dict[int, List[TraceEntry]], all_entries: List[TraceEntry]) -> List[DiagnosticFinding]:
        """Check for ID conflicts (same slave ID on different connections)"""
        findings = []
        
        # Group by slave ID and find unique connections
        slave_connections = defaultdict(set)
        for entry in all_entries:
            if entry.slave_id is not None and entry.connection_name:
                slave_connections[entry.slave_id].add(entry.connection_name)
        
        # Check for conflicts
        for slave_id, connections in slave_connections.items():
            if len(connections) > 1:
                findings.append(DiagnosticFinding(
                    severity="Warning",
                    category="ID Conflict",
                    message=f"Multiple connections use the same Slave ID {slave_id}",
                    details=f"Slave ID {slave_id} is used on: {', '.join(connections)}. This can cause conflicts."
                ))
        
        return findings
    
    def _check_repeated_exceptions(self, entries_by_slave: Dict[int, List[TraceEntry]]) -> List[DiagnosticFinding]:
        """Check for repeated exceptions"""
        findings = []
        exception_threshold = 3  # Warn if more than 3 exceptions
        
        for slave_id, entries in entries_by_slave.items():
            exceptions = [e for e in entries if e.status == TraceStatus.EXCEPTION]
            
            if len(exceptions) >= exception_threshold:
                # Group by exception code
                exception_codes = defaultdict(int)
                for e in exceptions:
                    if e.exception_code:
                        exception_codes[e.exception_code] += 1
                
                # Check for specific exception codes
                for exc_code, count in exception_codes.items():
                    if count >= exception_threshold:
                        exc_name = self._get_exception_name(exc_code)
                        findings.append(DiagnosticFinding(
                            severity="Error",
                            category="Exception",
                            message=f"Consistent Exception {exc_code} ({exc_name}) on Slave {slave_id}",
                            details=f"{count} times Exception {exc_code}. Wrong function code or device does not support it."
                        ))
        
        return findings
    
    def _check_error_rates(self, entries_by_session: Dict[str, List[TraceEntry]]) -> List[DiagnosticFinding]:
        """Check for high error rates per session"""
        findings = []
        error_rate_threshold = 0.3  # Warn if more than 30% errors
        
        for session_id, entries in entries_by_session.items():
            total = len(entries)
            errors = sum(1 for e in entries if e.status != TraceStatus.OK)
            
            if total > 10:  # Only check if we have enough data
                error_rate = errors / total
                if error_rate >= error_rate_threshold:
                    findings.append(DiagnosticFinding(
                        severity="Warning",
                        category="Error Rate",
                        message=f"High error rate on session '{session_id}' ({errors}/{total} = {error_rate*100:.1f}%)",
                        details=f"Over {error_rate_threshold*100}% of requests are failing. Check connection and configuration."
                    ))
        
        return findings
    
    def _check_slow_responses(self, entries_by_session: Dict[str, List[TraceEntry]]) -> List[DiagnosticFinding]:
        """Check for slow response times"""
        findings = []
        slow_threshold_ms = 1000  # Warn if response time > 1 second
        
        for session_id, entries in entries_by_session.items():
            response_times = [e.response_time_ms for e in entries if e.response_time_ms is not None]
            
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                max_time = max(response_times)
                
                if max_time > slow_threshold_ms:
                    findings.append(DiagnosticFinding(
                        severity="Info",
                        category="Performance",
                        message=f"Slow response time on session '{session_id}' (max: {max_time:.0f}ms, avg: {avg_time:.0f}ms)",
                        details=f"Maximum response time is {max_time:.0f}ms. Check network connection or device load."
                    ))
        
        return findings
    
    def _get_exception_name(self, exception_code: int) -> str:
        """Get human-readable exception name"""
        exception_names = {
            1: "Illegal Function",
            2: "Illegal Data Address",
            3: "Illegal Data Value",
            4: "Slave Device Failure",
            5: "Acknowledge",
            6: "Slave Device Busy",
            7: "Negative Acknowledge",
            8: "Memory Parity Error"
        }
        return exception_names.get(exception_code, f"Unknown ({exception_code})")

