"""Excel export utilities for templates and sessions"""
from pathlib import Path
from typing import List
import pandas as pd
from src.models.tag_definition import TagDefinition
from src.models.device_template import DeviceTemplate
from src.models.session_definition import SessionDefinition
from src.utils.logger import get_logger

logger = get_logger(__name__)


def export_tags_to_excel(
    file_path: Path,
    tags: List[TagDefinition],
    sheet_name: str = "Tags"
) -> bool:
    """Export tags to Excel file
    
    Args:
        file_path: Path to Excel file
        tags: List of tags to export
        sheet_name: Name of sheet to create
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create DataFrame
        data = {
            "Address Type": [tag.address_type.value for tag in tags],
            "Address": [tag.address for tag in tags],
            "Name": [tag.name for tag in tags],
            "Data Type": [tag.data_type.value for tag in tags],
            "Byte Order": [tag.byte_order.value for tag in tags],
            "Scale Factor": [tag.scale_factor for tag in tags],
            "Scale Offset": [tag.scale_offset for tag in tags],
            "Unit": [tag.unit for tag in tags]
        }
        
        df = pd.DataFrame(data)
        
        # Write to Excel
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        logger.info(f"Exported {len(tags)} tags to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to export tags to Excel: {e}")
        return False


def export_template_to_excel(
    file_path: Path,
    template: DeviceTemplate,
    sheet_name: str = "Tags"
) -> bool:
    """Export template to Excel file
    
    Args:
        file_path: Path to Excel file
        template: Template to export
        sheet_name: Name of sheet to create
    
    Returns:
        True if successful, False otherwise
    """
    return export_tags_to_excel(file_path, template.tags, sheet_name)


def export_session_to_excel(
    file_path: Path,
    session: SessionDefinition,
    sheet_name: str = "Tags"
) -> bool:
    """Export session tags to Excel file
    
    Args:
        file_path: Path to Excel file
        session: Session to export
        sheet_name: Name of sheet to create
    
    Returns:
        True if successful, False otherwise
    """
    return export_tags_to_excel(file_path, session.tags, sheet_name)

