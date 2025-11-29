"""Modbus function codes"""
from enum import IntEnum
from typing import Optional


class FunctionCode(IntEnum):
    """Modbus function codes"""
    READ_COILS = 0x01
    READ_DISCRETE_INPUTS = 0x02
    READ_HOLDING_REGISTERS = 0x03
    READ_INPUT_REGISTERS = 0x04
    WRITE_SINGLE_COIL = 0x05
    WRITE_SINGLE_REGISTER = 0x06
    WRITE_MULTIPLE_COILS = 0x0F
    WRITE_MULTIPLE_REGISTERS = 0x10


# Function code names for display
FUNCTION_CODE_NAMES = {
    FunctionCode.READ_COILS: "Read Coils",
    FunctionCode.READ_DISCRETE_INPUTS: "Read Discrete Inputs",
    FunctionCode.READ_HOLDING_REGISTERS: "Read Holding Registers",
    FunctionCode.READ_INPUT_REGISTERS: "Read Input Registers",
    FunctionCode.WRITE_SINGLE_COIL: "Write Single Coil",
    FunctionCode.WRITE_SINGLE_REGISTER: "Write Single Register",
    FunctionCode.WRITE_MULTIPLE_COILS: "Write Multiple Coils",
    FunctionCode.WRITE_MULTIPLE_REGISTERS: "Write Multiple Registers",
}


def is_read_function(function_code: int) -> bool:
    """Check if function code is a read operation"""
    return function_code in [
        FunctionCode.READ_COILS,
        FunctionCode.READ_DISCRETE_INPUTS,
        FunctionCode.READ_HOLDING_REGISTERS,
        FunctionCode.READ_INPUT_REGISTERS
    ]


def is_write_function(function_code: int) -> bool:
    """Check if function code is a write operation"""
    return function_code in [
        FunctionCode.WRITE_SINGLE_COIL,
        FunctionCode.WRITE_SINGLE_REGISTER,
        FunctionCode.WRITE_MULTIPLE_COILS,
        FunctionCode.WRITE_MULTIPLE_REGISTERS
    ]


def get_read_function_for_write(function_code: int) -> Optional[int]:
    """Convert write function code to corresponding read function code for polling"""
    """Returns None if function code is not a write operation"""
    write_to_read_map = {
        FunctionCode.WRITE_SINGLE_COIL: FunctionCode.READ_COILS,
        FunctionCode.WRITE_SINGLE_REGISTER: FunctionCode.READ_HOLDING_REGISTERS,
        FunctionCode.WRITE_MULTIPLE_COILS: FunctionCode.READ_COILS,
        FunctionCode.WRITE_MULTIPLE_REGISTERS: FunctionCode.READ_HOLDING_REGISTERS,
    }
    return write_to_read_map.get(function_code)