"""TCP Scanner for discovering Modbus TCP devices"""
import time
import ipaddress
from dataclasses import dataclass
from typing import Optional, Callable
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from src.protocol.function_codes import FunctionCode
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TcpDeviceInfo:
    """Information about a discovered Modbus TCP device"""
    ip_address: str
    port: int
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


class TcpScanner:
    """Scans network for Modbus TCP devices"""
    
    def __init__(
        self,
        timeout: float = 1.0
    ):
        """Initialize scanner with timeout"""
        self.timeout = timeout
        self.client: Optional[ModbusTcpClient] = None
        self.is_scanning = False
        self.progress_callback: Optional[Callable[[int, int, str], None]] = None  # (current, total, status)
        self.result_callback: Optional[Callable[[TcpDeviceInfo], None]] = None  # Called when device found
    
    def set_progress_callback(self, callback: Callable[[int, int, str], None]):
        """Set callback for progress updates (current, total, status)"""
        self.progress_callback = callback
    
    def set_result_callback(self, callback: Callable[[TcpDeviceInfo], None]):
        """Set callback for when a device is found"""
        self.result_callback = callback
    
    def _update_progress(self, current: int, total: int, status: str = ""):
        """Update progress"""
        if self.progress_callback:
            self.progress_callback(current, total, status)
    
    def _notify_device_found(self, device_info: TcpDeviceInfo):
        """Notify that a device was found"""
        if self.result_callback:
            self.result_callback(device_info)
    
    def _test_connection(self, ip_address: str, port: int) -> bool:
        """Test if we can establish a TCP connection to IP:port (quick test)"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)  # Shorter timeout for quick connection test
            result = sock.connect_ex((ip_address, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def _test_read(
        self,
        ip_address: str,
        port: int,
        device_id: int,
        function_code: int,
        start_address: int,
        quantity: int = 10
    ) -> tuple[bool, Optional[list]]:
        """Test reading from a device"""
        try:
            client = ModbusTcpClient(host=ip_address, port=port, timeout=self.timeout)
            if not client.connect():
                return False, None
            
            try:
                if function_code == FunctionCode.READ_COILS:
                    result = client.read_coils(
                        start_address,
                        count=quantity,
                        device_id=device_id
                    )
                    if result and not result.isError():
                        return True, result.bits
                elif function_code == FunctionCode.READ_DISCRETE_INPUTS:
                    result = client.read_discrete_inputs(
                        start_address,
                        count=quantity,
                        device_id=device_id
                    )
                    if result and not result.isError():
                        return True, result.bits
                elif function_code == FunctionCode.READ_HOLDING_REGISTERS:
                    result = client.read_holding_registers(
                        start_address,
                        count=quantity,
                        device_id=device_id
                    )
                    if result and not result.isError():
                        return True, result.registers
                elif function_code == FunctionCode.READ_INPUT_REGISTERS:
                    result = client.read_input_registers(
                        start_address,
                        count=quantity,
                        device_id=device_id
                    )
                    if result and not result.isError():
                        return True, result.registers
                
                return False, None
            finally:
                client.close()
        except ModbusException:
            return False, None
        except Exception as e:
            logger.debug(f"Read test error for {ip_address}:{port} device {device_id}: {e}")
            return False, None
    
    def _scan_register_type(
        self,
        ip_address: str,
        port: int,
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
            success, data = self._test_read(ip_address, port, device_id, function_code, start_addr, quantity)
            
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
            
            time.sleep(0.01)  # Small delay to avoid network congestion
        
        return found_addresses
    
    def scan_device(
        self,
        ip_address: str,
        port: int,
        device_id: int
    ) -> Optional[TcpDeviceInfo]:
        """Scan a single device at IP:port with device ID"""
        if not self.is_scanning:
            return None
        
        device_info = TcpDeviceInfo(
            ip_address=ip_address,
            port=port,
            device_id=device_id
        )
        
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
                0,
                1,
                f"Scanning {ip_address}:{port} device {device_id}: {name}..."
            )
            
            success, data = self._test_read(ip_address, port, device_id, func_code, 0, 10)
            
            if success:
                if func_code == FunctionCode.READ_COILS:
                    device_info.has_coils = True
                    device_info.coil_addresses = self._scan_register_type(
                        ip_address, port, device_id, func_code, max_address=100
                    )
                elif func_code == FunctionCode.READ_DISCRETE_INPUTS:
                    device_info.has_discrete_inputs = True
                    device_info.discrete_input_addresses = self._scan_register_type(
                        ip_address, port, device_id, func_code, max_address=100
                    )
                elif func_code == FunctionCode.READ_HOLDING_REGISTERS:
                    device_info.has_holding_registers = True
                    device_info.holding_register_addresses = self._scan_register_type(
                        ip_address, port, device_id, func_code, max_address=100
                    )
                elif func_code == FunctionCode.READ_INPUT_REGISTERS:
                    device_info.has_input_registers = True
                    device_info.input_register_addresses = self._scan_register_type(
                        ip_address, port, device_id, func_code, max_address=100
                    )
        
        # Only return device if we found something
        if (device_info.has_coils or device_info.has_discrete_inputs or
            device_info.has_holding_registers or device_info.has_input_registers):
            return device_info
        
        return None
    
    def _parse_ip_range(self, ip_range: str) -> list[str]:
        """Parse IP range string (e.g., '192.168.1.1-254' or '192.168.1.0/24')"""
        ip_list = []
        try:
            # Try CIDR notation first
            if '/' in ip_range:
                network = ipaddress.ip_network(ip_range, strict=False)
                for ip in network.hosts():  # Exclude network and broadcast
                    ip_list.append(str(ip))
            # Try range notation (e.g., 192.168.1.1-254)
            elif '-' in ip_range:
                parts = ip_range.split('.')
                if len(parts) == 4:
                    base = '.'.join(parts[:3])
                    last_part = parts[3]
                    if '-' in last_part:
                        start, end = last_part.split('-')
                        start_ip = int(start)
                        end_ip = int(end)
                        for i in range(start_ip, end_ip + 1):
                            ip_list.append(f"{base}.{i}")
                    else:
                        ip_list.append(ip_range)
                else:
                    ip_list.append(ip_range)
            # Single IP
            else:
                ip_list.append(ip_range)
        except Exception as e:
            logger.error(f"Error parsing IP range '{ip_range}': {e}")
            ip_list = [ip_range]
        
        return ip_list
    
    def scan(
        self,
        ip_range: str,
        ports: list[int],
        start_device_id: int = 1,
        end_device_id: int = 247
    ) -> list[TcpDeviceInfo]:
        """Scan for devices in the specified IP range, ports, and device ID range"""
        self.is_scanning = True
        found_devices = []
        
        try:
            # Parse IP range
            ip_addresses = self._parse_ip_range(ip_range)
            
            total_combinations = len(ip_addresses) * len(ports) * (end_device_id - start_device_id + 1)
            current = 0
            
            for ip_address in ip_addresses:
                if not self.is_scanning:
                    break
                
                for port in ports:
                    if not self.is_scanning:
                        break
                    
                    # First, do a quick TCP connection test
                    self._update_progress(
                        current,
                        total_combinations,
                        f"Testing {ip_address}:{port}..."
                    )
                    
                    if not self._test_connection(ip_address, port):
                        # No TCP connection possible, skip all device IDs for this IP:port
                        current += (end_device_id - start_device_id + 1)
                        continue
                    
                    # Found a responsive Modbus TCP server, scan device IDs
                    for device_id in range(start_device_id, end_device_id + 1):
                        if not self.is_scanning:
                            break
                        
                        current += 1
                        self._update_progress(
                            current,
                            total_combinations,
                            f"Scanning {ip_address}:{port} device ID {device_id}..."
                        )
                        
                        device_info = self.scan_device(ip_address, port, device_id)
                        
                        if device_info:
                            found_devices.append(device_info)
                            self._notify_device_found(device_info)
                        
                        time.sleep(0.05)  # Small delay between device IDs
            
            self._update_progress(total_combinations, total_combinations, "Scan complete")
            
        finally:
            self.is_scanning = False
        
        return found_devices
    
    def stop(self):
        """Stop scanning"""
        self.is_scanning = False

