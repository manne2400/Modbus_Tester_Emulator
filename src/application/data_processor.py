"""Data processor for type conversion, scaling, and endianness"""
import struct
from typing import List, Any, Union
from src.models.tag_definition import DataType, ByteOrder
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataProcessor:
    """Process raw Modbus data with type conversion and scaling"""
    
    @staticmethod
    def decode_value(
        registers: List[int],
        data_type: DataType,
        byte_order: ByteOrder,
        start_index: int = 0
    ) -> Any:
        """Decode value from registers based on data type and byte order"""
        try:
            if data_type == DataType.BOOL:
                return bool(registers[start_index] != 0)
            
            elif data_type == DataType.UINT16:
                return registers[start_index]
            
            elif data_type == DataType.INT16:
                value = registers[start_index]
                if value > 32767:
                    value = value - 65536
                return value
            
            elif data_type == DataType.UINT32:
                if start_index + 1 >= len(registers):
                    raise ValueError("Not enough registers for UINT32")
                word1, word2 = registers[start_index], registers[start_index + 1]
                
                if byte_order == ByteOrder.BIG_ENDIAN:
                    value = (word1 << 16) | word2
                elif byte_order == ByteOrder.LITTLE_ENDIAN:
                    value = (word2 << 16) | word1
                else:  # SWAPPED
                    value = ((word1 & 0xFF) << 24) | ((word1 & 0xFF00) << 8) | \
                            ((word2 & 0xFF) << 8) | (word2 & 0xFF00) >> 8
                return value
            
            elif data_type == DataType.INT32:
                if start_index + 1 >= len(registers):
                    raise ValueError("Not enough registers for INT32")
                word1, word2 = registers[start_index], registers[start_index + 1]
                
                if byte_order == ByteOrder.BIG_ENDIAN:
                    value = (word1 << 16) | word2
                elif byte_order == ByteOrder.LITTLE_ENDIAN:
                    value = (word2 << 16) | word1
                else:  # SWAPPED
                    value = ((word1 & 0xFF) << 24) | ((word1 & 0xFF00) << 8) | \
                            ((word2 & 0xFF) << 8) | (word2 & 0xFF00) >> 8
                
                # Convert to signed
                if value > 2147483647:
                    value = value - 4294967296
                return value
            
            elif data_type == DataType.FLOAT32:
                if start_index + 1 >= len(registers):
                    raise ValueError("Not enough registers for FLOAT32")
                word1, word2 = registers[start_index], registers[start_index + 1]
                
                # Convert to bytes
                if byte_order == ByteOrder.BIG_ENDIAN:
                    bytes_data = struct.pack('>HH', word1, word2)
                elif byte_order == ByteOrder.LITTLE_ENDIAN:
                    bytes_data = struct.pack('<HH', word2, word1)
                else:  # SWAPPED
                    bytes_data = struct.pack('>HH', word1, word2)
                    # Swap bytes within words
                    bytes_data = bytes_data[1:2] + bytes_data[0:1] + bytes_data[3:4] + bytes_data[2:3]
                
                return struct.unpack('>f', bytes_data)[0]
            
            else:
                return registers[start_index]
        
        except Exception as e:
            logger.error(f"Error decoding value: {e}")
            return None
    
    @staticmethod
    def apply_scaling(value: Any, scale_factor: float, scale_offset: float) -> float:
        """Apply scaling to a value"""
        try:
            if value is None:
                return 0.0
            return float(value) * scale_factor + scale_offset
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def decode_register_range(
        registers: List[int],
        data_type: DataType,
        byte_order: ByteOrder,
        start_address: int,
        quantity: int
    ) -> List[Any]:
        """Decode a range of registers"""
        decoded = []
        
        if data_type in [DataType.BOOL, DataType.UINT16, DataType.INT16]:
            # Each register is one value
            for i in range(min(quantity, len(registers))):
                decoded.append(
                    DataProcessor.decode_value(registers, data_type, byte_order, i)
                )
        
        elif data_type in [DataType.UINT32, DataType.INT32, DataType.FLOAT32]:
            # Each value uses 2 registers
            num_values = min(quantity // 2, len(registers) // 2)
            for i in range(num_values):
                decoded.append(
                    DataProcessor.decode_value(registers, data_type, byte_order, i * 2)
                )
        
        return decoded
    
    @staticmethod
    def encode_value(
        value: Any,
        data_type: DataType,
        byte_order: ByteOrder
    ) -> List[int]:
        """Encode value to registers for writing"""
        try:
            if data_type == DataType.BOOL:
                return [1 if value else 0]
            
            elif data_type == DataType.UINT16:
                return [int(value) & 0xFFFF]
            
            elif data_type == DataType.INT16:
                val = int(value)
                if val < 0:
                    val = val + 65536
                return [val & 0xFFFF]
            
            elif data_type == DataType.UINT32:
                val = int(value) & 0xFFFFFFFF
                word1 = (val >> 16) & 0xFFFF
                word2 = val & 0xFFFF
                
                if byte_order == ByteOrder.BIG_ENDIAN:
                    return [word1, word2]
                elif byte_order == ByteOrder.LITTLE_ENDIAN:
                    return [word2, word1]
                else:  # SWAPPED
                    return [word1, word2]  # Simplified
            
            elif data_type == DataType.INT32:
                val = int(value)
                if val < 0:
                    val = val + 4294967296
                word1 = (val >> 16) & 0xFFFF
                word2 = val & 0xFFFF
                
                if byte_order == ByteOrder.BIG_ENDIAN:
                    return [word1, word2]
                elif byte_order == ByteOrder.LITTLE_ENDIAN:
                    return [word2, word1]
                else:  # SWAPPED
                    return [word1, word2]  # Simplified
            
            elif data_type == DataType.FLOAT32:
                val = float(value)
                bytes_data = struct.pack('>f', val)
                
                if byte_order == ByteOrder.BIG_ENDIAN:
                    word1 = (bytes_data[0] << 8) | bytes_data[1]
                    word2 = (bytes_data[2] << 8) | bytes_data[3]
                    return [word1, word2]
                elif byte_order == ByteOrder.LITTLE_ENDIAN:
                    word1 = (bytes_data[2] << 8) | bytes_data[3]
                    word2 = (bytes_data[0] << 8) | bytes_data[1]
                    return [word1, word2]
                else:  # SWAPPED
                    word1 = (bytes_data[0] << 8) | bytes_data[1]
                    word2 = (bytes_data[2] << 8) | bytes_data[3]
                    return [word1, word2]
            
            else:
                return [int(value) & 0xFFFF]
        
        except Exception as e:
            logger.error(f"Error encoding value: {e}")
            return [0]
