"""Modbus TCP transport implementation"""
import time
from datetime import datetime
from queue import Queue, Empty
from threading import Lock
from typing import Optional
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from src.models.connection_profile import ConnectionProfile, ConnectionType
from src.models.log_entry import LogEntry, LogDirection
from src.transport.base_transport import BaseTransport
from src.utils.hex_formatter import bytes_to_hex_string
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TcpTransport(BaseTransport):
    """Modbus TCP transport"""
    
    def __init__(self, profile: ConnectionProfile):
        """Initialize TCP transport"""
        if profile.connection_type != ConnectionType.TCP:
            raise ValueError("Profile must be TCP type")
        super().__init__(profile)
        self.client: Optional[ModbusTcpClient] = None
        self.request_lock = Lock()  # Ensure one request at a time per connection
        self.request_queue: Queue = Queue()
    
    def connect(self) -> bool:
        """Connect to Modbus TCP device"""
        try:
            if self.client and self.client.is_socket_open():
                self.disconnect()
            
            self.client = ModbusTcpClient(
                host=self.profile.host,
                port=self.profile.port or 502,
                timeout=self.profile.timeout
            )
            
            if self.client.connect():
                self.is_connected = True
                logger.info(f"Connected to TCP {self.profile.host}:{self.profile.port}")
                return True
            else:
                logger.error(f"Failed to connect to TCP {self.profile.host}:{self.profile.port}")
                return False
        except Exception as e:
            logger.error(f"TCP connection error: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from Modbus TCP device"""
        if self.client:
            self.client.close()
            self.client = None
        self.is_connected = False
        logger.info("TCP disconnected")
    
    def _execute_request(self, func, *args, **kwargs):
        """Execute request with locking and logging"""
        if not self.is_connected or not self.client:
            return None, "Not connected"
        
        with self.request_lock:
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                response_time = (time.time() - start_time) * 1000
                
                if result.isError():
                    error_msg = f"Modbus error: {result}"
                    logger.error(error_msg)
                    return None, error_msg
                
                # Log response
                if hasattr(result, 'bits') or hasattr(result, 'registers'):
                    # Create log entry for response
                    hex_data = []
                    if hasattr(result, 'bits'):
                        hex_data = [1 if b else 0 for b in result.bits]
                    elif hasattr(result, 'registers'):
                        hex_data = result.registers
                    
                    log_entry = LogEntry(
                        timestamp=datetime.now(),
                        direction=LogDirection.RX,
                        hex_string=bytes_to_hex_string(hex_data),
                        comment=f"Response: {len(hex_data)} values, {response_time:.2f}ms"
                    )
                    self._log(log_entry)
                
                return result, None
            except ModbusException as e:
                error_msg = f"Modbus exception: {e}"
                logger.error(error_msg)
                return None, error_msg
            except Exception as e:
                error_msg = f"Request error: {e}"
                logger.error(error_msg)
                return None, error_msg
    
    def read_coils(
        self,
        slave_id: int,
        start_address: int,
        quantity: int
    ) -> tuple[Optional[list[bool]], Optional[str]]:
        """Read coils"""
        result, error = self._execute_request(
            self.client.read_coils,
            start_address,
            count=quantity,
            device_id=slave_id
        )
        if error:
            return None, error
        return result.bits if result else None, None
    
    def read_discrete_inputs(
        self,
        slave_id: int,
        start_address: int,
        quantity: int
    ) -> tuple[Optional[list[bool]], Optional[str]]:
        """Read discrete inputs"""
        result, error = self._execute_request(
            self.client.read_discrete_inputs,
            start_address,
            count=quantity,
            device_id=slave_id
        )
        if error:
            return None, error
        return result.bits if result else None, None
    
    def read_holding_registers(
        self,
        slave_id: int,
        start_address: int,
        quantity: int
    ) -> tuple[Optional[list[int]], Optional[str]]:
        """Read holding registers"""
        result, error = self._execute_request(
            self.client.read_holding_registers,
            start_address,
            count=quantity,
            device_id=slave_id
        )
        if error:
            return None, error
        return result.registers if result else None, None
    
    def read_input_registers(
        self,
        slave_id: int,
        start_address: int,
        quantity: int
    ) -> tuple[Optional[list[int]], Optional[str]]:
        """Read input registers"""
        result, error = self._execute_request(
            self.client.read_input_registers,
            start_address,
            count=quantity,
            device_id=slave_id
        )
        if error:
            return None, error
        return result.registers if result else None, None
    
    def write_single_coil(
        self,
        slave_id: int,
        address: int,
        value: bool
    ) -> tuple[bool, Optional[str]]:
        """Write single coil"""
        result, error = self._execute_request(
            self.client.write_coil,
            address,
            value,
            device_id=slave_id
        )
        if error:
            return False, error
        return True, None
    
    def write_single_register(
        self,
        slave_id: int,
        address: int,
        value: int
    ) -> tuple[bool, Optional[str]]:
        """Write single register"""
        result, error = self._execute_request(
            self.client.write_register,
            address,
            value,
            device_id=slave_id
        )
        if error:
            return False, error
        return True, None
    
    def write_multiple_coils(
        self,
        slave_id: int,
        start_address: int,
        values: list[bool]
    ) -> tuple[bool, Optional[str]]:
        """Write multiple coils"""
        result, error = self._execute_request(
            self.client.write_coils,
            start_address,
            values,
            device_id=slave_id
        )
        if error:
            return False, error
        return True, None
    
    def write_multiple_registers(
        self,
        slave_id: int,
        start_address: int,
        values: list[int]
    ) -> tuple[bool, Optional[str]]:
        """Write multiple registers"""
        result, error = self._execute_request(
            self.client.write_registers,
            start_address,
            values,
            device_id=slave_id
        )
        if error:
            return False, error
        return True, None
