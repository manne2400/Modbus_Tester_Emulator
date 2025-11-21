"""Excel import utilities for templates and tags"""
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
from src.models.tag_definition import TagDefinition, AddressType, DataType, ByteOrder
from src.utils.csv_import import _parse_data_type, _parse_byte_order, _parse_address_type
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExcelImportError(Exception):
    """Exception for Excel import errors"""
    pass


def import_tags_from_excel(
    file_path: Path,
    column_mapping: Dict[str, str],
    address_type: Optional[AddressType] = None,
    sheet_name: Optional[str] = None
) -> List[TagDefinition]:
    """Import tags from Excel file
    
    Args:
        file_path: Path to Excel file
        column_mapping: Mapping from Excel column names to tag fields
        address_type: Address type to use for all tags (if not in Excel)
        sheet_name: Name of sheet to read (None = first sheet)
    
    Returns:
        List of TagDefinition objects
    
    Raises:
        ExcelImportError: If import fails
    """
    tags = []
    
    try:
        # Read Excel file
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        if df.empty:
            raise ExcelImportError("Excel file is empty")
        
        # Validate required columns
        required_fields = ["address"]
        excel_columns = list(df.columns)
        
        if not excel_columns:
            raise ExcelImportError("Excel file has no columns")
        
        # Check if required columns are mapped
        for field in required_fields:
            if field not in column_mapping.values():
                raise ExcelImportError(f"Required field '{field}' is not mapped")
        
        # Find Excel column for each field
        field_to_excel_column = {v: k for k, v in column_mapping.items()}
        
        for row_num, (idx, row) in enumerate(df.iterrows(), start=2):  # Start at 2 (header is row 1)
            try:
                # Get address
                address_col = field_to_excel_column.get("address")
                if not address_col or address_col not in excel_columns:
                    raise ExcelImportError(f"Row {row_num}: Address column '{address_col}' not found")
                
                address_val = row[address_col]
                if pd.isna(address_val):
                    continue  # Skip empty rows
                
                try:
                    address = int(float(address_val))
                except (ValueError, TypeError):
                    logger.warning(f"Row {row_num}: Invalid address '{address_val}', skipping")
                    continue
                
                # Get name
                name = ""
                name_col = field_to_excel_column.get("name")
                if name_col and name_col in excel_columns:
                    name_val = row[name_col]
                    if not pd.isna(name_val):
                        name = str(name_val).strip()
                
                # Get data type
                data_type = DataType.UINT16
                data_type_col = field_to_excel_column.get("data_type")
                if data_type_col and data_type_col in excel_columns:
                    data_type_val = row[data_type_col]
                    if not pd.isna(data_type_val):
                        data_type = _parse_data_type(str(data_type_val))
                
                # Get byte order
                byte_order = ByteOrder.BIG_ENDIAN
                byte_order_col = field_to_excel_column.get("byte_order")
                if byte_order_col and byte_order_col in excel_columns:
                    byte_order_val = row[byte_order_col]
                    if not pd.isna(byte_order_val):
                        byte_order = _parse_byte_order(str(byte_order_val))
                
                # Get scale factor
                scale_factor = 1.0
                scale_factor_col = field_to_excel_column.get("scale_factor")
                if scale_factor_col and scale_factor_col in excel_columns:
                    scale_factor_val = row[scale_factor_col]
                    if not pd.isna(scale_factor_val):
                        try:
                            scale_factor = float(scale_factor_val)
                        except (ValueError, TypeError):
                            pass
                
                # Get scale offset
                scale_offset = 0.0
                scale_offset_col = field_to_excel_column.get("scale_offset")
                if scale_offset_col and scale_offset_col in excel_columns:
                    scale_offset_val = row[scale_offset_col]
                    if not pd.isna(scale_offset_val):
                        try:
                            scale_offset = float(scale_offset_val)
                        except (ValueError, TypeError):
                            pass
                
                # Get unit
                unit = ""
                unit_col = field_to_excel_column.get("unit")
                if unit_col and unit_col in excel_columns:
                    unit_val = row[unit_col]
                    if not pd.isna(unit_val):
                        unit = str(unit_val).strip()
                
                # Get address type
                tag_address_type = address_type or AddressType.HOLDING_REGISTER
                address_type_col = field_to_excel_column.get("address_type")
                if address_type_col and address_type_col in excel_columns:
                    address_type_val = row[address_type_col]
                    if not pd.isna(address_type_val):
                        tag_address_type = _parse_address_type(str(address_type_val))
                
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
        raise ExcelImportError(f"Failed to import Excel: {e}")


def detect_excel_columns(file_path: Path, sheet_name: Optional[str] = None) -> List[str]:
    """Detect column names in Excel file"""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=0)  # Read only header
        return list(df.columns)
    except Exception as e:
        logger.error(f"Failed to detect Excel columns: {e}")
        return []


def get_excel_sheet_names(file_path: Path) -> List[str]:
    """Get list of sheet names in Excel file"""
    try:
        xl_file = pd.ExcelFile(file_path)
        return xl_file.sheet_names
    except Exception as e:
        logger.error(f"Failed to get sheet names: {e}")
        return []

