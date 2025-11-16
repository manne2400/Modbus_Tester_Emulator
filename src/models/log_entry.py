"""LogEntry data model"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class LogDirection(Enum):
    """Log direction enumeration"""
    TX = "TX"
    RX = "RX"


@dataclass
class LogEntry:
    """Log entry for Modbus communication"""
    timestamp: datetime
    direction: LogDirection
    hex_string: str
    comment: str = ""
    error_description: Optional[str] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "direction": self.direction.value,
            "hex_string": self.hex_string,
            "comment": self.comment,
            "error_description": self.error_description,
            "session_id": self.session_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "LogEntry":
        """Create from dictionary"""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            direction=LogDirection(data["direction"]),
            hex_string=data["hex_string"],
            comment=data.get("comment", ""),
            error_description=data.get("error_description"),
            session_id=data.get("session_id")
        )
