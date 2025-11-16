"""Base transport interface"""
from abc import ABC, abstractmethod
from typing import Optional, Callable
from src.models.connection_profile import ConnectionProfile
from src.models.log_entry import LogEntry


class BaseTransport(ABC):
    """Abstract base class for Modbus transport layers"""
    
    def __init__(self, profile: ConnectionProfile):
        """Initialize transport with connection profile"""
        self.profile = profile
        self.is_connected = False
        self.log_callback: Optional[Callable[[LogEntry], None]] = None
    
    def set_log_callback(self, callback: Callable[[LogEntry], None]):
        """Set callback for logging"""
        self.log_callback = callback
    
    def _log(self, entry: LogEntry):
        """Internal logging helper"""
        if self.log_callback:
            self.log_callback(entry)
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to Modbus device"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnect from Modbus device"""
        pass
    
    @abstractmethod
    def read_coils(
        self,
        slave_id: int,
        start_address: int,
        quantity: int
    ) -> tuple[Optional[list[bool]], Optional[str]]:
        """Read coils (function code 01)"""
        pass
    
    @abstractmethod
    def read_discrete_inputs(
        self,
        slave_id: int,
        start_address: int,
        quantity: int
    ) -> tuple[Optional[list[bool]], Optional[str]]:
        """Read discrete inputs (function code 02)"""
        pass
    
    @abstractmethod
    def read_holding_registers(
        self,
        slave_id: int,
        start_address: int,
        quantity: int
    ) -> tuple[Optional[list[int]], Optional[str]]:
        """Read holding registers (function code 03)"""
        pass
    
    @abstractmethod
    def read_input_registers(
        self,
        slave_id: int,
        start_address: int,
        quantity: int
    ) -> tuple[Optional[list[int]], Optional[str]]:
        """Read input registers (function code 04)"""
        pass
    
    @abstractmethod
    def write_single_coil(
        self,
        slave_id: int,
        address: int,
        value: bool
    ) -> tuple[bool, Optional[str]]:
        """Write single coil (function code 05)"""
        pass
    
    @abstractmethod
    def write_single_register(
        self,
        slave_id: int,
        address: int,
        value: int
    ) -> tuple[bool, Optional[str]]:
        """Write single register (function code 06)"""
        pass
    
    @abstractmethod
    def write_multiple_coils(
        self,
        slave_id: int,
        start_address: int,
        values: list[bool]
    ) -> tuple[bool, Optional[str]]:
        """Write multiple coils (function code 15)"""
        pass
    
    @abstractmethod
    def write_multiple_registers(
        self,
        slave_id: int,
        start_address: int,
        values: list[int]
    ) -> tuple[bool, Optional[str]]:
        """Write multiple registers (function code 16)"""
        pass
