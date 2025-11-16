"""ConnectionProfile data model"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ConnectionType(Enum):
    """Connection type enumeration"""
    TCP = "TCP"
    RTU = "RTU"


@dataclass
class ConnectionProfile:
    """Connection profile configuration"""
    name: str
    connection_type: ConnectionType
    
    # TCP specific fields
    host: Optional[str] = None
    port: Optional[int] = None
    
    # RTU specific fields
    port_name: Optional[str] = None  # COM port name
    baudrate: Optional[int] = None
    parity: Optional[str] = None  # 'N', 'E', 'O'
    stopbits: Optional[int] = None
    bytesize: Optional[int] = None  # Data bits
    
    # Common fields
    timeout: float = 3.0
    retries: int = 3
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "connection_type": self.connection_type.value,
            "host": self.host,
            "port": self.port,
            "port_name": self.port_name,
            "baudrate": self.baudrate,
            "parity": self.parity,
            "stopbits": self.stopbits,
            "bytesize": self.bytesize,
            "timeout": self.timeout,
            "retries": self.retries
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ConnectionProfile":
        """Create from dictionary"""
        return cls(
            name=data["name"],
            connection_type=ConnectionType(data["connection_type"]),
            host=data.get("host"),
            port=data.get("port"),
            port_name=data.get("port_name"),
            baudrate=data.get("baudrate"),
            parity=data.get("parity"),
            stopbits=data.get("stopbits"),
            bytesize=data.get("bytesize"),
            timeout=data.get("timeout", 3.0),
            retries=data.get("retries", 3)
        )
