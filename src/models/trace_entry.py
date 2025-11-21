"""TraceEntry data model for frame/trace analysis"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List


class TraceDirection(Enum):
    """Trace direction enumeration"""
    TX = "TX"
    RX = "RX"


class TraceStatus(Enum):
    """Trace status enumeration"""
    OK = "OK"
    TIMEOUT = "Timeout"
    CRC_ERROR = "CRC Error"
    EXCEPTION = "Exception"
    ERROR = "Error"
    NO_RESPONSE = "No Response"


@dataclass
class TraceEntry:
    """Trace entry for Modbus frame analysis"""
    timestamp: datetime
    direction: TraceDirection
    session_id: Optional[str] = None
    connection_name: Optional[str] = None
    slave_id: Optional[int] = None
    function_code: Optional[int] = None
    start_address: Optional[int] = None
    quantity: Optional[int] = None
    raw_bytes: Optional[bytes] = None
    raw_hex_string: Optional[str] = None
    decoded_info: Optional[str] = None  # Human-readable description
    status: TraceStatus = TraceStatus.OK
    error_message: Optional[str] = None
    exception_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    address_range: Optional[str] = None  # e.g., "40001-40010"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "direction": self.direction.value,
            "session_id": self.session_id,
            "connection_name": self.connection_name,
            "slave_id": self.slave_id,
            "function_code": self.function_code,
            "start_address": self.start_address,
            "quantity": self.quantity,
            "raw_hex_string": self.raw_hex_string,
            "decoded_info": self.decoded_info,
            "status": self.status.value,
            "error_message": self.error_message,
            "exception_code": self.exception_code,
            "response_time_ms": self.response_time_ms,
            "address_range": self.address_range
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TraceEntry":
        """Create from dictionary"""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            direction=TraceDirection(data["direction"]),
            session_id=data.get("session_id"),
            connection_name=data.get("connection_name"),
            slave_id=data.get("slave_id"),
            function_code=data.get("function_code"),
            start_address=data.get("start_address"),
            quantity=data.get("quantity"),
            raw_hex_string=data.get("raw_hex_string"),
            decoded_info=data.get("decoded_info"),
            status=TraceStatus(data.get("status", "OK")),
            error_message=data.get("error_message"),
            exception_code=data.get("exception_code"),
            response_time_ms=data.get("response_time_ms"),
            address_range=data.get("address_range")
        )
    
    def get_address_range_str(self) -> str:
        """Get address range as string"""
        if self.address_range:
            return self.address_range
        if self.start_address is not None and self.quantity is not None:
            # Convert to Modbus address notation (40001, 30001, etc.)
            if self.function_code == 3:  # Holding Registers
                start = 40001 + self.start_address
                end = 40001 + self.start_address + self.quantity - 1
                return f"{start}-{end}"
            elif self.function_code == 4:  # Input Registers
                start = 30001 + self.start_address
                end = 30001 + self.start_address + self.quantity - 1
                return f"{start}-{end}"
            elif self.function_code == 1:  # Coils
                start = 1 + self.start_address
                end = 1 + self.start_address + self.quantity - 1
                return f"{start}-{end}"
            elif self.function_code == 2:  # Discrete Inputs
                start = 10001 + self.start_address
                end = 10001 + self.start_address + self.quantity - 1
                return f"{start}-{end}"
            else:
                return f"{self.start_address}-{self.start_address + self.quantity - 1}"
        return "N/A"
    
    def get_function_name(self) -> str:
        """Get human-readable function code name"""
        function_names = {
            1: "Read Coils",
            2: "Read Discrete Inputs",
            3: "Read Holding Registers",
            4: "Read Input Registers",
            5: "Write Single Coil",
            6: "Write Single Register",
            15: "Write Multiple Coils",
            16: "Write Multiple Registers"
        }
        if self.function_code:
            return function_names.get(self.function_code, f"Function {self.function_code}")
        return "Unknown"

