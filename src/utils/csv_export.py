"""CSV export utilities for templates and sessions"""
import csv
from pathlib import Path
from typing import List
from src.models.tag_definition import TagDefinition
from src.models.device_template import DeviceTemplate
from src.models.session_definition import SessionDefinition
from src.utils.logger import get_logger

logger = get_logger(__name__)


def export_tags_to_csv(
    file_path: Path,
    tags: List[TagDefinition],
    include_header: bool = True
) -> bool:
    """Export tags to CSV file
    
    Args:
        file_path: Path to CSV file
        tags: List of tags to export
        include_header: Whether to include header row
    
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            if include_header:
                writer.writerow([
                    "Address Type",
                    "Address",
                    "Name",
                    "Data Type",
                    "Byte Order",
                    "Scale Factor",
                    "Scale Offset",
                    "Unit"
                ])
            
            for tag in tags:
                writer.writerow([
                    tag.address_type.value,
                    tag.address,
                    tag.name,
                    tag.data_type.value,
                    tag.byte_order.value,
                    tag.scale_factor,
                    tag.scale_offset,
                    tag.unit
                ])
        
        logger.info(f"Exported {len(tags)} tags to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to export tags to CSV: {e}")
        return False


def export_template_to_csv(
    file_path: Path,
    template: DeviceTemplate,
    include_header: bool = True
) -> bool:
    """Export template to CSV file
    
    Args:
        file_path: Path to CSV file
        template: Template to export
        include_header: Whether to include header row
    
    Returns:
        True if successful, False otherwise
    """
    return export_tags_to_csv(file_path, template.tags, include_header)


def export_session_to_csv(
    file_path: Path,
    session: SessionDefinition,
    include_header: bool = True
) -> bool:
    """Export session tags to CSV file
    
    Args:
        file_path: Path to CSV file
        session: Session to export
        include_header: Whether to include header row
    
    Returns:
        True if successful, False otherwise
    """
    return export_tags_to_csv(file_path, session.tags, include_header)

