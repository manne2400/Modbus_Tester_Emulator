"""TagDefinition data model"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AddressType(Enum):
    """Address type enumeration"""
    COIL = "Coil"
    DISCRETE_INPUT = "Discrete Input"
    HOLDING_REGISTER = "Holding Register"
    INPUT_REGISTER = "Input Register"


class DataType(Enum):
    """Data type enumeration
    
    Note: INT32 is also known as DINT (Double Integer) in PLC terminology.
    Both refer to a 32-bit signed integer using 2 Modbus registers.
    """
    BOOL = "BOOL"
    INT16 = "INT16"
    UINT16 = "UINT16"
    INT32 = "INT32"  # Also known as DINT (Double Integer) - 32-bit signed integer
    UINT32 = "UINT32"
    FLOAT32 = "FLOAT32"


class ByteOrder(Enum):
    """Byte order enumeration"""
    BIG_ENDIAN = "Big Endian"
    LITTLE_ENDIAN = "Little Endian"
    SWAPPED = "Swapped"


@dataclass
class TagDefinition:
    """Tag definition for data mapping"""
    address_type: AddressType
    address: int
    name: str = ""
    data_type: DataType = DataType.UINT16
    byte_order: ByteOrder = ByteOrder.BIG_ENDIAN
    scale_factor: float = 1.0
    scale_offset: float = 0.0
    unit: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "address_type": self.address_type.value,
            "address": self.address,
            "name": self.name,
            "data_type": self.data_type.value,
            "byte_order": self.byte_order.value,
            "scale_factor": self.scale_factor,
            "scale_offset": self.scale_offset,
            "unit": self.unit
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TagDefinition":
        """Create from dictionary"""
        return cls(
            address_type=AddressType(data["address_type"]),
            address=data["address"],
            name=data.get("name", ""),
            data_type=DataType(data.get("data_type", "UINT16")),
            byte_order=ByteOrder(data.get("byte_order", "Big Endian")),
            scale_factor=data.get("scale_factor", 1.0),
            scale_offset=data.get("scale_offset", 0.0),
            unit=data.get("unit", "")
        )
