"""Modbus RTU transport implementation"""
import time
from datetime import datetime
from queue import Queue
from threading import Lock
from typing import Optional
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
from src.models.connection_profile import ConnectionProfile, ConnectionType
from src.models.log_entry import LogEntry, LogDirection
from src.transport.base_transport import BaseTransport
from src.utils.hex_formatter import bytes_to_hex_string
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RtuTransport(BaseTransport):
    """Modbus RTU transport"""
    
    def __init__(self, profile: ConnectionProfile):
        """Initialize RTU transport"""
        if profile.connection_type != ConnectionType.RTU:
            raise ValueError("Profile must be RTU type")
        super().__init__(profile)
        self.client: Optional[ModbusSerialClient] = None
        self.request_lock = Lock()  # Ensure sequential requests on RTU bus
    
    def connect(self) -> bool:
        """Connect to Modbus RTU device"""
        try:
            if self.client and self.client.is_socket_open():
                self.disconnect()
            
            # Map parity string to pyserial format
            parity_map = {'N': 'N', 'E': 'E', 'O': 'O', None: 'N'}
            parity = parity_map.get(self.profile.parity, 'N')
            
            self.client = ModbusSerialClient(
                port=self.profile.port_name,
                baudrate=self.profile.baudrate or 9600,
                parity=parity,
                stopbits=self.profile.stopbits or 1,
                bytesize=self.profile.bytesize or 8,
                timeout=self.profile.timeout
            )
            
            if self.client.connect():
                self.is_connected = True
                logger.info(f"Connected to RTU {self.profile.port_name}")
                return True
            else:
                logger.error(f"Failed to connect to RTU {self.profile.port_name}")
                return False
        except Exception as e:
            logger.error(f"RTU connection error: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from Modbus RTU device"""
        if self.client:
            self.client.close()
            self.client = None
        self.is_connected = False
        logger.info("RTU disconnected")
    
    def _execute_request(self, func, *args, **kwargs):
        """Execute request with locking and logging"""
        if not self.is_connected or not self.client:
            return None, "Not connected"
        
        with self.request_lock:  # RTU requires sequential requests
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
