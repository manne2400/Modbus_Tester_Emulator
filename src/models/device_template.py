"""DeviceTemplate data model"""
from dataclasses import dataclass, field
from typing import List, Optional
from .tag_definition import TagDefinition


@dataclass
class DeviceTemplate:
    """Device template containing tag definitions for a device type"""
    name: str
    tags: List[TagDefinition] = field(default_factory=list)
    version: Optional[str] = None
    note: Optional[str] = None
    default_slave_id: Optional[int] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    category: Optional[str] = None  # e.g., "Pump", "VFD", "VAV", "CTS"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "tags": [tag.to_dict() for tag in self.tags],
            "version": self.version,
            "note": self.note,
            "default_slave_id": self.default_slave_id,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "category": self.category
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DeviceTemplate":
        """Create from dictionary"""
        return cls(
            name=data["name"],
            tags=[TagDefinition.from_dict(tag_data) for tag_data in data.get("tags", [])],
            version=data.get("version"),
            note=data.get("note"),
            default_slave_id=data.get("default_slave_id"),
            manufacturer=data.get("manufacturer"),
            model=data.get("model"),
            category=data.get("category")
        )
    
    def get_tag_count(self) -> int:
        """Get number of tags in template"""
        return len(self.tags)
    
    def get_display_name(self) -> str:
        """Get display name for template"""
        parts = []
        if self.manufacturer:
            parts.append(self.manufacturer)
        if self.model:
            parts.append(self.model)
        if parts:
            return f"{self.name} ({' '.join(parts)})"
        return self.name

