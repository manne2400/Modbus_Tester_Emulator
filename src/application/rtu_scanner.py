"""RTU Scanner for discovering Modbus RTU devices"""
import time
from dataclasses import dataclass
from typing import Optional, Callable
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
from src.protocol.function_codes import FunctionCode
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DeviceInfo:
    """Information about a discovered Modbus device"""
    device_id: int
    has_coils: bool = False
    has_discrete_inputs: bool = False
    has_holding_registers: bool = False
    has_input_registers: bool = False
    coil_addresses: list[int] = None
    discrete_input_addresses: list[int] = None
    holding_register_addresses: list[int] = None
    input_register_addresses: list[int] = None
    
    def __post_init__(self):
        if self.coil_addresses is None:
            self.coil_addresses = []
        if self.discrete_input_addresses is None:
            self.discrete_input_addresses = []
        if self.holding_register_addresses is None:
            self.holding_register_addresses = []
        if self.input_register_addresses is None:
            self.input_register_addresses = []


class RtuScanner:
    """Scans RTU bus for Modbus devices"""
    
    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        parity: str = 'N',
        stopbits: int = 1,
        bytesize: int = 8,
        timeout: float = 0.5
    ):
        """Initialize scanner with serial port settings"""
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.timeout = timeout
        self.client: Optional[ModbusSerialClient] = None
        self.is_scanning = False
        self.progress_callback: Optional[Callable[[int, int, str], None]] = None  # (current, total, status)
        self.result_callback: Optional[Callable[[DeviceInfo], None]] = None  # Called when device found
    
    def set_progress_callback(self, callback: Callable[[int, int, str], None]):
        """Set callback for progress updates (current, total, status)"""
        self.progress_callback = callback
    
    def set_result_callback(self, callback: Callable[[DeviceInfo], None]):
        """Set callback for when a device is found"""
        self.result_callback = callback
    
    def _update_progress(self, current: int, total: int, status: str = ""):
        """Update progress"""
        if self.progress_callback:
            self.progress_callback(current, total, status)
    
    def _notify_device_found(self, device_info: DeviceInfo):
        """Notify that a device was found"""
        if self.result_callback:
            self.result_callback(device_info)
    
    def connect(self) -> bool:
        """Connect to serial port"""
        try:
            if self.client and self.client.is_socket_open():
                self.disconnect()
            
            self.client = ModbusSerialClient(
                port=self.port,
                baudrate=self.baudrate,
                parity=self.parity,
                stopbits=self.stopbits,
                bytesize=self.bytesize,
                timeout=self.timeout
            )
            
            if self.client.connect():
                logger.info(f"Scanner connected to {self.port}")
                return True
            else:
                logger.error(f"Failed to connect scanner to {self.port}")
                return False
        except Exception as e:
            logger.error(f"Scanner connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from serial port"""
        if self.client:
            self.client.close()
            self.client = None
        logger.info("Scanner disconnected")
    
    def _test_read(
        self,
        device_id: int,
        function_code: int,
        start_address: int,
        quantity: int = 10
    ) -> tuple[bool, Optional[list]]:
        """Test reading from a device"""
        if not self.client or not self.client.is_socket_open():
            return False, None
        
        try:
            if function_code == FunctionCode.READ_COILS:
                result = self.client.read_coils(
                    start_address,
                    count=quantity,
                    device_id=device_id
                )
                if result and not result.isError():
                    return True, result.bits
            elif function_code == FunctionCode.READ_DISCRETE_INPUTS:
                result = self.client.read_discrete_inputs(
                    start_address,
                    count=quantity,
                    device_id=device_id
                )
                if result and not result.isError():
                    return True, result.bits
            elif function_code == FunctionCode.READ_HOLDING_REGISTERS:
                result = self.client.read_holding_registers(
                    start_address,
                    count=quantity,
                    device_id=device_id
                )
                if result and not result.isError():
                    return True, result.registers
            elif function_code == FunctionCode.READ_INPUT_REGISTERS:
                result = self.client.read_input_registers(
                    start_address,
                    count=quantity,
                    device_id=device_id
                )
                if result and not result.isError():
                    return True, result.registers
            
            return False, None
        except ModbusException:
            return False, None
        except Exception as e:
            logger.debug(f"Read test error for device {device_id}: {e}")
            return False, None
    
    def _scan_register_type(
        self,
        device_id: int,
        function_code: int,
        max_address: int = 100
    ) -> list[int]:
        """Scan a register type to find addresses with data"""
        found_addresses = []
        
        # Test in chunks to speed up scanning
        chunk_size = 20
        for start_addr in range(0, max_address, chunk_size):
            if not self.is_scanning:
                break
            
            quantity = min(chunk_size, max_address - start_addr)
            success, data = self._test_read(device_id, function_code, start_addr, quantity)
            
            if success and data:
                # Check if data is non-zero or non-default
                # For coils/discrete inputs, check if any are True
                # For registers, check if any are non-zero
                has_data = False
                if isinstance(data, list):
                    if len(data) > 0:
                        if isinstance(data[0], bool):
                            has_data = any(data)
                        else:
                            has_data = any(val != 0 for val in data)
                
                if has_data:
                    # Add individual addresses that have data
                    for i, val in enumerate(data):
                        addr = start_addr + i
                        if isinstance(val, bool):
                            if val:
                                found_addresses.append(addr)
                        else:
                            if val != 0:
                                found_addresses.append(addr)
            
            time.sleep(0.01)  # Small delay to avoid bus congestion
        
        return found_addresses
    
    def scan_device(self, device_id: int) -> Optional[DeviceInfo]:
        """Scan a single device ID"""
        if not self.is_scanning:
            return None
        
        device_info = DeviceInfo(device_id=device_id)
        
        # Test each function code
        function_codes = [
            (FunctionCode.READ_COILS, "coils"),
            (FunctionCode.READ_DISCRETE_INPUTS, "discrete inputs"),
            (FunctionCode.READ_HOLDING_REGISTERS, "holding registers"),
            (FunctionCode.READ_INPUT_REGISTERS, "input registers"),
        ]
        
        for func_code, name in function_codes:
            if not self.is_scanning:
                break
            
            self._update_progress(
                device_id,
                247,
                f"Scanning device {device_id}: {name}..."
            )
            
            success, data = self._test_read(device_id, func_code, 0, 10)
            
            if success:
                if func_code == FunctionCode.READ_COILS:
                    device_info.has_coils = True
                    device_info.coil_addresses = self._scan_register_type(
                        device_id, func_code, max_address=100
                    )
                elif func_code == FunctionCode.READ_DISCRETE_INPUTS:
                    device_info.has_discrete_inputs = True
                    device_info.discrete_input_addresses = self._scan_register_type(
                        device_id, func_code, max_address=100
                    )
                elif func_code == FunctionCode.READ_HOLDING_REGISTERS:
                    device_info.has_holding_registers = True
                    device_info.holding_register_addresses = self._scan_register_type(
                        device_id, func_code, max_address=100
                    )
                elif func_code == FunctionCode.READ_INPUT_REGISTERS:
                    device_info.has_input_registers = True
                    device_info.input_register_addresses = self._scan_register_type(
                        device_id, func_code, max_address=100
                    )
        
        # Only return device if we found something
        if (device_info.has_coils or device_info.has_discrete_inputs or
            device_info.has_holding_registers or device_info.has_input_registers):
            return device_info
        
        return None
    
    def scan(
        self,
        start_device_id: int = 1,
        end_device_id: int = 247
    ) -> list[DeviceInfo]:
        """Scan for devices in the specified range"""
        if not self.connect():
            return []
        
        self.is_scanning = True
        found_devices = []
        
        try:
            total_devices = end_device_id - start_device_id + 1
            current = 0
            
            for device_id in range(start_device_id, end_device_id + 1):
                if not self.is_scanning:
                    break
                
                current += 1
                self._update_progress(
                    current,
                    total_devices,
                    f"Scanning device ID {device_id}..."
                )
                
                device_info = self.scan_device(device_id)
                
                if device_info:
                    found_devices.append(device_info)
                    self._notify_device_found(device_info)
                
                time.sleep(0.05)  # Small delay between devices
            
            self._update_progress(total_devices, total_devices, "Scan complete")
            
        finally:
            self.is_scanning = False
            self.disconnect()
        
        return found_devices
    
    def stop(self):
        """Stop scanning"""
        self.is_scanning = False

