"""SessionDefinition data model"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from .tag_definition import TagDefinition


class SessionStatus(Enum):
    """Session status enumeration"""
    STOPPED = "Stopped"
    RUNNING = "Running"
    ERROR = "Error"


@dataclass
class SessionDefinition:
    """Session definition configuration"""
    name: str
    connection_profile_name: str
    slave_id: int
    function_code: int
    start_address: int
    quantity: int
    poll_interval_ms: int = 1000
    
    tags: List[TagDefinition] = field(default_factory=list)
    status: SessionStatus = SessionStatus.STOPPED
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "connection_profile_name": self.connection_profile_name,
            "slave_id": self.slave_id,
            "function_code": self.function_code,
            "start_address": self.start_address,
            "quantity": self.quantity,
            "poll_interval_ms": self.poll_interval_ms,
            "tags": [tag.to_dict() for tag in self.tags],
            "status": self.status.value
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SessionDefinition":
        """Create from dictionary"""
        return cls(
            name=data["name"],
            connection_profile_name=data["connection_profile_name"],
            slave_id=data["slave_id"],
            function_code=data["function_code"],
            start_address=data["start_address"],
            quantity=data["quantity"],
            poll_interval_ms=data.get("poll_interval_ms", 1000),
            tags=[TagDefinition.from_dict(tag) for tag in data.get("tags", [])],
            status=SessionStatus(data.get("status", "Stopped"))
        )
