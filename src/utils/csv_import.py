"""CSV import utilities for templates and tags"""
import csv
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from src.models.tag_definition import TagDefinition, AddressType, DataType, ByteOrder
from src.models.device_template import DeviceTemplate
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CSVImportError(Exception):
    """Exception for CSV import errors"""
    pass


def import_tags_from_csv(
    file_path: Path,
    column_mapping: Dict[str, str],
    address_type: Optional[AddressType] = None
) -> List[TagDefinition]:
    """Import tags from CSV file
    
    Args:
        file_path: Path to CSV file
        column_mapping: Mapping from CSV column names to tag fields
            e.g., {"Address": "address", "Name": "name", "DataType": "data_type"}
        address_type: Address type to use for all tags (if not in CSV)
    
    Returns:
        List of TagDefinition objects
    
    Raises:
        CSVImportError: If import fails
    """
    tags = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Try to detect delimiter
            sample = f.read(1024)
            f.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(f, delimiter=delimiter)
            
            # Validate required columns
            required_fields = ["address"]
            csv_columns = reader.fieldnames
            if not csv_columns:
                raise CSVImportError("CSV file has no columns")
            
            # Check if required columns are mapped
            for field in required_fields:
                if field not in column_mapping.values():
                    raise CSVImportError(f"Required field '{field}' is not mapped")
            
            # Find CSV column for each field
            field_to_csv_column = {v: k for k, v in column_mapping.items()}
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                try:
                    # Get address
                    address_col = field_to_csv_column.get("address")
                    if not address_col or address_col not in row:
                        raise CSVImportError(f"Row {row_num}: Address column '{address_col}' not found")
                    
                    address_str = row[address_col].strip()
                    if not address_str:
                        continue  # Skip empty rows
                    
                    try:
                        address = int(address_str)
                    except ValueError:
                        logger.warning(f"Row {row_num}: Invalid address '{address_str}', skipping")
                        continue
                    
                    # Get name
                    name = ""
                    name_col = field_to_csv_column.get("name")
                    if name_col and name_col in row:
                        name = row[name_col].strip()
                    
                    # Get data type
                    data_type = DataType.UINT16
                    data_type_col = field_to_csv_column.get("data_type")
                    if data_type_col and data_type_col in row:
                        data_type_str = row[data_type_col].strip().upper()
                        data_type = _parse_data_type(data_type_str)
                    
                    # Get byte order
                    byte_order = ByteOrder.BIG_ENDIAN
                    byte_order_col = field_to_csv_column.get("byte_order")
                    if byte_order_col and byte_order_col in row:
                        byte_order_str = row[byte_order_col].strip()
                        byte_order = _parse_byte_order(byte_order_str)
                    
                    # Get scale factor
                    scale_factor = 1.0
                    scale_factor_col = field_to_csv_column.get("scale_factor")
                    if scale_factor_col and scale_factor_col in row:
                        try:
                            scale_factor = float(row[scale_factor_col].strip())
                        except ValueError:
                            pass
                    
                    # Get scale offset
                    scale_offset = 0.0
                    scale_offset_col = field_to_csv_column.get("scale_offset")
                    if scale_offset_col and scale_offset_col in row:
                        try:
                            scale_offset = float(row[scale_offset_col].strip())
                        except ValueError:
                            pass
                    
                    # Get unit
                    unit = ""
                    unit_col = field_to_csv_column.get("unit")
                    if unit_col and unit_col in row:
                        unit = row[unit_col].strip()
                    
                    # Get address type
                    tag_address_type = address_type or AddressType.HOLDING_REGISTER
                    address_type_col = field_to_csv_column.get("address_type")
                    if address_type_col and address_type_col in row:
                        address_type_str = row[address_type_col].strip()
                        tag_address_type = _parse_address_type(address_type_str)
                    
                    tag = TagDefinition(
                        address_type=tag_address_type,
                        address=address,
                        name=name or f"Address {address}",
                        data_type=data_type,
                        byte_order=byte_order,
                        scale_factor=scale_factor,
                        scale_offset=scale_offset,
                        unit=unit
                    )
                    
                    tags.append(tag)
                    
                except Exception as e:
                    logger.warning(f"Row {row_num}: Error parsing row: {e}")
                    continue
        
        logger.info(f"Imported {len(tags)} tags from {file_path}")
        return tags
        
    except Exception as e:
        raise CSVImportError(f"Failed to import CSV: {e}")


def _parse_data_type(data_type_str: str) -> DataType:
    """Parse data type string to DataType enum"""
    data_type_str = data_type_str.upper().strip()
    
    type_map = {
        "BOOL": DataType.BOOL,
        "BOOLEAN": DataType.BOOL,
        "INT16": DataType.INT16,
        "INT": DataType.INT16,
        "UINT16": DataType.UINT16,
        "UINT": DataType.UINT16,
        "WORD": DataType.UINT16,
        "INT32": DataType.INT32,
        "DINT": DataType.INT32,
        "UINT32": DataType.UINT32,
        "UDINT": DataType.UINT32,
        "DWORD": DataType.UINT32,
        "FLOAT32": DataType.FLOAT32,
        "FLOAT": DataType.FLOAT32,
        "REAL": DataType.FLOAT32
    }
    
    return type_map.get(data_type_str, DataType.UINT16)


def _parse_byte_order(byte_order_str: str) -> ByteOrder:
    """Parse byte order string to ByteOrder enum"""
    byte_order_str = byte_order_str.strip()
    
    if "big" in byte_order_str.lower() or "msb" in byte_order_str.lower():
        return ByteOrder.BIG_ENDIAN
    elif "little" in byte_order_str.lower() or "lsb" in byte_order_str.lower():
        return ByteOrder.LITTLE_ENDIAN
    elif "swap" in byte_order_str.lower():
        return ByteOrder.SWAPPED
    else:
        return ByteOrder.BIG_ENDIAN


def _parse_address_type(address_type_str: str) -> AddressType:
    """Parse address type string to AddressType enum"""
    address_type_str = address_type_str.upper().strip()
    
    type_map = {
        "COIL": AddressType.COIL,
        "COILS": AddressType.COIL,
        "DISCRETE_INPUT": AddressType.DISCRETE_INPUT,
        "DISCRETE_INPUTS": AddressType.DISCRETE_INPUT,
        "HOLDING_REGISTER": AddressType.HOLDING_REGISTER,
        "HOLDING_REGISTERS": AddressType.HOLDING_REGISTER,
        "INPUT_REGISTER": AddressType.INPUT_REGISTER,
        "INPUT_REGISTERS": AddressType.INPUT_REGISTER
    }
    
    return type_map.get(address_type_str, AddressType.HOLDING_REGISTER)


def detect_csv_columns(file_path: Path) -> List[str]:
    """Detect column names in CSV file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sample = f.read(1024)
            f.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(f, delimiter=delimiter)
            return list(reader.fieldnames) if reader.fieldnames else []
    except Exception as e:
        logger.error(f"Failed to detect CSV columns: {e}")
        return []

