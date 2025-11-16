"""Hex dump formatting utilities"""
from typing import List, Union


def bytes_to_hex_string(data: Union[bytes, List[int]], separator: str = " ") -> str:
    """Convert bytes or list of integers to hex string"""
    if isinstance(data, bytes):
        return separator.join(f"{b:02X}" for b in data)
    elif isinstance(data, list):
        return separator.join(f"{b:02X}" for b in data)
    else:
        return ""


def format_hex_dump(data: Union[bytes, List[int]], bytes_per_line: int = 16) -> str:
    """Format data as a hex dump with ASCII representation"""
    if isinstance(data, bytes):
        data_list = list(data)
    elif isinstance(data, list):
        data_list = data
    else:
        return ""
    
    lines = []
    for i in range(0, len(data_list), bytes_per_line):
        chunk = data_list[i:i + bytes_per_line]
        
        # Hex representation
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        hex_part = hex_part.ljust(bytes_per_line * 3 - 1)
        
        # ASCII representation
        ascii_part = "".join(
            chr(b) if 32 <= b < 127 else "."
            for b in chunk
        )
        
        lines.append(f"{i:08X}  {hex_part}  |{ascii_part}|")
    
    return "\n".join(lines)


def hex_string_to_bytes(hex_string: str) -> bytes:
    """Convert hex string to bytes"""
    # Remove spaces and separators
    hex_string = hex_string.replace(" ", "").replace("-", "").replace(":", "")
    
    try:
        return bytes.fromhex(hex_string)
    except ValueError:
        return b""
