"""Modbus protocol wrapper"""
from typing import Optional, Union
from src.transport.base_transport import BaseTransport
from src.protocol.function_codes import FunctionCode, is_read_function, is_write_function
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ModbusProtocol:
    """Modbus protocol wrapper that abstracts transport layer"""
    
    def __init__(self, transport: BaseTransport):
        """Initialize protocol with transport"""
        self.transport = transport
    
    def execute_read(
        self,
        function_code: int,
        slave_id: int,
        start_address: int,
        quantity: int,
        session_id: Optional[str] = None
    ) -> tuple[Optional[Union[list[bool], list[int]]], Optional[str]]:
        """Execute read operation"""
        if not is_read_function(function_code):
            return None, f"Invalid read function code: {function_code}"
        
        try:
            if function_code == FunctionCode.READ_COILS:
                return self.transport.read_coils(slave_id, start_address, quantity, session_id)
            elif function_code == FunctionCode.READ_DISCRETE_INPUTS:
                return self.transport.read_discrete_inputs(slave_id, start_address, quantity, session_id)
            elif function_code == FunctionCode.READ_HOLDING_REGISTERS:
                return self.transport.read_holding_registers(slave_id, start_address, quantity, session_id)
            elif function_code == FunctionCode.READ_INPUT_REGISTERS:
                return self.transport.read_input_registers(slave_id, start_address, quantity, session_id)
            else:
                return None, f"Unsupported read function code: {function_code}"
        except Exception as e:
            logger.error(f"Read operation error: {e}")
            return None, str(e)
    
    def execute_write(
        self,
        function_code: int,
        slave_id: int,
        start_address: int,
        values: Union[bool, int, list[bool], list[int]]
    ) -> tuple[bool, Optional[str]]:
        """Execute write operation"""
        if not is_write_function(function_code):
            return False, f"Invalid write function code: {function_code}"
        
        try:
            if function_code == FunctionCode.WRITE_SINGLE_COIL:
                if not isinstance(values, bool):
                    return False, "Write single coil requires bool value"
                return self.transport.write_single_coil(slave_id, start_address, values)
            
            elif function_code == FunctionCode.WRITE_SINGLE_REGISTER:
                if not isinstance(values, int):
                    return False, "Write single register requires int value"
                return self.transport.write_single_register(slave_id, start_address, values)
            
            elif function_code == FunctionCode.WRITE_MULTIPLE_COILS:
                if not isinstance(values, list) or not all(isinstance(v, bool) for v in values):
                    return False, "Write multiple coils requires list of bool"
                return self.transport.write_multiple_coils(slave_id, start_address, values)
            
            elif function_code == FunctionCode.WRITE_MULTIPLE_REGISTERS:
                if not isinstance(values, list) or not all(isinstance(v, int) for v in values):
                    return False, "Write multiple registers requires list of int"
                return self.transport.write_multiple_registers(slave_id, start_address, values)
            
            else:
                return False, f"Unsupported write function code: {function_code}"
        except Exception as e:
            logger.error(f"Write operation error: {e}")
            return False, str(e)
