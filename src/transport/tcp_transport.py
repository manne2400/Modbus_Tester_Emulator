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
from src.models.trace_entry import TraceEntry, TraceDirection, TraceStatus
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
        
        # Extract request parameters for TX logging
        slave_id = kwargs.get('device_id', None)
        session_id = kwargs.pop('session_id', None)
        connection_name = kwargs.pop('connection_name', None)
        function_code = kwargs.pop('function_code', None)
        start_address = kwargs.pop('start_address', None)
        quantity = kwargs.pop('quantity', None)
        
        # Determine function code from function name if not provided
        if function_code is None:
            func_name = func.__name__ if hasattr(func, '__name__') else str(func)
            if 'read_coils' in func_name:
                function_code = 1
            elif 'read_discrete_inputs' in func_name:
                function_code = 2
            elif 'read_holding_registers' in func_name:
                function_code = 3
            elif 'read_input_registers' in func_name:
                function_code = 4
            elif 'write_coil' in func_name:
                function_code = 5
            elif 'write_register' in func_name:
                function_code = 6
            elif 'write_coils' in func_name:
                function_code = 15
            elif 'write_registers' in func_name:
                function_code = 16
        
        # Extract start_address and quantity from args if not in kwargs
        if start_address is None and len(args) > 0:
            start_address = args[0]
        if quantity is None:
            if len(args) > 1:
                quantity = args[1] if isinstance(args[1], int) else len(args[1]) if isinstance(args[1], (list, tuple)) else None
            elif 'count' in kwargs:
                quantity = kwargs.get('count')
        
        # Log TX trace entry
        if function_code is not None:
            tx_entry = TraceEntry(
                timestamp=datetime.now(),
                direction=TraceDirection.TX,
                session_id=session_id,
                connection_name=connection_name or self.profile.name,
                slave_id=slave_id,
                function_code=function_code,
                start_address=start_address,
                quantity=quantity,
                decoded_info=self._get_decoded_info(function_code, start_address, quantity, args, kwargs),
                status=TraceStatus.OK
            )
            self._trace(tx_entry)
        
        with self.request_lock:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                response_time = (time.time() - start_time) * 1000
                
                if result.isError():
                    error_msg = f"Modbus error: {result}"
                    logger.error(error_msg)
                    
                    # Log RX trace entry with error
                    rx_entry = TraceEntry(
                        timestamp=datetime.now(),
                        direction=TraceDirection.RX,
                        session_id=session_id,
                        connection_name=connection_name or self.profile.name,
                        slave_id=slave_id,
                        function_code=function_code,
                        status=TraceStatus.ERROR,
                        error_message=error_msg,
                        response_time_ms=response_time
                    )
                    self._trace(rx_entry)
                    
                    return None, error_msg
                
                # Log response
                hex_data = []
                if hasattr(result, 'bits') or hasattr(result, 'registers'):
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
                
                # Log RX trace entry
                rx_entry = TraceEntry(
                    timestamp=datetime.now(),
                    direction=TraceDirection.RX,
                    session_id=session_id,
                    connection_name=connection_name or self.profile.name,
                    slave_id=slave_id,
                    function_code=function_code,
                    start_address=start_address,
                    quantity=quantity,
                    raw_hex_string=bytes_to_hex_string(hex_data) if hex_data else None,
                    decoded_info=f"Response: {len(hex_data)} values" if hex_data else None,
                    status=TraceStatus.OK,
                    response_time_ms=response_time
                )
                self._trace(rx_entry)
                
                return result, None
            except ModbusException as e:
                error_msg = f"Modbus exception: {e}"
                logger.error(error_msg)
                
                # Determine exception code if available
                exception_code = None
                if hasattr(e, 'exception_code'):
                    exception_code = e.exception_code
                
                # Log RX trace entry with exception
                response_time = (time.time() - start_time) * 1000
                rx_entry = TraceEntry(
                    timestamp=datetime.now(),
                    direction=TraceDirection.RX,
                    session_id=session_id,
                    connection_name=connection_name or self.profile.name,
                    slave_id=slave_id,
                    function_code=function_code,
                    status=TraceStatus.EXCEPTION,
                    error_message=error_msg,
                    exception_code=exception_code,
                    response_time_ms=response_time
                )
                self._trace(rx_entry)
                
                return None, error_msg
            except Exception as e:
                error_msg = f"Request error: {e}"
                logger.error(error_msg)
                
                # Check if it's a timeout
                status = TraceStatus.TIMEOUT if "timeout" in str(e).lower() else TraceStatus.ERROR
                
                # Log RX trace entry with error
                response_time = (time.time() - start_time) * 1000
                rx_entry = TraceEntry(
                    timestamp=datetime.now(),
                    direction=TraceDirection.RX,
                    session_id=session_id,
                    connection_name=connection_name or self.profile.name,
                    slave_id=slave_id,
                    function_code=function_code,
                    status=status,
                    error_message=error_msg,
                    response_time_ms=response_time
                )
                self._trace(rx_entry)
                
                return None, error_msg
    
    def _get_decoded_info(self, function_code: int, start_address: Optional[int], quantity: Optional[int], args: tuple, kwargs: dict) -> str:
        """Get human-readable decoded info for request"""
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
        func_name = function_names.get(function_code, f"Function {function_code}")
        
        if start_address is not None:
            if quantity is not None:
                return f"{func_name}, start {start_address}, qty {quantity}"
            else:
                return f"{func_name}, address {start_address}"
        return func_name
    
    def read_coils(
        self,
        slave_id: int,
        start_address: int,
        quantity: int,
        session_id: Optional[str] = None
    ) -> tuple[Optional[list[bool]], Optional[str]]:
        """Read coils"""
        result, error = self._execute_request(
            self.client.read_coils,
            start_address,
            count=quantity,
            device_id=slave_id,
            session_id=session_id,
            connection_name=self.profile.name,
            function_code=1,
            start_address=start_address,
            quantity=quantity
        )
        if error:
            return None, error
        return result.bits if result else None, None
    
    def read_discrete_inputs(
        self,
        slave_id: int,
        start_address: int,
        quantity: int,
        session_id: Optional[str] = None
    ) -> tuple[Optional[list[bool]], Optional[str]]:
        """Read discrete inputs"""
        result, error = self._execute_request(
            self.client.read_discrete_inputs,
            start_address,
            count=quantity,
            device_id=slave_id,
            session_id=session_id,
            connection_name=self.profile.name,
            function_code=2,
            start_address=start_address,
            quantity=quantity
        )
        if error:
            return None, error
        return result.bits if result else None, None
    
    def read_holding_registers(
        self,
        slave_id: int,
        start_address: int,
        quantity: int,
        session_id: Optional[str] = None
    ) -> tuple[Optional[list[int]], Optional[str]]:
        """Read holding registers"""
        result, error = self._execute_request(
            self.client.read_holding_registers,
            start_address,
            count=quantity,
            device_id=slave_id,
            session_id=session_id,
            connection_name=self.profile.name,
            function_code=3,
            start_address=start_address,
            quantity=quantity
        )
        if error:
            return None, error
        return result.registers if result else None, None
    
    def read_input_registers(
        self,
        slave_id: int,
        start_address: int,
        quantity: int,
        session_id: Optional[str] = None
    ) -> tuple[Optional[list[int]], Optional[str]]:
        """Read input registers"""
        result, error = self._execute_request(
            self.client.read_input_registers,
            start_address,
            count=quantity,
            device_id=slave_id,
            session_id=session_id,
            connection_name=self.profile.name,
            function_code=4,
            start_address=start_address,
            quantity=quantity
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
