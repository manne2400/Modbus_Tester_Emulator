"""PollResult data model"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Any
from enum import Enum


class PollStatus(Enum):
    """Poll status enumeration"""
    OK = "OK"
    TIMEOUT = "Timeout"
    ERROR = "Error"
    CRC_ERROR = "CRC Error"
    PROTOCOL_ERROR = "Protocol Error"
    EXCEPTION = "Exception"


@dataclass
class PollResult:
    """Result from a Modbus poll operation"""
    timestamp: datetime
    session_id: str
    raw_data: List[int]  # Raw register values or coil states
    decoded_values: List[Any]  # Decoded values based on data type
    status: PollStatus
    exception_code: Optional[int] = None
    error_message: Optional[str] = None
    response_time_ms: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "raw_data": self.raw_data,
            "decoded_values": self.decoded_values,
            "status": self.status.value,
            "exception_code": self.exception_code,
            "error_message": self.error_message,
            "response_time_ms": self.response_time_ms
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PollResult":
        """Create from dictionary"""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            session_id=data["session_id"],
            raw_data=data["raw_data"],
            decoded_values=data["decoded_values"],
            status=PollStatus(data["status"]),
            exception_code=data.get("exception_code"),
            error_message=data.get("error_message"),
            response_time_ms=data.get("response_time_ms")
        )
