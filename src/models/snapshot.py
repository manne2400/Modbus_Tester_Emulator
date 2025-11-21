"""Snapshot data model for capturing device state"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class SnapshotValueStatus(Enum):
    """Status of a snapshot value"""
    OK = "OK"
    TIMEOUT = "Timeout"
    ERROR = "Error"
    NOT_AVAILABLE = "Not Available"


@dataclass
class SnapshotValue:
    """A single value in a snapshot"""
    address: int
    tag_id: Optional[str] = None  # Tag name or ID
    tag_name: Optional[str] = None
    raw_value: Optional[Any] = None
    scaled_value: Optional[float] = None
    status: SnapshotValueStatus = SnapshotValueStatus.OK
    unit: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "address": self.address,
            "tag_id": self.tag_id,
            "tag_name": self.tag_name,
            "raw_value": self.raw_value,
            "scaled_value": self.scaled_value,
            "status": self.status.value,
            "unit": self.unit
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SnapshotValue":
        """Create from dictionary"""
        return cls(
            address=data["address"],
            tag_id=data.get("tag_id"),
            tag_name=data.get("tag_name"),
            raw_value=data.get("raw_value"),
            scaled_value=data.get("scaled_value"),
            status=SnapshotValueStatus(data.get("status", "OK")),
            unit=data.get("unit")
        )


@dataclass
class SnapshotSession:
    """Snapshot data for a single session"""
    session_id: str
    session_name: str
    connection_name: Optional[str] = None
    slave_id: Optional[int] = None
    function_code: Optional[int] = None
    values: List[SnapshotValue] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "session_id": self.session_id,
            "session_name": self.session_name,
            "connection_name": self.connection_name,
            "slave_id": self.slave_id,
            "function_code": self.function_code,
            "values": [v.to_dict() for v in self.values]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SnapshotSession":
        """Create from dictionary"""
        return cls(
            session_id=data["session_id"],
            session_name=data["session_name"],
            connection_name=data.get("connection_name"),
            slave_id=data.get("slave_id"),
            function_code=data.get("function_code"),
            values=[SnapshotValue.from_dict(v) for v in data.get("values", [])]
        )


@dataclass
class Snapshot:
    """Snapshot of device state at a point in time"""
    id: str
    name: str
    timestamp: datetime
    note: Optional[str] = None
    sessions: List[SnapshotSession] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "timestamp": self.timestamp.isoformat(),
            "note": self.note,
            "sessions": [s.to_dict() for s in self.sessions]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        """Create from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            note=data.get("note"),
            sessions=[SnapshotSession.from_dict(s) for s in data.get("sessions", [])]
        )
    
    def get_value_count(self) -> int:
        """Get total number of values in snapshot"""
        return sum(len(session.values) for session in self.sessions)
    
    def get_session(self, session_id: str) -> Optional[SnapshotSession]:
        """Get session by ID"""
        return next((s for s in self.sessions if s.session_id == session_id), None)

